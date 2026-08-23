from __future__ import annotations

from pathlib import Path

import gridfs
from bson import ObjectId

from .db import db


def save_model_to_gridfs(local_model_path: Path) -> ObjectId:
    fs = gridfs.GridFS(db)
    with local_model_path.open("rb") as f:
        return fs.put(
            f.read(),
            filename=local_model_path.name,
            content_type="application/octet-stream",
        )


def load_model_bytes_from_gridfs(file_id: str | ObjectId) -> bytes:
    fs = gridfs.GridFS(db)
    if isinstance(file_id, str):
        file_id = ObjectId(file_id)
    return fs.get(file_id).read()
