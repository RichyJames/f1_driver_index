from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"
SEASONS = [2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = Path("data/raw/multi_season")


def fetch_json(endpoint: str) -> dict[str, Any]:
    url = f"{BASE_URL}/{endpoint}"

    max_retries = 5
    wait_seconds = 2

    for attempt in range(max_retries):
        response = requests.get(url, timeout=30)

        if response.status_code == 429:
            print(f"Rate limited on {endpoint}... waiting {wait_seconds}s")
            time.sleep(wait_seconds)
            wait_seconds *= 2
            continue

        response.raise_for_status()
        return response.json()

    raise Exception(f"Failed after {max_retries} retries: {url}")


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

        time.sleep(1)  

    return all_races


def build_race_results_table(data: dict[str, Any]) -> pd.DataFrame:
    races = data["MRData"]["RaceTable"]["Races"]
    rows: list[dict[str, Any]] = []

    for race in races:
        for result in race.get("Results", []):
            driver = result["Driver"]
            constructor = result["Constructor"]

            rows.append(
                {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "race_name": race["raceName"],
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
        for result in race.get("QualifyingResults", []):
            driver = result["Driver"]
            constructor = result["Constructor"]

            rows.append(
                {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "race_name": race["raceName"],
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

    all_race_dfs = []
    all_quali_dfs = []

    for season in SEASONS:
        print(f"Fetching season {season}...")

        race_results_races = fetch_all_rounds(season, "results")
        qualifying_races = fetch_all_rounds(season, "qualifying")

        race_results_json = {"MRData": {"RaceTable": {"Races": race_results_races}}}
        qualifying_json = {"MRData": {"RaceTable": {"Races": qualifying_races}}}

        save_json(race_results_json, f"{season}_race_results.json")
        save_json(qualifying_json, f"{season}_qualifying.json")

        race_df = build_race_results_table(race_results_json)
        qualifying_df = build_qualifying_table(qualifying_json)

        race_df.to_csv(OUTPUT_DIR / f"{season}_race_results.csv", index=False)
        qualifying_df.to_csv(OUTPUT_DIR / f"{season}_qualifying.csv", index=False)

        print(
            f"Season {season}: {race_df['round'].nunique()} race rounds, "
            f"{qualifying_df['round'].nunique()} qualifying rounds"
        )

        all_race_dfs.append(race_df)
        all_quali_dfs.append(qualifying_df)

    combined_race_df = pd.concat(all_race_dfs, ignore_index=True)
    combined_quali_df = pd.concat(all_quali_dfs, ignore_index=True)

    combined_race_df.to_csv(OUTPUT_DIR / "all_seasons_race_results.csv", index=False)
    combined_quali_df.to_csv(OUTPUT_DIR / "all_seasons_qualifying.csv", index=False)

    print("\nDone.")
    print(f"Combined race rows: {len(combined_race_df)}")
    print(f"Combined qualifying rows: {len(combined_quali_df)}")
    print(f"Seasons included: {sorted(combined_race_df['season'].unique())}")


if __name__ == "__main__":
    main()