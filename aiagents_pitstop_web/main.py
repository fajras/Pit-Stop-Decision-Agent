import json
from aiagents_pitstop_agent.application import retrain_decision_service
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from aiagents_pitstop_agent.runners.retrain_worker import RetrainWorker
from aiagents_pitstop_agent.infrastructure.db import engine, Base
from aiagents_pitstop_agent.application.training_service import TrainingService
from aiagents_pitstop_agent.infrastructure.models import Experience
from aiagents_pitstop_agent.infrastructure.decision_repository import DecisionRepository
from aiagents_pitstop_agent.application.decision_service import DecisionService
from aiagents_pitstop_agent.infrastructure.db import SessionLocal
from aiagents_pitstop_agent.infrastructure.models import Decision
from aiagents_pitstop_agent.application.profile_service import ProfileService
from aiagents_pitstop_agent.application.feedback_service import FeedbackService
from aiagents_pitstop_agent.infrastructure.models import UserProfile
from aiagents_pitstop_agent.runners.retrain_worker import retrain_event
from pathlib import Path
from aiagents_pitstop_agent.application.queue_service import QueueService
from .worker import run_loop
import asyncio

stop_event = asyncio.Event()
Base.metadata.create_all(bind=engine)

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent          
PROJECT_ROOT = BASE_DIR.parent                  
UI_DIR = PROJECT_ROOT / "ui"                 

if not UI_DIR.exists():
    raise RuntimeError(f"UI directory not found at {UI_DIR}")

app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

@app.get("/")
def serve_ui():
    return FileResponse(UI_DIR / "index.html")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_profile_service():
    return ProfileService()

def get_feedback_service(
    profiles: ProfileService = Depends(get_profile_service)
):
    return FeedbackService(profiles)



@app.post("/api/laps")
def submit_lap(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get("userId", "anon")
    q = QueueService()
    queue_id = q.enqueue(db, user_id, payload)
    return {"status": "Queued", "taskId": queue_id}



def get_decision_service(db: Session = Depends(get_db)) -> DecisionService:
    return DecisionService(DecisionRepository(db))


@app.get("/api/decisions/{task_id}")
def get_decision(
    task_id: int,
    service: DecisionService = Depends(get_decision_service)
):
    return service.get_decision(task_id)


@app.post("/api/feedback")
def submit_feedback(
    payload: dict,
    db: Session = Depends(get_db),
    feedback_service: FeedbackService = Depends(get_feedback_service),
):
    decision_id = int(payload["decisionId"])
    position_delta = int(payload["positionDelta"])
    return feedback_service.submit_feedback(db, decision_id, position_delta)


@app.get("/api/profile/{user_id}")
def get_profile(
    user_id: str,
    db: Session = Depends(get_db),
    profiles: ProfileService = Depends(get_profile_service),
):
    prof = profiles.get_or_create(db, user_id)
    return {
        "userId": prof.user_id,
        "pitBias": float(prof.pit_bias),
        "stayBias": float(prof.stay_bias),
        "updates": int(prof.updates),
    }

@app.post("/api/session/end")
def end_session(db: Session = Depends(get_db)):
    temp_users = db.query(UserProfile).filter(
        UserProfile.is_temporary == True
    ).all()

    for prof in temp_users:
        db.query(Decision).filter(Decision.user_id == prof.user_id).delete()
        db.query(Experience).filter(Experience.user_id == prof.user_id).delete()
        db.delete(prof)

    db.commit()
    return {"status": "session cleared"}



from threading import Event
from aiagents_pitstop_agent.runners.retrain_worker import RetrainWorker

retrain_stop_event = Event()

retrain_worker = RetrainWorker(
    training_service=TrainingService(),
    session_factory=SessionLocal,
    stop_event=retrain_stop_event
)

@app.on_event("startup")
async def startup_event():
    retrain_worker.start()
    asyncio.create_task(run_loop(stop_event))

@app.on_event("shutdown")
async def shutdown_event():
    stop_event.set()          
    retrain_stop_event.set()  

@app.get("/api/learning-stats/{user_id}")
def get_learning_stats(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Experience)
        .filter(Experience.user_id == user_id)
        .order_by(Experience.id)
        .all()
    )

    data = []
    total = 0.0

    for idx, e in enumerate(rows, start=1):
        total += e.reward
        avg = total / idx
        data.append({
            "step": idx,
            "avgReward": round(avg, 3)
        })

    return data



@app.get("/api/retrain/status")
def get_retrain_status(db: Session = Depends(get_db)):
    service = retrain_decision_service.RetrainDecisionService(db)
    return service.get_status()





@app.post("/api/retrain")
def retrain_agent(db: Session = Depends(get_db)):
    service = retrain_decision_service.RetrainDecisionService(db)
    status = service.get_status()

    if not status.can_retrain:
        return {"status": "skipped", "reason": "Not eligible"}

    retrain_event.set()
    return {"status": "scheduled"}




