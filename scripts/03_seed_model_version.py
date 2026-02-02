from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from aiagents_pitstop_agent.infrastructure.db import SessionLocal
from aiagents_pitstop_agent.infrastructure.models import ModelVersion, SystemSettings

def main():
    db: Session = SessionLocal()

    try:
        # Root projekta
        ROOT = Path(__file__).resolve().parents[1]
        model_path = ROOT / "models" / "pitstop_model.joblib"

        if not model_path.exists():
            raise RuntimeError(f"Model file not found at {model_path}")

        # 1. Deaktiviraj sve modele
        db.query(ModelVersion).update({ModelVersion.active: False})

        # 2. Dodaj novi aktivni model
        mv = ModelVersion(
            version="v1",
            path=str(model_path),
            active=True
        )
        db.add(mv)

        # 3. System settings
        settings = db.execute(
            select(SystemSettings).limit(1)
        ).scalars().first()

        if settings is None:
            db.add(SystemSettings(
                enabled=True,
                new_experiences_since_train=0,
                retrain_threshold=20
            ))

        db.commit()
        print("Seed done. Active model:", mv.path)

    finally:
        db.close()

if __name__ == "__main__":
    main()
