#!/usr/bin/env python3
"""
Gold IV Data Fetcher - 使用 Alpha Vantage 免费版 API
使用 GLD ETF 作为黄金价格代理（免费版支持）
"""
import json
import os
from datetime import datetime
import requests

# 从环境变量获取 API Key
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

def fetch_gld_data():
    """
    使用 Alpha Vantage 获取 GLD (黄金ETF) 数据
    GLD 价格与黄金价格高度相关，可作为代理
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY not set")
        return None
    
    try:
        print("Fetching GLD data from Alpha Vantage...")
        
        # 使用 TIME_SERIES_DAILY 获取 GLD 数据
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GLD&apikey={ALPHA_VANTAGE_API_KEY}"
        
        print(f"API URL: {url.replace(ALPHA_VANTAGE_API_KEY, '***')}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 检查错误信息
        if 'Error Message' in data:
            print(f"API Error: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            print(f"API Note: {data['Note']}")
            return None
        
        if 'Time Series (Daily)' not in data:
            print(f"Unexpected response: {data}")
            return None
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)
        
        if len(dates) < 1:
            print("No data returned")
            return None
        
        # 获取最新数据
        latest_date = dates[0]
        latest_data = time_series[latest_date]
        
        close_price = float(latest_data['4. close'])
        
        # 计算涨跌幅
        if len(dates) >= 2:
            prev_date = dates[1]
            prev_close = float(time_series[prev_date]['4. close'])
            change_pct = ((close_price - prev_close) / prev_close) * 100
        else:
            change_pct = 0.0
        
        # GLD 到黄金价格的转换系数（GLD 约等于 1/10 黄金价格）
        gold_price = close_price * 10
        
        print(f"✓ GLD price: ${close_price:.2f}")
        print(f"✓ Estimated gold price: ${gold_price:.2f}")
        print(f"✓ Date: {latest_date}")
        print(f"✓ Change: {change_pct:.2f}%")
        
        return {
            'date': latest_date,
            'gold_price': round(gold_price, 2),
            'gold_change_pct': round(change_pct, 2),
            'updated_at': datetime.now().isoformat(),
            'source': 'alphavantage_gld'
        }
        
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed: {e}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    """主函数"""
    print("="*60)
    print("Gold Data Fetcher - Alpha Vantage Edition (Free Tier)")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print(f"API Key: {'✓ Set' if ALPHA_VANTAGE_API_KEY else '✗ Not set'}")
    print("="*60)
    
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
    new_data = fetch_gld_data()
    
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
