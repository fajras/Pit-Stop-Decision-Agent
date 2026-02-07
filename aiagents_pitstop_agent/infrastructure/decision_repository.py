from sqlalchemy.orm import Session
from aiagents_pitstop_agent.infrastructure.models import Decision, LapQueueItem


class DecisionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_decision(self, task_id: str) -> Decision | None:
        queue_item = (
            self.db.query(LapQueueItem)
            .filter(LapQueueItem.id == int(task_id))
            .one_or_none()
        )

        if queue_item is None:
            return None

        if queue_item.decision_id is None:
            return None

        return (
            self.db.query(Decision)
            .filter(Decision.id == queue_item.decision_id)
            .one_or_none()
        )
