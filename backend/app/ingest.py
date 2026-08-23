from datetime import datetime
from typing import Any

import requests
from dateutil.parser import isoparse

from .config import settings
from .db import db, ensure_indexes, record_pipeline_run


def fetch_open_meteo_air_quality(start_date: str, end_date: str) -> list[dict[str, Any]]:
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": settings.latitude,
        "longitude": settings.longitude,
        "timezone": settings.timezone,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    rows = []
    for i, ts in enumerate(times):
        rows.append(
            {
                "city": settings.city,
                "timestamp": isoparse(ts),
                "aqi": hourly.get("us_aqi", [None])[i],
                "pm10": hourly.get("pm10", [None])[i],
                "pm2_5": hourly.get("pm2_5", [None])[i],
                "co": hourly.get("carbon_monoxide", [None])[i],
                "no2": hourly.get("nitrogen_dioxide", [None])[i],
                "so2": hourly.get("sulphur_dioxide", [None])[i],
                "o3": hourly.get("ozone", [None])[i],
                "schema_version": "v1",
                "source": "open-meteo",
                "ingested_at": datetime.utcnow(),
            }
        )
    return rows


def upsert_features(rows: list[dict[str, Any]]) -> dict[str, int]:
    ensure_indexes()
    inserted = 0
    duplicates = 0
    col = db[settings.feature_collection]
    for row in rows:
        try:
            col.insert_one(row)
            inserted += 1
        except Exception:
            duplicates += 1
    summary = {"total": len(rows), "inserted": inserted, "duplicates": duplicates}
    record_pipeline_run("feature_ingestion", "success", summary)
    return summary
