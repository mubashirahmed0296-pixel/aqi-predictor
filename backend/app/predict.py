from datetime import timedelta
from io import BytesIO

import joblib
import pandas as pd

from .config import settings
from .db import db
from .features import create_time_series_features
from .storage import load_model_bytes_from_gridfs
from .utils import risk_level, utc_now


def _latest_registry():
    return db[settings.registry_collection].find_one(sort=[("registered_at", -1)])


def _load_latest_artifact(latest: dict) -> dict:
    if latest.get("gridfs_model_id"):
        model_bytes = load_model_bytes_from_gridfs(latest["gridfs_model_id"])
        return joblib.load(BytesIO(model_bytes))
    return joblib.load(latest["model_path"])


def latest_model_catalog() -> dict:
    latest = _latest_registry()
    if not latest:
        raise ValueError("No registered model found.")

    metrics = db[settings.metrics_collection].find_one(
        {"city": settings.city},
        sort=[("evaluated_at", -1)],
        projection={"_id": 0},
    )
    artifact = _load_latest_artifact(latest)
    all_models = artifact.get("all_models", {})
    supports_model_override = bool(all_models)
    available_models = sorted(
        {
            model_name
            for horizon_models in all_models.values()
            for model_name in horizon_models.keys()
        }
    )

    return {
        "city": settings.city,
        "registered_at": latest.get("registered_at"),
        "champion_model": latest.get("champion_model", {}),
        "available_models": available_models,
        "supports_model_override": supports_model_override,
        "overall_winner": latest.get("overall_winner") or (metrics or {}).get("overall_winner"),
        "overall_leaderboard": latest.get("overall_leaderboard") or (metrics or {}).get("overall_leaderboard", []),
        "feature_columns": latest.get("feature_columns") or artifact.get("feature_columns", []),
        "gridfs_model_id": latest.get("gridfs_model_id"),
        "metrics": (metrics or {}).get("metrics", {}),
    }


def predict_next_3_days(model_name: str | None = None) -> dict:
    latest = _latest_registry()
    if not latest:
        raise ValueError("No registered model found.")

    artifact = _load_latest_artifact(latest)
    models = artifact["models"]
    feature_columns = artifact["feature_columns"]
    all_models = artifact.get("all_models", {})
    normalized_model = (model_name or "champion").strip()

    if normalized_model and normalized_model.lower() != "champion":
        selected_models = {}
        missing_horizons = []
        for horizon in ("day_1", "day_2", "day_3"):
            model_for_horizon = all_models.get(horizon, {}).get(normalized_model)
            if model_for_horizon is None:
                missing_horizons.append(horizon)
            else:
                selected_models[horizon] = model_for_horizon
        if missing_horizons:
            raise ValueError(
                f"Model '{normalized_model}' is not available for {', '.join(missing_horizons)}. "
                "Retrain once after the model-selection update, or use model=champion."
            )
        models = selected_models
        model_label = {
            "day_1": normalized_model,
            "day_2": normalized_model,
            "day_3": normalized_model,
        }
        selection_mode = "single_model_override"
    else:
        model_label = latest["champion_model"]
        selection_mode = "horizon_champions"

    docs = list(
        db[settings.feature_collection]
        .find({"city": settings.city}, {"_id": 0})
        .sort("timestamp", 1)
    )
    raw = pd.DataFrame(docs)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True)
    feats = create_time_series_features(raw)
    # We only need features from the most recent daily row for next-day horizon models.
    daily = (
        feats.set_index("timestamp")
        .resample("D")
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("timestamp")
    )
    latest_row = daily.tail(1).copy()
    x = latest_row[feature_columns].ffill().dropna(axis=1, how="all")
    day1 = float(models["day_1"].predict(x)[0])
    day2 = float(models["day_2"].predict(x)[0])
    day3 = float(models["day_3"].predict(x)[0])

    base_day = utc_now().date()
    result = {
        "city": settings.city,
        "generated_at": utc_now().isoformat(),
        "selection_mode": selection_mode,
        "model": model_label,
        "supports_model_override": bool(all_models),
        "available_models": sorted(
            {
                candidate
                for horizon_models in all_models.values()
                for candidate in horizon_models.keys()
            }
        ),
        "predictions": [
            {"date": str(base_day + timedelta(days=1)), "aqi": day1, "risk": risk_level(day1)},
            {"date": str(base_day + timedelta(days=2)), "aqi": day2, "risk": risk_level(day2)},
            {"date": str(base_day + timedelta(days=3)), "aqi": day3, "risk": risk_level(day3)},
        ],
    }
    db[settings.predictions_collection].insert_one(result.copy())
    return result
