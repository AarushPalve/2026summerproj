# CSV File Catalog

This workspace contains a mix of raw season data, derived season summaries, and rolling match-level outputs. The tables below describe the CSVs currently in the project root.

## Raw Match Data

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `frc_matches_2026.csv` | 18,707 | 108 | Raw 2026 FRC match dataset. One row per match, with event metadata, alliance teams/scores, match timing, and per-alliance `score_breakdown.*` fields. This is the source file used by the season and match loaders. |

## Season Team Summaries

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `frc_matches_2026_opr.csv` | 3,677 | 38 | Season-level team summary derived from `frc_matches_2026.csv`. One row per team with season OPR and cOPR-style component values, plus `matches_played`. |
| `statbotics_team_year_2026.csv` | 3,724 | 196 | Local 2026 Statbotics team-year cache filtered from `statbotics_team_years_all.csv`. Contains website-style EPA fields, breakdown EPA fields, rankings, and local match-count helpers. |
| `statbotics_team_years_all.csv` | 55,974 | 181 | Full local Statbotics team-year cache across all available seasons. Used as the offline source for year-specific EPA exports. |

## Rolling Match-Level OPR Outputs

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `frc_matches_2026_match_opr_before.csv` | 112,246 | 48 | Rolling match-level OPR snapshot before each completed match. One row per team per match, with `played_index`, `matches_played`, `opr`, and `copr_*` columns. |
| `frc_matches_2026_match_opr_after.csv` | 112,246 | 48 | Rolling match-level OPR snapshot after each completed match. Same grain and columns as the `before` file, but updated after the match result is incorporated. |

## Rolling Match-Level EPA Outputs

| File | Rows | Columns | Description |
|---|---:|---:|---|
| `frc_matches_2026_match_epa_before.csv` | 112,246 | 50 | Rolling match-level EPA snapshot before each completed match. One row per team per match, with `played_index`, `matches_played`, `epa`, breakdown EPA columns, and local `win_odds` / `rp_odds`. |
| `frc_matches_2026_match_epa_after.csv` | 112,246 | 50 | Rolling match-level EPA snapshot after each completed match. Same grain and columns as the `before` file, updated after the match is absorbed into the local model. |

## Notes

- `played_index` is the chronological match order used by the loaders.
- The `before` files show team values immediately prior to that match.
- The `after` files show team values immediately after that match has been incorporated.
- `matches_played` is the number of completed matches a team has already played at the time of the row.
- The EPA match outputs are fully local approximations derived from the season match CSV and the local model logic in the notebooks; they do not call the Statbotics API at runtime.
