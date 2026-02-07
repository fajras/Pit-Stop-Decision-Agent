from pydantic import BaseModel


class RetrainStatusResponse(BaseModel):
    can_retrain: bool
    current: int
    threshold: int
    remaining: int
    reason: str | None = None
