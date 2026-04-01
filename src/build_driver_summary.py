import pandas as pd

# Load raw data
race_df = pd.read_csv("data/raw/2025_race_results.csv")
quali_df = pd.read_csv("data/raw/2025_qualifying.csv")

print("RACE COLUMNS:", race_df.columns)
print("QUALI COLUMNS:", quali_df.columns)

# Standardize driver field
race_df["driver"] = race_df["driver_name"]
quali_df["driver"] = quali_df["driver_name"]

# Convert numeric fields
race_df["finish_position"] = pd.to_numeric(race_df["finish_position"], errors="coerce")
race_df["grid"] = pd.to_numeric(race_df["grid"], errors="coerce")
race_df["points"] = pd.to_numeric(race_df["points"], errors="coerce")
quali_df["quali_position"] = pd.to_numeric(quali_df["quali_position"], errors="coerce")

# Build race-level derived variables
race_df["positions_gained"] = race_df["grid"] - race_df["finish_position"]
race_df["is_win"] = (race_df["finish_position"] == 1).astype(int)
race_df["is_podium"] = (race_df["finish_position"] <= 3).astype(int)
race_df["is_top10"] = (race_df["finish_position"] <= 10).astype(int)

# Simple DNF logic
race_df["is_dnf"] = (~race_df["status"].str.contains("Finished", case=False, na=False)).astype(int)

# Aggregate race metrics by driver
summary = race_df.groupby("driver").agg(
    constructor=("constructor", "last"),
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
    finish_position_std=("finish_position", "std")
).reset_index()

# Rate metrics
summary["dnf_rate"] = summary["dnfs"] / summary["races_entered"]
summary["top10_rate"] = summary["top10_finishes"] / summary["races_entered"]
summary["podium_rate"] = summary["podiums"] / summary["races_entered"]
summary["win_rate"] = summary["wins"] / summary["races_entered"]

# Aggregate qualifying metrics by driver
quali_summary = quali_df.groupby("driver").agg(
    average_qualifying_position=("quali_position", "mean")
).reset_index()

# Merge qualifying into main summary
summary = summary.merge(quali_summary, on="driver", how="left")

# Sort by total points
summary = summary.sort_values(by="total_points", ascending=False)

# Save processed file
output_path = "data/processed/driver_summary_2025.csv"
summary.to_csv(output_path, index=False)

print("\nDriver summary created:")
print(summary)
print(f"\nSaved to: {output_path}")