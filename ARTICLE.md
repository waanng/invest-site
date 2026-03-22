# 从零构建个人投资研究系统：黄金波动率追踪实战

> **作者**：王安  
> **背景**：北大+中科大，数据与AI领域从业者  
> **项目周期**：2周（从想法到上线）  
> **技术栈**：Python + GitHub Actions + Chart.js + GitHub Pages

---

## 一、为什么做这个项目

### 1.1 投资研究的痛点

作为一个有数据背景的投资者，我一直面临几个困扰：

- **数据分散**：金价、波动率、宏观经济数据分散在不同平台，难以统一分析
- **缺乏历史记录**：东方财富、同花顺等App只能看当天数据，无法建立自己的数据库
- **信号模糊**：什么时候该买期权？IV高了还是低了？缺乏量化标准
- **回顾困难**：交易后想复盘，却发现没有系统的数据记录

### 1.2 核心诉求

我需要一个系统，能够：
1. **自动记录**每日黄金价格和期权隐含波动率
2. **建立信号体系**判断IV高低，指导交易决策
3. **可视化展示**价格与波动率的关系
4. **零成本运行**（个人研究项目，不想投入服务器费用）

---

## 二、数据指标体系设计

### 2.1 核心指标选择

经过研究，我确定了以下核心指标：

| 指标 | 代码 | 来源 | 更新频率 | 用途 |
|------|------|------|----------|------|
| 黄金期货 | GC=F | Yahoo Finance | 每日 | 标的价格 |
| 黄金波动率指数 | ^GVZ | Yahoo Finance | 每日 | 期权IV水平 |
| PMI | - | 国家统计局 | 月度 | 经济周期判断 |
| PPI/CPI | - | 国家统计局 | 月度 | 通胀预期 |

**为什么不直接用黄金现货？**
- 黄金期货（GC=F）交易更活跃，数据更连续
- GVZ是基于黄金期权计算的波动率指数，对标GC=F
- 期货数据开盘时间更长（几乎24小时），适合盘后分析

### 2.2 信号体系设计

我设计了三层信号体系：

#### 信号A：IV绝对水平（判断贵贱）
```
GVZ < 13    → 强烈买入 Call（极度便宜）
GVZ 13-18   → 买入 Call（相对便宜）
GVZ 18-25   → 观望（合理定价）
GVZ 25-30   → 考虑卖出（相对昂贵）
GVZ > 30    → 强烈卖出（极度昂贵）
```

**逻辑依据**：GVZ是30天隐含波动率的年化数值，历史均值约18-20，极端值往往预示反转。

#### 信号B：IV与价格联动（判断情绪）
```
IV↑ + 价格↑ → 恐慌性买入，警惕追高风险
IV↑ + 价格↓ → 避险需求旺盛，逢低买入机会
IV↓ + 价格↑ → 健康上涨，可持有
IV↓ + 价格↓ → 恐慌出清，关注企稳信号
```

**逻辑依据**：波动率与价格的背离往往预示情绪极端点。价格上涨但IV下降，说明市场信心强；价格下跌但IV暴涨，说明恐慌抛售，可能见底。

#### 信号C：IV偏斜（待实现）
计划通过Call/Put IV差值判断市场情绪，需要更细化的期权数据。

### 2.3 数据采集策略

**数据更新时间选择**：
- 黄金期货（GC=F）北京时间交易时间：21:00-次日20:00
- 美国市场收盘：北京时间次日5:00（夏令时）
- **最佳采集时间**：北京时间 21:30（美国盘后，亚洲盘前，数据最稳定）

**对应UTC时间**：13:30

---

## 三、技术架构设计

### 3.1 架构选择：GitHub Pages + GitHub Actions

为什么选择这个组合？

| 方案 | 优点 | 缺点 | 成本 |
|------|------|------|------|
| **自建服务器** | 完全可控 | 维护复杂，需域名 | ￥300+/年 |
| **Vercel/Netlify** | 部署简单 | 数据源需要额外处理 | 免费 |
| **GitHub Pages** | 免费、自动部署、与代码仓库一体 | 静态网站 | **免费** |

**最终选择**：GitHub Pages + GitHub Actions
- **GitHub Pages**：托管静态网站，免费且自动部署
- **GitHub Actions**：定时执行Python脚本，自动采集数据并提交到仓库

### 3.2 项目结构

