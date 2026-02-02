import time
from aiagents_pitstop_agent.infrastructure.db import SessionLocal
from aiagents_pitstop_agent.application.queue_service import QueueService
from aiagents_pitstop_agent.application.scoring_service import ScoringService
from aiagents_pitstop_agent.application.training_service import TrainingService
from aiagents_pitstop_agent.application.profile_service import ProfileService
from aiagents_pitstop_agent.application.policies.pitstop_policy import PitStopPolicy
from aiagents_pitstop_agent.decision_engine.engine_registry import ModelRegistry
from aiagents_pitstop_agent.runners.scoring_runner import ScoringAgentRunner
from aiagents_pitstop_agent.runners.retrain_runner import RetrainAgentRunner


import asyncio

async def run_loop(stop_event):
    registry = ModelRegistry()
    profiles = ProfileService()
    policy = PitStopPolicy()

    scoring_service = ScoringService(
        registry=registry,
        profiles=profiles,
        policy=policy
    )

    queue = QueueService()

    scoring_runner = ScoringAgentRunner(
        queue=queue,
        scoring=scoring_service
    )

    retrain_runner = RetrainAgentRunner(
        training=TrainingService()
    )

    while not stop_event.is_set():
        db = SessionLocal()
        try:
            scoring_runner.step(db)
            retrain_runner.step(db)
        finally:
            db.close()

        await asyncio.sleep(0.5)
