import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "training.csv"

df = pd.read_csv(DATA_PATH)

df["action_flag"] = df["action"].map({"STAY": 0, "PIT": 1})

FEATURES = [
    "lap_number",
    "position",
    "tyre_life",
    "compound",
    "lap_time_sec",
    "action_flag",
]

TARGET = "reward"

X = df[FEATURES]
y = df[TARGET]

numeric = [
    "lap_number",
    "position",
    "tyre_life",
    "lap_time_sec",
    "action_flag",
]

categorical = ["compound"]

pre = ColumnTransformer([
    ("num", StandardScaler(), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])

model = Pipeline([
    ("preprocess", pre),
    ("model", RandomForestRegressor(n_estimators=100, random_state=42)),
])

# 2. Train
model.fit(X, y)

# 3. Save
Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/pitstop_model.joblib")

print("Model trained and saved to models/pitstop_model.joblib")
