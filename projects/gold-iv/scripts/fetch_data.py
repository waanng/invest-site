#!/usr/bin/env python3
"""
Gold IV Data Fetcher for GitHub Actions
"""
import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time

def fetch_with_retry(ticker, period="5d", max_retries=3, initial_delay=5):
    """Fetch data with retry and exponential backoff"""
    for attempt in range(max_retries):
        try:
            data = ticker.history(period=period)
            if not data.empty:
                return data
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Retry {attempt + 1}/{max_retries} after {delay}s delay")
                time.sleep(delay)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Error: {e}. Retry {attempt + 1}/{max_retries} after {delay}s")
                time.sleep(delay)
            else:
                raise
    return pd.DataFrame()

def fetch_data():
    """Fetch gold and GVZ data"""
    try:
        today = datetime.now()
        
        # Fetch gold data
        gold = yf.Ticker("GC=F")
        time.sleep(2)
        gold_hist = fetch_with_retry(gold, period="5d")
        
        if gold_hist.empty:
            print("No gold data available")
            return None
        
        latest_gold = gold_hist.iloc[-1]
        gold_date = gold_hist.index[-1].strftime('%Y-%m-%d')
        
        # Calculate change
        if len(gold_hist) >= 2:
            prev_close = float(gold_hist.iloc[-2]['Close'])
        else:
            prev_close = float(latest_gold['Open'])
        
        curr_close = float(latest_gold['Close'])
        
        # Fetch GVZ
        gvz = yf.Ticker("^GVZ")
        time.sleep(2)
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
        
        return {
            'date': gold_date,
            'gold_price': round(curr_close, 2),
            'gold_change_pct': round((curr_close - prev_close) / prev_close * 100, 2),
            **gvz_data,
            'updated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
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
        except:
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
        print(f"✓ Data fetch SUCCESS")
        return True
    else:
        print("✗ Failed to fetch data")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)