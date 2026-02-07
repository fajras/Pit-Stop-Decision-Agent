from aiagents_pitstop_agent.infrastructure.models import SystemSettings
from aiagents_pitstop_agent.application.dto.retrain_status_response import (
    RetrainStatusResponse,
)


class RetrainDecisionService:
    def __init__(self, db):
        self.db = db

    def get_status(self) -> RetrainStatusResponse:
        settings = (
            self.db.query(SystemSettings)
            .order_by(SystemSettings.id)
            .first()
        )

        if settings is None or not settings.enabled:
            return RetrainStatusResponse(
                can_retrain=False,
                current=0,
                threshold=0,
                remaining=0,
                reason="Retraining disabled",
            )

        current = settings.new_experiences_since_train
        threshold = settings.retrain_threshold
        remaining = max(threshold - current, 0)

        return RetrainStatusResponse(
            can_retrain=current >= threshold,
            current=current,
            threshold=threshold,
            remaining=remaining,
        )
