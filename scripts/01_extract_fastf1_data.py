import fastf1
import pandas as pd
from fastf1 import get_session

# 1. Enable cache
fastf1.Cache.enable_cache("data/fastf1_cache")

# 2. Odaberi utrku (prva testna)
SEASON = 2023
RACE_NAME = "Bahrain"
SESSION_TYPE = "R"  # Race

# 3. Load session
print("Loading FastF1 session...")
session = get_session(SEASON, RACE_NAME, SESSION_TYPE)
session.load()
print("Session loaded")

# 4. Odaberi jednog vozača za početak
driver_code = "VER"
laps = session.laps.pick_driver(driver_code)
laps = laps.reset_index(drop=True)

print(f"Total laps for {driver_code}: {len(laps)}")

ROWS = []

LOOKAHEAD_LAPS = 2  # reward nakon 2 kruga

for i in range(len(laps) - LOOKAHEAD_LAPS):
    lap = laps.iloc[i]
    future_lap = laps.iloc[i + LOOKAHEAD_LAPS]

    # Action: PIT ili STAY
    action = "PIT" if pd.notna(lap["PitInTime"]) else "STAY"

    # Reward: promjena pozicije (pozitivno = bolje)
    reward = lap["Position"] - future_lap["Position"]

    row = {
        "lap_number": lap["LapNumber"],
        "position": lap["Position"],
        "tyre_life": lap["TyreLife"],
        "compound": lap["Compound"],
        "lap_time_sec": lap["LapTime"].total_seconds() if pd.notna(lap["LapTime"]) else None,
        "action": action,
        "reward": reward,
    }

    ROWS.append(row)

# 5. Kreiraj DataFrame
df = pd.DataFrame(ROWS)

# 6. Snimi dataset
output_path = "data/training.csv"
df.to_csv(output_path, index=False)

print(f"Training dataset saved to {output_path}")
print(df.head())
