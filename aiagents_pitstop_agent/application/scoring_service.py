import pandas as pd
from sqlalchemy.orm import Session

from aiagents_pitstop_agent.decision_engine.engine_registry import ModelRegistry

from ..infrastructure.models import Decision

from .profile_service import ProfileService
from .policies.pitstop_policy import PitStopPolicy


class ScoringDecisionDraft:
    def __init__(
        self,
        user_id: str,
        action: str,
        reason: str,
        suggested_tyre: str | None,
        expected_pit: float,
        expected_stay: float,
        model_version: str,
        raw_features: dict,
    ):
        self.user_id = user_id
        self.action = action
        self.reason = reason
        self.suggested_tyre = suggested_tyre
        self.expected_pit = expected_pit
        self.expected_stay = expected_stay
        self.model_version = model_version
        self.raw_features = raw_features


class ScoringService:

    def __init__(
        self,
        registry: ModelRegistry,
        profiles: ProfileService,
        policy: PitStopPolicy,
    ):
        self._registry = registry
        self._profiles = profiles
        self._policy = policy

    # ---------- THINK ----------
    def think(self, db: Session, payload: dict) -> ScoringDecisionDraft:
        user_id = payload["userId"]

        lap = int(payload["lap"])
        position = int(payload["position"])
        tyre_life = float(payload["tyre_life"])
        compound = payload["tyre"]
        lap_time = float(payload["lap_time_sec"])

        model, version = self._registry.get_active_model(db)

        profile = self._profiles.get_or_create(
            db,
            user_id,
            is_temporary=user_id.startswith("guest-"),
        )

        base = {
            "lap_number": lap,
            "position": position,
            "tyre_life": tyre_life,
            "compound": compound,
            "lap_time_sec": lap_time,
        }

        X_stay = pd.DataFrame([{**base, "action_flag": 0}])
        X_pit = pd.DataFrame([{**base, "action_flag": 1}])

        expected_stay = float(model.predict(X_stay)[0]) + profile.stay_bias
        expected_pit = float(model.predict(X_pit)[0]) + profile.pit_bias

        decision = self._policy.decide(
            lap=lap,
            compound=compound,
            tyre_life=tyre_life,
            lap_time=lap_time,
            expected_pit=expected_pit,
            expected_stay=expected_stay,
        )

        return ScoringDecisionDraft(
            user_id=user_id,
            action=decision.action,
            reason=decision.reason,
            suggested_tyre=decision.suggested_tyre,
            expected_pit=expected_pit,
            expected_stay=expected_stay,
            model_version=version,
            raw_features=base,
        )

    # ---------- ACT ----------
    def act(self, db: Session, draft: ScoringDecisionDraft) -> Decision:
        decision = Decision(
            user_id=draft.user_id,
            action=draft.action,
            lap_number=draft.raw_features["lap_number"],
            position=draft.raw_features["position"],
            tyre_life=draft.raw_features["tyre_life"],
            compound=draft.raw_features["compound"],
            lap_time_sec=draft.raw_features["lap_time_sec"],
            expected_pit=draft.expected_pit,
            expected_stay=draft.expected_stay,
            model_version=draft.model_version,
            reason=draft.reason,
            suggested_tyre=draft.suggested_tyre,
        )

        db.add(decision)
        db.commit()
        db.refresh(decision)

        return decision
