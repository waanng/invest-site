#!/usr/bin/env python3
"""
Gold IV Data Fetcher for GitHub Actions
使用 yfinance 0.2.54+ 版本，支持自定义请求头绕过限速
"""
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime
import time
import random

def fetch_with_retry(ticker, period="5d", max_retries=5, initial_delay=10):
    """Fetch data with retry, random delays, and exponential backoff"""
    # 添加随机 User-Agent 和请求头
    headers = {
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 130)}.0.0.0 Safari/537.36'
    }
    
    # 设置 yfinance 会话
    ticker.session = headers
    
    for attempt in range(max_retries):
        try:
            # 添加随机延迟 2-5 秒
            jitter = random.uniform(2, 5)
            time.sleep(jitter)
            
            data = ticker.history(period=period)
            if not data.empty:
                return data
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt) + random.uniform(1, 3)
                print(f"Empty data, retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                time.sleep(delay)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt) + random.uniform(1, 3)
                print(f"Error: {str(e)[:50]}..., retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                time.sleep(delay)
            else:
                raise
    return pd.DataFrame()

def fetch_data():
    """Fetch gold and GVZ data"""
    try:
        print(f"[{datetime.now()}] Starting data fetch...")
        
        # Fetch gold data
        gold = yf.Ticker("GC=F")
        print("Fetching gold futures data...")
        gold_hist = fetch_with_retry(gold, period="5d")
        
        if gold_hist.empty:
            print("ERROR: No gold data available")
            return None
        
        latest_gold = gold_hist.iloc[-1]
        gold_date = gold_hist.index[-1].strftime('%Y-%m-%d')
        print(f"Gold data retrieved: {gold_date}")
        
        # Calculate change
        if len(gold_hist) >= 2:
            prev_close = float(gold_hist.iloc[-2]['Close'])
        else:
            prev_close = float(latest_gold['Open'])
        
        curr_close = float(latest_gold['Close'])
        
        # Fetch GVZ with delay between requests
        time.sleep(random.uniform(3, 6))
        gvz = yf.Ticker("^GVZ")
        print("Fetching GVZ data...")
        gvz_hist = fetch_with_retry(gvz, period="5d")
        
        gvz_data = {}
        if not gvz_hist.empty:
            latest_gvz = gvz_hist.iloc[-1]
            
            if len(gvz_hist) >= 2:
                prev_gvz = float(gvz_hist.iloc[-2]['Close'])
            else:
                prev_gvz = float(latest_gvz['Open'])
            
            curr_gvz = float(latest_gvz['Close'])
            
            gvz_data = {
                'gvz': round(curr_gvz, 2),
                'gvz_change_pct': round((curr_gvz - prev_gvz) / prev_gvz * 100, 2)
            }
            print(f"GVZ data retrieved: {curr_gvz}")
        else:
            print("WARNING: No GVZ data available")
        
        result = {
            'date': gold_date,
            'gold_price': round(curr_close, 2),
            'gold_change_pct': round((curr_close - prev_close) / prev_close * 100, 2),
            **gvz_data,
            'updated_at': datetime.now().isoformat()
        }
        
        print(f"Data fetch successful: {result}")
        return result
        
    except Exception as e:
        print(f"CRITICAL ERROR fetching data: {e}")
        return None

def main():
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Load existing data
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
    
    # Fetch new data
    new_data = fetch_data()
    
    if new_data:
        # Update or append
        existing_idx = next((i for i, d in enumerate(existing_data) 
                            if d['date'] == new_data['date']), None)
        
        if existing_idx is not None:
            existing_data[existing_idx] = new_data
            print(f"✓ Updated data for {new_data['date']}")
        else:
            existing_data.append(new_data)
            existing_data.sort(key=lambda x: x['date'])
            print(f"✓ Added new data for {new_data['date']}")
        
        # Save
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        print(f"✓ Total records: {len(existing_data)}")
        return True
    else:
        print("✗ Failed to fetch data")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
