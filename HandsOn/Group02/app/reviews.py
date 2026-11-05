"""App-generated data (FR-05): ratings, comments, tags and photos.

Stored in SQLite, keyed by the resource URI from the knowledge graph. This
data is kept apart from the open-data graph on purpose: it is ours, not the
City of Chicago's, and it changes on every review.
"""
from __future__ import annotations

import sqlite3
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterable

TAGS = ("family-friendly", "well-maintained", "crowded", "quiet", "historic", "accessible")
MAX_COMMENT = 1000
MAX_PHOTO_BYTES = 5 * 1024 * 1024
_MAGIC = {b"\x89PNG\r\n\x1a\n": ".png", b"\xff\xd8\xff": ".jpg"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_uri TEXT    NOT NULL,
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT    NOT NULL DEFAULT '',
    tags         TEXT    NOT NULL DEFAULT '',
    photo        TEXT,
    created_at   TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reviews_uri ON reviews (resource_uri);
"""


class ReviewError(ValueError):
    pass


@dataclass
class Aggregate:
    count: int = 0
    rating_sum: int = 0
    tags: Counter = field(default_factory=Counter)

    @property
    def average(self) -> float:
        return self.rating_sum / self.count if self.count else 0.0

    @classmethod
    def merge(cls, parts: Iterable["Aggregate"]) -> "Aggregate":
        total = cls()
        for part in parts:
            total.count += part.count
            total.rating_sum += part.rating_sum
            total.tags.update(part.tags)
        return total


def _photo_extension(head: bytes) -> str | None:
    for magic, ext in _MAGIC.items():
        if head.startswith(magic):
            return ext
    return None


class ReviewStore:
    def __init__(self, db_path: Path | str, upload_dir: Path | str) -> None:
        self.db_path = str(db_path)
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def add(
        self,
        resource_uri: str,
        rating,
        comment: str = "",
        tags: Iterable[str] = (),
        photo: BinaryIO | None = None,
    ) -> int:
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            raise ReviewError("Please choose a rating from 1 to 5 stars.") from None
        if not 1 <= rating <= 5:
            raise ReviewError("Please choose a rating from 1 to 5 stars.")
        comment = (comment or "").strip()
        if len(comment) > MAX_COMMENT:
            raise ReviewError(f"Reviews can be at most {MAX_COMMENT} characters.")
        clean_tags = []
        for tag in tags:
            if tag not in TAGS:
                raise ReviewError(f"Unknown tag: {tag}")
            if tag not in clean_tags:
                clean_tags.append(tag)

        photo_name = None
        if photo is not None:
            data = photo.read(MAX_PHOTO_BYTES + 1)
            if data:
                if len(data) > MAX_PHOTO_BYTES:
                    raise ReviewError("Photos can be at most 5 MB.")
                ext = _photo_extension(data[:8])
                if ext is None:
                    raise ReviewError("Photos must be JPEG or PNG images.")
                photo_name = uuid.uuid4().hex + ext
                (self.upload_dir / photo_name).write_bytes(data)

        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as db:
            cur = db.execute(
                "INSERT INTO reviews (resource_uri, rating, comment, tags, photo, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (resource_uri, rating, comment, ",".join(clean_tags), photo_name, created),
            )
            return int(cur.lastrowid)

    def for_resource(self, resource_uri: str) -> list[dict]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM reviews WHERE resource_uri = ? ORDER BY id DESC", (resource_uri,)
            ).fetchall()
        return [
            {**dict(r), "tags": [t for t in r["tags"].split(",") if t], "created_at": r["created_at"][:10]}
            for r in rows
        ]

    def all_aggregates(self) -> dict[str, Aggregate]:
        result: dict[str, Aggregate] = {}
        with self._connect() as db:
            for r in db.execute("SELECT resource_uri, rating, tags FROM reviews"):
                agg = result.setdefault(r["resource_uri"], Aggregate())
                agg.count += 1
                agg.rating_sum += r["rating"]
                agg.tags.update(t for t in r["tags"].split(",") if t)
        return result

    def aggregate(self, uris: Iterable[str]) -> Aggregate:
        """Ratings and tags of one resource, or of several pooled together."""
        uris = list(uris)
        total = Aggregate()
        if not uris:
            return total
        marks = ",".join("?" * len(uris))
        with self._connect() as db:
            for r in db.execute(f"SELECT rating, tags FROM reviews WHERE resource_uri IN ({marks})", uris):
                total.count += 1
                total.rating_sum += r["rating"]
                total.tags.update(t for t in r["tags"].split(",") if t)
        return total
