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
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def save_json(data: dict[str, Any], filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_season_rounds(season: int) -> list[int]:
    data = fetch_json(f"{season}/races.json?limit=100")
    races = data["MRData"]["RaceTable"]["Races"]
    return [int(r["round"]) for r in races]


def fetch_all_rounds(season: int, endpoint_name: str) -> list[dict[str, Any]]:
    all_races: list[dict[str, Any]] = []
    rounds = get_season_rounds(season)

    for rnd in rounds:
        data = fetch_json(f"{season}/{rnd}/{endpoint_name}.json")
        races = data["MRData"]["RaceTable"]["Races"]
        all_races.extend(races)

    return all_races


def build_race_results_table(data: dict[str, Any]) -> pd.DataFrame:
    races = data["MRData"]["RaceTable"]["Races"]
    rows: list[dict[str, Any]] = []

    for race in races:
        round_number = int(race["round"])
        race_name = race["raceName"]

        for result in race.get("Results", []):
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
                    "grid": pd.to_numeric(result.get("grid"), errors="coerce"),
                    "finish_position": pd.to_numeric(result.get("position"), errors="coerce"),
                    "points": pd.to_numeric(result.get("points"), errors="coerce"),
                    "status": result.get("status", ""),
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    race_results_races = fetch_all_rounds(SEASON, "results")
    qualifying_races = fetch_all_rounds(SEASON, "qualifying")

    race_results_json = {"MRData": {"RaceTable": {"Races": race_results_races}}}
    qualifying_json = {"MRData": {"RaceTable": {"Races": qualifying_races}}}

    save_json(race_results_json, f"{SEASON}_race_results.json")
    save_json(qualifying_json, f"{SEASON}_qualifying.json")

    race_df = build_race_results_table(race_results_json)
    qualifying_df = build_qualifying_table(qualifying_json)

    print("Number of race rows:", len(race_df))
    print("Number of qualifying rows:", len(qualifying_df))
    print("Unique race rounds:", race_df["round"].nunique())
    print("Unique qualifying rounds:", qualifying_df["round"].nunique())
    print("Rounds:", sorted(race_df["round"].unique()))

    race_df.to_csv(OUTPUT_DIR / f"{SEASON}_race_results.csv", index=False)
    qualifying_df.to_csv(OUTPUT_DIR / f"{SEASON}_qualifying.csv", index=False)


if __name__ == "__main__":
    main()