```
invest-site/
├── .github/workflows/
│   ├── update-gold.yml          # 黄金数据自动采集
│   └── update-rotation.yml      # 资产轮动数据采集
├── assets/css/
│   └── terminal.css             # 金融终端主题样式
├── projects/
│   ├── gold-iv/                 # 黄金IV项目
│   │   ├── index.html           # 项目页面
│   │   ├── data/
│   │   │   └── gold_data.json   # 历史数据
│   │   ├── scripts/
│   │   │   ├── fetch_data.py    # 数据采集（主）
│   │   │   ├── fetch_data_v2.py # 增强版（重试逻辑）
│   │   │   └── fetch_data_backup.py # Alpha Vantage备用
│   │   └── js/
│   │       └── gold-data.js     # 图表渲染
│   └── asset-rotation/          # 资产轮动项目
│       ├── index.html
│       ├── data/
│       └── js/
├── index.html                   # 主页
└── README.md
```

### 3.3 关键技术点

#### 1. 数据流设计
```
Yahoo Finance → Python脚本 → JSON文件 → GitHub Pages → 用户浏览器
     ↑                                              ↓
GitHub Actions (定时触发)                    Chart.js渲染图表
```

#### 2. 金融终端风格UI
为了营造专业感，我设计了金融终端风格的界面：

```css
/* 核心配色 */
--color-bg: #0d1117;          /* 深色背景 */
--color-gold: #ffd700;        /* 金色 - 黄金数据 */
--color-green: #00d084;       /* 绿色 - 上涨 */
--color-red: #ff4757;         /* 红色 - 下跌 */
--color-accent: #58a6ff;      /* 蓝色 - 强调 */

/* 字体 */
font-family: 'JetBrains Mono', monospace;  /* 等宽字体，数据对齐 */
```

#### 3. 自动化工作流
```yaml
# .github/workflows/update-gold.yml
name: Update Gold IV Data

on:
  schedule:
    - cron: '30 13 * * *'  # 每天UTC 13:30 = 北京时间21:30
  workflow_dispatch:       # 支持手动触发

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install yfinance pandas requests
      - run: cd projects/gold-iv && python scripts/fetch_data.py
      - run: git add . && git commit -m "Update data" && git push
```

---

## 四、实现过程与踩坑记录

### 4.1 Week 1：基础搭建

**Day 1-2：需求梳理与数据调研**
- 确定核心指标：金价 + GVZ波动率
- 验证数据源：Yahoo Finance API可用性测试
- 设计信号体系：参考VIX交易经验，设计GVZ分级信号

**Day 3-4：技术原型**
- 搭建GitHub Pages基础框架
- 编写第一个数据采集脚本（fetch_data.py）
- 本地测试数据获取和JSON存储

**Day 5-7：UI开发**
- 设计金融终端主题CSS
- 开发实时数据卡片组件
- 集成Chart.js绘制走势图

### 4.2 Week 2：完善与扩展

**Day 8-10：信号体系实现**
- 实现IV绝对水平信号（Signal A）
- 实现IV与价格联动信号（Signal B）
- 开发综合评分算法

**Day 11-12：第二个项目（资产轮动）**
- 设计"货币周期 × 信用周期"四象限框架
- 确定五大核心指标：30年国债收益率、股债比、房金比、金铜比、PPI-CPI剪刀差
- 开发月度数据录入界面（因为宏观数据无法自动获取）

**Day 13-14：测试与上线**
- 测试GitHub Actions定时任务
- 验证数据自动更新流程
- **踩坑**：Yahoo Finance限速问题

### 4.3 关键踩坑与解决

#### 坑1：Yahoo Finance速率限制

**现象**：
```
Error: Too Many Requests. Rate limited.
```

**原因**：
- yfinance库被大量使用，Yahoo加强了反爬虫
- 单个IP请求频率过高会被临时封禁

**解决方案**：
1. **增加重试逻辑**：指数退避 + 随机延迟
2. **User-Agent伪装**：模拟浏览器请求头
3. **备用数据源**：申请Alpha Vantage API作为备份

**代码示例**：
```python
def fetch_with_retry(ticker, max_retries=5):
    headers = {
        'User-Agent': f'Mozilla/5.0...Chrome/{random.randint(100,130)}...'
    }
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(2, 5))  # 随机延迟
            data = ticker.history(period="5d")
            if not data.empty:
                return data
        except:
            delay = 10 * (2 ** attempt) + random.uniform(1, 3)
            time.sleep(delay)  # 指数退避
    return pd.DataFrame()
```

#### 坑2：GitHub Actions时区问题

**现象**：定时任务没有按预期时间执行

**原因**：GitHub Actions使用UTC时间，需要换算

**解决**：
```yaml
# 北京时间21:30 = UTC 13:30
- cron: '30 13 * * *'
```

#### 坑3：数据格式兼容性

**现象**：JavaScript读取JSON时日期格式错误

