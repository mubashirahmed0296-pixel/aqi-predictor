from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import settings


def _mask_mongo_uri(uri: str) -> str:
    # mongodb+srv://user:pass@host -> mongodb+srv://user:***@host
    return re.sub(r"(mongodb(?:\+srv)?://[^:]+:)([^@]+)(@)", r"\1***\3", uri)


def main() -> None:
    checks: dict[str, dict[str, str]] = {}

    checks["env_file"] = {
        "status": "pass" if Path(".env").exists() else "fail",
        "detail": ".env present" if Path(".env").exists() else ".env missing",
    }

    bad_placeholder = "<cluster>" in settings.mongodb_uri or "<user>" in settings.mongodb_uri
    uri_kind = "mongodb+srv" if settings.mongodb_uri.startswith("mongodb+srv://") else "mongodb"
    checks["mongodb_uri_format"] = {
        "status": "fail" if bad_placeholder else "pass",
        "detail": f"{_mask_mongo_uri(settings.mongodb_uri)} (type={uri_kind})",
    }

    docker_installed = shutil.which("docker") is not None
    checks["docker_cli"] = {
        "status": "pass" if docker_installed else "warn",
        "detail": "docker found in PATH" if docker_installed else "docker not found in PATH",
    }
    if docker_installed:
        try:
            proc = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=8,
                check=False,
            )
            if proc.returncode == 0:
                checks["docker_engine"] = {"status": "pass", "detail": "docker engine reachable"}
            else:
                checks["docker_engine"] = {
                    "status": "warn",
                    "detail": "docker engine not reachable (start Docker Desktop)",
                }
        except Exception:
            checks["docker_engine"] = {
                "status": "warn",
                "detail": "docker engine check failed (start Docker Desktop)",
            }
    else:
        checks["docker_engine"] = {"status": "warn", "detail": "skipped; docker not installed"}

    if not bad_placeholder:
        try:
            client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            checks["mongodb_connectivity"] = {"status": "pass", "detail": "ping ok"}
        except PyMongoError as ex:
            checks["mongodb_connectivity"] = {"status": "fail", "detail": str(ex)}
    else:
        checks["mongodb_connectivity"] = {"status": "fail", "detail": "skipped due to invalid placeholder URI"}

    remediation = []
    if checks["mongodb_connectivity"]["status"] == "fail":
        remediation.append("Option A: start Docker Desktop and run `docker compose -f docker-compose.local.yml up -d mongo`.")
        remediation.append("Option B: use MongoDB Atlas and set a valid `MONGODB_URI` in backend/.env.")
    if bad_placeholder:
        remediation.append("Replace placeholder URI values (`<user>`, `<cluster>`) in backend/.env.")
    checks["remediation"] = {
        "status": "info",
        "detail": " | ".join(remediation) if remediation else "No remediation needed.",
    }

    out_dir = Path("artifacts/runtime")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "preflight_check.json"
    out_file.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    print(f"Wrote: {out_file}")

    if any(v["status"] == "fail" for v in checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
