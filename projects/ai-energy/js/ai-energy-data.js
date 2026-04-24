// 算力与能源投资研究数据渲染

const DATA_URL = 'data/ai_energy_data.json';

let aiEnergyData = {};
let charts = {};

async function init() {
  try {
    await loadData();
    updateStats();
    renderCharts();
    renderSignals();
    renderWatchlist();
  } catch (error) {
    console.error('初始化失败:', error);
    aiEnergyData = getSampleData();
    updateStats();
    renderCharts();
    renderSignals();
    renderWatchlist();
  }
}

async function loadData() {
  const sources = [
    DATA_URL,
    'https://raw.githubusercontent.com/waanng/invest-site/main/projects/ai-energy/data/ai_energy_data.json'
  ];

  for (const source of sources) {
    try {
      const response = await fetch(source + '?t=' + Date.now());
      if (response.ok) {
        aiEnergyData = await response.json();
        return;
      }
    } catch (error) {
      continue;
    }
  }

  aiEnergyData = getSampleData();
}

function getSampleData() {
  return {
    updated_at: new Date().toISOString(),
    stage: '能源瓶颈期',
    summary: 'AI资本开支仍在扩张，能源约束正在成为下一阶段主线。',
    capex: [
      { quarter: '2025Q1', msft: 16.7, goog: 17.2, amzn: 24.3, meta: 13.7, orcl: 3.2 },
      { quarter: '2025Q2', msft: 19.0, goog: 19.1, amzn: 25.8, meta: 15.1, orcl: 4.0 },
      { quarter: '2025Q3', msft: 20.1, goog: 21.0, amzn: 27.3, meta: 16.8, orcl: 4.8 },
      { quarter: '2025Q4', msft: 22.6, goog: 22.4, amzn: 29.1, meta: 18.4, orcl: 5.7 },
      { quarter: '2026Q1', msft: 24.2, goog: 24.0, amzn: 31.5, meta: 20.2, orcl: 6.8 }
    ],
    revenue: [
      { quarter: '2025Q1', nvda_data_center: 22.6, ai_server: 48.0 },
      { quarter: '2025Q2', nvda_data_center: 26.3, ai_server: 55.0 },
      { quarter: '2025Q3', nvda_data_center: 30.8, ai_server: 63.0 },
      { quarter: '2025Q4', nvda_data_center: 35.6, ai_server: 72.0 },
      { quarter: '2026Q1', nvda_data_center: 39.1, ai_server: 83.0 }
    ],
    power: [
      { quarter: '2025Q1', dc_power_demand: 38, ppa_capacity: 9.5, grid_queue: 31, industrial_power_price: 7.6 },
      { quarter: '2026Q1', dc_power_demand: 56, ppa_capacity: 19.7, grid_queue: 49, industrial_power_price: 8.9 }
    ],
    market: [],
    watchlist: [],
    signals: {
      capex_growth: 34.2,
      nvda_dc_growth: 73.0,
      power_demand_growth: 47.4,
      energy_bottleneck: 78,
      valuation_heat: 72
    }
  };
}

function updateStats() {
  const signals = aiEnergyData.signals || {};
  setText('capexGrowth', formatPercent(signals.capex_growth));
  setText('nvdaGrowth', formatPercent(signals.nvda_dc_growth));
  setText('powerGrowth', formatPercent(signals.power_demand_growth));
  setText('bottleneckIndex', formatScore(signals.energy_bottleneck));
  setText('currentStage', aiEnergyData.stage || '--');
  setText('stageSummary', aiEnergyData.summary || '--');

  const updatedAt = aiEnergyData.updated_at ? new Date(aiEnergyData.updated_at) : new Date();
  setText('lastDataUpdate', updatedAt.toLocaleDateString('zh-CN'));
}

function renderCharts() {
  renderCapexChart();
  renderRevenueChart();
  renderPowerChart();
  renderMarketChart();
}

function renderCapexChart() {
  const ctx = document.getElementById('capexChart');
  if (!ctx) return;

  destroyChart('capex');
  const rows = aiEnergyData.capex || [];

  charts.capex = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: rows.map(row => row.quarter),
      datasets: [
        { label: 'MSFT', data: rows.map(row => row.msft), backgroundColor: '#74b9ff' },
        { label: 'GOOG', data: rows.map(row => row.goog), backgroundColor: '#00ff88' },
        { label: 'AMZN', data: rows.map(row => row.amzn), backgroundColor: '#ffa502' },
        { label: 'META', data: rows.map(row => row.meta), backgroundColor: '#ff4757' },
        { label: 'ORCL', data: rows.map(row => row.orcl), backgroundColor: '#ffd700' }
      ]
    },
    options: baseChartOptions({
      stacked: true,
      yTitle: 'CAPEX / 十亿美元'
    })
  });
}

