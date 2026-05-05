#!/usr/bin/env python3
"""Update monthly macro data for the asset rotation page.

Data sources use AKShare macro interfaces:
- macro_china_pmi_yearly: official manufacturing PMI
- macro_china_ppi_yearly: China PPI YoY

If the provider is unavailable, the script exits without touching the data file.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "macro_data.json"


def read_existing() -> dict[str, dict]:
    if not DATA_FILE.exists():
        return {}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return {row["month"]: row for row in data if row.get("month")}


def value_is_valid(value) -> bool:
    if value is None:
        return False
    try:
        return not math.isnan(float(value))
    except (TypeError, ValueError):
        return False


def shift_month(month: str, months: int) -> str:
    year, month_num = [int(part) for part in month.split("-")]
    month_num += months
    while month_num <= 0:
        month_num += 12
        year -= 1
    while month_num > 12:
        month_num -= 12
        year += 1
    return f"{year:04d}-{month_num:02d}"


def dataframe_records(df, value_field="今值", month_shift=0) -> list[tuple[str, float]]:
    records = []

    if hasattr(df, "reset_index"):
        df = df.reset_index()

    for _, row in df.iterrows():
        date_value = row.get("日期") or row.get("index")
        value = row.get(value_field) if value_field in row else row.iloc[-1]

        if not date_value or not value_is_valid(value):
            continue

        month = shift_month(str(date_value)[:7], month_shift)
        records.append((month, round(float(value), 2)))

    return records


def merge_macro_data(existing: dict[str, dict], pmi_records, ppi_records) -> list[dict]:
    now = datetime.now().isoformat()

    for month, pmi in pmi_records:
        row = existing.setdefault(month, {"month": month})
        row["pmi"] = pmi
        row.setdefault("sources", {})
        row["sources"]["pmi"] = "AKShare macro_china_pmi_yearly"
        row["updated_at"] = now

    for month, ppi in ppi_records:
        row = existing.setdefault(month, {"month": month})
        row["ppi_yoy"] = ppi
        row.setdefault("sources", {})
        row["sources"]["ppi_yoy"] = "AKShare macro_china_ppi_yearly"
        row["updated_at"] = now

    rows = []
    for month in sorted(existing):
        row = existing[month]
        if "pmi" in row or "ppi_yoy" in row:
            row.setdefault("pmi", None)
            row.setdefault("ppi_yoy", None)
            row.setdefault("note", "")
            row.setdefault("sources", {})
            rows.append(row)

    return rows[-36:]


def main() -> int:
    try:
        import akshare as ak
    except ImportError:
        print("akshare is not installed; keeping existing macro data unchanged.")
        return 0

    try:
        pmi_df = ak.macro_china_pmi_yearly()
        ppi_df = ak.macro_china_ppi_yearly()
    except Exception as exc:
        print(f"Failed to fetch macro data: {exc}")
        return 0

    pmi_records = dataframe_records(pmi_df)
    ppi_records = dataframe_records(ppi_df, month_shift=-1)

    if not pmi_records and not ppi_records:
        print("No macro records fetched; keeping existing macro data unchanged.")
        return 0

    existing = read_existing()
    rows = merge_macro_data(existing, pmi_records, ppi_records)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Updated {DATA_FILE} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
