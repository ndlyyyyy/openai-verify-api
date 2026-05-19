from __future__ import annotations

from pydantic import BaseModel


class OpenAIResult(BaseModel):
    type: str
    outcome: str
    issuer: str | None = None
    validation_state: str | None = None


class OpenAIUpstreamResponse(BaseModel):
    object: str
    created_at: int
    results: list[OpenAIResult]


class VerificationResponse(BaseModel):
    filename: str
    media_type: str | None = None
    openai_generated: bool
    upstream: OpenAIUpstreamResponse
