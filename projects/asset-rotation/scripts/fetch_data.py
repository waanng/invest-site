#!/usr/bin/env python3
"""
资产轮动数据收集脚本
采集：国债收益率、黄金价格、A股指数、汇率
"""
import yfinance as yf
import requests
import json
import os
from datetime import datetime, timedelta
import time
import re

def fetch_bond_yield():
    """获取中国30年国债收益率"""
    try:
        # 从Investing.com获取（需要解析网页）
        url = "https://cn.investing.com/rates-bonds/china-30-year-bond-yield"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 解析HTML获取收益率
            content = response.text
            # 查找收益率数据（通常在data-last属性中）
            match = re.search(r'data-last="([\d.]+)"', content)
            if match:
                return float(match.group(1))
            
            # 备选：查找特定文本
            match = re.search(r'30年期国债收益率.*?([\d.]+)%', content)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"获取国债收益率失败: {e}")
    
    return None

def fetch_gold_price_cny():
    """获取人民币计价黄金价格"""
    try:
        # 获取美元金价
        gold_usd = yf.Ticker("GC=F")
        time.sleep(1)
        gold_hist = gold_usd.history(period="1d")
        
        if gold_hist.empty:
            return None
        
        gold_price_usd = float(gold_hist['Close'].iloc[-1])
        
        # 获取人民币汇率
        usdcny = yf.Ticker("USDCNY=X")
        time.sleep(1)
        fx_hist = usdcny.history(period="1d")
        
        if fx_hist.empty:
            return None
        
        exchange_rate = float(fx_hist['Close'].iloc[-1])
        
        # 转换为人民币/克 (1盎司=31.1035克)
        gold_price_cny_per_oz = gold_price_usd * exchange_rate
        gold_price_cny_per_g = gold_price_cny_per_oz / 31.1035
        
        return {
            'gold_usd': round(gold_price_usd, 2),
            'usdcny': round(exchange_rate, 4),
            'gold_cny_per_g': round(gold_price_cny_per_g, 2)
        }
    except Exception as e:
        print(f"获取黄金价格失败: {e}")
    
    return None

def fetch_stock_index():
    """获取沪深300指数"""
    try:
        # 沪深300代码（雅虎财经）
        ticker = yf.Ticker("000300.SS")
        time.sleep(1)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return None
        
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        return {
            'hs300_price': float(latest['Close']),
            'hs300_change_pct': round((latest['Close'] - prev['Close']) / prev['Close'] * 100, 2)
        }
    except Exception as e:
        print(f"获取沪深300失败: {e}")
    
    return None

def fetch_copper_price():
    """获取铜价（计算金铜比）"""
    try:
        # 铜期货代码
        copper = yf.Ticker("HG=F")
        time.sleep(1)
        hist = copper.history(period="1d")
        
        if hist.empty:
            return None
        
        return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"获取铜价失败: {e}")
    
    return None

def fetch_market_data():
    """获取所有市场数据"""
    print("="*60)
    print("资产轮动 - 市场数据采集")
    print("="*60)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 采集各项数据
    print("\n📊 正在采集数据...")
    
    bond_yield = fetch_bond_yield()
    print(f"  {'✓' if bond_yield else '✗'} 30年国债收益率: {bond_yield}%" if bond_yield else "  ✗ 30年国债收益率: 获取失败")
    
    gold_data = fetch_gold_price_cny()
    if gold_data:
        print(f"  ✓ 黄金价格: ${gold_data['gold_usd']}, ¥{gold_data['gold_cny_per_g']}/g")
    else:
        print("  ✗ 黄金价格: 获取失败")
    
    stock_data = fetch_stock_index()
    if stock_data:
        print(f"  ✓ 沪深300: {stock_data['hs300_price']} ({stock_data['hs300_change_pct']:+.2f}%)")
    else:
        print("  ✗ 沪深300: 获取失败")
    
    copper_price = fetch_copper_price()
    print(f"  {'✓' if copper_price else '✗'} 铜价: ${copper_price}" if copper_price else "  ✗ 铜价: 获取失败")
    
    # 构建数据记录
    record = {
        'date': today,
        'bond_yield_30y': bond_yield,
        'gold_price_usd': gold_data['gold_usd'] if gold_data else None,
        'usdcny': gold_data['usdcny'] if gold_data else None,
        'gold_price_cny': gold_data['gold_cny_per_g'] if gold_data else None,
        'hs300_price': stock_data['hs300_price'] if stock_data else None,
        'hs300_change_pct': stock_data['hs300_change_pct'] if stock_data else None,
        'copper_price': copper_price,
        'updated_at': datetime.now().isoformat()
    }
    
    return record

def save_daily_data(record):
    """保存每日数据"""
    os.makedirs('data', exist_ok=True)
    data_file = 'data/market_data.json'
    
    # 加载现有数据
    existing_data = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    
    # 更新或添加记录
    existing_idx = next((i for i, d in enumerate(existing_data) 
                        if d['date'] == record['date']), None)
    
    if existing_idx is not None:
        existing_data[existing_idx] = record
        print(f"\n✓ 更新 {record['date']} 数据")
    else:
        existing_data.append(record)
        existing_data.sort(key=lambda x: x['date'])
        print(f"\n✓ 添加 {record['date']} 新数据")
    
    # 保存
    with open(data_file, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    print(f"✓ 总计 {len(existing_data)} 条记录")
    return existing_data

def calculate_indicators(data):
    """计算核心指标"""
    if not data:
        return None
    
    latest = data[-1]
    
    # 股债性价比（简化版，需要PE数据）
    # 假设沪深300 PE为12（实际应从理杏仁等获取）
    assumed_pe = 12
    earnings_yield = 1 / assumed_pe * 100  # 盈利收益率
    bond_yield = latest.get('bond_yield_30y', 2.5)
    
    stock_bond_ratio = round(earnings_yield - bond_yield, 2)
    
    # 金铜比
    gold_copper_ratio = None
    if latest.get('gold_price_usd') and latest.get('copper_price'):
        gold_copper_ratio = round(latest['gold_price_usd'] / latest['copper_price'], 2)
    
    indicators = {
        'date': latest['date'],
        'stock_bond_ratio': stock_bond_ratio,  # 股债性价比
        'gold_copper_ratio': gold_copper_ratio,  # 金铜比
        'bond_yield': bond_yield,
        'calculation_time': datetime.now().isoformat()
    }
    
    return indicators

def main():
    """主函数"""
    # 获取市场数据
    record = fetch_market_data()
    
    if record:
        # 保存数据
        all_data = save_daily_data(record)
        
        # 计算指标
        indicators = calculate_indicators(all_data)
        
        if indicators:
            print("\n" + "="*60)
            print("核心指标")
            print("="*60)
            print(f"股债性价比: {indicators['stock_bond_ratio']}%")
            print(f"金铜比: {indicators['gold_copper_ratio']}")
            print(f"30年国债收益率: {indicators['bond_yield']}%")
            
            # 保存指标
            with open('data/indicators.json', 'w') as f:
                json.dump(indicators, f, indent=2)
        
        print("\n✓ 数据采集完成")
    else:
        print("\n✗ 数据采集失败")

if __name__ == "__main__":
    main()