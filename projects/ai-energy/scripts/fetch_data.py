"""Fetch market data for the AI energy research page.

Market baskets use Alpha Vantage via ALPHA_VANTAGE_API_KEY. Stooq is kept as
an optional fallback when STOOQ_API_KEY is available. Cloud CAPEX uses Alpha
Vantage CASH_FLOW quarterly reports when the API budget allows it.
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "ai_energy_data.json"
API_PAUSE_SECONDS = 13
BASKETS = {
    "compute_basket": ["NVDA", "AVGO", "ANET", "AMD", "DELL"],
    "energy_basket": ["CEG", "VST", "NEE", "XLU", "XLE"],
    "grid_basket": ["ETN", "PWR", "HUBB", "GEV", "GRID"],
}
CAPEX_SYMBOLS = {
    "msft": "MSFT",
    "goog": "GOOGL",
    "amzn": "AMZN",
    "meta": "META",
    "orcl": "ORCL",
}


def fetch_url(url: str) -> str:
    with urlopen(url, timeout=20) as response:
        return response.read().decode("utf-8")


def fetch_stooq_daily(ticker: str, api_key: str) -> dict[str, float]:
    params = urlencode({"s": f"{ticker.lower()}.us", "i": "d", "apikey": api_key})
    text = fetch_url(f"https://stooq.com/q/d/l/?{params}")
    rows = csv.DictReader(StringIO(text))

    prices = {}
    for row in rows:
        date = row.get("Date")
        close = row.get("Close")
        if date and close and close != "No data":
            prices[date] = float(close)
    return prices


def fetch_alpha_vantage_daily(ticker: str, api_key: str) -> dict[str, float]:
    params = urlencode({
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",
        "apikey": api_key,
    })
    payload = json.loads(fetch_url(f"https://www.alphavantage.co/query?{params}"))
    series = payload.get("Time Series (Daily)", {})

    prices = {}
    for date, values in series.items():
        close = values.get("4. close")
        if close:
            prices[date] = float(close)
    return prices


def fetch_alpha_vantage_cash_flow(ticker: str, api_key: str) -> list[dict]:
    params = urlencode({
        "function": "CASH_FLOW",
        "symbol": ticker,
        "apikey": api_key,
    })
    payload = json.loads(fetch_url(f"https://www.alphavantage.co/query?{params}"))

    if "Note" in payload or "Information" in payload:
        raise RuntimeError(payload.get("Note") or payload.get("Information"))
    if "Error Message" in payload:
        raise RuntimeError(payload["Error Message"])

    return payload.get("quarterlyReports", [])


def normalize_prices(prices: dict[str, float]) -> dict[str, float]:
    if not prices:
        return {}

    dates = sorted(prices)[-90:]
    base = prices[dates[0]]
    if not base:
        return {}

    return {date: round(prices[date] / base * 100, 2) for date in dates}


def load_ticker_series(ticker: str, alpha_vantage_key: str | None, stooq_key: str | None) -> dict[str, float]:
    try:
        if alpha_vantage_key:
            prices = fetch_alpha_vantage_daily(ticker, alpha_vantage_key)
            if prices:
                print(f"Loaded {ticker} from Alpha Vantage")
                time.sleep(API_PAUSE_SECONDS)
                return normalize_prices(prices)
    except Exception as exc:
        print(f"Alpha Vantage failed for {ticker}: {exc}")

    try:
        if stooq_key:
            prices = fetch_stooq_daily(ticker, stooq_key)
            if prices:
                print(f"Loaded {ticker} from Stooq")
                return normalize_prices(prices)
    except Exception as exc:
        print(f"Stooq failed for {ticker}: {exc}")

    return {}


def fiscal_quarter(date_text: str) -> str:
    year, month, _ = [int(part) for part in date_text.split("-")]
    quarter = (month - 1) // 3 + 1
    return f"{year}Q{quarter}"


def number_from_report(value) -> float | None:
    if value in (None, "None", ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_capex_data(alpha_vantage_key: str | None, existing_rows: list[dict]) -> list[dict]:
    if not alpha_vantage_key:
        return existing_rows

    capex_by_quarter: dict[str, dict[str, float | str]] = {}

    for field, ticker in CAPEX_SYMBOLS.items():
        try:
            reports = fetch_alpha_vantage_cash_flow(ticker, alpha_vantage_key)
            print(f"Loaded {ticker} cash flow from Alpha Vantage")
            time.sleep(API_PAUSE_SECONDS)
        except Exception as exc:
            print(f"Alpha Vantage cash flow failed for {ticker}: {exc}")
            continue

        for report in reports[:8]:
            fiscal_date = report.get("fiscalDateEnding")
            raw_capex = number_from_report(report.get("capitalExpenditures"))
            if not fiscal_date or raw_capex is None:
                continue

            quarter = fiscal_quarter(fiscal_date)
            row = capex_by_quarter.setdefault(quarter, {"quarter": quarter})
            row[field] = round(abs(raw_capex) / 1_000_000_000, 2)

    rows = [
        capex_by_quarter[quarter]
        for quarter in sorted(capex_by_quarter)
        if sum(1 for field in CAPEX_SYMBOLS if field in capex_by_quarter[quarter]) >= 3
    ][-6:]

    if len(rows) < 3:
        print("Not enough CAPEX coverage; keeping existing CAPEX data unchanged.")
        return existing_rows

    return rows


def should_update_capex() -> bool:
    mode = os.environ.get("UPDATE_CAPEX", "weekly").lower()
    if mode in ("1", "true", "yes", "always"):
        return True
    if mode in ("0", "false", "no", "never"):
        return False
    if mode == "monthly":
        return datetime.now(timezone.utc).day <= 7
    return datetime.now(timezone.utc).weekday() == 0


def calculate_capex_growth(capex_rows: list[dict]) -> float | None:
    valid_rows = [
        row for row in capex_rows
        if sum(1 for field in CAPEX_SYMBOLS if row.get(field) is not None) >= 3
    ]
    if len(valid_rows) < 2:
        return None

    latest = valid_rows[-1]
    comparison = valid_rows[-5] if len(valid_rows) >= 5 else valid_rows[-2]

    latest_total = sum(float(latest.get(field) or 0) for field in CAPEX_SYMBOLS)
    comparison_total = sum(float(comparison.get(field) or 0) for field in CAPEX_SYMBOLS)
    if comparison_total <= 0:
        return None

    return round((latest_total - comparison_total) / comparison_total * 100, 1)


def update_derived_signals(data: dict) -> None:
    signals = data.setdefault("signals", {})
    capex_growth = calculate_capex_growth(data.get("capex", []))
    if capex_growth is not None:
        signals["capex_growth"] = capex_growth

    market = data.get("market", [])
    if market:
        latest = market[-1]
        energy = float(latest.get("energy_basket") or 100)
        grid = float(latest.get("grid_basket") or 100)
        compute = float(latest.get("compute_basket") or 100)
        infrastructure_pressure = max(energy, grid) - compute
        signals["energy_bottleneck"] = max(
            0,
            min(100, round(65 + infrastructure_pressure * 0.7, 0)),
        )


def build_market_data(series_by_ticker: dict[str, dict[str, float]]) -> list[dict[str, float | str | None]]:
    all_dates = sorted({date for series in series_by_ticker.values() for date in series})
    sample_dates = all_dates[-18:]

    market = []
    for date in sample_dates:
        row: dict[str, float | str | None] = {"date": date}
        for basket_name, tickers in BASKETS.items():
            values = [
                series_by_ticker[ticker][date]
                for ticker in tickers
                if date in series_by_ticker.get(ticker, {})
            ]
            row[basket_name] = round(sum(values) / len(values), 2) if values else None
        if any(row.get(basket_name) is not None for basket_name in BASKETS):
            market.append(row)

    return market


def main() -> None:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    alpha_vantage_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    stooq_key = os.environ.get("STOOQ_API_KEY")

    if not alpha_vantage_key and not stooq_key:
        print("No market data API key configured; keeping existing data file unchanged.")
        return

    tickers = sorted({ticker for tickers in BASKETS.values() for ticker in tickers})
    series_by_ticker = {}

    for ticker in tickers:
        series = load_ticker_series(ticker, alpha_vantage_key, stooq_key)
        if series:
            series_by_ticker[ticker] = series

    market = build_market_data(series_by_ticker)
    coverage = sum(
        1
        for row in market
        for basket_name in BASKETS
        if row.get(basket_name) is not None
    )

    if not market or coverage < len(BASKETS) * 3:
        print("No valid market data fetched; keeping existing data file unchanged.")
        return

    data["market"] = market
    if should_update_capex():
        data["capex"] = build_capex_data(alpha_vantage_key, data.get("capex", []))
    else:
        print("Skipping CAPEX update outside the configured refresh window.")
    update_derived_signals(data)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["data_sources"] = {
        "market": "Alpha Vantage TIME_SERIES_DAILY / optional Stooq fallback",
        "capex": "Alpha Vantage CASH_FLOW quarterlyReports",
        "revenue": "manual: segment revenue / industry proxy",
        "power": "manual: data center power and grid bottleneck proxy",
        "watchlist": "manual: research universe and qualitative risk notes",
        "signals": "mixed: CAPEX and market-derived fields plus manual proxies",
    }

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Updated {DATA_FILE}")


if __name__ == "__main__":
    main()
