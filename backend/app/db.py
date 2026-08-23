from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient

from .config import settings


client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]


def ensure_indexes() -> None:
    db[settings.feature_collection].create_index(
        [("city", ASCENDING), ("timestamp", ASCENDING)], unique=True
    )
    db[settings.pipeline_runs_collection].create_index([("run_at", DESCENDING)])
    db[settings.metrics_collection].create_index([("evaluated_at", DESCENDING)])
    db[settings.registry_collection].create_index([("registered_at", DESCENDING)])
    db[settings.predictions_collection].create_index([("generated_at", DESCENDING)])


def record_pipeline_run(
    pipeline_name: str,
    status: str,
    details: dict[str, Any],
) -> None:
    db[settings.pipeline_runs_collection].insert_one(
        {
            "pipeline_name": pipeline_name,
            "status": status,
            "details": details,
            "run_at": datetime.now(timezone.utc),
        }
    )
