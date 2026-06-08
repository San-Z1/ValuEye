# PennyPilot

PennyPilot 是一个面向大学生和职场新人的轻量级理财学习与指数定投观察器。它抓取核心指数行情、估值分位和基金净值，生成终端报告与零构建静态工作台，帮助使用者练习预算分层、风险识别和长期定投决策。

> 免责声明：本项目仅用于学习、预算演练和投资思维训练，不构成任何投资建议。

## 功能亮点

- 跟踪沪深300、中证500、上证50、创业板指、中证1000、中证红利、恒生科技等核心指数。
- 读取指数 PE 分位，输出低估 / 合理 / 高估判断与定投信号。
- 跟踪宽基、黄金、红利、港股科技等基金净值。
- 根据风险画像生成学生可执行的月度资金分层方案。
- 提供热门理财选项地图：货币基金、银行活期、短债基金、纯债基金、宽基指数、红利低波、黄金 ETF、可转债、港股科技等。
- 保存历史快照并展示近 7 日趋势。
- 生成 `web/data.json`，供前端仪表盘读取。
- 前端工作台包含市场概览、估值分析、定投推荐、定投模拟器、理财产品地图、理财任务卡、投资前检查清单。
- 前端核心数据逻辑拆分到 `web/dashboard-core.js`，可直接用 Node 测试。
- 终端使用 `rich` 美化输出，保留脚本和模块两种运行方式。

## 运行方式

建议在项目根目录执行：

```bash
python -m finance_monitor.main
```

运行后会在终端输出市场报告，并生成或更新：

```text
web/data.json
```

离线课堂演示或网络不可用时，可以直接生成一份 schema v1 示例数据：

```bash
python -m finance_monitor.main --demo-data
```

前端可直接打开：

```text
web/index.html
```

如通过本地服务器预览，可使用任意静态服务，例如：

```bash
python -m http.server 8000
```

然后访问 `http://127.0.0.1:8000/web/`。

## 前端数据契约

`web/data.json` 当前 schema 版本为 `1`，核心结构如下：

```json
{
  "schema_version": 1,
  "generated_at": "2026-06-08T10:00:00",
  "indices": [],
  "funds": [],
  "products": [],
  "recommendation": {
    "risk_profile": "稳健型",
    "signal": "持有",
    "advice": "示例",
    "avg_pe_percentile": 24.4,
    "monthly_budget": 200,
    "allocations": []
  },
  "market_summary": {
    "avg_pe_percentile": 24.4,
    "overall_signal": "持有",
    "overall_advice": "示例"
  }
}
```

前端会校验 `schema_version`、数组字段和推荐字段；当数据超过 3 天未更新时，会显示过期提醒；当 `data.json` 不存在或格式不兼容时，会回退到内置示例数据。

## 测试

Python 单元测试：

```bash
python -m pytest -q
```

前端核心逻辑测试：

```bash
node --test web/dashboard-core.test.cjs
```

JS 语法检查：

```bash
node --check web/dashboard-core.js
node --check web/app.js
```

## 项目结构

- `finance_monitor/main.py`：主流程编排、终端报告、JSON 导出。
- `finance_monitor/demo_data.py`：离线演示数据，用于课堂展示和本地预览。
- `finance_monitor/config.py`：指数、基金、阈值和学生预算配置。
- `finance_monitor/data_fetcher.py`：BaoStock / akshare 数据获取。
- `finance_monitor/valuation.py`：估值判断和定投计划。
- `finance_monitor/json_export.py`：生成并校验 `web/data.json`。
- `finance_monitor/history.py`：历史数据持久化。
- `finance_monitor/insights.py`：趋势摘要与 sparkline。
- `finance_monitor/catalog.py`：理财选项库、风险画像和资金分层逻辑。
- `finance_monitor/display.py`：终端展示。
- `web/index.html`：静态工作台入口。
- `web/dashboard-core.js`：前端数据契约、归一化和定投计算核心。
- `web/app.js`：页面渲染和交互。
- `web/styles.css`：响应式样式与主题。
- `market_monitor.py`：旧入口兼容包装。

## 推荐定投组合示例

| 基金 | 代码 | 类型 | 稳健型配比 |
| --- | --- | --- | --- |
| 天弘沪深300ETF联接A | 000961 | 宽基核心 | 40% |
| 天弘中证500ETF联接A | 000962 | 宽基中盘 | 20% |
| 华安黄金ETF联接A | 000216 | 黄金对冲 | 15% |
| 天弘中证红利ETF联接A | 013794 | 红利防守 | 15% |
| 华夏恒生科技ETF联接A | 013402 | 港股卫星 | 10% |

## 使用原则

- 先留足 1-3 个月必要开销，再考虑波动资产。
- 不借钱投资，不用学费、房租和下月生活费投资。
- 买入前写下理由、风险、退出条件和可承受回撤。
- 定投适合长期纪律训练，不适合短期押涨跌。
- 高波动资产只能作为小比例学习仓位。
