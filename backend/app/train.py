import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import settings
from .db import db, ensure_indexes, record_pipeline_run
from .features import create_time_series_features, make_day_targets
from .storage import save_model_to_gridfs
from .utils import utc_now


FEATURE_COLUMNS = [
    "aqi",
    "pm10",
    "pm2_5",
    "co",
    "no2",
    "so2",
    "o3",
    "day",
    "month",
    "aqi_delta",
    "aqi_lag_1",
    "aqi_lag_2",
    "aqi_lag_3",
    "pm2_5_lag_1",
    "pm10_lag_1",
    "pm2_5_roll_3",
    "pm10_roll_3",
]


def _models() -> dict[str, Any]:
    return {
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(n_estimators=200, random_state=42),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
        "mlp_neural_net": make_pipeline(
            StandardScaler(),
            MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                max_iter=800,
                random_state=42,
                early_stopping=True,
            ),
        ),
    }


def _rmse(y_true, y_pred) -> float:
    return mean_squared_error(y_true, y_pred) ** 0.5


def _evaluate_model(name: str, model, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    splitter = TimeSeriesSplit(n_splits=3)
    fold_metrics = []
    for train_idx, test_idx in splitter.split(x):
        x_train, x_test = x.iloc[train_idx], x.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        fold_model = clone(model)
        fold_model.fit(x_train, y_train)
        preds = fold_model.predict(x_test)
        fold_metrics.append(
            {
                "rmse": _rmse(y_test, preds),
                "mae": mean_absolute_error(y_test, preds),
                "r2": r2_score(y_test, preds),
            }
        )
    return {
        "rmse": float(sum(m["rmse"] for m in fold_metrics) / len(fold_metrics)),
        "mae": float(sum(m["mae"] for m in fold_metrics) / len(fold_metrics)),
        "r2": float(sum(m["r2"] for m in fold_metrics) / len(fold_metrics)),
    }


def train_and_register() -> dict[str, Any]:
    ensure_indexes()
    docs = list(
        db[settings.feature_collection]
        .find({"city": settings.city}, {"_id": 0})
        .sort("timestamp", 1)
    )
    if len(docs) < 200:
        raise ValueError("Insufficient feature data. Need at least 200 records.")

    raw = pd.DataFrame(docs)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True)
    ts_df = create_time_series_features(raw)
    daily = make_day_targets(ts_df)
    daily = daily.dropna()

    x = daily[FEATURE_COLUMNS].ffill().dropna()
    y_all = {
        "day_1": daily["target_day_1"].loc[x.index],
        "day_2": daily["target_day_2"].loc[x.index],
        "day_3": daily["target_day_3"].loc[x.index],
    }

    if len(x) < 30:
        raise ValueError("Not enough processed daily points after feature creation.")

    horizon_models: dict[str, Any] = {}
    all_trained_models: dict[str, dict[str, Any]] = {}
    all_horizon_metrics: dict[str, list[dict[str, Any]]] = {}

    for horizon, y in y_all.items():
        metrics_rows = []
        trained_models = {}
        for name, model in _models().items():
            metrics = _evaluate_model(name, model, x, y)
            trained_models[name] = clone(model).fit(x, y)
            metrics_rows.append({"model": name, **metrics})

        metrics_df = pd.DataFrame(metrics_rows).sort_values("rmse", ascending=True)
        champion = metrics_df.iloc[0].to_dict()
        champion_name = champion["model"]
        champion_model = trained_models[champion_name]
        all_horizon_metrics[horizon] = json.loads(metrics_df.to_json(orient="records"))
        all_trained_models[horizon] = trained_models
        horizon_models[horizon] = {
            "champion_name": champion_name,
            "champion_model": champion_model,
            "summary": champion,
        }
        if champion["r2"] > 0.999:
            record_pipeline_run(
                "training",
                "warning",
                {
                    "reason": "suspiciously_high_r2",
                    "horizon": horizon,
                    "value": champion["r2"],
                },
            )

    model_dir = Path(settings.model_storage_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / f"champions_{utc_now().strftime('%Y%m%d_%H%M%S')}.joblib"
    joblib.dump(
        {
            "models": {
                "day_1": horizon_models["day_1"]["champion_model"],
                "day_2": horizon_models["day_2"]["champion_model"],
                "day_3": horizon_models["day_3"]["champion_model"],
            },
            "all_models": all_trained_models,
            "feature_columns": FEATURE_COLUMNS,
            "city": settings.city,
            "trained_at": utc_now().isoformat(),
        },
        model_path,
    )
    model_gridfs_id = str(save_model_to_gridfs(model_path))

    evaluated_at = utc_now()
    overall_rows = []
    for model_name in _models().keys():
        rmse_values = []
        mae_values = []
        r2_values = []
        rank_score = 0
        for horizon, rows in all_horizon_metrics.items():
            ranked_rows = sorted(rows, key=lambda row: row["rmse"])
            model_row = next(row for row in ranked_rows if row["model"] == model_name)
            rank_score += next(index for index, row in enumerate(ranked_rows, start=1) if row["model"] == model_name)
            rmse_values.append(model_row["rmse"])
            mae_values.append(model_row["mae"])
            r2_values.append(model_row["r2"])
        overall_rows.append(
            {
                "model": model_name,
                "composite_rank_score": rank_score,
                "avg_rmse": float(sum(rmse_values) / len(rmse_values)),
                "avg_mae": float(sum(mae_values) / len(mae_values)),
                "avg_r2": float(sum(r2_values) / len(r2_values)),
            }
        )
    overall_leaderboard = sorted(
        overall_rows,
        key=lambda row: (row["composite_rank_score"], row["avg_rmse"]),
    )
    overall_winner = overall_leaderboard[0]
    db[settings.metrics_collection].insert_one(
        {
            "city": settings.city,
            "evaluated_at": evaluated_at,
            "metrics": all_horizon_metrics,
            "overall_leaderboard": overall_leaderboard,
            "overall_winner": overall_winner,
        }
    )
    db[settings.registry_collection].insert_one(
        {
            "city": settings.city,
            "registered_at": evaluated_at,
            "champion_model": {
                "day_1": horizon_models["day_1"]["champion_name"],
                "day_2": horizon_models["day_2"]["champion_name"],
                "day_3": horizon_models["day_3"]["champion_name"],
            },
            "model_path": str(model_path),
            "gridfs_model_id": model_gridfs_id,
            "feature_columns": FEATURE_COLUMNS,
            "available_models": list(_models().keys()),
            "overall_winner": overall_winner,
            "overall_leaderboard": overall_leaderboard,
            "summary": {
                "day_1": horizon_models["day_1"]["summary"],
                "day_2": horizon_models["day_2"]["summary"],
                "day_3": horizon_models["day_3"]["summary"],
            },
        }
    )
    record_pipeline_run(
        "training",
        "success",
        {
            "champions": {
                "day_1": horizon_models["day_1"]["champion_name"],
                "day_2": horizon_models["day_2"]["champion_name"],
                "day_3": horizon_models["day_3"]["champion_name"],
            },
            "model_path": str(model_path),
            "gridfs_model_id": model_gridfs_id,
            "overall_winner": overall_winner["model"],
        },
    )
    return {
        "champion": {
            "day_1": horizon_models["day_1"]["champion_name"],
            "day_2": horizon_models["day_2"]["champion_name"],
            "day_3": horizon_models["day_3"]["champion_name"],
        },
        "overall_winner": overall_winner,
        "overall_leaderboard": overall_leaderboard,
        "model_path": str(model_path),
        "gridfs_model_id": model_gridfs_id,
        "metrics": all_horizon_metrics,
    }
