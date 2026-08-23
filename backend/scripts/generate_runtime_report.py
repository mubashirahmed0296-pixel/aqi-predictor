from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.db import db


def _safe_get_latest(collection: str, sort_field: str):
    return db[collection].find_one(sort=[(sort_field, -1)], projection={"_id": 0})


def main() -> None:
    latest_metrics = _safe_get_latest(settings.metrics_collection, "evaluated_at")
    latest_registry = _safe_get_latest(settings.registry_collection, "registered_at")
    latest_quality = _safe_get_latest("quality_audits", "audited_at")
    # Use insertion order for predictions to avoid string-sort edge cases on timestamp fields.
    latest_prediction = db[settings.predictions_collection].find_one(
        sort=[("_id", -1)], projection={"_id": 0}
    )

    lines = ["# Runtime Report Snippet", ""]
    lines.append(f"- City: `{settings.city}`")
    lines.append("")

    lines.append("## Latest Registry")
    if latest_registry:
        lines.append(f"- Registered at: `{latest_registry.get('registered_at')}`")
        lines.append(f"- Champion models: `{latest_registry.get('champion_model')}`")
        lines.append(f"- GridFS model id: `{latest_registry.get('gridfs_model_id')}`")
    else:
        lines.append("- Not available yet. Run training first.")
    lines.append("")

    lines.append("## Latest Metrics")
    if latest_metrics:
        lines.append(f"- Evaluated at: `{latest_metrics.get('evaluated_at')}`")
        lines.append("```json")
        lines.append(json.dumps(latest_metrics.get("metrics", {}), indent=2, default=str))
        lines.append("```")
    else:
        lines.append("- Not available yet. Run training first.")
    lines.append("")

    lines.append("## Latest Quality Audit")
    if latest_quality:
        lines.append("```json")
        lines.append(json.dumps(latest_quality, indent=2, default=str))
        lines.append("```")
    else:
        lines.append("- Not available yet. Run quality audit first.")
    lines.append("")

    lines.append("## Latest Prediction")
    if latest_prediction:
        lines.append("```json")
        lines.append(json.dumps(latest_prediction, indent=2, default=str))
        lines.append("```")
    else:
        lines.append("- Not available yet. Run prediction endpoint first.")

    out_dir = Path("artifacts/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "runtime_report_snippet.md"
    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {out_file}")


if __name__ == "__main__":
    main()