function renderRevenueChart() {
  const ctx = document.getElementById('revenueChart');
  if (!ctx) return;

  destroyChart('revenue');
  const rows = aiEnergyData.revenue || [];

  charts.revenue = new Chart(ctx, {
    type: 'line',
    data: {
      labels: rows.map(row => row.quarter),
      datasets: [
        {
          label: 'NVDA数据中心收入',
          data: rows.map(row => row.nvda_data_center),
          borderColor: '#00ff88',
          backgroundColor: 'rgba(0, 255, 136, 0.12)',
          tension: 0.35,
          fill: true,
          borderWidth: 2
        },
        {
          label: 'AI服务器收入指数',
          data: rows.map(row => row.ai_server),
          borderColor: '#ffd700',
          backgroundColor: 'rgba(255, 215, 0, 0.08)',
          yAxisID: 'y1',
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: dualAxisOptions('十亿美元', '收入指数')
  });
}

function renderPowerChart() {
  const ctx = document.getElementById('powerChart');
  if (!ctx) return;

  destroyChart('power');
  const rows = aiEnergyData.power || [];

  charts.power = new Chart(ctx, {
    type: 'line',
    data: {
      labels: rows.map(row => row.quarter),
      datasets: [
        {
          label: '数据中心电力需求',
          data: rows.map(row => row.dc_power_demand),
          borderColor: '#ff4757',
          backgroundColor: 'rgba(255, 71, 87, 0.12)',
          tension: 0.35,
          fill: true,
          borderWidth: 2
        },
        {
          label: 'PPA签约容量',
          data: rows.map(row => row.ppa_capacity),
          borderColor: '#74b9ff',
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: '电网排队压力',
          data: rows.map(row => row.grid_queue),
          borderColor: '#ffd700',
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: baseChartOptions({ yTitle: '指数 / GW' })
  });
}

function renderMarketChart() {
  const ctx = document.getElementById('marketChart');
  if (!ctx) return;

  destroyChart('market');
  const rows = aiEnergyData.market || [];

  charts.market = new Chart(ctx, {
    type: 'line',
    data: {
      labels: rows.map(row => row.date.slice(5)),
      datasets: [
        {
          label: '算力链',
          data: rows.map(row => row.compute_basket),
          borderColor: '#00ff88',
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: '能源链',
          data: rows.map(row => row.energy_basket),
          borderColor: '#ffa502',
          tension: 0.35,
          borderWidth: 2
        },
        {
          label: '电网设备',
          data: rows.map(row => row.grid_basket),
          borderColor: '#74b9ff',
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: baseChartOptions({ yTitle: '相对表现指数' })
  });
}

function renderSignals() {
  const signals = aiEnergyData.signals || {};
  const capex = Number(signals.capex_growth || 0);
  const power = Number(signals.power_demand_growth || 0);
  const bottleneck = Number(signals.energy_bottleneck || 0);
  const valuation = Number(signals.valuation_heat || 0);

  setSignal('signalCapex', capex > 25 ? '扩张' : '放缓', capex > 25 ? '云厂商继续加大AI基础设施投入' : '资本开支增速边际走弱', capex > 25 ? 'signal-buy' : 'signal-hold');
  setSignal('signalPower', power > 35 ? '紧张' : '可控', power > 35 ? '数据中心用电需求快速上行' : '能源供给仍可匹配需求', power > 35 ? 'signal-buy' : 'signal-hold');
  setSignal('signalValuation', valuation > 80 ? '过热' : '偏热', valuation > 80 ? '高估值资产回撤风险上升' : '估值需用业绩继续消化', valuation > 80 ? 'signal-sell' : 'signal-hold');
  setSignal('signalAllocation', bottleneck > 70 ? '能源优先' : '算力优先', bottleneck > 70 ? '电力、电网、核电权重高于纯芯片弹性' : '芯片、服务器、网络仍是主线', bottleneck > 70 ? 'signal-buy' : 'signal-hold');
}

function renderWatchlist() {
  const tbody = document.getElementById('watchlistBody');
  if (!tbody) return;

  const rows = aiEnergyData.watchlist || [];
  tbody.innerHTML = rows.map(row => {
    const signalClass = row.signal.includes('强') ? 'signal-buy' : row.signal.includes('观察') ? 'signal-hold' : 'signal-hold';
    return `
      <tr>
        <td class="mono">${row.ticker}</td>
        <td>${row.name}</td>
        <td>${row.segment}</td>
        <td class="mono">${row.score}</td>
        <td><span class="signal-tag ${signalClass}">${row.signal}</span></td>
        <td style="font-family: var(--font-sans); color: var(--text-secondary);">${row.risk}</td>
      </tr>
    `;
  }).join('');
}

function setSignal(id, title, desc, className) {
  const el = document.getElementById(id);
  if (!el) return;

  el.innerHTML = `
    <div class="signal-tag ${className}" style="margin-bottom: 12px;">${title}</div>
    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.5;">${desc}</div>
  `;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function formatPercent(value) {
  return Number.isFinite(Number(value)) ? `${Number(value).toFixed(1)}%` : '--';
}

function formatScore(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(0) : '--';
}

function destroyChart(name) {
  if (charts[name]) {
    charts[name].destroy();
  }
}

function baseChartOptions({ yTitle = '', stacked = false } = {}) {
  return {
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
        stacked,
        ticks: { color: '#606070' },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      },
      y: {
        stacked,
        title: {
          display: Boolean(yTitle),
          text: yTitle,
          color: '#a0a0b0'
        },
        ticks: { color: '#606070', font: { family: 'JetBrains Mono' } },
        grid: { color: 'rgba(255, 255, 255, 0.05)' }
      }
    }
  };
}

function dualAxisOptions(leftTitle, rightTitle) {
  const options = baseChartOptions({ yTitle: leftTitle });
  options.scales.y1 = {
    type: 'linear',
    position: 'right',
    title: {
      display: true,
      text: rightTitle,
      color: '#a0a0b0'
    },
    ticks: { color: '#606070', font: { family: 'JetBrains Mono' } },
    grid: { display: false }
  };
  return options;
}

document.addEventListener('DOMContentLoaded', init);
