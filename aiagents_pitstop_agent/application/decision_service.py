from aiagents_pitstop_agent.infrastructure.decision_dto import DecisionResponse
from fastapi import HTTPException


class DecisionStatus:
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"


class DecisionService:

    def __init__(self, repo):
        self.repo = repo

    def get_decision(self, task_id: int) -> DecisionResponse:
        result = self.repo.get_with_state(task_id)

        if result is None:
            raise HTTPException(status_code=404, detail="Task not found")

        queue_item, decision = result

        # PENDING STATES
        if queue_item.status in ("Queued", "Processing"):
            return DecisionResponse(
                task_id=task_id,
                status=DecisionStatus.PENDING,
                message="Decision pending"
            )

        # FAILED STATE
        if queue_item.status == "Failed":
            raise HTTPException(
                status_code=500,
                detail=queue_item.error_text or "Decision failed"
            )

        # DONE STATE
        if queue_item.status == "Done":
            if decision is None:
                raise HTTPException(
                    status_code=500,
                    detail="Decision missing"
                )

            return DecisionResponse(
                task_id=task_id,
                status=DecisionStatus.READY,
                payload={
                    "action": decision.action,
                    "reason": decision.reason,
                    "suggestedTyre": decision.suggested_tyre,
                },
                message="Decision completed"
            )

        # INVALID STATE
        raise HTTPException(
            status_code=409,
            detail=f"Invalid decision state: {queue_item.status}"
        )