**原因**：Python生成的ISO格式日期带时区信息，JavaScript解析不一致

**解决**：统一使用简单日期格式 `'YYYY-MM-DD'`

---

## 五、成果展示

### 5.1 网站功能

**访问地址**：https://waanng.github.io/invest-site/

**黄金IV追踪项目**：
- ✅ 实时数据卡片：金价、GVZ、涨跌幅
- ✅ 交易信号系统：A/B/C三层信号 + 综合评分
- ✅ 交互式图表：价格走势、波动率对比、相关性分析
- ✅ 历史数据表：最近30天记录

**资产轮动项目**：
- ✅ 周期定位四象限图
- ✅ 五大核心指标监测
- ✅ 触发信号提醒
- ✅ 配置建议生成
- ✅ 月度数据录入界面

### 5.2 数据示例

```json
{
  "date": "2026-03-20",
  "gold_price": 4574.9,
  "gold_change_pct": -0.56,
  "gvz": 35.25,
  "gvz_change_pct": 13.53,
  "updated_at": "2026-03-22T00:46:43.084289"
}
```

**信号解读**：
- GVZ = 35.25 > 30 → **强烈卖出信号**（IV极度昂贵）
- 价格↓ + IV↑ → **避险需求旺盛**，但IV过高不适合买入
- 综合评分：2/10（极低）→ 建议观望

---

## 六、经验总结与给读者的建议

### 6.1 什么情况下适合这个项目

**推荐**：
- 有明确的研究课题（如黄金IV、资产轮动）
- 需要长期积累历史数据
- 愿意投入时间建立系统（2周左右）
- 希望零成本运行

**不推荐**：
- 只需要临时查看数据（直接用TradingView）
- 追求实时高频数据（GitHub Actions最快5分钟一次）
- 不熟悉基础编程（需要会Python和HTML/CSS）

### 6.2 快速启动清单

如果你也想搭建类似系统，按这个顺序：

**Phase 1：验证数据可行性（1-2天）**
- [ ] 确定研究课题和核心指标
- [ ] 验证数据源可用性（Yahoo Finance/Alpha Vantage等）
- [ ] 本地测试数据采集脚本

**Phase 2：搭建基础框架（2-3天）**
- [ ] 创建GitHub仓库并启用Pages
- [ ] 设计数据存储格式（JSON）
- [ ] 开发基础UI框架

**Phase 3：实现自动化（2-3天）**
- [ ] 配置GitHub Actions定时任务
- [ ] 测试数据自动更新流程
- [ ] 添加错误处理和日志

**Phase 4：完善功能（1周+）**
- [ ] 设计并实现信号体系
- [ ] 开发可视化图表
- [ ] 添加数据导出/备份功能

### 6.3 技术选型建议

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| 静态展示 | GitHub Pages | 免费、自动部署、版本控制 |
| 简单后端 | Cloudflare Workers | 免费额度充足，可处理轻量API |
| 数据库存储 | Supabase/Firebase | 免费额度足够个人使用 |
| 定时任务 | GitHub Actions | 与代码仓库一体，易于管理 |
| 图表库 | Chart.js | 轻量、文档完善、免费 |

### 6.4 避坑指南

1. **不要频繁采集数据**：免费API都有频率限制，日线数据每天一次足够
2. **一定要做错误处理**：网络波动、API故障是常态，要有重试和备用方案
3. **数据格式要统一**：Python和JavaScript的日期/数字格式容易冲突
4. **Git提交不要太频繁**：每次采集都提交，如果失败会产生大量垃圾提交
5. **监控数据新鲜度**：在页面显示最后更新时间，超过3天提醒检查

---

## 七、后续规划

目前系统运行良好，计划未来增加：

1. **更多资产类别**：美股VIX、原油波动率OVX
2. **回测功能**：基于历史数据的策略回测
3. **邮件提醒**：重要信号触发时发送邮件通知
4. **移动端优化**：目前桌面端体验更好，需要改进移动端

---

## 结语

这个项目的核心价值不在于技术有多复杂，而在于**建立了一个可持续的投资研究基础设施**。通过自动化的数据采集和可视化的信号体系，我可以：

- **系统性记录**市场数据，积累研究素材
- **量化判断**交易时机，减少情绪干扰
- **复盘验证**交易决策，持续优化策略

如果你也有类似的投资研究需求，希望这篇文章能给你一些启发。记住：**最好的系统不是最复杂的，而是最适合你的、能持续运行的**。

---

**项目代码**：https://github.com/waanng/invest-site  
**欢迎Star和Fork**，有任何问题可以在GitHub Issues中讨论。

**联系作者**：王安 (waanng@example.com)
