from dataclasses import dataclass
from typing import Any, Dict, Optional
from fastapi import HTTPException


class DecisionStatus:
    READY = "READY"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    INVALID = "INVALID"
    PENDING_RETRAIN = "PENDING_RETRAIN"


class DecisionService:
    def __init__(self, decision_repo):
        self._repo = decision_repo

    def get_decision(self, task_id: str) -> Dict[str, Any]:
        decision = self._repo.get_decision(task_id)

        if decision is None:
            raise HTTPException(status_code=404, detail="Decision not ready")

        confidence = decision.expected_pit
        if confidence is None:
            confidence = decision.expected_stay

        return {
            "task_id": task_id,
            "status": DecisionStatus.READY,
            "payload": {
                "action": decision.action,
                "confidence": confidence,
                "reason": decision.reason,
                "suggestedTyre": decision.suggested_tyre,
            },
            "message": "Decision completed",
        }


    def _validate_state(self, status_value: str, decision_obj: Any) -> None:
        if status_value == DecisionStatus.INVALID:
            raise HTTPException(status_code=409, detail="Invalid decision state")

        if status_value == DecisionStatus.PENDING_RETRAIN:
            raise HTTPException(status_code=423, detail="Decision pending retrain")

        if status_value == DecisionStatus.FAILED:
            err = getattr(decision_obj, "error", None) or "Decision failed"
            raise HTTPException(status_code=500, detail=str(err))

    
