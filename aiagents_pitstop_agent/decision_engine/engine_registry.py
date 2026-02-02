import joblib
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..infrastructure.models import ModelVersion


class ModelRegistry:
    _loaded_version = None
    _model = None

    @classmethod
    def get_active_model(cls, db: Session):
        mv = db.execute(
            select(ModelVersion)
            .where(ModelVersion.active == True)
            .order_by(ModelVersion.id.desc())
            .limit(1)
        ).scalars().first()

        if mv is None:
            raise RuntimeError("No active model version")

        if cls._loaded_version != mv.version:
            cls._model = joblib.load(mv.path)
            cls._loaded_version = mv.version

        return cls._model, mv.version
