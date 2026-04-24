"""Fetch market data for the AI energy research page.

Company fundamentals stay manual for now. Market baskets use Alpha Vantage
via ALPHA_VANTAGE_API_KEY. Stooq is kept as an optional fallback when
STOOQ_API_KEY is available.
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
BASKETS = {
    "compute_basket": ["NVDA", "AVGO", "ANET", "AMD", "DELL"],
    "energy_basket": ["CEG", "VST", "NEE", "XLU", "XLE"],
    "grid_basket": ["ETN", "PWR", "HUBB", "GEV", "GRID"],
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
                time.sleep(13)
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
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Updated {DATA_FILE}")


if __name__ == "__main__":
    main()
