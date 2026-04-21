"""Reusable dashboard queries from SQLite."""
from __future__ import annotations

from collections import Counter
import re

from .. import config
from ..db import fetchall, fetchone

CODE_SPLIT_RE = re.compile(r"[,/;、，]+")


def _split_codes(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in CODE_SPLIT_RE.split(value) if part.strip()]


def _crop_exists_in_table(table: str, crop: str) -> bool:
    row = fetchone(f"SELECT 1 AS ok FROM {table} WHERE [作物] = ? LIMIT 1", (crop,))
    return bool(row)


def _candidate_crop_names(crop: str) -> list[str]:
    candidates: list[str] = []

    def add(value: str | None):
        if value and value not in candidates:
            candidates.append(value)

    add(crop)

    taxonomy_rows = fetchall(
        """
        SELECT crop_root, cat_lv1, cat_lv2, cat_lv3
        FROM crop_taxonomy
        WHERE crop_root = ? OR crop_full = ?
        LIMIT 20
        """,
        (crop, crop),
    )
    for row in taxonomy_rows:
        add(row.get("crop_root"))
        add(row.get("cat_lv3"))
        add(row.get("cat_lv2"))
        add(row.get("cat_lv1"))

    if "稻" in crop:
        add("水稻")
    if "玉米" in crop:
        add("玉米")
    if any(token in crop for token in ("柑", "橘", "柚", "檸檬", "橙")):
        add("柑桔類")
    if "葉菜" in crop:
        add("葉菜類")
    if "包葉" in crop:
        add("十字花科包葉菜類")
    if "小葉" in crop:
        add("十字花科小葉菜類")
    if "根菜" in crop:
        add("十字花科根菜類")
    if "瓜" in crop:
        add("瓜果類")
        add("瓜菜類")
    if "豆" in crop:
        add("豆菜類")

    return candidates


def _resolve_reference_crop_name(crop: str, table: str) -> str:
    for candidate in _candidate_crop_names(crop):
        if _crop_exists_in_table(table, candidate):
            return candidate

    for candidate in _candidate_crop_names(crop):
        rows = fetchall(
            f"""
            SELECT DISTINCT [作物] AS crop
            FROM {table}
            WHERE [作物] LIKE ?
            ORDER BY LENGTH([作物]) ASC
            LIMIT 1
            """,
            (f"%{candidate}%",),
        )
        if rows:
            return rows[0]["crop"]

    return crop


def get_summary_counts() -> dict:
    return {
        "crop_area_rows": fetchone("SELECT COUNT(*) AS n FROM crop_area")["n"],
        "crop_area_total": fetchone("SELECT ROUND(SUM(area_ha), 1) AS n FROM crop_area")["n"],
        "crop_count": fetchone("SELECT COUNT(DISTINCT crop) AS n FROM crop_area")["n"],
        "county_count": fetchone("SELECT COUNT(DISTINCT county) AS n FROM crop_area")["n"],
        "town_count": fetchone("SELECT COUNT(DISTINCT town) AS n FROM crop_area")["n"],
        "producer_count": fetchone("SELECT COUNT(*) AS n FROM traceability_producer")["n"],
        "product_count": fetchone("SELECT COUNT(*) AS n FROM traceability_product")["n"],
        "inspection_count": fetchone("SELECT COUNT(*) AS n FROM inspection")["n"],
        "inspection_pass_rate": round(
            fetchone("SELECT AVG(CASE WHEN is_pass THEN 1.0 ELSE 0 END) AS r FROM inspection")["r"] * 100,
            1,
        ),
        "pesticide_count": fetchone("SELECT COUNT(*) AS n FROM pesticide_full")["n"],
        "coverage_risk_count": fetchone("SELECT COUNT(*) AS n FROM coverage_risk")["n"],
        "crop_dict_count": fetchone("SELECT COUNT(*) AS n FROM crop_dict")["n"],
    }


