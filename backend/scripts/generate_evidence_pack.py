from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "report.md",
    "COMPLIANCE_PLAYBOOK.md",
    "EVALUATION_VIVA_SCRIPT.md",
    "FINAL_EXECUTION_CHECKLIST.md",
    "PROJECT_EXECUTION_PLAN.md",
    "RISK_REGISTER.md",
    "MONGODB_UNBLOCK_GUIDE.md",
    "docker-compose.local.yml",
    "scripts/bootstrap_local.ps1",
    "scripts/run_all_local.ps1",
    "scripts/set_mongo_uri.ps1",
    "backend/app/api.py",
    "backend/app/train.py",
    "backend/app/predict.py",
    "backend/app/quality.py",
    "backend/scripts/run_backfill.py",
    "backend/scripts/autofill_report_from_runtime.py",
    "backend/scripts/preflight_check.py",
    "backend/scripts/run_ingest.py",
    "backend/scripts/run_train.py",
    "backend/scripts/run_quality_audit.py",
    "backend/scripts/run_eda.py",
    "backend/scripts/run_explainability.py",
    "backend/scripts/generate_runtime_report.py",
    ".github/workflows/feature-pipeline.yml",
    ".github/workflows/training-pipeline.yml",
    ".github/workflows/manual-recovery.yml",
]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    out_dir = root / "submission_evidence"
    out_dir.mkdir(parents=True, exist_ok=True)

    found = []
    missing = []
    for rel in REQUIRED_FILES:
        p = root / rel
        if p.exists():
            found.append(rel)
        else:
            missing.append(rel)

    ts = datetime.now(timezone.utc).isoformat()
    report = [
        f"# Submission Evidence Snapshot",
        "",
        f"Generated at (UTC): `{ts}`",
        "",
        f"## Found ({len(found)})",
    ]
    report.extend([f"- {f}" for f in found])
    report.append("")
    report.append(f"## Missing ({len(missing)})")
    report.extend([f"- {m}" for m in missing] if missing else ["- None"])
    report.append("")
    report.append("## Next Action")
    if missing:
        report.append("- Resolve missing artifacts before final submission.")
    else:
        report.append("- Proceed to populate runtime outputs, screenshots, and links in report.")

    out_file = out_dir / "evidence_snapshot.md"
    out_file.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote: {out_file}")


if __name__ == "__main__":
    main()
