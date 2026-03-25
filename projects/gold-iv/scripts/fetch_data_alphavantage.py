#!/usr/bin/env python3
"""
Gold IV Data Fetcher - 使用 Alpha Vantage 作为主要数据源
"""
import json
import os
from datetime import datetime
import requests
import pandas as pd

# 从环境变量获取 API Key
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

def fetch_gold_from_alphavantage():
    """
    使用 Alpha Vantage 获取黄金价格数据
    
    免费版限制：25次/天
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY not set")
        return None
    
    try:
        print("Fetching gold data from Alpha Vantage...")
        
        # 方法1: 使用 XAUUSD 商品数据
        # 注意：Alpha Vantage 免费版对商品数据有延迟，我们使用外汇对近似
        # 或者使用其他方式
        
        # 使用 TIME_SERIES_DAILY 获取黄金ETF数据（如GLD）作为代理
        # 或者使用 CURRENCY_EXCHANGE_RATE 获取 XAU/USD
        
        # 尝试获取 XAU/USD 汇率
        url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=XAU&to_currency=USD&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'Realtime Currency Exchange Rate' in data:
            exchange_data = data['Realtime Currency Exchange Rate']
            gold_price = float(exchange_data['5. Exchange Rate'])
            
            print(f"✓ Gold price fetched: ${gold_price:.2f}")
            
            # 获取历史数据计算涨跌幅（需要另一次API调用）
            # 使用 TIME_SERIES_DAILY 获取前几天的数据
            hist_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={ALPHA_VANTAGE_API_KEY}"
            hist_response = requests.get(hist_url, timeout=30)
            hist_data = hist_response.json()
            
            if 'Time Series (Daily)' in hist_data:
                time_series = hist_data['Time Series (Daily)']
                dates = sorted(time_series.keys(), reverse=True)
                
                if len(dates) >= 2:
                    latest_date = dates[0]
                    prev_date = dates[1]
                    
                    latest_price = float(time_series[latest_date]['4. close'])
                    prev_price = float(time_series[prev_date]['4. close'])
                    
                    # 使用黄金ETF(GLD)的涨跌幅来估算
                    gold_change_pct = ((latest_price - prev_price) / prev_price) * 100
                    
                    return {
                        'date': latest_date,
                        'gold_price': round(gold_price, 2),
                        'gold_change_pct': round(gold_change_pct, 2),
                        'updated_at': datetime.now().isoformat(),
                        'source': 'alphavantage_xau'
                    }
            
            # 如果无法获取历史数据，只返回当前价格
            return {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'gold_price': round(gold_price, 2),
                'gold_change_pct': 0.0,
                'updated_at': datetime.now().isoformat(),
                'source': 'alphavantage_xau'
            }
        
        else:
            print(f"Error: Unexpected API response: {data}")
            return None
            
    except Exception as e:
        print(f"Error fetching from Alpha Vantage: {e}")
        return None

def fetch_gold_from_alphavantage_v2():
    """
    备用方案：使用商品数据接口
    """
    try:
        print("Trying Alpha Vantage commodity data...")
        
        # 使用商品数据接口
        url = f"https://www.alphavantage.co/query?function=COMMODITY_INTERVAL&symbol=XAUUSD&interval=daily&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            latest = data['data'][0]
            gold_date = latest['date']
            gold_price = float(latest['close'])
            
            # 计算涨跌幅
            if len(data['data']) >= 2:
                prev_price = float(data['data'][1]['close'])
                change_pct = ((gold_price - prev_price) / prev_price) * 100
            else:
                change_pct = 0.0
            
            print(f"✓ Gold price: ${gold_price:.2f} on {gold_date}")
            
            return {
                'date': gold_date,
                'gold_price': round(gold_price, 2),
                'gold_change_pct': round(change_pct, 2),
                'updated_at': datetime.now().isoformat(),
                'source': 'alphavantage_commodity'
            }
        else:
            print(f"Error: No data in response: {data}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def fetch_data():
    """
    主函数：获取数据
    优先使用 Alpha Vantage
    """
    print("="*60)
    print("Gold Data Fetcher - Alpha Vantage Edition")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print(f"API Key: {'✓ Set' if ALPHA_VANTAGE_API_KEY else '✗ Not set'}")
    print("="*60)
    
    # 尝试方法1：商品数据接口
    data = fetch_gold_from_alphavantage_v2()
    
    if data:
        print("\n✓ SUCCESS: Data fetched from Alpha Vantage")
        return data
    
    print("\n✗ FAILED: Could not fetch data")
    return None

def main():
    """主函数"""
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    # 加载现有数据
    data_file = 'data/gold_data.json'
    existing_data = []
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
            print(f"Loaded {len(existing_data)} existing records")
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")
            existing_data = []
    
    # 获取新数据
    new_data = fetch_data()
    
    if new_data:
        # 检查是否已存在该日期的数据
        existing_idx = next((i for i, d in enumerate(existing_data) 
                            if d['date'] == new_data['date']), None)
        
        if existing_idx is not None:
            existing_data[existing_idx] = new_data
            print(f"\n✓ Updated data for {new_data['date']}")
        else:
            existing_data.append(new_data)
            existing_data.sort(key=lambda x: x['date'])
            print(f"\n✓ Added new data for {new_data['date']}")
        
        # 保存
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"✓ Total records: {len(existing_data)}")
        print(f"✓ Data saved to {data_file}")
        return True
    else:
        print("\n✗ Failed to fetch data")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
