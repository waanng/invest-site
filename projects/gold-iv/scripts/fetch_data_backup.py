#!/usr/bin/env python3
"""
Gold IV Data Fetcher - 备用方案（Alpha Vantage API）
当 Yahoo Finance 失败时切换到 Alpha Vantage
需要 API Key: https://www.alphavantage.co/support/#api-key
"""
import json
import os
import time
from datetime import datetime
import requests

# 从环境变量获取 API Key
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

def fetch_from_alphavantage():
    """使用 Alpha Vantage 获取黄金数据"""
    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY not set")
        return None
    
    try:
        # 获取黄金价格
        url = f"https://www.alphavantage.co/query?function=COMMODITY_INTERVAL&symbol=XAUUSD&interval=daily&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'data' in data:
            latest = data['data'][0]
            gold_date = latest['date']
            curr_close = float(latest['close'])
            prev_close = float(data['data'][1]['close']) if len(data['data']) > 1 else curr_close
            
            return {
                'date': gold_date,
                'gold_price': round(curr_close, 2),
                'gold_change_pct': round((curr_close - prev_close) / prev_close * 100, 2),
                'gvz': None,  # Alpha Vantage 没有波动率数据
                'gvz_change_pct': None,
                'updated_at': datetime.now().isoformat(),
                'source': 'alphavantage'
            }
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
    
    return None

def main():
    """主函数：使用 Alpha Vantage 获取数据"""
    print("=== Starting Alpha Vantage backup fetch ===")
    
    # 检查 API Key
    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY environment variable not set")
        return False
    
    # 获取数据
    print("Fetching data from Alpha Vantage...")
    data = fetch_from_alphavantage()
    
    if not data:
        print("✗ Failed to fetch data from Alpha Vantage")
        return False
    
    # 保存数据
    print(f"✓ Fetched data for {data['date']}")
    data_file = 'data/gold_data.json'
    existing_data = []
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
            print(f"✓ Loaded {len(existing_data)} existing records")
        except Exception as e:
            print(f"Warning: Could not load existing data: {e}")
            existing_data = []
    
    # 更新或追加
    existing_idx = next((i for i, d in enumerate(existing_data) 
                        if d['date'] == data['date']), None)
    
    if existing_idx is not None:
        existing_data[existing_idx] = data
        print(f"✓ Updated existing record for {data['date']}")
    else:
        existing_data.append(data)
        existing_data.sort(key=lambda x: x['date'])
        print(f"✓ Added new record for {data['date']}")
    
    # 保存
    try:
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        print(f"✓ Data saved successfully. Total records: {len(existing_data)}")
        return True
    except Exception as e:
        print(f"✗ Failed to save data: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
