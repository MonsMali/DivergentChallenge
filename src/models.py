"""Pydantic models for structured data flowing between pipeline steps."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Account(BaseModel):
    company: str
    industry: str
    employees: Optional[int] = None
    region: str


class Deal(BaseModel):
    deal_id: int
    company: str
    stage: Optional[str] = None
    amount: float
    owner: str
    close_date: Optional[date] = None
    probability: float
    call_note: Optional[str] = None

    @field_validator("probability")
    @classmethod
    def probability_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        return v


class Activity(BaseModel):
    deal_id: int
    last_contact_days: int
    meetings: int
    email_threads: int


class EnrichedDeal(BaseModel):
    deal_id: int
    company: str
    stage: Optional[str] = None
    amount: float
    owner: str
    close_date: Optional[date] = None
    probability: float
    call_note: Optional[str] = None
    industry: Optional[str] = None
    employees: Optional[int] = None
    region: Optional[str] = None
    last_contact_days: Optional[int] = None
    meetings: Optional[int] = None
    email_threads: Optional[int] = None
    has_account_match: bool = False
    data_quality_flags: list[str] = Field(default_factory=list)
    risk_score: Optional[float] = None
    sentiment: Optional[str] = None

    @field_validator("probability")
    @classmethod
    def probability_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        return v


class DataQualityReport(BaseModel):
    total_deals: int
    complete_deals: int
    incomplete_deals: int
    missing_fields_summary: dict[str, int] = Field(default_factory=dict)
    orphaned_companies: list[str] = Field(default_factory=list)


class AnalysisPlan(BaseModel):
    relevant_deals: list[int] | str = Field(
        default="all",
        description="List of deal IDs to analyze, or 'all'",
    )
    analysis_type: str = Field(
        default="general",
        description="One of: risk, priority, actions, general",
    )
    filters_to_apply: dict = Field(default_factory=dict)
    reasoning: str = ""


class StepTokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0


class TokenUsage(BaseModel):
    steps: dict[str, StepTokenUsage] = Field(default_factory=dict)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0

    def add_step(self, name: str, input_tokens: int, output_tokens: int, cost: float) -> None:
        self.steps[name] = StepTokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost


class PipelineResult(BaseModel):
    query: str
    plan: AnalysisPlan
    enriched_deals: list[EnrichedDeal]
    synthesis: str
    data_quality: DataQualityReport
    token_usage: TokenUsage
