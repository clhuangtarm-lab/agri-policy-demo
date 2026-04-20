"""SQLite connection helper.

OneDrive 同步會鎖 SQLite 檔（產生 disk I/O error）。
為避免讀取衝突，啟動時把 DB 快取到本機 temp，再從該路徑連線。
若設定了環境變數 DATABASE_PATH，則直接使用該路徑（不做快取）。
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

from . import config


def _resolve_runtime_db() -> Path:
    """決定執行時要開啟哪個 DB 檔。

    優先順序：
      1. DATABASE_PATH 環境變數（若有）
      2. config.DB_PATH 本機直用（>1MB）
      3. OneDrive/mnt 位置的 DB：複製到 temp 再開啟
      4. ETL 的 build temp 位置（/tmp/agri_demo_build/demo.db）作為 fallback
    """
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        return Path(env_path)

    src = Path(config.DB_PATH)
    src_str = str(src).lower()
    is_synced = "/mnt/" in src_str or "onedrive" in src_str

    # 若主位置檔案可用且非 OneDrive 路徑，直接用
    if src.exists() and src.stat().st_size > 1024 * 1024 and not is_synced:
        return src

    cache = Path(tempfile.gettempdir()) / "agri_demo_runtime" / "demo.db"
    cache.parent.mkdir(parents=True, exist_ok=True)

    if src.exists() and src.stat().st_size > 1024 * 1024:
        if not cache.exists() or cache.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(src, cache)
        return cache

    # fallback：ETL 的 build temp
    build_temp = Path(tempfile.gettempdir()) / "agri_demo_build" / "demo.db"
    if build_temp.exists() and build_temp.stat().st_size > 1024 * 1024:
        return build_temp

    raise FileNotFoundError(
        f"No usable DB. tried: {src} ({src.stat().st_size if src.exists() else 'missing'} bytes), "
        f"{build_temp}"
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
