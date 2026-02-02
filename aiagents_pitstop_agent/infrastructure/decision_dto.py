from typing import Any, Dict, Optional
from pydantic import BaseModel


class DecisionResponse(BaseModel):
    task_id: str
    status: str
    payload: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
