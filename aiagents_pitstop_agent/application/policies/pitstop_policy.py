from dataclasses import dataclass
from enum import Enum


class PitStopAction(str, Enum):
    PIT = "PIT"
    STAY = "STAY"


@dataclass(frozen=True)
class PitStopDecision:
    action: PitStopAction
    reason: str
    suggested_tyre: str | None


class PitStopPolicy:
    TYRE_DEGRADATION_LIMIT = 8.0
    LAP_TIME_LIMIT = 89.0
    PIT_ADVANTAGE_MARGIN = 0.5

    def decide(
        self,
        *,
        lap: int,
        compound: str,
        tyre_life: float,
        lap_time: float,
        expected_pit: float,
        expected_stay: float
    ) -> PitStopDecision:

        reasons: list[str] = []

        if tyre_life >= self.TYRE_DEGRADATION_LIMIT:
            reasons.append("High tyre degradation")

        if lap_time >= self.LAP_TIME_LIMIT:
            reasons.append("Significant lap time loss")

        if expected_pit > expected_stay + self.PIT_ADVANTAGE_MARGIN:
            reasons.append("Pit strategy historically beneficial")

        if expected_pit > expected_stay and len(reasons) >= 2:
            return PitStopDecision(
                action=PitStopAction.PIT,
                reason=", ".join(reasons[:2]),
                suggested_tyre=self._next_tyre(compound, lap)
            )

        return PitStopDecision(
            action=PitStopAction.STAY,
            reason="Tyres still within optimal window",
            suggested_tyre=None
        )

    def _next_tyre(self, current: str, lap: int, total: int = 50) -> str:
        if current == "SOFT":
            return "MEDIUM"
        if current == "MEDIUM":
            return "HARD" if lap < total * 0.6 else "SOFT"
        return "SOFT"
