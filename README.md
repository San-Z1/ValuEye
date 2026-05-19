# ValuEye

一个面向大学生的轻量级指数定投观察器。它会抓取核心指数行情、估值分位、基金净值，并给出本月定投建议。

## 功能

- 跟踪沪深300、中证500、上证50
- 读取指数 PE 分位并输出低估 / 合理 / 高估判断
- 跟踪三只宽基 ETF 联接基金净值
- 保存历史快照并显示近 7 日趋势
- 生成本月预算拆分和操作建议
- 终端使用 `rich` 美化输出

## 运行

推荐从仓库根目录执行：

```bash
python -m finance_monitor.main
```

也可以直接运行旧入口，兼容脚本会转到新的主程序。

## 测试

```bash
python -m pytest -q
```

## 项目结构

- `finance_monitor/main.py`：主流程编排
- `finance_monitor/data_fetcher.py`：BaoStock / akshare 数据获取
- `finance_monitor/valuation.py`：估值判断与定投方案
- `finance_monitor/history.py`：历史数据持久化
- `finance_monitor/insights.py`：趋势摘要与 sparkline
- `finance_monitor/display.py`：终端展示
- `market_monitor.py`：旧入口兼容包装

## 说明

- `finance_monitor/history.json` 保存运行时数据，请当作真实状态文件看待
- 投资有风险，以上仅供学习交流，不构成投资建议
