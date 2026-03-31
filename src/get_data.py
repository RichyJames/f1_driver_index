from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
SEASON = 2025
OUTPUT_DIR = Path("data/raw")


def fetch_json(endpoint: str) -> dict[str, Any]:
    """Fetch JSON from the Jolpica API."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def save_json(data: dict[str, Any], filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_race_results_table(data: dict[str, Any]) -> pd.DataFrame:
    races = data["MRData"]["RaceTable"]["Races"]
    rows: list[dict[str, Any]] = []

    for race in races:
        round_number = int(race["round"])
        race_name = race["raceName"]
        for result in race.get("Results", []):
            driver = result["Driver"]
            constructor = result["Constructor"]
            grid = int(result.get("grid", 0))
            finish_position = result.get("position")
            points = float(result.get("points", 0))
            status = result.get("status", "")

            rows.append(
                {
                    "season": int(race["season"]),
                    "round": round_number,
                    "race_name": race_name,
                    "driver_id": driver["driverId"],
                    "driver_code": driver.get("code", ""),
                    "driver_name": f"{driver['givenName']} {driver['familyName']}",
                    "constructor": constructor["name"],
                    "grid": grid,
                    "finish_position": pd.to_numeric(finish_position, errors="coerce"),
                    "points": points,
                    "status": status,
                }
            )

    return pd.DataFrame(rows)


def build_qualifying_table(data: dict[str, Any]) -> pd.DataFrame:
    races = data["MRData"]["RaceTable"]["Races"]
    rows: list[dict[str, Any]] = []

    for race in races:
        round_number = int(race["round"])
        race_name = race["raceName"]
        for result in race.get("QualifyingResults", []):
            driver = result["Driver"]
            constructor = result["Constructor"]
            rows.append(
                {
                    "season": int(race["season"]),
                    "round": round_number,
                    "race_name": race_name,
                    "driver_id": driver["driverId"],
                    "driver_code": driver.get("code", ""),
                    "driver_name": f"{driver['givenName']} {driver['familyName']}",
                    "constructor": constructor["name"],
                    "quali_position": pd.to_numeric(result.get("position"), errors="coerce"),
                    "q1": result.get("Q1"),
                    "q2": result.get("Q2"),
                    "q3": result.get("Q3"),
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    race_results_json = fetch_json(f"{SEASON}/results.json?limit=2000")
    qualifying_json = fetch_json(f"{SEASON}/qualifying.json?limit=2000")

    save_json(race_results_json, f"{SEASON}_race_results.json")
    save_json(qualifying_json, f"{SEASON}_qualifying.json")

    race_df = build_race_results_table(race_results_json)
    qualifying_df = build_qualifying_table(qualifying_json)

    race_df.to_csv(OUTPUT_DIR / f"{SEASON}_race_results.csv", index=False)
    qualifying_df.to_csv(OUTPUT_DIR / f"{SEASON}_qualifying.csv", index=False)

    print("Saved files:")
    print(f"- {OUTPUT_DIR / f'{SEASON}_race_results.json'}")
    print(f"- {OUTPUT_DIR / f'{SEASON}_qualifying.json'}")
    print(f"- {OUTPUT_DIR / f'{SEASON}_race_results.csv'}")
    print(f"- {OUTPUT_DIR / f'{SEASON}_qualifying.csv'}")
    print()
    print("Race results preview:")
    print(race_df.head())
    print()
    print("Qualifying preview:")
    print(qualifying_df.head())


if __name__ == "__main__":
    main()
