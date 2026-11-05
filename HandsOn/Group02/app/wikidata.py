"""Linked-data enrichment: follow owl:sameAs to Wikidata.

For each park or artist with an owl:sameAs link, the public Wikidata SPARQL
endpoint is asked for a label, description, image, Wikipedia article and a
few facts. Answers are cached on disk; if Wikidata is unreachable the pages
simply show what our own graph knows.
"""
from __future__ import annotations

import json
import logging
import re
import threading
import time
from pathlib import Path
from urllib.parse import quote, unquote

import requests

from kg import USER_AGENT
from queries import WIKIDATA_ENTITY

log = logging.getLogger(__name__)

ENDPOINT = "https://query.wikidata.org/sparql"
QID = re.compile(r"^https?://www\.wikidata\.org/entity/(Q[0-9]+)$")
TTL_SECONDS = 30 * 24 * 3600
BACKOFF_SECONDS = 120


def qid_of(uri: str | None) -> str | None:
    match = QID.match(uri or "")
    return match.group(1) if match else None


def _commons(image_url: str) -> dict:
    """Turn a P18 Special:FilePath URL into a thumbnail and its file page."""
    filename = unquote(image_url.rsplit("/", 1)[-1])
    encoded = quote(filename.replace(" ", "_"))
    return {
        "thumb": f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=640",
        "page": f"https://commons.wikimedia.org/wiki/File:{encoded}",
        "file": filename,
    }


def _merge(rows: list[dict]) -> dict:
    """Collect the (key, value) rows into one record."""
    out: dict = {"occupations": [], "citizenships": []}
    lists = {"occupation": "occupations", "citizenship": "citizenships"}
    for row in rows:
        key, value = row["key"]["value"], row["value"]["value"]
        if key in lists:
            if value not in out[lists[key]] and len(out[lists[key]]) < 5:
                out[lists[key]].append(value)
        elif key not in out:
            out[key] = value
    for key in ("birth", "death", "inception"):
        if key in out:
            out[key] = out[key][:10].lstrip("+")
    if "image" in out:
        out["image"] = _commons(out["image"])
    if "area" in out:
        try:
            out["area"] = round(float(out["area"]), 1)
        except ValueError:
            del out["area"]
    return out


class WikidataClient:
    def __init__(
        self,
        cache_path: Path | str,
        seed_path: Path | str | None = None,
        enabled: bool = True,
        endpoint: str = ENDPOINT,
        timeout: float = 10,
    ) -> None:
        """seed_path: read-only cache shipped with the app (see warm_wikidata.py);
        cache_path: where answers fetched at runtime are written."""
        self.cache_path = Path(cache_path)
        self.enabled = enabled
        self.endpoint = endpoint
        self.timeout = timeout
        self._lock = threading.Lock()
        self._offline_until = 0.0
        self._cache: dict = {}
        for path in (seed_path, self.cache_path):
            if path is None:
                continue
            try:
                self._cache.update(json.loads(Path(path).read_text("utf-8")))
            except (OSError, ValueError):
                pass

    def _save(self) -> None:
        tmp = self.cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._cache, ensure_ascii=False, indent=1), "utf-8")
        tmp.replace(self.cache_path)

    def entity(self, uri: str | None) -> dict | None:
        """Facts about a Wikidata entity, or None when unknown or unreachable."""
        qid = qid_of(uri)
        if qid is None:
            return None
        with self._lock:
            cached = self._cache.get(qid)
        if cached and time.time() - cached["fetched"] < TTL_SECONDS:
            return {**cached["data"], "qid": qid, "uri": uri}
        if not self.enabled or time.time() < self._offline_until:
            return {**cached["data"], "qid": qid, "uri": uri} if cached else None
        try:
            response = requests.get(
                self.endpoint,
                params={"query": WIKIDATA_ENTITY % {"qid": qid}, "format": "json"},
                headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = _merge(response.json()["results"]["bindings"])
        except (requests.RequestException, ValueError, KeyError) as exc:
            log.warning("Wikidata unreachable for %s: %s", qid, exc)
            self._offline_until = time.time() + BACKOFF_SECONDS
            return {**cached["data"], "qid": qid, "uri": uri} if cached else None
        with self._lock:
            self._cache[qid] = {"fetched": time.time(), "data": data}
            try:
                self._save()
            except OSError as exc:
                log.warning("Could not write the Wikidata cache: %s", exc)
        return {**data, "qid": qid, "uri": uri}
