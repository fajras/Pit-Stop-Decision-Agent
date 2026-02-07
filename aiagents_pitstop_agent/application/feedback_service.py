from sqlalchemy import select
from aiagents_pitstop_agent.application.profile_service import ProfileService
from aiagents_pitstop_agent.infrastructure.models import Decision, Experience, SystemSettings
from sqlalchemy.orm import Session

class FeedbackService:
    def __init__(self, profile_service: ProfileService):
        self._profiles = profile_service

    def submit_feedback(self, db: Session, decision_id: int, position_delta: int):
        decision = db.get(Decision, decision_id)
        if decision is None:
            return {
                "status": "skipped",
                "reason": "Decision not yet available"
            }

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

        settings = (
            db.execute(select(SystemSettings).limit(1))
            .scalars()
            .first()
        )
        if settings is not None:
            settings.new_experiences_since_train += 1

        self._profiles.apply_feedback(
            db,
            decision.user_id,
            decision.action,
            reward
        )

        db.commit()

        return {
            "status": "stored",
            "reward": reward
        }
