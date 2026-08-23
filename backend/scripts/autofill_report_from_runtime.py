from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from app.config import settings
from app.db import db


def _latest(collection: str, sort_field: str) -> dict[str, Any] | None:
    return db[collection].find_one(sort=[(sort_field, -1)], projection={"_id": 0})


def _replace_block(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    block = f"{start}\n{replacement}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"Marker block not found: {start} ... {end}")
    return pattern.sub(block, text)


def _format_num(v: Any) -> str:
    try:
        return f"{float(v):.3f}"
    except Exception:
        return "[n/a]"


def _build_metrics_table(metrics_doc: dict[str, Any] | None, registry_doc: dict[str, Any] | None) -> str:
    header = "| Horizon | Champion Model | RMSE | MAE | R2 |\n|---|---|---:|---:|---:|"
    if not metrics_doc or not registry_doc:
        return "\n".join(
            [
                header,
                "| Day+1 | [fill] | [fill] | [fill] | [fill] |",
                "| Day+2 | [fill] | [fill] | [fill] | [fill] |",
                "| Day+3 | [fill] | [fill] | [fill] | [fill] |",
            ]
        )

    metrics = metrics_doc.get("metrics", {})
    champions = registry_doc.get("champion_model", {})

    def row(h_key: str, label: str) -> str:
        items = metrics.get(h_key, [])
        best = items[0] if items else {}
        return (
            f"| {label} | {champions.get(h_key, '[n/a]')} | "
            f"{_format_num(best.get('rmse'))} | {_format_num(best.get('mae'))} | {_format_num(best.get('r2'))} |"
        )

    return "\n".join([header, row("day_1", "Day+1"), row("day_2", "Day+2"), row("day_3", "Day+3")])


def _build_runtime_summary(
    metrics_doc: dict[str, Any] | None,
    registry_doc: dict[str, Any] | None,
    quality_doc: dict[str, Any] | None,
    prediction_doc: dict[str, Any] | None,
) -> str:
    lines = []
    lines.append(f"- City: `{settings.city}`")
    lines.append(f"- Latest registry timestamp: `{(registry_doc or {}).get('registered_at', '[n/a]')}`")
    lines.append(f"- Latest metrics timestamp: `{(metrics_doc or {}).get('evaluated_at', '[n/a]')}`")
    lines.append(f"- Latest quality audit timestamp: `{(quality_doc or {}).get('audited_at', '[n/a]')}`")
    lines.append(f"- Latest prediction timestamp: `{(prediction_doc or {}).get('generated_at', '[n/a]')}`")
    lines.append("")

    lines.append("Latest quality audit:")
    lines.append("```json")
    lines.append(json.dumps(quality_doc or {"note": "Run quality audit first."}, indent=2, default=str))
    lines.append("```")
    lines.append("")
    lines.append("Latest prediction snapshot:")
    lines.append("```json")
    lines.append(json.dumps(prediction_doc or {"note": "Run /predict first."}, indent=2, default=str))
    lines.append("```")
    return "\n".join(lines)


def _build_links_block(args: argparse.Namespace) -> str:
    return "\n".join(
        [
            f"- GitHub repository: `{args.repo_link or '[add]'}`",
            f"- Live deployment: `{args.live_link or '[add]'}`",
            f"- Demo video fallback: `{args.video_link or '[add]'}`",
            f"- Screenshots folder/reference: `{args.screens_link or '[add]'}`",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-fill report.md from latest runtime artifacts.")
    parser.add_argument("--repo-link", default="", help="GitHub repository URL")
    parser.add_argument("--live-link", default="", help="Live deployment URL")
    parser.add_argument("--video-link", default="", help="Demo video URL")
    parser.add_argument("--screens-link", default="", help="Screenshots folder/reference URL")
    parser.add_argument("--report-path", default="report.md", help="Path to report markdown file")
    args = parser.parse_args()

    report_path = Path(args.report_path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")

    metrics_doc = _latest(settings.metrics_collection, "evaluated_at")
    registry_doc = _latest(settings.registry_collection, "registered_at")
    quality_doc = _latest("quality_audits", "audited_at")
    # Use insertion order for predictions to avoid string-sort edge cases on timestamp fields.
    prediction_doc = db[settings.predictions_collection].find_one(
        sort=[("_id", -1)],
        projection={"_id": 0},
    )

    text = report_path.read_text(encoding="utf-8")
    text = _replace_block(
        text,
        "<!-- AUTO_METRICS_TABLE_START -->",
        "<!-- AUTO_METRICS_TABLE_END -->",
        _build_metrics_table(metrics_doc, registry_doc),
    )
    text = _replace_block(
        text,
        "<!-- AUTO_LINKS_START -->",
        "<!-- AUTO_LINKS_END -->",
        _build_links_block(args),
    )
    text = _replace_block(
        text,
        "<!-- AUTO_RUNTIME_SUMMARY_START -->",
        "<!-- AUTO_RUNTIME_SUMMARY_END -->",
        _build_runtime_summary(metrics_doc, registry_doc, quality_doc, prediction_doc),
    )
    report_path.write_text(text, encoding="utf-8")
    print(f"Updated report: {report_path}")


if __name__ == "__main__":
    main()
