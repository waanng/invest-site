# 黄金波动率数据获取问题解决方案

## 问题概述

**现象**：Yahoo Finance 对 yfinance 库实施严格速率限制，导致数据获取失败  
**错误**：`Too Many Requests. Rate limited.`  
**影响**：数据已 3 天未更新（最后更新 2026-03-19）

---

## 已实施的改进

### 1. 增强版数据获取脚本
- 文件：`scripts/fetch_data_v2.py`（备用）
- 改进点：
  - 随机 User-Agent 伪装请求
  - 请求间隔增加到 2-5 秒随机延迟
  - 重试次数增至 5 次
  - 指数退避 + 随机抖动
  - 详细的日志输出

### 2. 备用数据源（Alpha Vantage）
- 文件：`scripts/fetch_data_backup.py`
- 特点：
  - 当 Yahoo Finance 失败时自动切换
  - 免费额度：25 次/天（足够使用）
  - 需要申请 API Key

### 3. 更新的 GitHub Actions
- 使用最新版 actions (v4/v5)
- 添加 pip 缓存加速
- 主数据源失败后自动切换到备用
- 添加数据文件存在性检查

---

## 快速修复步骤

### 步骤 1：替换主脚本（推荐）
```bash
cd /Users/waanng/Documents/Playground/invest-site/projects/gold-iv
mv scripts/fetch_data.py scripts/fetch_data_old.py
mv scripts/fetch_data_v2.py scripts/fetch_data.py
```

### 步骤 2：申请 Alpha Vantage API Key（备用方案）
1. 访问 https://www.alphavantage.co/support/#api-key
2. 免费注册获取 API Key
3. 在 GitHub 仓库添加 Secret：
   - 路径：Settings → Secrets and variables → Actions
   - 名称：`ALPHA_VANTAGE_API_KEY`
   - 值：你的 API Key

### 步骤 3：提交并推送
```bash
git add .
git commit -m "Fix data fetching: add retry logic, backup source, and improve GitHub Actions"
git push
```

### 步骤 4：手动触发测试
1. 进入 GitHub 仓库
2. Actions → Update Gold IV Data
3. 点击 "Run workflow"
4. 查看执行日志

---

## 技术细节

### Yahoo Finance 限制原因
- yfinance 库大量用户导致 Yahoo 服务器压力
- Yahoo 加强了反爬虫检测
- 单纯的请求延迟无法完全规避

### 解决方案对比

| 方案 | 成本 | 可靠性 | 实施难度 | 推荐度 |
|------|------|--------|----------|--------|
| 增强 yfinance | 免费 | 中 | 低 | ⭐⭐⭐⭐ |
| Alpha Vantage | 免费(25次/天) | 高 | 低 | ⭐⭐⭐⭐⭐ |
| Twelve Data | 免费(800次/天) | 高 | 低 | ⭐⭐⭐⭐⭐ |
| 付费 API | $10-50/月 | 极高 | 低 | ⭐⭐⭐ |

### Alpha Vantage 限制
- 免费版：25 API calls/day
- 足够使用（每天只需要 1-2 次请求）
- 超出限制会返回错误信息

---

## 监控建议

### 1. 设置失败通知
在 `.github/workflows/update-gold.yml` 添加：
```yaml
- name: Notify on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    slack-message: "⚠️ 黄金数据获取失败，请检查 GitHub Actions"
```

### 2. 数据新鲜度检查
在网页添加提示：
```javascript
const lastUpdate = new Date(data.updated_at);
const daysDiff = (new Date() - lastUpdate) / (1000 * 60 * 60 * 24);
if (daysDiff > 2) {
  showWarning("数据已过期，可能数据获取出现问题");
}
```

---

## 当前状态

- ✅ 重试逻辑已添加
- ✅ 备用数据源脚本已创建
- ✅ GitHub Actions 已更新
- ⏳ 等待用户决定是否：
  1. 使用增强版脚本（fetch_data_v2.py）
  2. 申请 Alpha Vantage API Key
  3. 直接提交当前改动

建议：先实施步骤 1（使用增强版脚本），如果仍有问题再申请 Alpha Vantage API Key。
