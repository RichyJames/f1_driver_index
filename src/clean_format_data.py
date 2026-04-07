import pandas as pd

SEASON = 2025

df = pd.read_csv(f"data/processed/driver_summary_{SEASON}.csv")

decimal_cols = [
    "points_per_race",
    "average_finish_position",
    "average_grid_position",
    "average_positions_gained",
    "finish_position_std",
    "dnf_rate",
    "top10_rate",
    "podium_rate",
    "win_rate",
    "average_qualifying_position"
]

df[decimal_cols] = df[decimal_cols].round(2)

int_cols = [
    "races_entered",
    "total_points",
    "wins",
    "podiums",
    "top10_finishes",
    "dnfs"
]

df[int_cols] = df[int_cols].astype(int)


df.to_csv(f"data/processed/driver_summary_{SEASON}_clean.csv", index=False)

print(df.head())