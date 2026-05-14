# ValuEye - 大学生理财监控系统

一个专为大学生设计的轻量级 A 股指数监控与定投决策工具。每天自动抓取市场数据，帮你判断该买还是该等。

## 功能

- 监控沪深300、中证500、上证50 三大指数行情
- 获取 PE 估值和历史百分位，判断市场高估/低估
- 跟踪三只指数基金净值
- 根据估值水平给出买入/持有/观望建议
- 计算每月定投计划（默认预算 200 元）
- 终端美化输出，一目了然

## 安装

```bash
# 克隆项目
git clone https://github.com/San-Z1/ValuEye.git
cd ValuEye/finance_monitor

# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 测试

```bash
pip install pytest
python -m pytest finance_monitor/ -v
```

Windows 用户也可以双击 `手动查看.bat` 直接运行。

## 输出示例

```
                     ValuEye 核心指数行情
┌────────────┬─────────┬────────┬────────────┐
│ 指数       │  最新价 │ 涨跌幅 │    日期    │
├────────────┼─────────┼────────┼────────────┤
│ 沪深300    │ 4914.60 │ -1.68% │ 2026-05-14 │
│ 中证500    │ 8670.16 │ -2.78% │ 2026-05-14 │
│ 上证50     │ 2996.57 │ -1.66% │ 2026-05-14 │
└────────────┴─────────┴────────┴────────────┘

                     指数估值分析
┌────────────┬───────┬──────────┬──────────┬──────────┐
│ 指数       │    PE │ PE百分位 │ 估值水平 │ 操作建议 │
├────────────┼───────┼──────────┼──────────┼──────────┤
│ 沪深300    │ 14.17 │    22.0% │   低估   │   买入   │
│ 中证500    │ 32.42 │    33.2% │   合理   │   持有   │
│ 上证50     │ 11.46 │    18.1% │   低估   │   买入   │
└────────────┴───────┴──────────┴──────────┴──────────┘
```

## 自定义配置

编辑 `config.py`：

```python
# 修改每月预算
MONTHLY_BUDGET = 200.0

# 修改估值阈值
UNDERVALUED_THRESHOLD = 30   # 低于此值 = 低估
OVERVALUED_THRESHOLD = 70    # 高于此值 = 高估
```

## 每月操作流程

```
月初拿到生活费
    │
    ├── 40 元 → 余额宝（应急）
    │
    └── 160 元 → 看报告建议
         │
         ├── 低估/合理 → 分三份买入基金
         └── 高估     → 也放余额宝，不买
```

## 项目结构

```
ValuEye/
├── finance_monitor/
│   ├── main.py           # 入口，串联整个流程
│   ├── config.py         # 配置：指数、基金、阈值、预算
│   ├── data_fetcher.py   # 数据获取：BaoStock + akshare
│   ├── valuation.py      # 分析：估值判断 + 定投计算
│   ├── display.py        # 输出：rich 美化表格
│   ├── test_valuation.py # 核心逻辑测试
│   ├── requirements.txt  # Python 依赖
│   ├── 手动查看.bat       # 双击运行
│   ├── run_daily.bat     # 定时任务用
│   ├── setup_task.bat    # 一键设置 Windows 定时任务
│   └── 教程.md           # 完整教程（从零开始）
├── market_monitor.py     # v1 原型（已弃用）
├── LICENSE
├── README.md
└── .gitignore
```

## 技术栈

- [BaoStock](http://baostock.com/) - 免费 A 股行情数据
- [akshare](https://akshare.akfamily.xyz/) - 免费金融数据接口
- [rich](https://github.com/Textualize/rich) - 终端美化输出

## 免责声明

- 本项目仅供学习交流，不构成任何投资建议
- 投资有风险，入市需谨慎
- 过往业绩不代表未来表现

## License

MIT
