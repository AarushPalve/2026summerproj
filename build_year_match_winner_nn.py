import json
from pathlib import Path


def build_notebook() -> dict:
    cell1 = """import ast
import json
import math
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def set_seed(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


set_seed(42)


def resolve_year() -> int:
    raw = input("Enter season year [2026]: ").strip()
    if not raw:
        return 2026
    if not raw.isdigit():
        raise ValueError("Please enter a four-digit season year.")
    return int(raw)


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


def numeric_cols(df: pd.DataFrame) -> list[str]:
    cols = []
    for column in df.columns:
        if column in {"team_number", "played_index", "match_number", "set_number"}:
            continue
        if column.startswith("breakdown_") or column in {"epa", "matches_played"}:
            cols.append(column)
    return cols


def summarize_alliance(group: pd.DataFrame, feature_columns: list[str], prefix: str) -> dict:
    numeric = group[feature_columns].apply(pd.to_numeric, errors="coerce")
    mean = numeric.mean().add_prefix(f"{prefix}_mean_")
    std = numeric.std(ddof=0).fillna(0).add_prefix(f"{prefix}_std_")
    out = {**mean.to_dict(), **std.to_dict()}
    out[f"{prefix}_team_count"] = float(len(group))
    return out


class MatchWinnerNet(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def build_dataset(year: int):
    match_csv = Path(f"frc_matches_{year}.csv")
    before_csv = Path(f"frc_matches_{year}_match_epa_before.csv")
    if not match_csv.exists():
        raise FileNotFoundError(f"Missing match CSV: {match_csv}")
    if not before_csv.exists():
        raise FileNotFoundError(
            f"Missing pre-match EPA CSV: {before_csv}. Run year_match_EPA_loader.ipynb first."
        )

    match_df = pd.read_csv(
        match_csv,
        usecols=["key", "winning_alliance", "played_index", "comp_level", "match_number", "set_number"],
        low_memory=False,
    )
    match_df = match_df[match_df["winning_alliance"].isin(["red", "blue"])].copy()
    match_df = match_df.rename(columns={"key": "match_key"})

    before_df = pd.read_csv(before_csv, low_memory=False)
    before_df = before_df[before_df["phase"].eq("before")].copy() if "phase" in before_df.columns else before_df.copy()

    feature_columns = numeric_cols(before_df)
    if not feature_columns:
        raise RuntimeError("No numeric pre-match feature columns were found.")

    meta_lookup = match_df.set_index("match_key")
    rows = []
    skipped = 0
    for match_key, group in before_df.groupby("match_key", sort=False):
        if match_key not in meta_lookup.index:
            skipped += 1
            continue

        meta = meta_lookup.loc[match_key]
        if isinstance(meta, pd.DataFrame):
            meta = meta.iloc[0]
        if pd.isna(meta["winning_alliance"]):
            skipped += 1
            continue

        red = group[group["alliance"].eq("red")]
        blue = group[group["alliance"].eq("blue")]
        if red.empty or blue.empty:
            skipped += 1
            continue

        row = {
            "match_key": match_key,
            "played_index": float(meta["played_index"]),
            "comp_level": str(meta["comp_level"]),
            "match_number": float(meta["match_number"]),
            "set_number": float(meta["set_number"]),
            "red_win": 1.0 if str(meta["winning_alliance"]) == "red" else 0.0,
        }
        row.update(summarize_alliance(red, feature_columns, "red"))
        row.update(summarize_alliance(blue, feature_columns, "blue"))
        rows.append(row)

    dataset = pd.DataFrame(rows).sort_values(["played_index", "match_number", "set_number"]).reset_index(drop=True)
    if dataset.empty:
        raise RuntimeError("No match rows were assembled for training.")
    return dataset, feature_columns, skipped
"""

    cell2 = """year = resolve_year()
dataset, base_feature_columns, skipped_matches = build_dataset(year)

comp_levels = ["qm", "sf", "f"]
for level in comp_levels:
    dataset[f"comp_level_{level}"] = (dataset["comp_level"] == level).astype(float)

feature_columns = [
    col
    for col in dataset.columns
    if col not in {"match_key", "played_index", "comp_level", "match_number", "set_number", "red_win"}
]

dataset = dataset[["match_key", "played_index", "comp_level", "match_number", "set_number", "red_win"] + feature_columns].copy()
dataset = dataset.replace([np.inf, -np.inf], np.nan).fillna(0.0)

split_idx = max(1, int(len(dataset) * 0.8))
train_df = dataset.iloc[:split_idx].reset_index(drop=True)
val_df = dataset.iloc[split_idx:].reset_index(drop=True)
if val_df.empty:
    val_df = train_df.iloc[-max(1, len(train_df) // 5):].reset_index(drop=True)
    train_df = train_df.iloc[: len(train_df) - len(val_df)].reset_index(drop=True)
    if train_df.empty:
        raise RuntimeError("Not enough samples to train a validation split.")

X_train = train_df[feature_columns].to_numpy(dtype=np.float32)
y_train = train_df["red_win"].to_numpy(dtype=np.float32)
X_val = val_df[feature_columns].to_numpy(dtype=np.float32)
y_val = val_df["red_win"].to_numpy(dtype=np.float32)

feature_mean = X_train.mean(axis=0)
feature_std = X_train.std(axis=0)
feature_std[feature_std < 1e-6] = 1.0
X_train = (X_train - feature_mean) / feature_std
X_val = (X_val - feature_mean) / feature_std

train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
val_x = torch.from_numpy(X_val)
val_y = torch.from_numpy(y_val)
train_loader = DataLoader(train_ds, batch_size=256, shuffle=True, drop_last=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MatchWinnerNet(len(feature_columns)).to(device)

pos = float(y_train.sum())
neg = float(len(y_train) - y_train.sum())
pos_weight = torch.tensor([neg / max(pos, 1.0)], dtype=torch.float32, device=device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

best_state = None
best_val_loss = float("inf")
best_epoch = 0
patience = 8
patience_left = patience
history = []

for epoch in range(1, 61):
    model.train()
    total_loss = 0.0
    total_count = 0
    for xb, yb in train_loader:
        xb = xb.to(device)
        yb = yb.to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(xb)
        loss = criterion(logits, yb)
        loss.backward()
        optimizer.step()
        total_loss += float(loss.item()) * len(xb)
        total_count += len(xb)

    model.eval()
    with torch.no_grad():
        val_logits = model(val_x.to(device))
        val_loss = float(criterion(val_logits, val_y.to(device)).item())
        val_probs = torch.sigmoid(val_logits).cpu().numpy()

    train_loss = total_loss / max(total_count, 1)
    val_pred = (val_probs >= 0.5).astype(np.float32)
    val_acc = float(accuracy_score(y_val, val_pred))
    val_auc = float(roc_auc_score(y_val, val_probs)) if len(np.unique(y_val)) > 1 else float("nan")
    history.append(
        {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_acc": val_acc,
            "val_auc": val_auc,
        }
    )
    print(
        f"epoch {epoch:02d} train_loss={train_loss:.4f} val_loss={val_loss:.4f} "
        f"val_acc={val_acc:.4f} val_auc={val_auc:.4f}"
    )

    if val_loss + 1e-5 < best_val_loss:
        best_val_loss = val_loss
        best_epoch = epoch
        patience_left = patience
        best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    else:
        patience_left -= 1
        if patience_left <= 0:
            print(f"Early stopping at epoch {epoch}. Best epoch: {best_epoch}.")
            break

if best_state is None:
    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

model.load_state_dict(best_state)
model.eval()

with torch.no_grad():
    train_probs = torch.sigmoid(model(torch.from_numpy(X_train).to(device))).cpu().numpy()
    val_probs = torch.sigmoid(model(val_x.to(device))).cpu().numpy()

train_acc = float(accuracy_score(y_train, (train_probs >= 0.5).astype(np.float32)))
val_acc = float(accuracy_score(y_val, (val_probs >= 0.5).astype(np.float32)))
train_auc = float(roc_auc_score(y_train, train_probs)) if len(np.unique(y_train)) > 1 else float("nan")
val_auc = float(roc_auc_score(y_val, val_probs)) if len(np.unique(y_val)) > 1 else float("nan")
train_logloss = float(log_loss(y_train, np.clip(train_probs, 1e-6, 1 - 1e-6)))
val_logloss = float(log_loss(y_val, np.clip(val_probs, 1e-6, 1 - 1e-6)))

artifact_path = Path(f"match_winner_nn_{year}.pt")
metadata_path = Path(f"match_winner_nn_{year}_metadata.json")
bundle = {
    "year": year,
    "model_state_dict": best_state,
    "feature_columns": feature_columns,
    "feature_mean": feature_mean.tolist(),
    "feature_std": feature_std.tolist(),
    "comp_levels": comp_levels,
    "base_feature_columns": base_feature_columns,
    "training_history": history,
    "metrics": {
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "train_auc": train_auc,
        "val_auc": val_auc,
        "train_log_loss": train_logloss,
        "val_log_loss": val_logloss,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "skipped_matches": int(skipped_matches),
    },
}
torch.save(bundle, artifact_path)
metadata_path.write_text(
    json.dumps(
        {
            "year": year,
            "artifact_path": str(artifact_path),
            "feature_count": len(feature_columns),
            "base_feature_columns": base_feature_columns,
            "metrics": bundle["metrics"],
        },
        indent=2,
    ),
    encoding="utf-8",
)

print(f"Training rows: {len(train_df):,}")
print(f"Validation rows: {len(val_df):,}")
print(f"Saved model bundle to {artifact_path}")
print(f"Saved metadata to {metadata_path}")
print(json.dumps(bundle["metrics"], indent=2))
"""

    cell3 = """def load_match_winner_model(model_path: str | Path):
    bundle = torch.load(Path(model_path), map_location="cpu")
    model = MatchWinnerNet(len(bundle["feature_columns"]))
    model.load_state_dict(bundle["model_state_dict"])
    model.eval()
    return model, bundle


def predict_match_probability(model, bundle, feature_frame: pd.DataFrame) -> pd.Series:
    ordered = feature_frame[bundle["feature_columns"]].to_numpy(dtype=np.float32)
    mean = np.asarray(bundle["feature_mean"], dtype=np.float32)
    std = np.asarray(bundle["feature_std"], dtype=np.float32)
    scaled = (ordered - mean) / std
    with torch.no_grad():
        logits = model(torch.from_numpy(scaled))
        probs = torch.sigmoid(logits).cpu().numpy()
    return pd.Series(probs, index=feature_frame.index, name="red_win_probability")


model, bundle = load_match_winner_model(Path(f"match_winner_nn_{year}.pt"))
sample_predictions = predict_match_probability(model, bundle, dataset.head(10))
pd.concat([dataset.head(10)[["match_key", "red_win"]], sample_predictions], axis=1)
"""

    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Match Winner Neural Network\n",
                    "\n",
                    "This notebook trains a neural network to predict the red alliance win probability for each match.\n",
                    "\n",
                    "It only uses information available before the match starts: pre-match EPA/breakdown values from `frc_matches_<year>_match_epa_before.csv` plus match metadata such as `match_number`, `set_number`, and `comp_level`.\n",
                    "\n",
                    "The model artifact is saved locally for later inference.\n",
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
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": cell3.splitlines(True),
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
    Path("year_match_winner_nn.ipynb").write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print("wrote year_match_winner_nn.ipynb")


if __name__ == "__main__":
    main()