def get_top_crops(limit: int = 10) -> list[dict]:
    return fetchall(
        """
        SELECT crop,
               ROUND(total_area, 1) AS total_area,
               county_count
        FROM agg_crop
        ORDER BY total_area DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_county_totals(limit: int | None = None) -> list[dict]:
    sql = """
        SELECT county,
               ROUND(total_area, 1) AS total_area,
               crop_count,
               town_count
        FROM agg_county
        ORDER BY total_area DESC
    """
    if limit is not None:
        sql += " LIMIT ?"
        return fetchall(sql, (limit,))
    return fetchall(sql)


def get_high_risk_crops(limit: int = 20) -> list[dict]:
    return fetchall(
        """
        SELECT [作物] AS crop,
               ROUND(CAST([全台種植面積(公頃)] AS REAL), 1) AS area_ha,
               CAST([高風險機制占比] AS REAL) AS high_risk_ratio,
               ROUND(CAST([加權風險暴露] AS REAL), 1) AS exposure,
               CAST([有效登記農藥數] AS INTEGER) AS registration_count
        FROM analysis_a
        ORDER BY CAST([加權風險暴露] AS REAL) DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_low_coverage_crops(limit: int = 20) -> list[dict]:
    return fetchall(
        """
        SELECT [作物] AS crop,
               CAST([有效登記筆數] AS INTEGER) AS registration_count,
               [充裕度等級] AS coverage_level,
               CAST([IRAC代碼種數] AS INTEGER) AS irac_code_count
        FROM coverage_risk
        ORDER BY CAST([有效登記筆數] AS REAL) ASC, [作物] ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_coverage_level_distribution() -> list[dict]:
    return fetchall(
        """
        SELECT [充裕度等級] AS label,
               COUNT(*) AS count
        FROM coverage_risk
        GROUP BY [充裕度等級]
        ORDER BY count DESC, [充裕度等級] ASC
        """
    )


def get_vulnerable_crops(limit: int = 12) -> list[dict]:
    return fetchall(
        """
        SELECT [作物] AS crop,
               ROUND(CAST([種植面積] AS REAL), 1) AS area_ha,
               CAST([有效登記數] AS INTEGER) AS registration_count,
               ROUND(CAST([IRAC多樣性] AS REAL), 1) AS irac_diversity,
               [風險說明] AS risk_note
        FROM analysis_b
        ORDER BY CAST([有效登記數] AS REAL) ASC, CAST([種植面積] AS REAL) DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_county_risk(limit: int | None = None) -> list[dict]:
    sql = """
        SELECT [縣市] AS county,
               ROUND(CAST([總種植面積] AS REAL), 1) AS area_ha,
               ROUND(CAST([加權風險暴露] AS REAL), 1) AS exposure,
               [前3高風險作物] AS top_crops_text
        FROM analysis_c
        ORDER BY CAST([加權風險暴露] AS REAL) DESC
    """
    if limit is not None:
        sql += " LIMIT ?"
        rows = fetchall(sql, (limit,))
    else:
        rows = fetchall(sql)
    for row in rows:
        row["county_key"] = config.normalize_county_name(row["county"])
        row["top_crops"] = [item.strip() for item in re.split(r"[；;]", row["top_crops_text"] or "") if item.strip()]
    return rows


def get_crops_by_county(county: str, limit: int = 12) -> list[dict]:
    return fetchall(
        """
        SELECT crop,
               ROUND(area_ha, 1) AS area_ha,
               town_count
        FROM agg_county_crop
        WHERE county = ?
        ORDER BY area_ha DESC
        LIMIT ?
        """,
        (county, limit),
    )


def get_county_crop_matrix(crop: str) -> list[dict]:
    return fetchall(
        """
        SELECT county,
               ROUND(area_ha, 1) AS area_ha,
               town_count
        FROM agg_county_crop
        WHERE crop = ?
        ORDER BY area_ha DESC
        """,
        (crop,),
    )


def get_township_risk(limit: int = 40) -> list[dict]:
    return fetchall(
        """
        WITH crop_risk AS (
            SELECT [作物] AS crop,
                   CAST([高風險機制占比] AS REAL) AS high_risk_ratio
            FROM analysis_a
        ),
        township_crop AS (
            SELECT ca.county,
                   ca.town,
                   ca.crop,
                   SUM(ca.area_ha) AS crop_area,
                   SUM(ca.area_ha * COALESCE(cr.high_risk_ratio, 0)) AS crop_exposure
            FROM crop_area ca
            LEFT JOIN crop_risk cr ON cr.crop = ca.crop
            GROUP BY ca.county, ca.town, ca.crop
        ),
        township_total AS (
            SELECT county,
                   town,
                   ROUND(SUM(crop_area), 1) AS area_ha,
                   ROUND(SUM(crop_exposure), 1) AS exposure,
                   COUNT(DISTINCT crop) AS crop_count
            FROM township_crop
            GROUP BY county, town
        ),
        township_ranked AS (
            SELECT tc.county,
                   tc.town,
                   tt.area_ha,
                   tt.exposure,
                   tt.crop_count,
                   tc.crop,
                   tc.crop_area,
                   ROW_NUMBER() OVER (
                       PARTITION BY tc.county, tc.town
                       ORDER BY tc.crop_area DESC, tc.crop
                   ) AS crop_rank
            FROM township_crop tc
            JOIN township_total tt
              ON tt.county = tc.county
             AND tt.town = tc.town
        )
        SELECT county,
               town,
               area_ha,
               exposure,
               crop_count,
               crop AS top_crop,
               ROUND(CASE WHEN area_ha > 0 THEN crop_area / area_ha ELSE 0 END, 4) AS top_crop_ratio
        FROM township_ranked
        WHERE crop_rank = 1
        ORDER BY exposure DESC, area_ha DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_crop_matrix_rows(keyword: str = "", limit: int = 30) -> list[dict]:
    pattern = f"%{keyword.strip()}%"
    return fetchall(
        """
        WITH irac_codes AS (
            SELECT DISTINCT [作物] AS crop, [IRAC代碼] AS code
            FROM irac_diversity
            WHERE TRIM(COALESCE([IRAC代碼], '')) <> ''
        ),
        irac_summary AS (
            SELECT crop,
                   COUNT(*) AS irac_code_count,
                   GROUP_CONCAT(code, ', ') AS irac_codes
            FROM irac_codes
            GROUP BY crop
        ),
        coverage AS (
            SELECT [作物] AS crop,
                   CAST([全量] AS INTEGER) AS total_count,
                   CAST([農藥製] AS INTEGER) AS domestic_count,
                   CAST([農藥進] AS INTEGER) AS import_count
            FROM crop_coverage_full
        ),
        notes AS (
            SELECT [作物] AS crop,
                   ROUND(CAST([IRAC多樣性] AS REAL), 1) AS irac_diversity,
                   [風險說明] AS risk_note
            FROM analysis_b
        )
        SELECT a.[作物] AS crop,
               ROUND(CAST(a.[全台種植面積(公頃)] AS REAL), 1) AS area_ha,
               CAST(a.[高風險機制占比] AS REAL) AS high_risk_ratio,
               ROUND(CAST(a.[加權風險暴露] AS REAL), 1) AS exposure,
               CAST(a.[有效登記農藥數] AS INTEGER) AS registration_count,
               COALESCE(cov.total_count, 0) AS total_count,
               COALESCE(cov.domestic_count, 0) AS domestic_count,
               COALESCE(cov.import_count, 0) AS import_count,
               COALESCE(cvr.[充裕度等級], '未分級') AS coverage_level,
               COALESCE(CAST(cvr.[IRAC代碼種數] AS INTEGER), 0) AS coverage_irac_code_count,
               COALESCE(irac.irac_code_count, 0) AS irac_code_count,
               COALESCE(irac.irac_codes, '') AS irac_codes,
               COALESCE(notes.irac_diversity, 0) AS irac_diversity,
               COALESCE(notes.risk_note, '') AS risk_note
        FROM analysis_a a
        LEFT JOIN coverage_risk cvr ON cvr.[作物] = a.[作物]
        LEFT JOIN coverage cov ON cov.crop = a.[作物]
        LEFT JOIN irac_summary irac ON irac.crop = a.[作物]
        LEFT JOIN notes ON notes.crop = a.[作物]
        WHERE a.[作物] LIKE ?
        ORDER BY CAST(a.[加權風險暴露] AS REAL) DESC, a.[作物] ASC
        LIMIT ?
        """,
        (pattern, limit),
    )


def get_crop_detail(crop: str) -> dict | None:
    rows = fetchall(
        """
        SELECT a.[作物] AS crop,
               ROUND(CAST(a.[全台種植面積(公頃)] AS REAL), 1) AS area_ha,
               CAST(a.[高風險機制占比] AS REAL) AS high_risk_ratio,
               ROUND(CAST(a.[加權風險暴露] AS REAL), 1) AS exposure,
               CAST(a.[有效登記農藥數] AS INTEGER) AS registration_count
        FROM analysis_a a
        WHERE a.[作物] = ?
        LIMIT 1
        """,
        (crop,),
    )
    if not rows:
        return None

    row = rows[0]
    reference_crop = _resolve_reference_crop_name(crop, "irac_diversity")
    coverage_crop = _resolve_reference_crop_name(crop, "coverage_risk")
    coverage_full_crop = _resolve_reference_crop_name(crop, "crop_coverage_full")
    note_crop = _resolve_reference_crop_name(crop, "analysis_b")

    coverage = fetchone(
        """
        SELECT [充裕度等級] AS coverage_level,
               CAST([IRAC代碼種數] AS INTEGER) AS coverage_irac_code_count
        FROM coverage_risk
        WHERE [作物] = ?
        LIMIT 1
        """,
        (coverage_crop,),
    ) or {}
    coverage_full = fetchone(
        """
        SELECT CAST([全量] AS INTEGER) AS total_count,
               CAST([農藥製] AS INTEGER) AS domestic_count,
               CAST([農藥進] AS INTEGER) AS import_count
        FROM crop_coverage_full
        WHERE [作物] = ?
        LIMIT 1
        """,
        (coverage_full_crop,),
    ) or {}
    irac_summary = fetchone(
        """
        WITH irac_codes AS (
            SELECT DISTINCT [IRAC代碼] AS code
            FROM irac_diversity
            WHERE [作物] = ?
              AND TRIM(COALESCE([IRAC代碼], '')) <> ''
        )
        SELECT COUNT(*) AS irac_code_count,
               GROUP_CONCAT(code, ', ') AS irac_codes
        FROM irac_codes
        """,
        (reference_crop,),
    ) or {}
    notes = fetchone(
        """
        SELECT ROUND(CAST([IRAC多樣性] AS REAL), 1) AS irac_diversity,
               [風險說明] AS risk_note
        FROM analysis_b
        WHERE [作物] = ?
        LIMIT 1
        """,
        (note_crop,),
    ) or {}

    row.update(
        {
            "total_count": coverage_full.get("total_count", 0) or 0,
            "domestic_count": coverage_full.get("domestic_count", 0) or 0,
            "import_count": coverage_full.get("import_count", 0) or 0,
            "coverage_level": coverage.get("coverage_level", "未分級") or "未分級",
            "coverage_irac_code_count": coverage.get("coverage_irac_code_count", 0) or 0,
            "irac_code_count": irac_summary.get("irac_code_count", 0) or 0,
            "irac_codes": irac_summary.get("irac_codes", "") or "",
            "irac_diversity": notes.get("irac_diversity", 0) or 0,
            "risk_note": notes.get("risk_note", "") or "",
            "reference_crop": reference_crop,
        }
    )
    return row


def get_crop_irac_profile(crop: str, limit: int = 12) -> list[dict]:
    reference_crop = _resolve_reference_crop_name(crop, "irac_diversity")
    return fetchall(
        """
        SELECT [IRAC代碼] AS code,
               CAST([筆數] AS INTEGER) AS count,
               CAST([占IRAC有值比例] AS REAL) AS share
        FROM irac_diversity
        WHERE [作物] = ?
          AND TRIM(COALESCE([IRAC代碼], '')) <> ''
        ORDER BY CAST([筆數] AS REAL) DESC, [IRAC代碼] ASC
        LIMIT ?
        """,
        (reference_crop, limit),
    )


def get_crop_county_distribution(crop: str, limit: int = 10) -> list[dict]:
    return fetchall(
        """
        WITH crop_risk AS (
            SELECT CAST([高風險機制占比] AS REAL) AS high_risk_ratio
            FROM analysis_a
            WHERE [作物] = ?
            LIMIT 1
        )
        SELECT county,
               ROUND(area_ha, 1) AS area_ha,
               town_count,
               ROUND(area_ha * COALESCE((SELECT high_risk_ratio FROM crop_risk), 0), 1) AS exposure_estimate
        FROM agg_county_crop
        WHERE crop = ?
        ORDER BY area_ha DESC
        LIMIT ?
        """,
        (crop, crop, limit),
    )


def search_crop(keyword: str, limit: int = 20) -> list[dict]:
    return fetchall(
        """
        SELECT crop_code, crop_name
        FROM crop_dict
        WHERE crop_name LIKE ?
        LIMIT ?
        """,
        (f"%{keyword}%", limit),
    )


def resolve_crop_name(requested_crop: str | None) -> str | None:
    if requested_crop:
        row = fetchone(
            """
            SELECT [作物] AS crop
            FROM analysis_a
            WHERE [作物] = ?
            LIMIT 1
            """,
            (requested_crop,),
        )
        if row:
            return row["crop"]
    top = get_high_risk_crops(1)
    return top[0]["crop"] if top else None


def get_pesticide_summary() -> dict:
    return fetchone(
        """
        SELECT COUNT(*) AS total_records,
               SUM(CASE WHEN TRIM(COALESCE(IRAC, '')) <> '' THEN 1 ELSE 0 END) AS irac_records,
               SUM(CASE WHEN TRIM(COALESCE(ForeignMaker, '')) <> '' THEN 1 ELSE 0 END) AS foreign_records,
               SUM(CASE WHEN TRIM(COALESCE(formCode, '')) <> '' THEN 1 ELSE 0 END) AS form_records,
               SUM(CASE WHEN TRIM(COALESCE(RevocationType, '')) <> '' THEN 1 ELSE 0 END) AS revoked_records,
               COUNT(DISTINCT CASE WHEN TRIM(COALESCE(PesticideCategoryCh, '')) <> '' THEN PesticideCategoryCh END) AS category_count
        FROM pesticide_full
        """
    )


def get_pesticide_form_distribution(limit: int = 8) -> list[dict]:
    return fetchall(
        """
        SELECT formCode AS label,
               COUNT(*) AS count
        FROM pesticide_full
        WHERE TRIM(COALESCE(formCode, '')) <> ''
        GROUP BY formCode
        ORDER BY count DESC, formCode ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_pesticide_origin_distribution(limit: int = 10) -> list[dict]:
    return fetchall(
        """
        SELECT ForeignMaker AS label,
               COUNT(*) AS count
        FROM pesticide_full
        WHERE TRIM(COALESCE(ForeignMaker, '')) <> ''
        GROUP BY ForeignMaker
        ORDER BY count DESC, ForeignMaker ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_pesticide_revocation_distribution(limit: int = 8) -> list[dict]:
    return fetchall(
        """
        SELECT RevocationType AS label,
               COUNT(*) AS count
        FROM pesticide_full
        WHERE TRIM(COALESCE(RevocationType, '')) <> ''
        GROUP BY RevocationType
        ORDER BY count DESC, RevocationType ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_pesticide_category_distribution(limit: int = 8) -> list[dict]:
    return fetchall(
        """
        SELECT COALESCE(NULLIF(TRIM(PesticideCategoryCh), ''), '未標示') AS label,
               COUNT(*) AS count
        FROM pesticide_full
        GROUP BY COALESCE(NULLIF(TRIM(PesticideCategoryCh), ''), '未標示')
        ORDER BY count DESC, label ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_pesticide_irac_distribution(limit: int = 10) -> list[dict]:
    rows = fetchall(
        """
        SELECT IRAC
        FROM pesticide_full
        WHERE TRIM(COALESCE(IRAC, '')) <> ''
        """
    )
    counter: Counter[str] = Counter()
    for row in rows:
        for code in _split_codes(row["IRAC"]):
            counter[code] += 1
    return [{"label": label, "count": count} for label, count in counter.most_common(limit)]


def get_key_findings() -> list[dict]:
    top_crop = get_high_risk_crops(1)
    top_county = get_county_risk(1)
    low_coverage = get_low_coverage_crops(3)
    vulnerable = [row for row in get_vulnerable_crops(5) if row["area_ha"] and row["area_ha"] >= 100]
    findings = []

    if top_crop:
        row = top_crop[0]
        findings.append(
            {
                "tone": "high",
                "title": f"{row['crop']} 為全台加權暴露最高作物",
                "body": f"種植面積 {row['area_ha']:,.1f} 公頃，高風險占比 {row['high_risk_ratio']:.1%}，顯示應優先納入政策監測。",
            }
        )
    if top_county:
        row = top_county[0]
        findings.append(
            {
                "tone": "high",
                "title": f"{row['county']} 為縣市暴露首位",
                "body": f"縣市總暴露 {row['exposure']:,.1f}，前三高風險作物為 {'、'.join(row['top_crops'][:3]) or '待補'}。",
            }
        )
    if low_coverage:
        crops = "、".join(item["crop"] for item in low_coverage[:3])
        findings.append(
            {
                "tone": "mid",
                "title": "低覆蓋作物需優先檢視",
                "body": f"{crops} 的有效登記筆數偏低，可作為標案中『覆蓋缺口辨識』的示範案例。",
            }
        )
    if vulnerable:
        row = vulnerable[0]
        findings.append(
            {
                "tone": "mid",
                "title": f"{row['crop']} 屬低登記高需求類型",
                "body": row["risk_note"] or f"目前僅有 {row['registration_count']} 筆有效登記，IRAC 多樣性 {row['irac_diversity']}。",
            }
        )
    return findings


def get_traceability_summary() -> dict:
    return fetchone(
        """
        SELECT
            (SELECT COUNT(*) FROM traceability_producer) AS producer_count,
            (SELECT COUNT(*) FROM traceability_product) AS product_count,
            (SELECT COUNT(DISTINCT TraceCode) FROM traceability_product) AS trace_code_count,
            (SELECT COUNT(*) FROM inspection) AS inspection_count,
            (SELECT ROUND(AVG(CASE WHEN is_pass THEN 1.0 ELSE 0 END) * 100, 1) FROM inspection) AS inspection_pass_rate,
            (SELECT COUNT(*) FROM traceability_producer WHERE Status = '通過') AS active_producer_count
        """
    )


def get_traceability_status_distribution() -> list[dict]:
    return fetchall(
        """
        SELECT Status AS label,
               COUNT(*) AS count
        FROM traceability_producer
        WHERE TRIM(COALESCE(Status, '')) <> ''
        GROUP BY Status
        ORDER BY count DESC, Status ASC
        """
    )


def get_traceability_county_distribution(limit: int | None = None) -> list[dict]:
    sql = """
        SELECT county_raw AS county,
               producer_count
        FROM agg_producer_county
        WHERE TRIM(COALESCE(county_raw, '')) <> ''
        ORDER BY producer_count DESC, county_raw ASC
    """
    if limit is not None:
        sql += " LIMIT ?"
        return fetchall(sql, (limit,))
    return fetchall(sql)


def get_traceability_crop_distribution(limit: int | None = None) -> list[dict]:
    sql = """
        SELECT crop_root AS crop,
               COUNT(*) AS product_count,
               COUNT(DISTINCT TraceCode) AS trace_count
        FROM traceability_product
        WHERE TRIM(COALESCE(crop_root, '')) <> ''
        GROUP BY crop_root
        ORDER BY product_count DESC, crop_root ASC
    """
    if limit is not None:
        sql += " LIMIT ?"
        return fetchall(sql, (limit,))
    return fetchall(sql)


def get_traceability_inspection_distribution(limit: int | None = None) -> list[dict]:
    sql = """
        SELECT crop_root AS crop,
               COUNT(*) AS inspection_count,
               ROUND(AVG(CASE WHEN is_pass THEN 1.0 ELSE 0 END) * 100, 1) AS pass_rate
        FROM inspection
        WHERE TRIM(COALESCE(crop_root, '')) <> ''
        GROUP BY crop_root
        ORDER BY inspection_count DESC, crop_root ASC
    """
    if limit is not None:
        sql += " LIMIT ?"
        return fetchall(sql, (limit,))
    return fetchall(sql)


def get_traceability_county_crop_rows() -> list[dict]:
    return fetchall(
        """
        SELECT SUBSTR(tp.Address, 1, 3) AS county,
               pr.crop_root AS crop,
               COUNT(*) AS product_count,
               COUNT(DISTINCT pr.TraceCode) AS trace_count,
               COUNT(DISTINCT tp.Producer) AS producer_count
        FROM traceability_product pr
        JOIN traceability_producer tp
          ON tp.TraceCode = pr.TraceCode
        WHERE TRIM(COALESCE(pr.crop_root, '')) <> ''
          AND TRIM(COALESCE(tp.Address, '')) <> ''
        GROUP BY SUBSTR(tp.Address, 1, 3), pr.crop_root
        ORDER BY product_count DESC, county ASC, crop ASC
        """
    )


def get_traceability_sample_records(limit: int = 240) -> list[dict]:
    return fetchall(
        """
        SELECT pr.TraceCode AS trace_code,
               pr.crop_root AS crop,
               pr.Product AS product,
               pr.Place AS place,
               tp.Producer AS producer,
               SUBSTR(tp.Address, 1, 3) AS county,
               tp.Address AS address,
               tp.Status AS status,
               tp.ModifyDate AS modify_date
        FROM traceability_product pr
        JOIN traceability_producer tp
          ON tp.TraceCode = pr.TraceCode
        WHERE TRIM(COALESCE(pr.crop_root, '')) <> ''
          AND TRIM(COALESCE(tp.Address, '')) <> ''
        ORDER BY tp.ModifyDate DESC, pr.TraceCode ASC
        LIMIT ?
        """,
        (limit,),
    )


def get_traceability_filtered_records(
    county: str | None = None,
    crop: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[dict]:
    conditions = [
        "TRIM(COALESCE(pr.crop_root, '')) <> ''",
        "TRIM(COALESCE(tp.Address, '')) <> ''",
    ]
    params: list[object] = []

    if county:
        conditions.append("SUBSTR(tp.Address, 1, 3) = ?")
        params.append(county)
    if crop:
        conditions.append("pr.crop_root = ?")
        params.append(crop)
    if status:
        conditions.append("tp.Status = ?")
        params.append(status)

    params.append(limit)
    where_sql = " AND ".join(conditions)
    return fetchall(
        f"""
        SELECT pr.TraceCode AS trace_code,
               pr.crop_root AS crop,
               pr.Product AS product,
               pr.Place AS place,
               tp.Producer AS producer,
               SUBSTR(tp.Address, 1, 3) AS county,
               tp.Address AS address,
               tp.Status AS status,
               tp.ModifyDate AS modify_date
        FROM traceability_product pr
        JOIN traceability_producer tp
          ON tp.TraceCode = pr.TraceCode
        WHERE {where_sql}
        ORDER BY tp.ModifyDate DESC, pr.TraceCode ASC
        LIMIT ?
        """,
        tuple(params),
    )
