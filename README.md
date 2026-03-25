# Investment Research Terminal

> 投资研究终端 - 系统性投资研究项目数据展示与分析平台

## 项目简介

这是一个基于 **GitHub Pages** 的投资研究项目网站，采用金融终端风格设计，用于展示各类投资研究课题的数据和分析。

### 核心功能

- 📊 **实时数据追踪**: 黄金价格、期权隐含波动率、宏观经济指标
- 🎯 **交易信号系统**: 基于数据指标的三层信号体系
- 📝 **投资博客**: 记录研究思考和实践经验
- 🤖 **全自动运行**: GitHub Actions 定时采集数据，零成本托管

### 当前研究项目

1. **黄金期权IV追踪** (Gold IV Research) 🥇
   - 追踪黄金隐含波动率（GVZ）与金价关系
   - 自动数据采集（每日北京时间 21:30，黄金收盘后）
   - 三层交易信号体系（IV绝对水平、IV与价格联动、IV偏斜）
   - 状态：🟢 运行中

2. **资产轮动策略** (Asset Rotation) 🔄
   - 基于"货币周期 × 信用周期"四象限框架
   - 五大核心指标监测（国债收益率、股债比、房金比、金铜比、PPI-CPI）
   - 月度宏观数据录入与配置建议
   - 状态：🟢 运行中

3. **投资博客** (Investment Blog) 📝
   - 记录投资研究方法论和实践经验
   - 系统构建教程和技术分享
   - 状态：🟢 运行中

## 网站访问

