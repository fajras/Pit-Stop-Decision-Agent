import joblib
import pandas as pd

class PitStopModel:
    def __init__(self):
        self.model = joblib.load("models/pitstop_model.joblib")

    def predict(self, payload: dict):
        base = {
            "lap_number": float(payload.get("lap", 0)),
            "position": float(payload.get("position", 0)),
            "tyre_life": float(payload.get("tyre_life", 0)),
            "compound": payload.get("tyre", "UNKNOWN"),
            "lap_time_sec": float(payload.get("lap_time_sec", 0)),
        }

        # STAY
        X_stay = pd.DataFrame([{**base, "action_flag": 0}])
        reward_stay = self.model.predict(X_stay)[0]

        # PIT
        X_pit = pd.DataFrame([{**base, "action_flag": 1}])
        reward_pit = self.model.predict(X_pit)[0]

        return reward_pit, reward_stay
