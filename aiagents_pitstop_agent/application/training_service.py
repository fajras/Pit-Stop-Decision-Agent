import os
import uuid
import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from sklearn.ensemble import RandomForestRegressor
from ..infrastructure.models import Experience, ModelVersion


class TrainingService:

    def train_and_activate(self, db: Session):
        experiences = db.execute(select(Experience)).scalars().all()
        if not experiences:
            return None

        df = pd.DataFrame([{
            "lap_number": e.lap_number,
            "position": e.position,
            "tyre_life": e.tyre_life,
            "compound": e.compound,
            "lap_time_sec": e.lap_time_sec,
            "action_flag": 1 if e.action == "PIT" else 0,
            "reward": e.reward,
        } for e in experiences])

        df["compound"] = df["compound"].astype("category").cat.codes

        X = df.drop(columns=["reward"])
        y = df["reward"]

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )
        model.fit(X, y)

        os.makedirs("models", exist_ok=True)

        version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        path = f"models/{version}.joblib"

        joblib.dump(model, path)

        db.execute(update(ModelVersion).values(active=False))
        db.add(ModelVersion(version=version, path=path, active=True))
        db.commit()

        return {
            "event": "MODEL_RETRAINED",
            "version": version,
            "samples": len(df)
        }
