// 黄金IV数据管理与图表渲染
// Gold IV Data Manager & Chart Renderer

const DATA_URL = 'data/gold_data.json';
const UPDATE_INTERVAL = 60000; // 1分钟刷新

let chartInstances = {};
let currentData = [];

// 初始化
async function init() {
    try {
        await loadData();
        updateStats();
        renderCharts();
        renderTable();
        updateSignals();
        
        // 定时刷新
        setInterval(async () => {
            await loadData();
            updateStats();
            renderCharts();
            updateSignals();
        }, UPDATE_INTERVAL);
        
    } catch (error) {
        console.error('初始化失败:', error);
        showError();
    }
}

// 加载数据
async function loadData() {
    try {
        // 尝试从多个来源加载数据
        const sources = [
            'data/gold_data.json',
            '../../dashboard/data/gold_iv_data.json',
            'https://raw.githubusercontent.com/waanng/invest-site/main/projects/gold-iv/data/gold_data.json'
        ];
        
        for (const source of sources) {
            try {
                const response = await fetch(source + '?t=' + Date.now());
                if (response.ok) {
                    const data = await response.json();
                    currentData = Array.isArray(data) ? data : (data.data || []);
                    if (currentData.length > 0) {
                        console.log('数据加载成功:', source);
                        break;
                    }
                }
            } catch (e) {
                continue;
            }
        }
        
        // 如果没有数据，使用示例数据
        if (currentData.length === 0) {
            console.log('使用示例数据');
            currentData = generateSampleData();
        }
        
        // 按日期排序
        currentData.sort((a, b) => new Date(a.date) - new Date(b.date));
        
    } catch (error) {
        console.error('加载数据失败:', error);
        currentData = generateSampleData();
    }
}

// 生成示例数据
function generateSampleData() {
    const data = [];
    const basePrice = 3020;
    const baseGVZ = 20;
    
    for (let i = 60; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        // 模拟价格波动
        const trend = Math.sin(i / 10) * 50;
        const noise = (Math.random() - 0.5) * 30;
        const price = basePrice + trend + noise + (60 - i) * 2;
        
        // 模拟GVZ（与价格负相关）
        const gvzNoise = (Math.random() - 0.5) * 4;
        const gvz = baseGVZ - (trend / 50) * 5 + gvzNoise;
        
        const prevPrice = i < 60 ? basePrice + Math.sin((i + 1) / 10) * 50 + (60 - i - 1) * 2 : price;
        
        data.push({
            date: date.toISOString().split('T')[0],
            gold_price: Math.round(price * 100) / 100,
            gold_change_pct: Math.round((price - prevPrice) / prevPrice * 100 * 100) / 100,
            gvz: Math.round(Math.max(10, Math.min(40, gvz)) * 100) / 100,
            gvz_change_pct: Math.round(((Math.random() - 0.5) * 6) * 100) / 100
        });
    }
    
    return data;
}

// 更新统计数据
function updateStats() {
    if (currentData.length === 0) return;
    
    const latest = currentData[currentData.length - 1];
    const prev = currentData.length > 1 ? currentData[currentData.length - 2] : latest;
    
    // 金价
    const goldPriceEl = document.getElementById('goldPrice');
    const goldChangeEl = document.getElementById('goldChange');
    
    if (goldPriceEl) {
        goldPriceEl.textContent = `$${latest.gold_price.toFixed(2)}`;
    }
    if (goldChangeEl) {
        const change = latest.gold_change_pct || 0;
        const isUp = change >= 0;
        goldChangeEl.innerHTML = `
            <span class="mono ${isUp ? 'change-up' : 'change-down'}">
                ${isUp ? '▲' : '▼'} ${Math.abs(change).toFixed(2)}%
            </span>
        `;
    }
    
    // GVZ
    const gvzValueEl = document.getElementById('gvzValue');
    const gvzChangeEl = document.getElementById('gvzChange');
    const gvzBadgeEl = document.getElementById('gvzBadge');
    
    if (gvzValueEl && latest.gvz) {
        gvzValueEl.textContent = latest.gvz.toFixed(2);
        
        // 根据GVZ水平设置badge颜色
        if (gvzBadgeEl) {
            if (latest.gvz < 13) {
                gvzBadgeEl.className = 'card-badge badge-up';
                gvzBadgeEl.textContent = 'LOW';
            } else if (latest.gvz > 30) {
                gvzBadgeEl.className = 'card-badge badge-down';
                gvzBadgeEl.textContent = 'HIGH';
            } else {
                gvzBadgeEl.className = 'card-badge';
                gvzBadgeEl.textContent = 'NORM';
            }
        }
    }
    
    if (gvzChangeEl && latest.gvz_change_pct !== undefined) {
        const change = latest.gvz_change_pct;
        const isUp = change >= 0;
        gvzChangeEl.innerHTML = `
            <span class="mono ${isUp ? 'change-up' : 'change-down'}">
                ${isUp ? '▲' : '▼'} ${Math.abs(change).toFixed(2)}%
            </span>
        `;
    }
    
    // IV评估
    if (latest.gvz) {
        const ivStatusEl = document.getElementById('ivStatus');
        const ivDescEl = document.getElementById('ivDesc');
        const ivBadgeEl = document.getElementById('ivBadge');
        
        let status, desc, badgeClass;
        if (latest.gvz < 13) {
            status = '极低';
            desc = '极度便宜';
            badgeClass = 'badge-up';
        } else if (latest.gvz < 18) {
            status = '偏低';
            desc = '相对便宜';
            badgeClass = 'badge-up';
        } else if (latest.gvz < 25) {
            status = '正常';
            desc = '合理定价';
            badgeClass = '';
        } else if (latest.gvz < 30) {
            status = '偏高';
            desc = '相对昂贵';
            badgeClass = 'badge-down';
        } else {
            status = '极高';
            desc = '极度昂贵';
            badgeClass = 'badge-down';
        }
        
        if (ivStatusEl) ivStatusEl.textContent = status;
        if (ivDescEl) ivDescEl.innerHTML = `<span>${desc}</span>`;
        if (ivBadgeEl) {
            ivBadgeEl.className = 'card-badge ' + badgeClass;
            ivBadgeEl.textContent = latest.gvz.toFixed(1);
        }
    }
}

