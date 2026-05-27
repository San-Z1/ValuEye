# PennyPilot

一个面向大学生和职场新人的轻量级理财学习与指数定投观察器。它会抓取核心指数行情、估值分位、基金净值，给出定投建议，并提供可直接打开的前端理财工作台。

## 功能

- 跟踪沪深300、中证500、上证50、创业板指、中证1000、中证红利、恒生科技 7 大指数
- 读取指数 PE 分位并输出低估 / 合理 / 高估判断
- 跟踪 5 只推荐定投基金净值（宽基、黄金、红利、港股）
- 根据风险画像（保守/稳健/成长）自动推荐定投配比
- 保存历史快照并显示近 7 日趋势
- 生成 `web/data.json` 供前端读取
- 前端仪表盘包含市场概览、估值分析、定投推荐、定投模拟器、理财学习、检查清单
- 深浅主题切换，响应式布局
- 终端使用 `rich` 美化输出
- 静态前端无需构建，可直接打开 `web/index.html`

## 推荐定投组合

| 基金 | 代码 | 类型 | 稳健型配比 |
|------|------|------|-----------|
| 天弘沪深300ETF联接A | 000961 | 宽基核心 | 40% |
| 天弘中证500ETF联接A | 000962 | 宽基中盘 | 20% |
| 华安黄金ETF联接A | 000216 | 黄金对冲 | 15% |
| 天弘中证红利ETF联接A | 013794 | 红利防守 | 15% |
| 华夏恒生科技ETF联接A | 013402 | 港股卫星 | 10% |

## 运行

推荐从仓库根目录执行：

```bash
python -m finance_monitor.main
```

运行后会自动在终端输出报告，并生成 `web/data.json` 供前端读取。

## 前端工作台

直接打开：

```text
web/index.html
```

工作台包含：
- 市场概览：7 大指数实时行情卡片
- 估值分析：PE 分位可视化（绿/黄/红三色 + 进度条）
- 定投推荐：5 只基金配比 + 实时净值
- 定投模拟器：复利计算器 + 资产增长曲线
- 理财学习：思维训练卡片
- 检查清单：投资前自检

支持深浅主题切换，零依赖可直接打开，适合部署到 GitHub Pages。

## 测试

```bash
python -m pytest -q
```

## 项目结构

- `finance_monitor/main.py`：主流程编排 + JSON 导出
- `finance_monitor/config.py`：指数/基金/阈值/DCA 预设配置
- `finance_monitor/data_fetcher.py`：BaoStock / akshare 数据获取（含恒生科技）
- `finance_monitor/valuation.py`：估值判断与定投方案
- `finance_monitor/json_export.py`：生成 web/data.json
- `finance_monitor/history.py`：历史数据持久化
- `finance_monitor/insights.py`：趋势摘要与 sparkline
- `finance_monitor/catalog.py`：理财选项库、风险画像、资金分层逻辑
- `finance_monitor/display.py`：终端展示
- `web/`：前端仪表盘（index.html + app.js + styles.css）
- `market_monitor.py`：旧入口兼容包装

## 说明

- `finance_monitor/history.json` 保存运行时数据，请当作真实状态文件看待
- 投资有风险，以上仅供学习交流，不构成投资建议
