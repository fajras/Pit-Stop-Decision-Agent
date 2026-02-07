from aiagents_pitstop_agent.infrastructure.models import Experience, SystemSettings

class RetrainDecisionService:
    def __init__(self, db):
        self.db = db

    def get_status(self):
        settings = (
            self.db.query(SystemSettings)
            .order_by(SystemSettings.id)
            .first()
        )

        if settings is None or not settings.enabled:
            return {
                "can_retrain": False,
                "current": 0,
                "threshold": 0,
                "remaining": 0,
                "reason": "Retraining disabled"
            }

        current = (
            self.db.query(Experience)
            .count()
        )

        threshold = settings.retrain_threshold
        remaining = threshold - current if current < threshold else 0

        return {
            "can_retrain": current >= threshold,
            "current": current,
            "threshold": threshold,
            "remaining": remaining
        }