// 更新信号系统
function updateSignals() {
    if (currentData.length === 0) return;
    
    const latest = currentData[currentData.length - 1];
    
    // 信号A: IV绝对水平
    const signalAEl = document.getElementById('signalA');
    const signalADescEl = document.getElementById('signalADesc');
    
    if (latest.gvz) {
        let signalA, descA;
        if (latest.gvz < 13) {
            signalA = '强烈买入';
            descA = 'Call极度便宜';
        } else if (latest.gvz < 18) {
            signalA = '买入';
            descA = 'Call相对便宜';
        } else if (latest.gvz > 30) {
            signalA = '强烈卖出';
            descA = '极度昂贵';
        } else if (latest.gvz > 25) {
            signalA = '卖出';
            descA = '相对昂贵';
        } else {
            signalA = '观望';
            descA = '定价合理';
        }
        
        if (signalAEl) signalAEl.textContent = signalA;
        if (signalADescEl) signalADescEl.textContent = descA;
    }
    
    // 信号B: IV变化趋势
    const signalBEl = document.getElementById('signalB');
    const signalBDescEl = document.getElementById('signalBDesc');
    
    if (latest.gvz_change_pct !== undefined && latest.gold_change_pct !== undefined) {
        const ivUp = latest.gvz_change_pct > 0;
        const priceUp = latest.gold_change_pct > 0;
        
        let signalB, descB;
        if (ivUp && priceUp) {
            signalB = '警惕';
            descB = '恐慌性买入';
        } else if (ivUp && !priceUp) {
            signalB = '买入';
            descB = '避险需求';
        } else if (!ivUp && priceUp) {
            signalB = '持有';
            descB = '健康上涨';
        } else {
            signalB = '关注';
            descB = '恐慌出清';
        }
        
        if (signalBEl) signalBEl.textContent = signalB;
        if (signalBDescEl) signalBDescEl.textContent = descB;
    }
    
    // 信号C: IV偏斜（暂用GVZ作为替代）
    const signalCEl = document.getElementById('signalC');
    const signalCDescEl = document.getElementById('signalCDesc');
    
    if (latest.gvz) {
        let signalC, descC;
        if (latest.gvz < 15) {
            signalC = '乐观';
            descC = '看涨情绪';
        } else if (latest.gvz > 28) {
            signalC = '恐慌';
            descC = '看跌情绪';
        } else {
            signalC = '中性';
            descC = '多空平衡';
        }
        
        if (signalCEl) signalCEl.textContent = signalC;
        if (signalCDescEl) signalCDescEl.textContent = descC;
    }
    
    // 综合评分（简化版）
    const totalScoreEl = document.getElementById('totalScore');
    const totalActionEl = document.getElementById('totalAction');
    const signalValueEl = document.getElementById('signalValue');
    const signalDescEl = document.getElementById('signalDesc');
    const signalBadgeEl = document.getElementById('signalBadge');
    
    if (latest.gvz) {
        let score, action, badgeClass;
        if (latest.gvz < 15) {
            score = '8/10';
            action = '考虑买入Call';
            badgeClass = 'badge-up';
        } else if (latest.gvz > 28) {
            score = '2/10';
            action = '考虑卖出';
            badgeClass = 'badge-down';
        } else {
            score = '5/10';
            action = '观望等待';
            badgeClass = '';
        }
        
        if (totalScoreEl) totalScoreEl.textContent = score;
        if (totalActionEl) totalActionEl.textContent = action;
        if (signalValueEl) signalValueEl.textContent = score;
        if (signalDescEl) signalDescEl.innerHTML = `<span>${action}</span>`;
        if (signalBadgeEl) {
            signalBadgeEl.className = 'card-badge ' + badgeClass;
            signalBadgeEl.textContent = score.split('/')[0];
        }
    }
}

