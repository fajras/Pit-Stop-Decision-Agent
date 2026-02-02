import json
from sqlalchemy.orm import Session
from aiagents_core.software_agent import SoftwareAgent

from ..application.queue_service import QueueService
from ..application.scoring_service import ScoringService
from ..application.scoring_service import ScoringDecisionDraft


class ScoringTickResult:
    def __init__(
        self,
        queue_id: int,
        decision_id: int,
        action: str,
        model_version: str,
    ):
        self.queue_id = queue_id
        self.decision_id = decision_id
        self.action = action
        self.model_version = model_version


class ScoringAgentRunner(
    SoftwareAgent[dict, str, ScoringTickResult, None]
):
    """
    Scoring agent – jedan tick = obrada jedne poruke iz queue-a

    Sense  → čita jednu queued poruku
    Think  → ML + policy odluka (bez DB upisa)
    Act    → persist Decision + update queue status
    """

    def __init__(
        self,
        queue: QueueService,
        scoring: ScoringService,
    ):
        self._queue = queue
        self._scoring = scoring

    def step(self, db: Session) -> ScoringTickResult | None:
        # ---------- SENSE ----------
        item = self._queue.dequeue_next(db)
        if item is None:
            return None  # no-work tick

        try:
            payload = json.loads(item.payload_json)

            # ---------- THINK ----------
            draft: ScoringDecisionDraft = self._scoring.think(
                db,
                payload,
            )

            # ---------- ACT ----------
            decision = self._scoring.act(
                db,
                draft,
            )

            self._queue.mark_done(
                db,
                item,
                decision.id,
            )

            return ScoringTickResult(
                queue_id=item.id,
                decision_id=decision.id,
                action=decision.action,
                model_version=decision.model_version,
            )

        except Exception as ex:
            self._queue.mark_failed(
                db,
                item,
                str(ex),
            )
            return None
