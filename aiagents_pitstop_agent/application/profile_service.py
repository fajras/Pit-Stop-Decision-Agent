from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..infrastructure.models import UserProfile

class ProfileService:
    def get_or_create(
        self,
        db: Session,
        user_id: str,
        is_temporary: bool = False
    ) -> UserProfile:
        prof = db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        ).scalars().first()

        if prof is None:
            prof = UserProfile(
                user_id=user_id,
                pit_bias=0.0,
                stay_bias=0.0,
                updates=0,
                is_temporary=is_temporary
            )
            db.add(prof)
            db.commit()
            db.refresh(prof)

        return prof

    def apply_feedback(
        self,
        db: Session,
        user_id: str,
        action: str,
        reward: float,
        alpha: float = 1
    ):
        prof = self.get_or_create(
            db,
            user_id,
            is_temporary=user_id.startswith("guest-")
        )

        if action == "PIT":
            prof.pit_bias = float(prof.pit_bias) + (alpha if reward > 0 else -alpha)
        else:
            prof.stay_bias = float(prof.stay_bias) + (alpha if reward > 0 else -alpha)

        prof.updates = int(prof.updates) + 1
        prof.updated_at = datetime.utcnow()

        db.commit()
