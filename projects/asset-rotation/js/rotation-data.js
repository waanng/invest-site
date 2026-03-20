// 资产轮动数据管理与渲染
// Asset Rotation Data Manager

const DATA_URL = 'data/market_data.json';
const INDICATORS_URL = 'data/indicators.json';

let marketData = [];
let indicators = {};

// 初始化
async function init() {
    try {
        await loadData();
        updateUI();
    } catch (error) {
        console.error('初始化失败:', error);
        useSampleData();
    }
}

// 加载数据
async function loadData() {
    try {
        // 尝试从多个来源加载
        const sources = [
            'data/market_data.json',
            'https://raw.githubusercontent.com/waanng/invest-site/main/projects/asset-rotation/data/market_data.json'
        ];
        
        for (const source of sources) {
            try {
                const response = await fetch(source + '?t=' + Date.now());
                if (response.ok) {
                    const data = await response.json();
                    if (Array.isArray(data) && data.length > 0) {
                        marketData = data;
                        console.log('市场数据加载成功:', source);
                        break;
                    }
                }
            } catch (e) {
                continue;
            }
        }
        
        // 加载指标数据
        try {
            const response = await fetch(INDICATORS_URL + '?t=' + Date.now());
            if (response.ok) {
                indicators = await response.json();
            }
        } catch (e) {
            console.log('指标数据加载失败，使用默认值');
        }
        
        // 如果没有数据，使用示例数据
        if (marketData.length === 0) {
            useSampleData();
        }
        
    } catch (error) {
        console.error('加载数据失败:', error);
        useSampleData();
    }
}

// 使用示例数据
function useSampleData() {
    console.log('使用示例数据');
    
    // 当前数据（2026-03-20）
    marketData = [{
        date: '2026-03-20',
        bond_yield_30y: 2.27,
        gold_price_usd: 3025.50,
        usdcny: 7.25,
        gold_price_cny: 705.0,
        hs300_price: 3850.0,
        hs300_change_pct: -0.5,
        copper_price: 4.15,
        updated_at: new Date().toISOString()
    }];
    
    indicators = {
        date: '2026-03-20',
        stock_bond_ratio: 5.21,
        gold_copper_ratio: 729.0,
        bond_yield: 2.27,
        house_gold_ratio: 8.0,
        calculation_time: new Date().toISOString()
    };
}

// 更新UI
function updateUI() {
    if (marketData.length === 0) return;
    
    const latest = marketData[marketData.length - 1];
    
    // 更新国债收益率
    const bondYieldEl = document.getElementById('bondYield');
    if (bondYieldEl && latest.bond_yield_30y) {
        bondYieldEl.textContent = latest.bond_yield_30y.toFixed(2) + '%';
        
        // 根据收益率设置颜色
        if (latest.bond_yield_30y > 2.8) {
            bondYieldEl.style.color = 'var(--color-up)';
        } else if (latest.bond_yield_30y < 2.0) {
            bondYieldEl.style.color = 'var(--color-warn)';
        }
    }
    
    // 更新股债性价比
    const stockBondRatioEl = document.getElementById('stockBondRatio');
    if (stockBondRatioEl && indicators.stock_bond_ratio) {
        stockBondRatioEl.textContent = indicators.stock_bond_ratio.toFixed(2) + '%';
    }
    
    // 更新房金比
    const houseGoldRatioEl = document.getElementById('houseGoldRatio');
    if (houseGoldRatioEl && indicators.house_gold_ratio) {
        houseGoldRatioEl.textContent = indicators.house_gold_ratio.toFixed(1);
    }
    
    // 更新金铜比
    const goldCopperRatioEl = document.getElementById('goldCopperRatio');
    if (goldCopperRatioEl && indicators.gold_copper_ratio) {
        goldCopperRatioEl.textContent = indicators.gold_copper_ratio.toFixed(0);
    }
    
    // 更新信号状态
    updateSignalStatus();
}

// 更新信号状态
function updateSignalStatus() {
    // 这里应该根据实际数据更新信号状态
    // 目前使用示例数据
    
    // 信号1: PPI (示例: -1.4%)
    const ppiValue = -1.4;
    const ppiEl = document.getElementById('ppiValue');
    const ppiStatusEl = document.getElementById('signal1-status');
    
    if (ppiEl) ppiEl.textContent = ppiValue.toFixed(1) + '%';
    if (ppiStatusEl) {
        if (ppiValue > 0) {
            ppiStatusEl.textContent = '已触发';
            ppiStatusEl.className = 'signal-tag signal-buy';
        } else {
            ppiStatusEl.textContent = '观望中';
            ppiStatusEl.className = 'signal-tag signal-hold';
        }
    }
    
    // 信号2: PMI (示例: 49.0%)
    const pmiValue = 49.0;
    const pmiEl = document.getElementById('pmiValue');
    const pmiStatusEl = document.getElementById('signal2-status');
    
    if (pmiEl) pmiEl.textContent = pmiValue.toFixed(1) + '%';
    if (pmiStatusEl) {
        if (pmiValue >= 50) {
            pmiStatusEl.textContent = '已触发';
            pmiStatusEl.className = 'signal-tag signal-buy';
        } else {
            pmiStatusEl.textContent = '观望中';
            pmiStatusEl.className = 'signal-tag signal-hold';
        }
    }
    
    // 信号3: 国债收益率 (示例: 2.27%)
    const yieldValue = 2.27;
    const yieldEl = document.getElementById('yieldValue');
    const yieldStatusEl = document.getElementById('signal3-status');
    
    if (yieldEl) yieldEl.textContent = yieldValue.toFixed(2) + '%';
    if (yieldStatusEl) {
        if (yieldValue > 2.8) {
            yieldStatusEl.textContent = '已触发';
            yieldStatusEl.className = 'signal-tag signal-buy';
        } else {
            yieldStatusEl.textContent = '观望中';
            yieldStatusEl.className = 'signal-tag signal-hold';
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);