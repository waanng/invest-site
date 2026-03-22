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
    """主函数：先尝试 Yahoo Finance，失败则切换到 Alpha Vantage"""
    # 先尝试 Yahoo Finance
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/fetch_data.py'],
            capture_output=True,
            text=True,
            cwd='/Users/waanng/Documents/Playground/invest-site/projects/gold-iv'
        )
        
        if 'success' in result.stdout.lower() or result.returncode == 0:
            print("Yahoo Finance data fetch successful")
            return
    except Exception as e:
        print(f"Yahoo Finance failed: {e}")
    
    # 切换到 Alpha Vantage
    print("Switching to Alpha Vantage backup...")
    data = fetch_from_alphavantage()
    
    if data:
        # 保存数据逻辑
        data_file = 'data/gold_data.json'
        existing_data = []
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
        
        # 更新或追加
        existing_idx = next((i for i, d in enumerate(existing_data) 
                            if d['date'] == data['date']), None)
        
        if existing_idx is not None:
            existing_data[existing_idx] = data
        else:
            existing_data.append(data)
            existing_data.sort(key=lambda x: x['date'])
        
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"✓ Alpha Vantage data saved: {data['date']}")
    else:
        print("✗ All data sources failed")

if __name__ == "__main__":
    main()
