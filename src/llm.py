"""Thin wrapper around the Anthropic SDK with token tracking."""

from __future__ import annotations

import json
import logging

import anthropic

from src.config import ANTHROPIC_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

# Pricing per million tokens by model family
_PRICING = {
    "sonnet": {"input": 3.0, "output": 15.0},
    "haiku": {"input": 0.8, "output": 4.0},
}


def _get_pricing(model: str) -> tuple[float, float]:
    if "haiku" in model:
        p = _PRICING["haiku"]
    else:
        p = _PRICING["sonnet"]
    return p["input"], p["output"]

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
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    input_cost, output_cost = _get_pricing(model)
    cost = (input_tokens * input_cost / 1_000_000) + (
        output_tokens * output_cost / 1_000_000
    )
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": round(cost, 6),
    }
    logger.debug("LLM call: %d in / %d out / $%.6f", input_tokens, output_tokens, cost)
    return text, usage


def _strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences that models sometimes add around JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


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

    try:
        return json.loads(_strip_markdown_fences(text)), usage
    except json.JSONDecodeError:
        logger.warning("JSON parse failed, retrying with repair prompt")
        repair_prompt = (
            "Your previous response was not valid JSON. "
            "Here is what you returned:\n\n"
            f"{text}\n\n"
            "Please return ONLY the corrected valid JSON, nothing else."
        )
        text2, usage2 = call_llm(full_system, repair_prompt, model)
        merged_usage = {
            "input_tokens": usage["input_tokens"] + usage2["input_tokens"],
            "output_tokens": usage["output_tokens"] + usage2["output_tokens"],
            "cost": round(usage["cost"] + usage2["cost"], 6),
        }
        return json.loads(_strip_markdown_fences(text2)), merged_usage
