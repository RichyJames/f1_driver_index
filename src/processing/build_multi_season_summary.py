# src/processing/build_multi_season_summary.py

import pandas as pd

RACE_FILE = "data/raw/multi_season/all_seasons_race_results.csv"
QUALI_FILE = "data/raw/multi_season/all_seasons_qualifying.csv"
OUTPUT_FILE = "data/processed/driver_summary_2021_2025.csv"

race_df = pd.read_csv(RACE_FILE)
quali_df = pd.read_csv(QUALI_FILE)

race_df["positions_gained"] = race_df["grid"] - race_df["finish_position"]
race_df["is_win"] = (race_df["finish_position"] == 1).astype(int)
race_df["is_podium"] = (race_df["finish_position"] <= 3).astype(int)
race_df["is_top10"] = (race_df["finish_position"] <= 10).astype(int)
race_df["is_dnf"] = (~race_df["status"].str.contains("Finished", case=False, na=False)).astype(int)

summary = race_df.groupby("driver_name").agg(
    seasons_present=("season", "nunique"),
    races_entered=("round", "count"),
    total_points=("points", "sum"),
    points_per_race=("points", "mean"),
    average_finish_position=("finish_position", "mean"),
    average_grid_position=("grid", "mean"),
    average_positions_gained=("positions_gained", "mean"),
    wins=("is_win", "sum"),
    podiums=("is_podium", "sum"),
    top10_finishes=("is_top10", "sum"),
    dnfs=("is_dnf", "sum"),
    finish_position_std=("finish_position", "std"),
).reset_index()

summary["dnf_rate"] = summary["dnfs"] / summary["races_entered"]
summary["top10_rate"] = summary["top10_finishes"] / summary["races_entered"]
summary["podium_rate"] = summary["podiums"] / summary["races_entered"]
summary["win_rate"] = summary["wins"] / summary["races_entered"]

quali_summary = quali_df.groupby("driver_name").agg(
    average_qualifying_position=("quali_position", "mean")
).reset_index()

summary = summary.merge(quali_summary, on="driver_name", how="left")


summary = summary[(summary["seasons_present"] >= 2) & (summary["races_entered"] >= 20)]

summary = summary.sort_values(by="points_per_race", ascending=False)

summary.to_csv(OUTPUT_FILE, index=False)

print("Multi-season summary created.")
print(summary.head(15))
print(f"\nSaved to: {OUTPUT_FILE}")