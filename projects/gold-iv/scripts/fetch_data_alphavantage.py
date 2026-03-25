#!/usr/bin/env python3
"""
Gold IV Data Fetcher - 双数据源版本
- Alpha Vantage: 黄金价格 (避免 Yahoo Finance 黄金 API 限制)
- Yahoo Finance: GVZ 指数 (调用频率低，不受限制)
"""
import json
import os
import time
from datetime import datetime
import requests
import yfinance as yf

# 从环境变量获取 API Key
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

def fetch_gold_from_alphavantage():
    """
    使用 Alpha Vantage 获取黄金价格
    免费版限制：25次/天
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY not set")
        return None
    
    try:
        print("Fetching gold price from Alpha Vantage...")
        
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data:
            print(f"API Error: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            print(f"API Rate Limit: {data['Note']}")
            return None
        
        if 'Time Series (Daily)' not in data:
            print(f"Unexpected response: {list(data.keys())}")
            return None
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) < 1:
            print("No data returned")
            return None
        
        latest_date = dates[0]
        latest_data = time_series[latest_date]
        close_price = float(latest_data['4. close'])
        
        # 计算涨跌幅
        if len(dates) >= 2:
            prev_close = float(time_series[dates[1]]['4. close'])
            change_pct = ((close_price - prev_close) / prev_close) * 100
        else:
            change_pct = 0.0
        
        # GLD 到黄金价格的转换系数（GLD 约等于 1/10 黄金价格）
        gold_price = close_price * 10
        
        print(f"✓ Gold: ${gold_price:.2f} ({change_pct:+.2f}%)")
        
        return {
            'date': latest_date,
            'gold_price': round(gold_price, 2),
            'gold_change_pct': round(change_pct, 2)
        }
        
    except Exception as e:
        print(f"Error fetching gold: {e}")
        return None

def fetch_gvz_from_yahoo():
    """
    使用 Yahoo Finance 获取 GVZ 数据
    GVZ 调用频率低，通常不会触发限制
    """
    try:
        print("Fetching GVZ from Yahoo Finance...")
        
        gvz = yf.Ticker("^GVZ")
        time.sleep(1)  # 短暂延迟避免限制
        
        hist = gvz.history(period="5d")
        
        if hist.empty:
            print("No GVZ data available")
            return None
        
        latest = hist.iloc[-1]
        gvz_date = hist.index[-1].strftime('%Y-%m-%d')
        
        # 计算涨跌幅
        if len(hist) >= 2:
            prev_close = float(hist.iloc[-2]['Close'])
        else:
            prev_close = float(latest['Open'])
        
        curr_close = float(latest['Close'])
        change_pct = ((curr_close - prev_close) / prev_close) * 100
        
        print(f"✓ GVZ: {curr_close:.2f} ({change_pct:+.2f}%)")
        
        return {
            'gvz': round(curr_close, 2),
            'gvz_change_pct': round(change_pct, 2)
        }
        
    except Exception as e:
        print(f"Error fetching GVZ: {e}")
        return None

def fetch_data():
    """
    获取完整数据：黄金价格 + GVZ
    """
    print("="*60)
    print("Gold Data Fetcher - Dual Source Edition")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print(f"Alpha Vantage API: {'✓' if ALPHA_VANTAGE_API_KEY else '✗'}")
    print("="*60)
    
    # 获取黄金价格
    gold_data = fetch_gold_from_alphavantage()
    
    if not gold_data:
        print("\n✗ Failed to fetch gold price")
        return None
    
    # 获取 GVZ 数据
    gvz_data = fetch_gvz_from_yahoo()
    
    if not gvz_data:
        print("Warning: Could not fetch GVZ, using gold data only")
        gvz_data = {}
    
    # 合并数据
    result = {
        **gold_data,
        **gvz_data,
        'updated_at': datetime.now().isoformat(),
        'source': 'alphavantage+yahoo'
    }
    
    print(f"\n✓ SUCCESS: Data fetched")
    return result

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
