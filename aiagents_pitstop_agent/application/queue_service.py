import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..infrastructure.models import LapQueueItem


class QueueService:

    def enqueue(self, db: Session, user_id: str, payload: dict) -> int:
        item = LapQueueItem(
            user_id=user_id,
            payload_json=json.dumps(payload),
            status="Queued"
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item.id

    def dequeue_next(self, db: Session) -> LapQueueItem | None:
        stmt = (
            select(LapQueueItem)
            .where(LapQueueItem.status == "Queued")
            .order_by(LapQueueItem.id)
            .limit(1)
        )

        item = db.execute(stmt).scalars().first()
        if item is None:
            return None

        item.status = "Processing"
        item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(item)
        return item

    def mark_done(self, db: Session, item: LapQueueItem, decision_id: int):
        item.status = "Done"
        item.decision_id = decision_id
        item.updated_at = datetime.utcnow()
        db.commit()

    def mark_failed(self, db: Session, item: LapQueueItem, error: str):
        item.status = "Failed"
        item.error_text = error
        item.updated_at = datetime.utcnow()
        db.commit()
