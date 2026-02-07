from sqlalchemy.orm import Session
from sqlalchemy import select
from aiagents_core.software_agent import SoftwareAgent

from ..infrastructure.models import SystemSettings
from ..application.training_service import TrainingService
from .retrain_worker import retrain_event


class RetrainAgentRunner(
    SoftwareAgent[None, None, dict, None]
):

    def __init__(self, training: TrainingService):
        self._training = training

    def step(self, db: Session) -> dict | None:
        # ---------- SENSE ----------
        settings = db.execute(
            select(SystemSettings).limit(1)
        ).scalars().first()

        if settings is None:
            return None

        if not settings.enabled:
            return None

        if settings.new_experiences_since_train < settings.retrain_threshold:
            return None

        # ---------- THINK ----------
        # prag je pređen → retrain treba da se desi

        # ---------- ACT ----------
        if not retrain_event.is_set():
            retrain_event.set()

        # ---------- LEARN ----------
        settings.new_experiences_since_train = 0
        db.commit()

        return {"retrain_scheduled": True}
