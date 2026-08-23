from __future__ import annotations

from typing import Any

import pandas as pd

from .config import settings
from .db import db, record_pipeline_run
from .features import create_time_series_features, make_day_targets
from .utils import utc_now


def run_data_quality_audit() -> dict[str, Any]:
    docs = list(
        db[settings.feature_collection]
        .find({"city": settings.city}, {"_id": 0})
        .sort("timestamp", 1)
    )
    if not docs:
        raise ValueError("No feature data found for selected city.")

    raw = pd.DataFrame(docs)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], utc=True)

    duplicate_count = int(raw.duplicated(subset=["city", "timestamp"]).sum())
    null_counts = raw.isnull().sum().to_dict()
    total_rows = len(raw)

    # Expected range check for Open-Meteo AQI scale.
    out_of_range_aqi = int(((raw["aqi"] < 0) | (raw["aqi"] > 500)).fillna(False).sum())

    ts_df = create_time_series_features(raw)
    daily = make_day_targets(ts_df)
    target_columns = {"target_day_1", "target_day_2", "target_day_3"}
    leakage_columns = sorted(target_columns.intersection(raw.columns))
    leakage_hint = bool(leakage_columns)

    audit = {
        "city": settings.city,
        "audited_at": utc_now(),
        "row_count": total_rows,
        "duplicate_rows": duplicate_count,
        "null_counts": null_counts,
        "aqi_out_of_range_rows": out_of_range_aqi,
        "daily_training_rows": int(len(daily)),
        "leakage_check": {
            "target_columns_present_in_raw_features": leakage_columns,
            "future_targets_created_after_feature_generation": True,
        },
        "leakage_risk_hint": leakage_hint,
        "status": "pass"
        if duplicate_count == 0 and out_of_range_aqi == 0 and not leakage_hint
        else "warning",
    }
    db["quality_audits"].insert_one(audit.copy())
    record_pipeline_run(
        "data_quality_audit",
        "success",
        {
            "duplicates": duplicate_count,
            "aqi_out_of_range_rows": out_of_range_aqi,
            "status": audit["status"],
        },
    )
    return audit
