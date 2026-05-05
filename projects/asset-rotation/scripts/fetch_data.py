#!/usr/bin/env python3
"""
资产轮动数据收集脚本
数据源：
- Alpha Vantage API：黄金价格、铜价
- 东方财富 API：沪深300、30年国债收益率

更新日志：
- 2026-04-15: 添加 Alpha Vantage API 支持
  黄金和铜价使用 Alpha Vantage（解决 Yahoo Finance 限流问题）
  沪深300和国债收益率使用东方财富实时行情
"""

import requests
import json
import os
from datetime import datetime
import time

MAX_RETRIES = 3
RETRY_DELAY = 2
GLD_TO_GOLD_OZ_MULTIPLIER = 10
POUNDS_PER_METRIC_TON = 2204.62262185

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")


def fetch_with_retry(url, max_retries=MAX_RETRIES, timeout=30):
    """带重试的 HTTP 请求"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAY * (2**attempt)
                time.sleep(wait_time)
            else:
                raise
    return None


def fetch_gold_from_alphavantage():
    """从 Alpha Vantage 获取黄金价格 (GLD ETF)"""
    if not ALPHA_VANTAGE_API_KEY:
        return None

    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={ALPHA_VANTAGE_API_KEY}"
        data = fetch_with_retry(url)

        if data is None:
            return None, "REQUEST_FAILED"

        if "Error Message" in data:
            return None, f"API_ERROR: {data['Error Message']}"

        if "Note" in data:
            return None, f"RATE_LIMIT: {data['Note']}"

        if "Information" in data:
            return None, f"API_INFO: {data['Information']}"

        if "Time Series (Daily)" not in data:
            return None, f"UNEXPECTED_RESPONSE: {list(data.keys())}"

        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys(), reverse=True)

        if len(dates) < 1:
            return None, "NO_DATA"

        latest_date = dates[0]
        latest_data = time_series[latest_date]
        close_price = float(latest_data["4. close"])

        if len(dates) >= 2:
            prev_close = float(time_series[dates[1]]["4. close"])
            change_pct = ((close_price - prev_close) / prev_close) * 100
        else:
            change_pct = 0.0

        gold_price = close_price * GLD_TO_GOLD_OZ_MULTIPLIER

        return {
            "date": latest_date,
            "gold_price": round(gold_price, 2),
            "gold_change_pct": round(change_pct, 2),
        }, None

    except Exception as e:
        return None, f"EXCEPTION: {str(e)}"


def normalize_gold_oz_price(gold_price):
    """Normalize GLD proxy price to approximate USD/oz gold price."""
    if not gold_price:
        return None
    return gold_price * GLD_TO_GOLD_OZ_MULTIPLIER if gold_price < 1000 else gold_price


def normalize_copper_lb_price(copper_price):
    """Normalize copper price to USD/lb.

    Alpha Vantage COPPER returns USD/metric ton, while older records used
    futures-like USD/lb values. Keep both historical formats readable.
    """
    if not copper_price:
        return None
    return copper_price / POUNDS_PER_METRIC_TON if copper_price > 100 else copper_price


def calculate_gold_copper_ratio(gold_price, copper_price):
    gold_oz = normalize_gold_oz_price(gold_price)
    copper_lb = normalize_copper_lb_price(copper_price)
    if not gold_oz or not copper_lb:
        return None
    return round(gold_oz / copper_lb, 2)


def fetch_copper_from_alphavantage():
    """从 Alpha Vantage 获取铜价 (铜期货)"""
    if not ALPHA_VANTAGE_API_KEY:
        return None

    try:
        url = f"https://www.alphavantage.co/query?function=COPPER&datatype=json&apikey={ALPHA_VANTAGE_API_KEY}"
        data = fetch_with_retry(url)

        if data is None:
            return None, "REQUEST_FAILED"

        if "Error Message" in data:
            return None, f"API_ERROR: {data['Error Message']}"

        if "Note" in data:
            return None, f"RATE_LIMIT: {data['Note']}"

        if "data" not in data or not data["data"]:
            return None, "NO_DATA"

        latest = data["data"][0]
        copper_price = float(latest["value"])

        return {
            "date": latest["date"],
            "copper_price": round(copper_price, 4),
        }, None

    except Exception as e:
        return None, f"EXCEPTION: {str(e)}"


def fetch_realtime_data(secid):
    """获取东方财富实时行情"""
    url = f"https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f43,f57,f58,f169,f170,f171,f45,f46,f44,f168",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fltt": "2",
        "invt": "2",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/",
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            if data and data.get("data"):
                return data["data"]
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def fetch_hs300():
    """获取沪深300指数（东方财富）"""
    data = fetch_realtime_data("1.000300")
    if data:
        try:
            close = float(data.get("f43", 0))
            prev_close = float(data.get("f44", 0))
            if close > 0 and prev_close > 0:
                change_pct = (close - prev_close) / prev_close * 100
                return {
                    "hs300_price": round(close, 2),
                    "hs300_change_pct": round(change_pct, 2),
                }
        except:
            pass
    return None


def fetch_bond_yield():
    """获取30年国债收益率（东方财富）"""
    data = fetch_realtime_data("1.019547")
    if data:
        try:
            close = float(data.get("f43", 0))
            if close > 0:
                if close > 100:
                    close = close / 100
                return round(close, 4)
        except:
            pass
    return None


def fetch_market_data():
    """获取所有市场数据"""
    print("=" * 60)
    print("资产轮动 - 市场数据采集")
    print("=" * 60)
    print(f"Alpha Vantage API: {'✓ 已配置' if ALPHA_VANTAGE_API_KEY else '✗ 未配置'}")

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"采集日期: {today}")
    print("\n正在采集数据...")

    errors = []

    bond_yield = fetch_bond_yield()
    print(
        f"  {'✓' if bond_yield else '✗'} 30年国债收益率: {bond_yield}%"
        if bond_yield
        else "  ✗ 30年国债收益率: 获取失败"
    )

    gold_data, gold_error = fetch_gold_from_alphavantage()
    if gold_error:
        errors.append(f"黄金: {gold_error}")
        print(f"  ✗ 黄金价格: 获取失败 ({gold_error})")
    elif gold_data:
        print(
            f"  ✓ 黄金价格: ${gold_data['gold_price']} ({gold_data['gold_change_pct']:+.2f}%)"
        )
    else:
        print("  ✗ 黄金价格: 未获取到数据")

    stock_data = fetch_hs300()
    if stock_data:
        print(
            f"  ✓ 沪深300: {stock_data['hs300_price']} ({stock_data['hs300_change_pct']:+.2f}%)"
        )
    else:
        print("  ✗ 沪深300: 获取失败")

    copper_data, copper_error = fetch_copper_from_alphavantage()
    if copper_error:
        errors.append(f"铜价: {copper_error}")
        print(f"  ✗ 铜价: 获取失败 ({copper_error})")
    elif copper_data:
        print(f"  ✓ 铜价: ${copper_data['copper_price']}")
    else:
        print("  ✗ 铜价: 未获取到数据")

    record = {
        "date": today,
        "bond_yield_30y": bond_yield,
        "gold_price_usd": gold_data["gold_price"] if gold_data else None,
        "gold_change_pct": gold_data["gold_change_pct"] if gold_data else None,
        "usdcny": 7.2,
        "gold_price_cny": round(gold_data["gold_price"] * 7.2 / 31.1035, 2)
        if gold_data
        else None,
        "hs300_price": stock_data["hs300_price"] if stock_data else None,
        "hs300_change_pct": stock_data["hs300_change_pct"] if stock_data else None,
        "copper_price": copper_data["copper_price"] if copper_data else None,
        "updated_at": datetime.now().isoformat(),
    }

    return record, errors if errors else None


def save_daily_data(record):
    """保存每日数据"""
    os.makedirs("data", exist_ok=True)
    data_file = "data/market_data.json"

    existing_data = []
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                existing_data = json.load(f)
        except:
            existing_data = []

    existing_idx = next(
        (i for i, d in enumerate(existing_data) if d["date"] == record["date"]), None
    )

    if existing_idx is not None:
        existing_data[existing_idx] = record
        print(f"\n✓ 更新 {record['date']} 数据")
    else:
        existing_data.append(record)
        existing_data.sort(key=lambda x: x["date"])
        print(f"\n✓ 添加 {record['date']} 新数据")

    with open(data_file, "w") as f:
        json.dump(existing_data, f, indent=2)

    print(f"✓ 总计 {len(existing_data)} 条记录")
    return existing_data


def calculate_indicators(data):
    """计算核心指标"""
    if not data:
        return None

    latest = data[-1]

    assumed_pe = 12
    earnings_yield = 1 / assumed_pe * 100
    bond_yield = latest.get("bond_yield_30y")

    if bond_yield is None:
        bond_yield = 2.5

    stock_bond_ratio = round(earnings_yield - bond_yield, 2)

    gold_copper_ratio = calculate_gold_copper_ratio(
        latest.get("gold_price_usd"),
        latest.get("copper_price"),
    )

    indicators = {
        "date": latest["date"],
        "stock_bond_ratio": stock_bond_ratio,
        "gold_copper_ratio": gold_copper_ratio,
        "bond_yield": bond_yield,
        "calculation_time": datetime.now().isoformat(),
    }

    return indicators


def main():
    """主函数"""
    record, errors = fetch_market_data()

    if record:
        all_data = save_daily_data(record)

        indicators = calculate_indicators(all_data)

        if indicators:
            print("\n" + "=" * 60)
            print("核心指标")
            print("=" * 60)
            print(f"股债性价比: {indicators['stock_bond_ratio']}%")
            print(f"金铜比: {indicators['gold_copper_ratio']}")
            print(f"30年国债收益率: {indicators['bond_yield']}%")

            with open("data/indicators.json", "w") as f:
                json.dump(indicators, f, indent=2)

        if errors:
            print(f"\n⚠️  部分数据获取失败: {errors}")
            return True
        print("\n✓ 数据采集完成")
        return True
    else:
        print("\n✗ 数据采集失败")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
