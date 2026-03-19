# Investment Research Terminal

> 投资研究终端 - 系统性投资研究项目数据展示与分析平台

## 项目简介

这是一个基于 **GitHub Pages** 的投资研究项目网站，采用金融终端风格设计，用于展示各类投资研究课题的数据和分析。

### 当前研究项目

1. **黄金期权IV追踪** (Gold IV Research)
   - 追踪黄金隐含波动率与金价关系
   - 自动数据采集（每日北京时间 10:00）
   - 交易信号体系
   - 状态：🟢 运行中

2. **资产轮动策略** (Asset Rotation)
   - 基于市场周期的资产配置研究
   - 状态：🟡 筹建中

## 网站访问

**在线地址**: `https://waanng.github.io/invest-site/`

## 技术特性

### 设计风格
- **金融终端主题**: 深色背景 + 荧光绿/金色数据配色
- **专业布局**: 左侧导航 + 顶部状态栏 + 主内容区
- **等宽字体**: 使用 JetBrains Mono 显示数据
- **响应式设计**: 支持桌面和移动端

### 功能模块
- **实时数据卡片**: 展示最新金价、GVZ、信号评分
- **交互式图表**: Chart.js 绘制的走势对比图、相关性散点图
- **交易信号系统**: 基于 IV 绝对水平、变化趋势、偏斜的综合评分
- **历史数据表格**: 最近30天数据记录

### 自动化
- **数据采集**: GitHub Actions 定时任务（每天 UTC 02:00 / 北京时间 10:00）
- **自动部署**: 数据更新后自动重新部署网站
- **零成本运行**: 完全使用 GitHub 免费服务

## 项目结构

```
invest-site/
├── .github/
│   └── workflows/
│       └── update-gold.yml      # 黄金数据自动更新
├── assets/
│   └── css/
│       └── terminal.css         # 金融终端主题样式
├── projects/
│   ├── gold-iv/
│   │   ├── index.html           # 黄金项目页面
│   │   ├── data/
│   │   │   └── gold_data.json   # 数据文件
│   │   ├── scripts/
│   │   │   └── fetch_data.py    # 数据采集脚本
│   │   └── js/
│   │       └── gold-data.js     # 数据渲染逻辑
│   └── asset-rotation/
│       └── index.html           # 资产轮动项目（筹建中）
├── index.html                   # 主页
└── README.md                    # 本文件
```

## 部署指南

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建仓库: waanng/invest-site
# 选择 Public（启用 GitHub Pages）
```

### 2. 上传代码

```bash
cd invest-site

git init
git add .
git commit -m "Initial commit: Investment Research Terminal"
git remote add origin https://github.com/waanng/invest-site.git
git branch -M main
git push -u origin main
```

### 3. 启用 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main /(root)
4. 点击 **Save**

### 4. 启用 GitHub Actions

1. 点击 **Actions** 标签
2. 点击 **I understand my workflows, go ahead and enable them**

### 5. 等待部署

- 首次部署需要 2-3 分钟
- 访问 `https://waanng.github.io/invest-site/`

## 数据说明

### 数据来源
- **金价**: Yahoo Finance (GC=F)
- **GVZ**: Yahoo Finance (^GVZ)
- **更新频率**: 每日一次（北京时间 10:00）

### 信号体系

**信号A: IV绝对水平**
- GVZ < 13: 强烈买入 Call（极度便宜）
- GVZ 13-18: 买入 Call（相对便宜）
- GVZ 18-25: 观望（合理定价）
- GVZ 25-30: 考虑卖出（相对昂贵）
- GVZ > 30: 强烈卖出（极度昂贵）

**信号B: IV变化趋势**
- IV↑ + 价格↑: 恐慌性买入，警惕
- IV↑ + 价格↓: 避险需求，逢低买入
- IV↓ + 价格↑: 健康上涨，持有
- IV↓ + 价格↓: 恐慌出清，关注

**信号C: IV偏斜**（待实现）
- Call/Put IV 差值判断市场情绪

## 扩展新项目

### 添加新研究项目的步骤

1. **创建项目目录**
```bash
mkdir projects/new-project
cd projects/new-project
```

2. **创建基础文件**
```
new-project/
├── index.html          # 项目页面
├── data/
│   └── data.json       # 数据文件
├── scripts/
│   └── fetch_data.py   # 数据采集脚本
└── js/
    └── chart.js        # 图表逻辑
```

3. **添加导航链接**
编辑 `index.html` 和所有项目的侧边栏导航，添加新项目链接。

4. **创建 GitHub Actions**
复制 `.github/workflows/update-gold.yml` 并修改：
- 修改 `name`
- 修改数据获取路径
- 修改提交信息

5. **提交代码**
```bash
git add .
git commit -m "Add new project: XXX"
git push
```

## 本地开发

```bash
# 启动本地服务器（在项目根目录）
python3 -m http.server 8080

# 访问 http://localhost:8080
```

## 技术栈

- **前端**: HTML5, CSS3, Vanilla JavaScript
- **图表**: Chart.js
- **样式**: 自定义 CSS（金融终端主题）
- **字体**: JetBrains Mono (Google Fonts)
- **数据采集**: Python + yfinance
- **自动化**: GitHub Actions
- **托管**: GitHub Pages

## 许可证

MIT License

## 更新日志

- **2026-03-19**: 初始版本，包含黄金IV追踪项目

---

**Invest Research Terminal** | Data-Driven Investment Research