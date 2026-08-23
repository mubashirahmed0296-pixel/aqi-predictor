#it calcualtes absolute average shap values for each feature and saves them to a json file.
#  It uses the latest model from the registry and the latest data from the database to compute the shap values. 
# The output is saved in the artifacts/explainability directory.



from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.config import settings
from app.db import db
from app.features import create_time_series_features, make_day_targets


def _load_latest_data() -> tuple[pd.DataFrame, pd.Series]:
    docs = list(
        db[settings.feature_collection]
        .find({"city": settings.city}, {"_id": 0})
        .sort("timestamp", 1)
    )
    raw = pd.DataFrame(docs)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True)
    feats = create_time_series_features(raw)
    daily = make_day_targets(feats).dropna()
    feature_cols = [
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
    x = daily[feature_cols].ffill().dropna()
    y = daily["target_day_1"].loc[x.index]
    return x, y


def main() -> None:
    latest = db[settings.registry_collection].find_one(sort=[("registered_at", -1)])
    if not latest:
        raise RuntimeError("No model registry entry found; run training first.")

    x, _ = _load_latest_data()
    model_path = latest["model_path"]

    import joblib
    import shap

    artifact = joblib.load(model_path)
    model = artifact["models"]["day_1"]
    explainer = shap.Explainer(model, x.sample(min(50, len(x)), random_state=42))
    values = explainer(x.sample(min(100, len(x)), random_state=21))
    importance = pd.DataFrame(
        {
            "feature": x.columns,
            "mean_abs_shap": abs(values.values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    out_dir = Path("artifacts/explainability")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "shap_day1_importance.json"
    out_file.write_text(
        json.dumps(importance.to_dict(orient="records"), indent=2),
        encoding="utf-8",
    )
    print(f"Saved explainability output: {out_file}")


if __name__ == "__main__":
    main()
