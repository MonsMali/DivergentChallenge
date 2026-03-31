"""Thin wrapper around the Anthropic SDK with token tracking."""

from __future__ import annotations

import json
import logging

import anthropic

from src.config import ANTHROPIC_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

# Pricing per million tokens (Claude Sonnet 4)
_INPUT_COST_PER_MTOK = 3.0
_OUTPUT_COST_PER_MTOK = 15.0

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
) -> tuple[str, dict]:
    """Call the Anthropic messages API and return (response_text, usage_dict).

    usage_dict contains: input_tokens, output_tokens, cost.
    """
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (input_tokens * _INPUT_COST_PER_MTOK / 1_000_000) + (
        output_tokens * _OUTPUT_COST_PER_MTOK / 1_000_000
    )
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": round(cost, 6),
    }
    logger.debug("LLM call: %d in / %d out / $%.6f", input_tokens, output_tokens, cost)
    return text, usage


def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
) -> tuple[dict | list, dict]:
    """Call the LLM expecting a JSON response. Retries once on parse failure."""
    full_system = (
        system_prompt
        + "\n\nRespond ONLY with valid JSON. No markdown fences, no preamble."
    )
    text, usage = call_llm(full_system, user_prompt, model)

    # Strip markdown fences if the model wraps anyway
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned), usage
    except json.JSONDecodeError:
        logger.warning("JSON parse failed, retrying with repair prompt")
        repair_prompt = (
            "Your previous response was not valid JSON. "
            "Here is what you returned:\n\n"
            f"{text}\n\n"
            "Please return ONLY the corrected valid JSON, nothing else."
        )
        text2, usage2 = call_llm(full_system, repair_prompt, model)
        # Merge usage
        merged_usage = {
            "input_tokens": usage["input_tokens"] + usage2["input_tokens"],
            "output_tokens": usage["output_tokens"] + usage2["output_tokens"],
            "cost": round(usage["cost"] + usage2["cost"], 6),
        }
        cleaned2 = text2.strip()
        if cleaned2.startswith("```"):
            cleaned2 = cleaned2.split("\n", 1)[1] if "\n" in cleaned2 else cleaned2[3:]
            if cleaned2.endswith("```"):
                cleaned2 = cleaned2[:-3].strip()
        return json.loads(cleaned2), merged_usage
