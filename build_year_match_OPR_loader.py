import json
from pathlib import Path


def build_notebook() -> dict:
    cell1 = """import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd


def resolve_input_csv() -> Path:
    raw = input("Enter match CSV path or season year [auto-detect latest frc_matches_*.csv]: ").strip()
    if not raw:
        candidates = sorted(
            Path.cwd().glob("frc_matches_*.csv"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError("No frc_matches_*.csv file was found in the current directory.")
        return candidates[0]
    if raw.isdigit():
        return Path(f"frc_matches_{raw}.csv")
    return Path(raw)


def parse_team_keys(value):
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None or pd.isna(value):
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return [value]
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    return []


def team_number_from_key(team_key):
    if isinstance(team_key, str):
        match = re.search(r"(\\d+)", team_key)
        if match:
            return int(match.group(1))
    return int(team_key)


def infer_components(df: pd.DataFrame) -> list[str]:
    components = []
    seen = set()
    for column in df.columns:
        if not column.startswith("score_breakdown."):
            continue
        parts = column.split(".", 2)
        if len(parts) != 3:
            continue
        component = parts[2]
        if component in seen:
            continue
        series = pd.to_numeric(df[column], errors="coerce")
        if series.notna().any():
            seen.add(component)
            components.append(component)
    return components


def numeric_value(value) -> float:
    if isinstance(value, (int, float, np.integer, np.floating)) and not pd.isna(value):
        return float(value)
    coerced = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    return float(coerced) if pd.notna(coerced) else 0.0


def sort_matches(df: pd.DataFrame) -> pd.DataFrame:
    if "played_index" in df.columns:
        cols = [col for col in ["played_index", "actual_time", "time", "event_key", "match_number", "set_number"] if col in df.columns]
        return df.sort_values(cols, na_position="last").reset_index(drop=True)
    sort_cols = [col for col in ["actual_time", "time", "event_key", "match_number", "set_number"] if col in df.columns]
    if sort_cols:
        return df.sort_values(sort_cols, na_position="last").reset_index(drop=True)
    return df.reset_index(drop=True)
"""

    cell2 = """csv_path = resolve_input_csv()
if not csv_path.exists():
    raise FileNotFoundError(f"Could not find input CSV: {csv_path}")

df = pd.read_csv(csv_path, low_memory=False)
components = infer_components(df)
df = sort_matches(df)

required_cols = ["alliances.red.score", "alliances.blue.score", "alliances.red.team_keys", "alliances.blue.team_keys"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"{csv_path.name} is missing required columns: {missing}")

completed_matches = []
team_numbers = set()
for _, row in df.iterrows():
    red_score = pd.to_numeric(pd.Series([row.get("alliances.red.score")]), errors="coerce").iloc[0]
    blue_score = pd.to_numeric(pd.Series([row.get("alliances.blue.score")]), errors="coerce").iloc[0]
    red_team_keys = parse_team_keys(row.get("alliances.red.team_keys"))
    blue_team_keys = parse_team_keys(row.get("alliances.blue.team_keys"))
    if pd.isna(red_score) or pd.isna(blue_score) or not red_team_keys or not blue_team_keys:
        continue
    row_dict = row.to_dict()
    completed_matches.append(row_dict)
    team_numbers.update(team_number_from_key(team_key) for team_key in red_team_keys)
    team_numbers.update(team_number_from_key(team_key) for team_key in blue_team_keys)

if not completed_matches:
    raise RuntimeError(f"No completed matches were found in {csv_path}.")

team_numbers = sorted(team_numbers)
team_index = {team_number: index for index, team_number in enumerate(team_numbers)}
team_count = len(team_numbers)
target_names = ["opr"] + [f"copr_{component.replace('.', '_')}" for component in components]
target_count = len(target_names)

regularization = 1.0
theta = np.zeros((team_count, target_count), dtype=float)
precision_inv = np.eye(team_count, dtype=float) / regularization

pre_rows = []
post_rows = []
matches_played = {team_number: 0 for team_number in team_numbers}
completed_df = pd.DataFrame(completed_matches)


def build_target_vector(match_row, color):
    values = [numeric_value(match_row.get(f"alliances.{color}.score"))]
    for component in components:
        values.append(numeric_value(match_row.get(f"score_breakdown.{color}.{component}")))
    return np.asarray(values, dtype=float)


def collect_rows(match_row, color, phase, played_index):
    team_keys = parse_team_keys(match_row.get(f"alliances.{color}.team_keys"))
    team_rows = []
    for team_key in team_keys:
        team_number = team_number_from_key(team_key)
        idx = team_index[team_number]
        row = {
            "played_index": played_index,
            "phase": phase,
            "alliance": color,
            "team_number": team_number,
            "team_key": f"frc{team_number}",
            "matches_played": matches_played[team_number],
            "match_key": match_row.get("key"),
            "event_key": match_row.get("event_key"),
            "comp_level": match_row.get("comp_level"),
            "match_number": match_row.get("match_number"),
            "set_number": match_row.get("set_number"),
            "actual_time": match_row.get("actual_time"),
            "played_time_utc": match_row.get("played_time_utc"),
            "opr": theta[idx, 0],
        }
        for target_idx, target_name in enumerate(target_names[1:], start=1):
            row[target_name] = theta[idx, target_idx]
        team_rows.append(row)
    return team_rows


def update_model(match_row, color):
    team_keys = parse_team_keys(match_row.get(f"alliances.{color}.team_keys"))
    team_numbers_row = [team_number_from_key(team_key) for team_key in team_keys]
    team_indices = [team_index[team_number] for team_number in team_numbers_row]
    y = build_target_vector(match_row, color)

    v = precision_inv[:, team_indices].sum(axis=1)
    denom = 1.0 + float(v[team_indices].sum())
    if denom <= 0:
        raise RuntimeError("Encountered a non-positive update denominator while computing rolling OPR.")

    pred = theta[team_indices].sum(axis=0)
    residual = y - pred
    gain = v / denom
    theta[:] = theta + gain[:, None] * residual[None, :]
    precision_inv[:] = precision_inv - np.outer(gain, v)


for played_index, (_, match_row) in enumerate(completed_df.iterrows(), start=1):
    pre_rows.extend(collect_rows(match_row, "red", "before", played_index))
    pre_rows.extend(collect_rows(match_row, "blue", "before", played_index))

    update_model(match_row, "red")
    update_model(match_row, "blue")
    for team_key in parse_team_keys(match_row.get("alliances.red.team_keys")):
        matches_played[team_number_from_key(team_key)] += 1
    for team_key in parse_team_keys(match_row.get("alliances.blue.team_keys")):
        matches_played[team_number_from_key(team_key)] += 1

    post_rows.extend(collect_rows(match_row, "red", "after", played_index))
    post_rows.extend(collect_rows(match_row, "blue", "after", played_index))

pre_df = pd.DataFrame(pre_rows)
post_df = pd.DataFrame(post_rows)

if "matches_played" not in pre_df.columns or "matches_played" not in post_df.columns:
    raise RuntimeError("Failed to build match-level OPR outputs.")

sort_cols = ["played_index", "alliance", "team_number"]
pre_df = pre_df.sort_values(sort_cols).reset_index(drop=True)
post_df = post_df.sort_values(sort_cols).reset_index(drop=True)

pre_output = csv_path.with_name(f"{csv_path.stem}_match_opr_before.csv")
post_output = csv_path.with_name(f"{csv_path.stem}_match_opr_after.csv")
pre_df.to_csv(pre_output, index=False)
post_df.to_csv(post_output, index=False)

print(f"Loaded {len(completed_matches):,} completed matches from {csv_path.name}")
print(f"Computed rolling before/after estimates for {len(pre_df):,} team-match rows")
print(f"Wrote {pre_output.name}")
print(f"Wrote {post_output.name}")
pre_df.head(12)
"""

    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Rolling Match OPR Loader\n",
                    "\n",
                    "This notebook loads a year-specific match CSV, computes rolling OPR-style and cOPR-style values immediately before and after each match, and writes two CSVs.\n",
                    "\n",
                    "The notebook is fully local at runtime and does not call any external API.",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": cell1.splitlines(True),
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": cell2.splitlines(True),
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.14.2",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    nb = build_notebook()
    Path("year_match_OPR_loader.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print("wrote year_match_OPR_loader.ipynb")


if __name__ == "__main__":
    main()
