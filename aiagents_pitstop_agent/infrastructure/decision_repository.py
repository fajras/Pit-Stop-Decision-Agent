from sqlalchemy.orm import Session
from aiagents_pitstop_agent.infrastructure.models import Decision, LapQueueItem


class DecisionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_with_state(self, task_id: int):
        return (
            self.db.query(LapQueueItem, Decision)
            .outerjoin(Decision, Decision.id == LapQueueItem.decision_id)
            .filter(LapQueueItem.id == task_id)
            .one_or_none()
        )