**在线地址**: [https://waanng.github.io/invest-site/](https://waanng.github.io/invest-site/)

**项目文章**: [从零构建个人投资研究系统](https://waanng.github.io/invest-site/blog/posts/building-investment-research-system.html)

## 技术特性

### 设计风格
- **金融终端主题**: 深色背景 + 荧光绿/金色数据配色
- **专业布局**: 左侧导航 + 顶部状态栏 + 主内容区
- **等宽字体**: 使用 JetBrains Mono 显示数据
- **响应式设计**: 支持桌面和移动端

### 功能模块

#### 数据展示
- **实时数据卡片**: 展示最新金价、GVZ、信号评分
- **交互式图表**: Chart.js 绘制的走势对比图、相关性散点图
- **历史数据表格**: 最近30天数据记录

#### 信号系统
- **三层信号体系**: IV绝对水平、IV与价格联动、综合评分
- **可视化信号**: 红绿灯式信号指示器
- **配置建议**: 基于信号的交易建议

#### 博客系统
- **文章列表**: 支持标签、阅读时间、精选标记
- **文章详情**: 目录导航、代码高亮、响应式排版
- **动态加载**: JSON 数据管理文章

### 自动化架构

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  Alpha Vantage  │────▶│              │     │              │
│  (黄金价格)     │     │   Python     │     │   JSON       │
│  主要数据源     │     │   数据采集   │────▶│   本地存储   │
└─────────────────┘     │   脚本       │     │              │
                        └──────────────┘     └──────────────┘
┌─────────────────┐              │                     │
│  Yahoo Finance  │              │                     │
│  (GVZ指数)      │──────────────┘                     │
│  补充数据源     │                                    │
└─────────────────┘              ▼                     ▼
                        ┌──────────────┐     ┌──────────────┐
                        │ GitHub Actions│     │ GitHub Pages │
                        │ 自动执行      │────▶│ 自动部署     │
                        └──────────────┘     └──────────────┘
```

**特性**:
- **双数据源**: Alpha Vantage（黄金价格）+ Yahoo Finance（GVZ指数）
- **智能分工**: 避免单一数据源限流问题
- **详细日志**: 每步执行都有详细输出
- **零成本运行**: 完全使用 GitHub 免费服务

## 项目结构

```
invest-site/
├── .github/
│   └── workflows/
│       ├── update-gold.yml          # 黄金数据自动更新（21:30 CST）
│       └── update-rotation.yml      # 资产轮动数据更新
├── assets/
│   └── css/
│       ├── terminal.css             # 金融终端主题样式
│       └── blog.css                 # 博客页面样式
├── blog/
│   ├── index.html                   # 博客首页
│   ├── data/
│   │   └── blog-data.json           # 博客文章数据
│   └── posts/
│       └── *.html                   # 博客文章详情页
├── projects/
│   ├── gold-iv/
│   │   ├── index.html               # 黄金项目页面
│   │   ├── data/
│   │   │   └── gold_data.json       # 历史数据
│   │   ├── scripts/
│   │   │   ├── fetch_data.py        # 主数据采集脚本
│   │   │   ├── fetch_data_backup.py # Alpha Vantage备用
│   │   │   └── diagnose.py          # 诊断工具
│   │   └── js/
│   │       └── gold-data.js         # 前端数据渲染
│   └── asset-rotation/
│       ├── index.html               # 资产轮动页面
│       ├── data/
│       │   ├── market_data.json     # 市场数据
│       │   ├── indicators.json      # 计算指标
│       │   └── macro_data.json      # 宏观数据
│       └── js/
│           └── rotation-data.js     # 数据渲染与录入
├── index.html                       # 主页
├── README.md                        # 本文件
└── ARTICLE.md                       # 项目详细介绍文章
```

## 部署指南

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 上创建仓库: waanng/invest-site
# 选择 Public（启用 GitHub Pages）
```

### 2. 上传代码

```bash
git clone https://github.com/waanng/invest-site.git
cd invest-site
```

### 3. 启用 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main /(root)
4. 点击 **Save**

### 4. 启用 GitHub Actions

1. 点击 **Actions** 标签
2. 点击 **I understand my workflows, go ahead and enable them**

### 5. 配置 Alpha Vantage API Key（可选但推荐）

1. 访问 [Alpha Vantage](https://www.alphavantage.co/support/#api-key) 免费申请 API Key
2. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. Name: `ALPHA_VANTAGE_API_KEY`
5. Value: 你的 API Key

### 6. 等待部署

- 首次部署需要 2-3 分钟
- 访问 `https://waanng.github.io/invest-site/`

## 数据说明

### 数据来源

| 数据类型 | 来源 | 代码/API | 更新频率 |
|---------|------|----------|----------|
| 黄金价格 | Alpha Vantage | GLD ETF | 每日 21:30 CST |
| 黄金波动率 | Yahoo Finance | ^GVZ | 每日 21:30 CST |
| 宏观经济 | 国家统计局 | - | 月度手动录入 |

**为什么选择 21:30 更新时间？**
- 黄金期货（GC=F）北京时间 20:00 收盘
- 21:30 数据已稳定，且是美国盘后、亚洲盘前

### 信号体系

**信号A: IV绝对水平**
```
GVZ < 13    → 强烈买入 Call（极度便宜）
GVZ 13-18   → 买入 Call（相对便宜）
GVZ 18-25   → 观望（合理定价）
GVZ 25-30   → 考虑卖出（相对昂贵）
GVZ > 30    → 强烈卖出（极度昂贵）
```

**信号B: IV与价格联动**
```
IV↑ + 价格↑ → 恐慌性买入，警惕追高风险
IV↑ + 价格↓ → 避险需求旺盛，逢低买入机会
IV↓ + 价格↑ → 健康上涨，可持有
IV↓ + 价格↓ → 恐慌出清，关注企稳信号
```

**信号C: IV偏斜**（待实现）
- Call/Put IV 差值判断市场情绪

## 故障排查

### 数据未更新？

1. **查看 GitHub Actions 日志**
   - 访问 `https://github.com/waanng/invest-site/actions`
   - 检查最新执行记录

2. **运行诊断工具**
   ```bash
   cd projects/gold-iv
   python scripts/diagnose.py
   ```

3. **常见问题**
   - Alpha Vantage API Key 无效 → 检查 GitHub Secrets 配置
   - Alpha Vantage 限流（25次/天）→ 明日自动恢复
   - Yahoo Finance GVZ 获取失败 → 检查网络连接
   - 网络问题 → 查看 Actions 日志中的详细错误

### 手动触发更新

1. 进入 Actions → Update Gold IV Data
2. 点击 **Run workflow**
3. 可选：勾选 **Enable debug mode** 查看详细日志

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

### 发布博客文章

1. **创建文章 HTML 文件**
```bash
touch blog/posts/my-article.html
```

2. **更新文章数据**
编辑 `blog/data/blog-data.json`，添加新文章：
```json
{
  "id": "my-article",
  "title": "文章标题",
  "summary": "文章摘要",
  "date": "2026-03-23",
  "author": "王安",
  "tags": ["标签1", "标签2"],
  "url": "posts/my-article.html"
}
```

3. **提交发布**
```bash
git add .
git commit -m "Add blog post: 文章标题"
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
- **数据采集**: Python + yfinance + requests
- **自动化**: GitHub Actions
- **托管**: GitHub Pages

## 许可证

MIT License

## 更新日志

- **2026-03-25**:
  - 重构数据获取架构：双数据源分离
  - Alpha Vantage 获取黄金价格（避免 Yahoo Finance 黄金 API 限流）
  - Yahoo Finance 获取 GVZ 指数（低频率调用不受限制）
  - 添加详细日志输出，便于排查问题

- **2026-03-24**: 
  - 修复 GitHub Actions 数据更新问题
  - 添加 Alpha Vantage 备用数据源
  - 添加诊断工具 diagnose.py
  - 改进错误处理和日志输出

- **2026-03-22**: 
  - 添加投资博客系统
  - 发布第一篇文章《从零构建个人投资研究系统》
  - 添加博客文章列表和详情页

- **2026-03-21**: 
  - 添加资产轮动策略研究项目
  - 实现四象限周期定位
  - 添加五大核心指标监测

- **2026-03-19**: 
  - 初始版本，包含黄金IV追踪项目
  - 建立三层信号体系
  - GitHub Actions 自动数据采集

---

**Invest Research Terminal** | Data-Driven Investment Research

**作者**: 王安 (北大+中科大，数据与AI从业者)

**联系**: [GitHub Issues](https://github.com/waanng/invest-site/issues)
