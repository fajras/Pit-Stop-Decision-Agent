from aiagents_pitstop_agent.infrastructure.models import Experience

RETRAIN_THRESHOLD = 20  

class RetrainDecisionService:
    def __init__(self, db):
        self.db = db

    def get_status(self):
        count = (
            self.db.query(Experience)
            .count()
        )

        remaining = max(0, RETRAIN_THRESHOLD - count)

        return {
            "can_retrain": count >= RETRAIN_THRESHOLD,
            "current": count,
            "threshold": RETRAIN_THRESHOLD,
            "remaining": remaining
        }
