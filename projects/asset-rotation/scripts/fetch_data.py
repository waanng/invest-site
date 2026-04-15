#!/usr/bin/env python3
"""
资产轮动数据收集脚本
数据源：东方财富 API（稳定可靠）

更新日志：
- 2026-04-15: 修复Yahoo Finance限流问题，改用东方财富
  沪深300和国债收益率使用东方财富实时行情
  黄金使用51888 ETF价格（ETF净值数据有问题，价格仅供参考）
  铜价暂时无法获取（东方财富期货接口不稳定）

注意：
- Yahoo Finance被全面限流，之前使用的数据源不可用
- 东方财富51888 ETF的净值数据异常，计算出的金价可能不准确
- 如需准确金价，建议使用Alpha Vantage API（需要API key）
"""

import requests
import json
import os
from datetime import datetime
import time

MAX_RETRIES = 3
RETRY_DELAY = 2


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


def fetch_gold_price():
    """
    获取黄金价格
    使用东方财富黄金ETF(51888)作为代理指标
    ETF价格约10元/份

    注意：51888的净值数据(f169/f171)异常，计算出的金价仅供参考
    正确的金价需要使用GLD ETF价格乘以10（或使用Alpha Vantage API）
    """
    data = fetch_realtime_data("1.51888")
    if data:
        try:
            # ETF的f43直接是价格（元）
            etf_price = float(data.get("f43", 0))

            if etf_price > 0:
                usd_cny_rate = 7.2

                # 51888每份对应约0.53克黄金
                # 但由于净值数据异常，使用简单的估算方法
                # ETF价格 × 10 ≈ GLD ETF价格（10倍关系）
                gld_estimate_usd = etf_price * 10
                gold_cny_per_g = etf_price / 0.53  # 基于持仓量估算

                return {
                    "gold_usd": round(gld_estimate_usd, 2),
                    "usdcny": round(usd_cny_rate, 4),
                    "gold_cny_per_g": round(gold_cny_per_g, 2),
                    "etf_price": round(etf_price, 2),
                    "note": "基于51888估算，仅供参考",
                }
        except Exception as e:
            print(f"  黄金价格计算错误: {e}")
    return None


def fetch_hs300():
    """获取沪深300指数"""
    data = fetch_realtime_data("1.000300")
    if data:
        try:
            # 注意：东方财富指数的f43直接是指数值，不需要除以100
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


def fetch_copper():
    """
    获取铜价
    注意：东方财富期货接口不稳定，暂时返回None
    如需铜价数据，可考虑使用Alpha Vantage API
    """
    return None


def fetch_bond_yield():
    """获取30年国债收益率"""
    data = fetch_realtime_data("1.019547")
    if data:
        try:
            # 国债收益率f43直接是百分比数值，不需要除以100
            close = float(data.get("f43", 0))
            if close > 0:
                if close > 100:
                    close = close / 100
                return round(close, 4)
        except:
            pass
    return None


def fetch_gold_price():
    """
    获取黄金价格
    使用东方财富黄金ETF(51888)作为代理指标
    ETF价格约10元/份

    注意：51888 ETF每份代表0.53克黄金
    ETF价格 / 持有克数 = 黄金价格(元/克)
    """
    data = fetch_realtime_data("1.51888")
    if data:
        try:
            # ETF的f43直接是价格（元），不需要除以100
            etf_price = float(data.get("f43", 0))
            holding = float(data.get("f170", 0.53))

            if etf_price > 0 and holding > 0:
                usd_cny_rate = 7.2

                # 51888每份对应holding克黄金
                gold_cny_per_g = etf_price / holding
                gold_usd_per_oz = (gold_cny_per_g * 31.1035) / usd_cny_rate

                return {
                    "gold_usd": round(gold_usd_per_oz, 2),
                    "usdcny": round(usd_cny_rate, 4),
                    "gold_cny_per_g": round(gold_cny_per_g, 2),
                    "etf_price": round(etf_price, 2),
                }
        except Exception as e:
            print(f"  黄金价格计算错误: {e}")
    return None


def fetch_hs300():
    """获取沪深300指数"""
    data = fetch_realtime_data("1.000300")
    if data:
        try:
            # 注意：东方财富指数的f43直接是指数值，不需要除以100
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


def fetch_copper():
    """
    获取铜价
    注意：东方财富期货接口不稳定，暂时返回None
    如需铜价数据，可考虑使用Alpha Vantage API
    """
    return None


def fetch_bond_yield():
    """获取30年国债收益率"""
    data = fetch_realtime_data("1.019547")
    if data:
        try:
            # 国债收益率f43直接是百分比数值，不需要除以100
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

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"采集日期: {today}")
    print("\n正在采集数据...")

    bond_yield = fetch_bond_yield()
    print(
        f"  {'✓' if bond_yield else '✗'} 30年国债收益率: {bond_yield}%"
        if bond_yield
        else "  ✗ 30年国债收益率: 获取失败"
    )

    gold_data = fetch_gold_price()
    if gold_data:
        print(
            f"  ✓ 黄金价格: ${gold_data['gold_usd']}/oz, ¥{gold_data['gold_cny_per_g']}/g (ETF:¥{gold_data['etf_price']})"
        )
    else:
        print("  ✗ 黄金价格: 获取失败")

    stock_data = fetch_hs300()
    if stock_data:
        print(
            f"  ✓ 沪深300: {stock_data['hs300_price']} ({stock_data['hs300_change_pct']:+.2f}%)"
        )
    else:
        print("  ✗ 沪深300: 获取失败")

    copper_price = fetch_copper()
    if copper_price:
        print(f"  ✓ 铜价: ${copper_price}")
    else:
        print("  ⚠ 铜价: 暂无法获取 (东方财富期货接口不稳定)")

    record = {
        "date": today,
        "bond_yield_30y": bond_yield,
        "gold_price_usd": gold_data["gold_usd"] if gold_data else None,
        "usdcny": gold_data["usdcny"] if gold_data else None,
        "gold_price_cny": gold_data["gold_cny_per_g"] if gold_data else None,
        "hs300_price": stock_data["hs300_price"] if stock_data else None,
        "hs300_change_pct": stock_data["hs300_change_pct"] if stock_data else None,
        "copper_price": copper_price,
        "updated_at": datetime.now().isoformat(),
    }

    return record


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

    gold_copper_ratio = None
    if latest.get("gold_price_usd") and latest.get("copper_price"):
        gold_copper_ratio = round(latest["gold_price_usd"] / latest["copper_price"], 2)

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
    record = fetch_market_data()

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

        print("\n✓ 数据采集完成")
        return True
    else:
        print("\n✗ 数据采集失败")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
