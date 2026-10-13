"""Deterministic acquisition of the official UCI SECOM archive."""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from yieldguard.config import project_path

EXPECTED_MEMBERS = {"secom.data", "secom_labels.data", "secom.names"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _locate_members(archive: zipfile.ZipFile) -> dict[str, str]:
    by_leaf: dict[str, str] = {}
    for member in archive.namelist():
        leaf = PurePosixPath(member).name
        if leaf in EXPECTED_MEMBERS:
            if leaf in by_leaf:
                raise ValueError(f"Archive contains duplicate member named {leaf!r}")
            by_leaf[leaf] = member
    missing = EXPECTED_MEMBERS - by_leaf.keys()
    if missing:
        raise ValueError(f"Archive is missing expected members: {sorted(missing)}")
    return by_leaf


def acquire_dataset(config: dict[str, Any], force: bool = False) -> dict[str, Any]:
    """Download, validate, and safely extract the official SECOM source files."""
    data_config = config["data"]
    archive_path = project_path(data_config["landing_archive"])
    raw_directory = archive_path.parent
    manifest_path = raw_directory / "source_manifest.json"
    raw_directory.mkdir(parents=True, exist_ok=True)

    if force or not archive_path.exists():
        temporary_path = archive_path.with_suffix(".download")
        request = urllib.request.Request(
            data_config["source_url"],
            headers={"User-Agent": "YieldGuard/0.1 (+UCI dataset 179)"},
        )
        try:
            with (
                urllib.request.urlopen(request, timeout=60) as response,  # noqa: S310
                temporary_path.open("wb") as target,
            ):
                shutil.copyfileobj(response, target)
            temporary_path.replace(archive_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    with zipfile.ZipFile(archive_path) as archive:
        located = _locate_members(archive)
        for leaf, member in located.items():
            destination = raw_directory / leaf
            with archive.open(member) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)

    files = {
        name: {
            "bytes": (raw_directory / name).stat().st_size,
            "sha256": sha256_file(raw_directory / name),
        }
        for name in sorted(EXPECTED_MEMBERS)
    }
    manifest = {
        "dataset": "SECOM",
        "dataset_id": int(data_config["dataset_id"]),
        "source_url": data_config["source_url"],
        "doi": "10.24432/C54305",
        "license": "CC BY 4.0",
        "archive": {
            "bytes": archive_path.stat().st_size,
            "sha256": sha256_file(archive_path),
        },
        "files": files,
        "acquired_at_utc": datetime.now(UTC).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
