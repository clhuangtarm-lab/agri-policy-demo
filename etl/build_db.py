"""
ETL：把 23 支 MOA API 與 reference 檔案清洗整合進 SQLite。

執行：
    cd output/demo_platform
    python -m etl.build_db

輸出：
    data/demo.db（含 crop_dict / crop_area / traceability_producer / traceability_product
                  / pesticide_coverage / inspection / aggregates_* 等表）
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd


# ---------- 路徑 ----------
HERE = Path(__file__).resolve().parent.parent
DATA_ROOT = HERE.parent.parent  # agri_policy_project/
API_DIR = DATA_ROOT / "workspace" / "etl" / "raw_fixed" / "api"
REF_DIR = DATA_ROOT / "input" / "reference"
PEST_DIR = REF_DIR / "Pesticide"
FINAL_DB_PATH = HERE / "data" / "demo.db"
FINAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# OneDrive 對 SQLite 同步會鎖檔。先在本機 temp 建 DB，結束後一次性複製過去。
_TEMP_DIR = Path(tempfile.gettempdir()) / "agri_demo_build"
_TEMP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _TEMP_DIR / "demo.db"


# ---------- 作物根名抽取 ----------
_NOISE_PREFIX = re.compile(r"^(履歷|有機|CAS|無毒|經典|精選)")
_SPACES = re.compile(r"[\s\r\n\t]+")
_SIZE_SUFFIX = re.compile(r"[\(（][^)）]{0,20}[\)）]$")  # 移除尾端括號
_QTY_SUFFIX = re.compile(r"[\-－]?\s*\d+\s*[GgKkMm]?[Gg]?\s*$")  # '600G', '1KG'


def extract_crop_root(name: str) -> str:
    """從 '甘藷-紫心600G' / '水稻-池農無毒\\n米' 萃取 '甘藷' / '水稻'。"""
    if not name or pd.isna(name):
        return ""
    s = str(name).strip()
    s = _SPACES.sub("", s)
    s = _NOISE_PREFIX.sub("", s)
    s = _SIZE_SUFFIX.sub("", s)
    # 取 '-' 之前
    if "-" in s:
        s = s.split("-", 1)[0]
    s = _QTY_SUFFIX.sub("", s).strip()
    return s


# ---------- 小工具 ----------
def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------- ETL 主體 ----------
def build():
    log(f"輸出 DB: {DB_PATH}")
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)

    # 1. 作物字典（API-14 + 作物分類對照表）
    log("1/7 建作物字典與分類")
    crop_dict = pd.DataFrame(load_json(API_DIR / "API-14_CropType.json"))
    crop_dict.columns = ["crop_code", "crop_name"]
    # 作物分類對照表
    try:
        crop_tax = pd.read_csv(REF_DIR / "作物分類對照表_研究分析版.csv")
        crop_tax_lite = crop_tax[[
            "crop_name_full", "category_lv1_name", "category_lv2_name",
            "category_lv3_name", "family_name", "variety_name",
            "include_theme1", "include_theme2", "include_theme3"
        ]].copy()
        crop_tax_lite.columns = [
            "crop_full", "cat_lv1", "cat_lv2", "cat_lv3",
            "family", "variety", "in_theme1", "in_theme2", "in_theme3"
        ]
        crop_tax_lite["crop_root"] = crop_tax_lite["crop_full"].apply(
            lambda x: x.split("-")[0] if isinstance(x, str) else ""
        )
        crop_tax_lite.to_sql("crop_taxonomy", conn, index=False)
        log(f"  crop_taxonomy: {len(crop_tax_lite):,} rows")
    except Exception as e:
        log(f"  (略過 crop_taxonomy: {e})")

    crop_dict.to_sql("crop_dict", conn, index=False)

    # 作物別名
    try:
        alias = pd.read_csv(REF_DIR / "作物名稱_alias拆分.csv")
        alias = alias[["crop_name_full", "alias", "category_lv1_name",
                       "category_lv2_name", "category_lv3_name"]].copy()
        alias.columns = ["crop_full", "alias", "cat_lv1", "cat_lv2", "cat_lv3"]
        alias.to_sql("crop_alias", conn, index=False)
        log(f"  crop_alias: {len(alias):,} rows")
    except Exception as e:
        log(f"  (略過 crop_alias: {e})")

    # 2. 農情調查（113 年度，使用 clean 版）
    log("2/7 載入農情調查（agri_clean）")
    agri = pd.read_csv(PEST_DIR / "agri_clean.csv")
    agri.columns = ["county", "town", "crop", "year", "season", "area_ha"]
    agri["area_ha"] = pd.to_numeric(agri["area_ha"], errors="coerce").fillna(0)
    agri = agri[agri["area_ha"] > 0]
    agri.to_sql("crop_area", conn, index=False)
    log(f"  crop_area: {len(agri):,} rows")

    # 3. 履歷（API-19 + API-20，TraceCode 接合）
    log("3/7 載入履歷")
    producer = pd.DataFrame(load_json(API_DIR / "API-19_TWAgriProductsTraceabilityType_ProducerInfo.json"))
    product = pd.DataFrame(load_json(API_DIR / "API-20_TWAgriProductsTraceabilityType_ProductInfo.json"))

    # 履歷產品抽出作物根名
    product["crop_root"] = product["Product"].apply(extract_crop_root)

    # 寫入
    producer.to_sql("traceability_producer", conn, index=False)
    product.to_sql("traceability_product", conn, index=False)
    log(f"  producer: {len(producer):,} / product: {len(product):,}")

    # 4. 藥檢（API-23）
    log("4/7 載入藥檢結果")
    inspect = pd.DataFrame(load_json(API_DIR / "API-23_SalesResumeAgriproductsResultsType.json"))
    inspect["crop_root"] = inspect["ProductName"].apply(
        lambda s: extract_crop_root(re.sub(r"^履歷", "", str(s)) if s else "")
    )
    # 合格分類（簡化：含「合格」算合格）
    inspect["is_pass"] = inspect["InspectResult"].astype(str).str.contains("合格", na=False)
    inspect.to_sql("inspection", conn, index=False)
    log(f"  inspection: {len(inspect):,} rows（合格 {inspect['is_pass'].sum():,}）")

    # 5. 農藥 + 覆蓋度（Pesticide 既有 csv）
    log("5/7 載入農藥 + 覆蓋度")
    pest_full = pd.read_csv(PEST_DIR / "pesticide_full.csv")
    pest_full.to_sql("pesticide_full", conn, index=False)

    for fname, tbl in [
        ("coverage_risk.csv", "coverage_risk"),
        ("irac_diversity.csv", "irac_diversity"),
        ("crop_coverage_full.csv", "crop_coverage_full"),
    ]:
        try:
            df = pd.read_csv(PEST_DIR / fname)
            df.to_sql(tbl, conn, index=False)
            log(f"  {tbl}: {len(df):,} rows")
        except Exception as e:
            log(f"  (略過 {tbl}: {e})")

    # 既有分析成果
    log("6/7 載入既有 analysis_A-F")
    for letter in ["A", "B", "C", "D", "E", "F"]:
        try:
            df = pd.read_csv(PEST_DIR / f"analysis_{letter}.csv")
            df.to_sql(f"analysis_{letter.lower()}", conn, index=False)
            log(f"  analysis_{letter.lower()}: {len(df):,} rows")
        except Exception as e:
            log(f"  (略過 analysis_{letter}: {e})")

    # 7. 預聚合：for P-00 首頁 / P-11 地圖
    log("7/7 建聚合表與索引")
    cur = conn.cursor()

    # 縣市作物面積（for 地圖）
    cur.execute("""
        CREATE TABLE agg_county_crop AS
        SELECT county, crop, SUM(area_ha) AS area_ha,
               COUNT(DISTINCT town) AS town_count
        FROM crop_area
        GROUP BY county, crop
    """)
    # 縣市總面積
    cur.execute("""
        CREATE TABLE agg_county AS
        SELECT county, SUM(area_ha) AS total_area,
               COUNT(DISTINCT crop) AS crop_count,
               COUNT(DISTINCT town) AS town_count
        FROM crop_area
        GROUP BY county
    """)
    # 作物總面積排行
    cur.execute("""
        CREATE TABLE agg_crop AS
        SELECT crop, SUM(area_ha) AS total_area,
               COUNT(DISTINCT county) AS county_count
        FROM crop_area
        GROUP BY crop
    """)
    # 履歷縣市聚合（從 Address 取第一個縣市字串）
    cur.execute("""
        CREATE TABLE agg_producer_county AS
        SELECT SUBSTR(Address, 1, 3) AS county_raw, COUNT(*) AS producer_count
        FROM traceability_producer
        GROUP BY county_raw
        ORDER BY producer_count DESC
    """)
    # 索引
    for stmt in [
        "CREATE INDEX ix_crop_area_county ON crop_area(county)",
        "CREATE INDEX ix_crop_area_crop ON crop_area(crop)",
        "CREATE INDEX ix_product_trace ON traceability_product(TraceCode)",
        "CREATE INDEX ix_product_crop ON traceability_product(crop_root)",
        "CREATE INDEX ix_producer_trace ON traceability_producer(TraceCode)",
        "CREATE INDEX ix_inspect_crop ON inspection(crop_root)",
    ]:
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError as e:
            log(f"  (索引略過 {e})")

    conn.commit()
    conn.close()

    # 複製至最終位置
    log(f"複製 DB → {FINAL_DB_PATH}")
    shutil.copy2(DB_PATH, FINAL_DB_PATH)
    size_mb = FINAL_DB_PATH.stat().st_size / 1024 / 1024
    log(f"完成。DB 大小 {size_mb:.1f} MB")


if __name__ == "__main__":
    build()
