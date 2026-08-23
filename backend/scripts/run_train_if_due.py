import os
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.db import db, ensure_indexes, record_pipeline_run
from app.train import train_and_register


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _latest_successful_training() -> dict[str, Any] | None:
    return db[settings.pipeline_runs_collection].find_one(
        {"pipeline_name": "training", "status": "success"},
        sort=[("run_at", -1)],
    )


def main() -> None:
    min_interval_hours = float(os.getenv("TRAINING_MIN_INTERVAL_HOURS", "20"))
    ensure_indexes()

    latest = _latest_successful_training()
    now = datetime.now(timezone.utc)

    if latest and latest.get("run_at"):
        last_run_at = _as_utc(latest["run_at"])
        age_hours = (now - last_run_at).total_seconds() / 3600
        if age_hours < min_interval_hours:
            print(
                {
                    "status": "skipped",
                    "reason": "latest_training_is_fresh",
                    "last_training_run_at": last_run_at.isoformat(),
                    "age_hours": round(age_hours, 2),
                    "min_interval_hours": min_interval_hours,
                }
            )
            return

    try:
        result = train_and_register()
        record_pipeline_run(
            "training_catchup",
            "success",
            {
                "reason": "training_was_due",
                "min_interval_hours": min_interval_hours,
                "overall_winner": result["overall_winner"]["model"],
                "champion": result["champion"],
            },
        )
        print(result)
    except Exception as exc:
        record_pipeline_run(
            "training_catchup",
            "failure",
            {
                "reason": "training_catchup_failed",
                "error": str(exc),
                "min_interval_hours": min_interval_hours,
            },
        )
        raise


if __name__ == "__main__":
    main()
