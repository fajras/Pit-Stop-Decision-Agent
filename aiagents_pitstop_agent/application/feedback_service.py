from sqlalchemy.orm import Session
from sqlalchemy import select
from ..infrastructure.models import Decision, Experience, SystemSettings
from .profile_service import ProfileService

class FeedbackService:
    def __init__(self, profile_service: ProfileService):
        self._profiles = profile_service

    def submit_feedback(self, db: Session, decision_id: int, position_delta: int):
        decision = db.get(Decision, decision_id)
        if decision is None:
            raise ValueError("Decision not found")

        reward = float(position_delta)

        exp = Experience(
            decision_id=decision.id,
            user_id=decision.user_id,
            action=decision.action,
            reward=reward,
            lap_number=decision.lap_number,
            position=decision.position,
            tyre_life=decision.tyre_life,
            compound=decision.compound,
            lap_time_sec=decision.lap_time_sec,
        )
        db.add(exp)

        settings = db.execute(select(SystemSettings).limit(1)).scalars().first()
        if settings is None:
            settings = SystemSettings(enabled=True, new_experiences_since_train=0, retrain_threshold=20)
            db.add(settings)

        settings.new_experiences_since_train += 1

        self._profiles.apply_feedback(db, decision.user_id, decision.action, reward)

        db.commit()

        return {"stored": True, "reward": reward}