// 渲染图表
function renderCharts() {
    renderPriceGvzChart();
    renderCorrelationChart();
}

// 价格与GVZ对比图
function renderPriceGvzChart() {
    const ctx = document.getElementById('priceGvzChart');
    if (!ctx) return;
    
    if (chartInstances.priceGvz) {
        chartInstances.priceGvz.destroy();
    }
    
    const labels = currentData.map(d => d.date.slice(5)); // 显示 MM-DD
    const prices = currentData.map(d => d.gold_price);
    const gvzValues = currentData.map(d => d.gvz || 20);
    
    chartInstances.priceGvz = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '金价',
                data: prices,
                borderColor: '#ffd700',
                backgroundColor: 'rgba(255, 215, 0, 0.1)',
                yAxisID: 'y',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4
            }, {
                label: 'GVZ',
                data: gvzValues,
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                yAxisID: 'y1',
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#a0a0b0',
                        font: { family: 'JetBrains Mono' }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#606070', maxTicksLimit: 10 },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    ticks: { color: '#ffd700', font: { family: 'JetBrains Mono' } },
                    grid: { color: 'rgba(255, 215, 0, 0.05)' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    ticks: { color: '#00ff88', font: { family: 'JetBrains Mono' } },
                    grid: { display: false }
                }
            }
        }
    });
}

// 相关性散点图
function renderCorrelationChart() {
    const ctx = document.getElementById('correlationChart');
    if (!ctx) return;
    
    if (chartInstances.correlation) {
        chartInstances.correlation.destroy();
    }
    
    const scatterData = currentData.map(d => ({
        x: d.gold_change_pct || 0,
        y: d.gvz_change_pct || 0
    }));
    
    const pointColors = scatterData.map(d => 
        d.x >= 0 ? '#00ff88' : '#ff4757'
    );
    
    chartInstances.correlation = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: '价格 vs IV',
                data: scatterData,
                backgroundColor: pointColors,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '金价涨跌 %',
                        color: '#a0a0b0'
                    },
                    ticks: { color: '#606070' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    title: {
                        display: true,
                        text: 'GVZ变化 %',
                        color: '#a0a0b0'
                    },
                    ticks: { color: '#606070' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            }
        }
    });
}

// 渲染历史表格
function renderTable() {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;
    
    const recentData = [...currentData].reverse().slice(0, 30);
    
    let html = '';
    recentData.forEach(row => {
        const priceChange = row.gold_change_pct || 0;
        const gvzChange = row.gvz_change_pct || 0;
        
        // IV等级
        let ivLevel = '--';
        if (row.gvz) {
            if (row.gvz < 13) ivLevel = '<span style="color: var(--color-up);">极低</span>';
            else if (row.gvz < 18) ivLevel = '<span style="color: var(--color-up);">偏低</span>';
            else if (row.gvz < 25) ivLevel = '<span style="color: var(--text-muted);">正常</span>';
            else if (row.gvz < 30) ivLevel = '<span style="color: var(--color-down);">偏高</span>';
            else ivLevel = '<span style="color: var(--color-down);">极高</span>';
        }
        
        // 信号
        let signal = '--';
        if (row.gvz) {
            if (row.gvz < 15) signal = '<span class="signal-tag signal-buy">买入</span>';
            else if (row.gvz > 28) signal = '<span class="signal-tag signal-sell">卖出</span>';
            else signal = '<span class="signal-tag signal-hold">观望</span>';
        }
        
        html += `
            <tr>
                <td class="mono">${row.date}</td>
                <td class="mono">$${row.gold_price?.toFixed(2) || '--'}</td>
                <td class="mono ${priceChange >= 0 ? 'change-up' : 'change-down'}">
                    ${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)}%
                </td>
                <td class="mono">${row.gvz?.toFixed(2) || '--'}</td>
                <td class="mono ${gvzChange >= 0 ? 'change-up' : 'change-down'}">
                    ${gvzChange >= 0 ? '+' : ''}${gvzChange.toFixed(2)}%
                </td>
                <td>${ivLevel}</td>
                <td>${signal}</td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// 显示错误
function showError() {
    const tbody = document.getElementById('historyTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: var(--color-down);">
                    数据加载失败，请刷新页面重试
                </td>
            </tr>
        `;
    }
}

// 更新图表时间范围
window.updateCharts = function(range) {
    console.log('切换时间范围:', range);
    // 这里可以实现时间范围过滤
    renderCharts();
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);