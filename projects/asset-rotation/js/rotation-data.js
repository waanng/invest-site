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
    console.log('Updating UI, marketData:', marketData.length, 'indicators:', Object.keys(indicators));
    
    // 使用最新的市场数据或示例数据
    let latest = marketData.length > 0 ? marketData[marketData.length - 1] : null;
    
    // 更新国债收益率
    const bondYieldEl = document.getElementById('bondYield');
    if (bondYieldEl) {
        const yield = latest?.bond_yield_30y || indicators?.bond_yield || 2.27;
        bondYieldEl.textContent = yield.toFixed(2) + '%';
        
        // 根据收益率设置颜色
        if (yield > 2.8) {
            bondYieldEl.style.color = 'var(--color-up)';
        } else if (yield < 2.0) {
            bondYieldEl.style.color = 'var(--color-warn)';
        }
    }
    
    // 更新股债性价比
    const stockBondRatioEl = document.getElementById('stockBondRatio');
    if (stockBondRatioEl) {
        const ratio = indicators?.stock_bond_ratio || 5.21;
        stockBondRatioEl.textContent = ratio.toFixed(2) + '%';
    }
    
    // 更新房金比
    const houseGoldRatioEl = document.getElementById('houseGoldRatio');
    if (houseGoldRatioEl) {
        const ratio = indicators?.house_gold_ratio || 8.0;
        houseGoldRatioEl.textContent = ratio.toFixed(1);
    }
    
    // 更新金铜比
    const goldCopperRatioEl = document.getElementById('goldCopperRatio');
    if (goldCopperRatioEl) {
        const ratio = indicators?.gold_copper_ratio || 729;
        goldCopperRatioEl.textContent = ratio.toFixed(0);
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

// 检查是否需要更新宏观数据
function checkDataUpdateNeeded() {
    const today = new Date();
    const currentDay = today.getDate();
    
    // 获取上次更新日期（从localStorage或默认值）
    const lastUpdateStr = localStorage.getItem('macroDataLastUpdate');
    let lastUpdate = lastUpdateStr ? new Date(lastUpdateStr) : new Date('2026-03-01');
    
    const daysSinceUpdate = Math.floor((today - lastUpdate) / (1000 * 60 * 60 * 24));
    
    // 如果距离上次更新超过25天，或者今天是每月的10-20号之间
    const isUpdateWindow = currentDay >= 10 && currentDay <= 20;
    const needsUpdate = daysSinceUpdate >= 25 || (isUpdateWindow && daysSinceUpdate >= 20);
    
    // 显示或隐藏提醒
    const alertSection = document.getElementById('dataAlert');
    if (alertSection) {
        alertSection.style.display = needsUpdate ? 'block' : 'none';
        
        if (needsUpdate) {
            // 更新状态显示
            const lastMonth = lastUpdate.toISOString().slice(0, 7); // YYYY-MM
            const currentMonth = today.toISOString().slice(0, 7);
            
            // 检查各项数据状态（简化版，实际应该从数据文件读取）
            const pmiStatus = document.getElementById('pmiStatus');
            const ppiStatus = document.getElementById('ppiStatus');
            const cpiStatus = document.getElementById('cpiStatus');
            const socialStatus = document.getElementById('socialStatus');
            
            if (lastMonth < currentMonth) {
                // 需要更新本月数据
                if (pmiStatus) pmiStatus.textContent = '待更新';
                if (ppiStatus) ppiStatus.textContent = '待更新';
                if (cpiStatus) cpiStatus.textContent = '待更新';
                if (socialStatus) socialStatus.textContent = '待更新';
            }
        }
    }
}

// 打开数据更新模态框
function openDataUpdateModal() {
    const modal = document.getElementById('updateModal');
    if (modal) {
        modal.style.display = 'flex';
        // 设置默认月份为当前月份
        const monthInput = document.getElementById('dataMonth');
        if (monthInput) {
            const today = new Date();
            monthInput.value = today.toISOString().slice(0, 7);
        }
    }
}

// 关闭数据更新模态框
function closeDataUpdateModal() {
    const modal = document.getElementById('updateModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 提交宏观数据
function submitMacroData() {
    const month = document.getElementById('dataMonth').value;
    const pmi = document.getElementById('inputPMI').value;
    const ppi = document.getElementById('inputPPI').value;
    const cpi = document.getElementById('inputCPI').value;
    const social = document.getElementById('inputSocial').value;
    const note = document.getElementById('inputNote').value;
    
    if (!month) {
        alert('请选择数据月份');
        return;
    }
    
    // 构建数据对象
    const macroData = {
        month: month,
        pmi: pmi ? parseFloat(pmi) : null,
        ppi: ppi ? parseFloat(ppi) : null,
        cpi: cpi ? parseFloat(cpi) : null,
        social_financing: social ? parseFloat(social) : null,
        note: note,
        updated_at: new Date().toISOString()
    };
    
    // 保存到localStorage（临时存储）
    let allMacroData = JSON.parse(localStorage.getItem('macroDataHistory') || '[]');
    
    // 检查是否已存在该月份数据
    const existingIndex = allMacroData.findIndex(d => d.month === month);
    if (existingIndex >= 0) {
        allMacroData[existingIndex] = macroData;
    } else {
        allMacroData.push(macroData);
    }
    
    localStorage.setItem('macroDataHistory', JSON.stringify(allMacroData));
    localStorage.setItem('macroDataLastUpdate', new Date().toISOString());
    
    // 生成JSON文件内容
    const jsonContent = JSON.stringify(allMacroData, null, 2);
    
    // 创建下载链接
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `macro_data_${month}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    alert(`数据已保存！\n\n请将下载的JSON文件上传到GitHub仓库的 projects/asset-rotation/data/ 目录下，并提交更新。\n\n上传路径：invest-site/projects/asset-rotation/data/macro_data.json`);
    
    closeDataUpdateModal();
    checkDataUpdateNeeded(); // 重新检查更新状态
    
    // 刷新页面以显示新数据
    setTimeout(() => location.reload(), 1000);
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('updateModal');
    if (event.target === modal) {
        closeDataUpdateModal();
    }
}

// 暴露函数到全局作用域（供HTML onclick调用）
window.openDataUpdateModal = openDataUpdateModal;
window.closeDataUpdateModal = closeDataUpdateModal;
window.submitMacroData = submitMacroData;
window.checkDataUpdateNeeded = checkDataUpdateNeeded;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    init();
    checkDataUpdateNeeded();
    
    // 每天检查一次是否需要更新
    setInterval(checkDataUpdateNeeded, 24 * 60 * 60 * 1000);
});