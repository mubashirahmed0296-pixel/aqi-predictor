from typing import Any

import requests

from .config import settings


def latest_workflow_runs() -> list[dict[str, Any]]:
    if not settings.github_repo:
        return []

    owner_repo = settings.github_repo.strip()
    if "<" in owner_repo or ">" in owner_repo or "/" not in owner_repo:
        return []

    url = f"https://api.github.com/repos/{owner_repo}/actions/runs"
    headers = {}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException:
        return []

    runs = response.json().get("workflow_runs", [])[:5]
    return [
        {
            "name": r.get("name"),
            "status": r.get("status"),
            "conclusion": r.get("conclusion"),
            "updated_at": r.get("updated_at"),
            "html_url": r.get("html_url"),
        }
        for r in runs
    ]
