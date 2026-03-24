#!/usr/bin/env python3
"""
数据获取诊断工具
用于排查 GitHub Actions 执行问题
"""
import yfinance as yf
import json
import os
import sys
from datetime import datetime
import time

def test_yahoo_connection():
    """测试 Yahoo Finance 连接"""
    print("=" * 50)
    print("测试1: Yahoo Finance 连接")
    print("=" * 50)
    
    try:
        print("正在连接 Yahoo Finance...")
        gold = yf.Ticker("GC=F")
        time.sleep(2)
        
        print("获取黄金期货数据...")
        hist = gold.history(period="5d")
        
        if hist.empty:
            print("✗ 错误: 获取到的数据为空")
            return False
        
        latest = hist.iloc[-1]
        print(f"✓ 成功获取数据")
        print(f"  最新日期: {hist.index[-1].strftime('%Y-%m-%d')}")
        print(f"  收盘价: ${latest['Close']:.2f}")
        print(f"  数据条数: {len(hist)}")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_file_access():
    """测试文件系统访问"""
    print("\n" + "=" * 50)
    print("测试2: 文件系统访问")
    print("=" * 50)
    
    try:
        # 测试目录创建
        os.makedirs('data', exist_ok=True)
        print("✓ 成功创建/访问 data 目录")
        
        # 测试文件写入
        test_file = 'data/test_write.json'
        test_data = {'test': True, 'time': datetime.now().isoformat()}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        print(f"✓ 成功写入测试文件")
        
        # 测试文件读取
        with open(test_file, 'r') as f:
            loaded = json.load(f)
        print(f"✓ 成功读取测试文件")
        
        # 清理测试文件
        os.remove(test_file)
        print(f"✓ 成功删除测试文件")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_data_integrity():
    """测试现有数据完整性"""
    print("\n" + "=" * 50)
    print("测试3: 现有数据完整性")
    print("=" * 50)
    
    data_file = 'data/gold_data.json'
    
    if not os.path.exists(data_file):
        print(f"⚠ 数据文件不存在: {data_file}")
        return True  # 这不是错误，只是没有数据
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        print(f"✓ 成功加载数据文件")
        print(f"  记录数: {len(data)}")
        
        if len(data) > 0:
            latest = data[-1]
            print(f"  最新记录日期: {latest.get('date', 'N/A')}")
            print(f"  最新金价: ${latest.get('gold_price', 'N/A')}")
            
            # 检查数据新鲜度
            last_date = datetime.strptime(latest['date'], '%Y-%m-%d')
            today = datetime.now()
            days_diff = (today - last_date).days
            
            if days_diff > 1:
                print(f"⚠ 警告: 数据已过期 {days_diff} 天")
            else:
                print(f"✓ 数据是最新的")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False

def test_environment():
    """测试环境变量"""
    print("\n" + "=" * 50)
    print("测试4: 环境变量")
    print("=" * 50)
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python 版本: {sys.version}")
    print(f"Python 路径: {sys.executable}")
    
    # 检查 API Key
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
    if api_key:
        print(f"✓ Alpha Vantage API Key 已设置 (长度: {len(api_key)})")
    else:
        print("⚠ Alpha Vantage API Key 未设置")
    
    return True

def main():
    """运行所有诊断测试"""
    print("\n" + "🔍 " * 25)
    print("数据获取诊断工具")
    print("🔍 " * 25 + "\n")
    
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'Yahoo Finance 连接': test_yahoo_connection(),
        '文件系统访问': test_file_access(),
        '数据完整性': test_data_integrity(),
        '环境变量': test_environment()
    }
    
    # 打印总结
    print("\n" + "=" * 50)
    print("诊断总结")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有测试通过")
        print("如果 GitHub Actions 仍失败，请检查:")
        print("  1. GitHub Actions 执行日志")
        print("  2. Yahoo Finance 是否限流")
        print("  3. 定时任务是否正确触发")
    else:
        print("✗ 部分测试失败")
        print("请根据上述错误信息修复问题")
    print("=" * 50 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
