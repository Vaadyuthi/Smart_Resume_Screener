from pydantic import BaseModel
from pydantic import Field


class ScreeningRequest(BaseModel):

    job_description: str = Field(
        min_length=20
    )

    resume_ids: list[int] | None = None


class LLMResult(BaseModel):

    score: float = Field(
        ge=1,
        le=10
    )

    strengths: list[str] = []

    gaps: list[str] = []

    recommendation: str

    justification: str