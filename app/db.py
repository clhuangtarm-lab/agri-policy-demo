"""SQLite connection helper with runtime DB validation."""
from __future__ import annotations

import importlib
import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

from . import config

REQUIRED_TABLES = (
    "crop_area",
    "analysis_a",
    "analysis_c",
    "coverage_risk",
    "irac_diversity",
    "crop_coverage_full",
    "pesticide_full",
)


def _is_usable_db(path: Path) -> bool:
    if not path.exists() or path.stat().st_size <= 1024 * 1024:
        return False
    try:
        conn = sqlite3.connect(path)
        try:
            existing = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        finally:
            conn.close()
    except sqlite3.Error:
        return False
    return all(table in existing for table in REQUIRED_TABLES)


def _bootstrap_initialized_db() -> None:
    try:
        build_module = importlib.import_module("etl.build_db")
        build_module.build()
    except Exception as exc:  # pragma: no cover - startup safeguard
        raise FileNotFoundError(
            "No usable initialized DB found and ETL bootstrap failed."
        ) from exc


def _resolve_runtime_db() -> Path:
    env_path = os.getenv("DATABASE_PATH")
    env_db = Path(env_path) if env_path else None
    if env_path:
        if _is_usable_db(env_db):
            return env_db

    src = Path(config.DB_PATH)
    src_str = str(src).lower()
    is_synced = "/mnt/" in src_str or "onedrive" in src_str

    if _is_usable_db(src) and not is_synced:
        return src

    cache = Path(tempfile.gettempdir()) / "agri_demo_runtime" / "demo.db"
    cache.parent.mkdir(parents=True, exist_ok=True)

    if _is_usable_db(src):
        if not cache.exists() or cache.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, cache)
        return cache

    build_temp = Path(tempfile.gettempdir()) / "agri_demo_build" / "demo.db"
    if _is_usable_db(build_temp):
        return build_temp

    _bootstrap_initialized_db()

    for candidate in (env_db, src, build_temp):
        if candidate and _is_usable_db(candidate):
            return candidate

    raise FileNotFoundError(
        "No usable initialized DB found. "
        f"Checked DATABASE_PATH={env_path!r}, src={src} "
        f"({src.stat().st_size if src.exists() else 'missing'} bytes), "
        f"build_temp={build_temp}"
    )


RUNTIME_DB = _resolve_runtime_db()


def connect():
    conn = sqlite3.connect(RUNTIME_DB)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def cursor():
    conn = connect()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def fetchall(sql: str, params=()):
    conn = connect()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetchone(sql: str, params=()):
    conn = connect()
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
