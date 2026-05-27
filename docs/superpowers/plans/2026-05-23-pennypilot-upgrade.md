# PennyPilot 全面升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 PennyPilot 从 3 指数/3 基金升级为 7 指数/6 基金，新增完整前端仪表盘 + 定投模拟器 + 深浅主题切换。

**Architecture:** Python 后端抓取数据后生成 `web/data.json`，前端零依赖静态页面读取 JSON 渲染仪表盘。终端输出保持不变。

**Tech Stack:** Python (baostock, akshare, rich), HTML/CSS/JS (零依赖), SVG (图表)

---

## 文件结构

```
PennyPilot/
├── finance_monitor/
│   ├── config.py            ← 修改：扩展指数/基金/DCA 预设
│   ├── data_fetcher.py      ← 修改：新增恒生科技获取
│   ├── catalog.py           ← 修改：扩展产品库
│   ├── json_export.py       ← 新增：生成 web/data.json
│   ├── main.py              ← 修改：新增 JSON 导出步骤
│   ├── test_valuation.py    ← 修改：新增测试用例
│   ├── display.py           ← 不变
│   ├── valuation.py         ← 不变
│   ├── history.py           ← 不变
│   └── insights.py          ← 不变
├── web/
│   ├── index.html           ← 重写：6 区域仪表盘
│   ├── app.js               ← 重写：JSON 读取 + 渲染 + 模拟器
│   └── styles.css           ← 重写：CSS 变量 + 深浅主题
└── README.md                ← 更新
```

---

### Task 1: 扩展 config.py — 指数、基金、DCA 预设

**Files:**
- Modify: `finance_monitor/config.py`

**目标:** 将 3 个指数扩展到 7 个，3 只基金扩展到 5 只，新增 DCA 预设和资产类别。

- [ ] **Step 1: 扩展 INDICES 列表**

将 `config.py` 中的 `INDICES` 从 3 个扩展到 7 个：

```python
INDICES = [
    {"name": "沪深300", "code": "sh.000300", "lg_name": "沪深300"},
    {"name": "中证500", "code": "sh.000905", "lg_name": "中证500"},
    {"name": "上证50", "code": "sh.000016", "lg_name": "上证50"},
    {"name": "创业板指", "code": "sz.399006", "lg_name": "创业板指"},
    {"name": "中证1000", "code": "sh.000852", "lg_name": "中证1000"},
    {"name": "中证红利", "code": "sh.000922", "lg_name": "中证红利"},
    {"name": "恒生科技", "code": "hk:HSTECH", "lg_name": None},
]
```

注意：恒生科技的 `lg_name` 为 `None`，因为乐咕乐股不支持港股估值，`code` 使用 `hk:` 前缀标识走 akshare 路径。

- [ ] **Step 2: 扩展 FUNDS 列表**

将 `FUNDS` 从 3 只扩展到 5 只：

```python
FUNDS = [
    {"name": "天弘沪深300ETF联接A", "code": "000961", "category": "宽基核心"},
    {"name": "天弘中证500ETF联接A", "code": "000962", "category": "宽基中盘"},
    {"name": "华安黄金ETF联接A", "code": "000216", "category": "黄金对冲"},
    {"name": "天弘中证红利ETF联接A", "code": "013794", "category": "红利防守"},
    {"name": "华夏恒生科技ETF联接A", "code": "013402", "category": "港股卫星"},
]
```

- [ ] **Step 3: 新增 DCA_PRESETS 和 ASSET_CATEGORIES**

在 `config.py` 末尾新增：

```python
DCA_PRESETS = {
    "保守型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.40},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.35},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.10},
    ],
    "稳健型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.40},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.20},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.15},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "013402", "name": "华夏恒生科技ETF联接A", "ratio": 0.10},
    ],
    "成长型": [
        {"code": "000961", "name": "天弘沪深300ETF联接A", "ratio": 0.30},
        {"code": "000962", "name": "天弘中证500ETF联接A", "ratio": 0.25},
        {"code": "013794", "name": "天弘中证红利ETF联接A", "ratio": 0.15},
        {"code": "013402", "name": "华夏恒生科技ETF联接A", "ratio": 0.15},
        {"code": "000216", "name": "华安黄金ETF联接A", "ratio": 0.15},
    ],
}

ASSET_CATEGORIES = {
    "000961": "宽基核心",
    "000962": "宽基中盘",
    "000216": "黄金对冲",
    "013794": "红利防守",
    "013402": "港股卫星",
}
```

- [ ] **Step 4: 运行 Python 验证配置无语法错误**

Run: `python -c "from finance_monitor.config import INDICES, FUNDS, DCA_PRESETS; print(f'{len(INDICES)} indices, {len(FUNDS)} funds, {len(DCA_PRESETS)} presets')"`
Expected: `7 indices, 5 funds, 3 presets`

- [ ] **Step 5: 提交**

```bash
git add finance_monitor/config.py
git commit -m "feat: expand config to 7 indices, 5 funds, DCA presets"
```

---

### Task 2: 扩展 data_fetcher.py — 恒生科技获取

**Files:**
- Modify: `finance_monitor/data_fetcher.py`

**目标:** 新增 `get_hk_index_data()` 函数，通过 akshare 获取恒生科技指数行情。

- [ ] **Step 1: 新增 get_hk_index_data 函数**

在 `data_fetcher.py` 末尾新增：

```python
def get_hk_index_data() -> dict[str, Any] | None:
    """Fetch the latest Hang Seng Tech Index via akshare."""
    try:
        df = ak.stock_hk_index_daily_em(symbol="HSTECH")
        if df is None or df.empty:
            return None

        close_col = _pick_column(list(df.columns), ("收盘", "close", "收盘价"))
        date_col = _pick_column(list(df.columns), ("日期", "date", "时间"))
        if close_col is None or date_col is None:
            return None

        latest = df.iloc[-1]
        close = _to_float(latest[close_col])
        if close is None:
            return None

        change_pct = None
        if len(df) >= 2:
            prev_close = _to_float(df.iloc[-2][close_col])
            if prev_close and prev_close != 0:
                change_pct = round(((close - prev_close) / prev_close) * 100, 2)

        return {
            "close": round(close, 4),
            "change_pct": change_pct,
            "date": str(latest[date_col]),
        }
    except Exception as exc:
        print(f"  [akshare] 恒生科技指数获取失败: {exc}")
        return None
```

- [ ] **Step 2: 在 main.py 的 _fetch_all_index_data 中识别恒生科技**

打开 `finance_monitor/main.py`，修改 `_fetch_all_index_data` 函数。当 `item["code"]` 以 `hk:` 开头时，调用 `get_hk_index_data()` 而不是 `get_index_data()`：

```python
def _fetch_all_index_data() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in INDICES:
        console.print(f"  获取 [cyan]{item['name']}[/] 行情...", end=" ")
        if item["code"].startswith("hk:"):
            data = get_hk_index_data()
        else:
            data = get_index_data(item["code"])
        if data:
            data["name"] = item["name"]
            results.append(data)
            console.print("[green]OK[/]")
        else:
            console.print("[red]失败[/]")
    return results
```

同样修改 `_fetch_all_valuations`，跳过 `lg_name` 为 `None` 的指数：

```python
def _fetch_all_valuations() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in INDICES:
        if item["lg_name"] is None:
            console.print(f"  [cyan]{item['name']}[/] 估值... [dim]跳过（无PE数据）[/]")
            continue
        console.print(f"  获取 [cyan]{item['name']}[/] 估值...", end=" ")
        valuation = get_index_valuation(item["lg_name"])
        if valuation:
            valuation["name"] = item["name"]
            valuation.update(judge_valuation(valuation["pe_percentile"]))
            results.append(valuation)
            console.print("[green]OK[/]")
        else:
            console.print("[yellow]无数据[/]")
    return results
```

- [ ] **Step 3: 更新 main.py 的 import**

在 `main.py` 的 import 区域，确保 `get_hk_index_data` 被导入。在 try/except 块中添加：

```python
from .data_fetcher import (
    bs_login,
    bs_logout,
    get_fund_nav,
    get_hk_index_data,
    get_index_data,
    get_index_valuation,
)
```

以及 fallback import：

```python
from data_fetcher import (
    bs_login,
    bs_logout,
    get_fund_nav,
    get_hk_index_data,
    get_index_data,
    get_index_valuation,
)
```

- [ ] **Step 4: 运行 Python 验证无语法错误**

Run: `python -c "from finance_monitor.data_fetcher import get_hk_index_data; print('OK')"`
Expected: `OK`

- [ ] **Step 5: 提交**

```bash
git add finance_monitor/data_fetcher.py finance_monitor/main.py
git commit -m "feat: add Hang Seng Tech index via akshare"
```

---

### Task 3: 扩展 catalog.py — 新增产品选项

**Files:**
- Modify: `finance_monitor/catalog.py`

**目标:** 在 `PRODUCT_OPTIONS` 中新增恒生科技基金选项，更新 `build_student_allocation` 以支持新基金配比。

- [ ] **Step 1: 在 PRODUCT_OPTIONS 末尾新增恒生科技选项**

在 `PRODUCT_OPTIONS` 元组的最后一个元素后、闭合括号前，新增：

```python
    ProductOption(
        name="恒生科技 ETF / 联接基金",
        category="卫星配置",
        risk=5,
        liquidity="T+1/T+2",
        horizon="3年以上",
        role="港股科技龙头的地域分散仓",
        starter_tip="港股波动大，控制仓位，不追涨。",
    ),
```

- [ ] **Step 2: 运行测试验证**

Run: `python -m pytest finance_monitor/test_valuation.py::TestCatalog -v`
Expected: 所有 PASS（`product_catalog_has_risk_labels` 断言 `len(products) >= 6`，现在应该是 9）

- [ ] **Step 3: 提交**

```bash
git add finance_monitor/catalog.py
git commit -m "feat: add Hang Seng Tech to product catalog"
```

---

### Task 4: 新增 json_export.py — 生成 web/data.json

**Files:**
- Create: `finance_monitor/json_export.py`

**目标:** 创建新模块，将所有数据序列化为前端可读的 JSON 文件。

- [ ] **Step 1: 创建 json_export.py**

```python
"""Export market data to web/data.json for the frontend dashboard."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from .config import ASSET_CATEGORIES, BASE_DIR, DCA_PRESETS, MONTHLY_BUDGET
except ImportError:  # pragma: no cover
    from config import ASSET_CATEGORIES, BASE_DIR, DCA_PRESETS, MONTHLY_BUDGET

WEB_DIR = BASE_DIR.parent / "web"
DATA_FILE = WEB_DIR / "data.json"


def _build_indices(
    indices_data: list[dict[str, Any]],
    valuations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    valuation_map = {item["name"]: item for item in valuations}
    result = []
    for idx in indices_data:
        v = valuation_map.get(idx["name"], {})
        result.append({
            "name": idx["name"],
            "close": idx.get("close"),
            "change_pct": idx.get("change_pct"),
            "date": idx.get("date"),
            "pe": v.get("pe"),
            "pe_percentile": v.get("pe_percentile"),
            "level": v.get("level", "无数据"),
            "signal": v.get("signal", "观望"),
        })
    return result


def _build_funds(funds_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for fund in funds_data:
        nav = fund.get("nav")
        nav_prev = fund.get("nav_prev")
        change_pct = None
        if nav is not None and nav_prev and nav_prev != 0:
            change_pct = round(((nav - nav_prev) / nav_prev) * 100, 2)
        result.append({
            "name": fund["name"],
            "code": fund.get("code", ""),
            "nav": nav,
            "change_pct": change_pct,
            "date": fund.get("date"),
            "category": ASSET_CATEGORIES.get(fund.get("code", ""), ""),
        })
    return result


def _build_recommendation(
    risk_profile: str,
    signal: str,
    advice: str,
    avg_pe_percentile: float | None,
) -> dict[str, Any]:
    preset = DCA_PRESETS.get(risk_profile, DCA_PRESETS["稳健型"])
    budget = float(MONTHLY_BUDGET)
    allocations = [
        {
            "fund": item["name"],
            "code": item["code"],
            "ratio": item["ratio"],
            "amount": round(budget * item["ratio"], 2),
        }
        for item in preset
    ]
    return {
        "risk_profile": risk_profile,
        "signal": signal,
        "advice": advice,
        "monthly_budget": budget,
        "allocations": allocations,
    }


def export_to_json(
    indices_data: list[dict[str, Any]],
    valuations: list[dict[str, Any]],
    funds_data: list[dict[str, Any]],
    risk_profile: str,
    signal: str,
    advice: str,
    avg_pe_percentile: float | None,
) -> Path:
    """Write all market data to web/data.json and return the file path."""
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "indices": _build_indices(indices_data, valuations),
        "funds": _build_funds(funds_data),
        "recommendation": _build_recommendation(
            risk_profile, signal, advice, avg_pe_percentile,
        ),
        "market_summary": {
            "avg_pe_percentile": avg_pe_percentile,
            "overall_signal": signal,
            "overall_advice": advice,
        },
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=str(DATA_FILE.parent), suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    return DATA_FILE
```

- [ ] **Step 2: 验证无语法错误**

Run: `python -c "from finance_monitor.json_export import export_to_json; print('OK')"`
Expected: `OK`

- [ ] **Step 3: 提交**

```bash
git add finance_monitor/json_export.py
git commit -m "feat: add json_export module for frontend data"
```

---

### Task 5: 更新 main.py — 接入 JSON 导出

**Files:**
- Modify: `finance_monitor/main.py`

**目标:** 在 `_run()` 末尾调用 `export_to_json`，在终端报告后生成 `web/data.json`。

- [ ] **Step 1: 添加 import**

在 `main.py` 的 try import 块中添加：

```python
from .json_export import export_to_json
```

在 fallback import 块中添加：

```python
from json_export import export_to_json
```

- [ ] **Step 2: 修改 _summarize_market 返回 risk_profile**

修改 `_summarize_market` 函数，让它同时返回风险画像名称：

```python
def _summarize_market(valuations: list[dict[str, Any]]) -> tuple[float | None, str, str, str]:
    valid = [item for item in valuations if item.get("pe_percentile") is not None]
    if not valid:
        return None, "持有", "数据不足，建议按常规定投", "稳健型"

    avg_pe_percentile = sum(float(item["pe_percentile"]) for item in valid) / len(valid)
    overall = judge_valuation(avg_pe_percentile)
    if avg_pe_percentile < UNDERVALUED_THRESHOLD:
        risk_label = "成长型"
    elif avg_pe_percentile > OVERVALUED_THRESHOLD:
        risk_label = "保守型"
    else:
        risk_label = "稳健型"
    return avg_pe_percentile, overall["signal"], overall["advice"], risk_label
```

注意：需要在 import 中加入 `UNDERVALUED_THRESHOLD` 和 `OVERVALUED_THRESHOLD`。在 config import 行添加：

```python
from .config import FUNDS, INDICES, OVERVALUED_THRESHOLD, STUDENT_PROFILE, TREND_WINDOW, UNDERVALUED_THRESHOLD
```

以及 fallback：

```python
from config import FUNDS, INDICES, OVERVALUED_THRESHOLD, STUDENT_PROFILE, TREND_WINDOW, UNDERVALUED_THRESHOLD
```

- [ ] **Step 3: 在 _run() 末尾添加 JSON 导出**

在 `_run()` 函数的 `print_footer()` 之前，添加：

```python
    console.print("[bold]7. 生成前端数据[/]")
    try:
        json_path = export_to_json(
            indices_data, valuations, funds_data,
            risk_profile, overall_signal, overall_advice,
            avg_pe_percentile,
        )
        console.print(f"  已生成 [cyan]{json_path}[/]\n")
    except Exception as exc:
        console.print(f"  [yellow]JSON 导出失败: {exc}[/]\n")
```

同时更新 `_summarize_market` 的调用：

```python
avg_pe_percentile, overall_signal, overall_advice, risk_profile = _summarize_market(valuations)
```

- [ ] **Step 4: 验证无语法错误**

Run: `python -c "from finance_monitor.main import main; print('OK')"`
Expected: `OK`

- [ ] **Step 5: 提交**

```bash
git add finance_monitor/main.py
git commit -m "feat: integrate JSON export into main pipeline"
```

---

### Task 6: 重写 styles.css — CSS 变量 + 深浅主题

**Files:**
- Rewrite: `web/styles.css`

**目标:** 用 CSS 变量实现完整的主题系统，支持深浅切换。

- [ ] **Step 1: 创建完整的 styles.css**

```css
/* ===== Theme Variables ===== */
:root {
  --bg: #f8fafc;
  --bg-secondary: #f1f5f9;
  --card: #ffffff;
  --text: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --border-hover: #cbd5e1;
  --accent: #0284c7;
  --accent-light: #e0f2fe;
  --success: #22c55e;
  --success-bg: #f0fdf4;
  --success-border: #bbf7d0;
  --danger: #ef4444;
  --danger-bg: #fef2f2;
  --danger-border: #fecaca;
  --warning: #eab308;
  --warning-bg: #fffbeb;
  --warning-border: #fde68a;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.04);
  --radius: 8px;
  --radius-lg: 12px;
  --font: "Segoe UI", "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
}

[data-theme="dark"] {
  --bg: #0f172a;
  --bg-secondary: #1e293b;
  --card: #1e293b;
  --text: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: #334155;
  --border-hover: #475569;
  --accent: #38bdf8;
  --accent-light: #0c4a6e;
  --success: #4ade80;
  --success-bg: #052e16;
  --success-border: #166534;
  --danger: #f87171;
  --danger-bg: #450a0a;
  --danger-border: #991b1b;
  --warning: #facc15;
  --warning-bg: #422006;
  --warning-border: #854d0e;
  --shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.2);
}

/* ===== Reset ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}

/* ===== Navigation ===== */
.app-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}

.nav-brand {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--accent);
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
  list-style: none;
}

.nav-links a {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text-secondary);
  transition: background 0.2s, border-color 0.2s;
}

.theme-toggle:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* ===== Layout ===== */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.section-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--accent);
  text-transform: uppercase;
}

.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
}

/* ===== Cards ===== */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: var(--shadow-md);
}

/* ===== Grid Layouts ===== */
.index-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}

.valuation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.dca-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.simulator-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 768px) {
  .dca-grid, .simulator-grid, .bottom-grid {
    grid-template-columns: 1fr;
  }
  .nav-links { display: none; }
}

/* ===== Index Cards ===== */
.index-card {
  text-align: center;
  padding: 12px 8px;
}

.index-card .name {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.index-card .value {
  font-size: 1.1rem;
  font-weight: 700;
}

.index-card .change {
  font-size: 0.75rem;
  margin-top: 2px;
}

.change-up { color: var(--success); }
.change-down { color: var(--danger); }

/* ===== Valuation Cards ===== */
.valuation-card {
  text-align: center;
  padding: 12px;
  border-radius: var(--radius);
}

.valuation-card .name {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.valuation-card .percentile {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 2px;
}

.valuation-card .signal {
  font-size: 0.7rem;
  font-weight: 600;
  margin-bottom: 6px;
}

.valuation-bar {
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.valuation-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.val-undervalued {
  background: var(--success-bg);
  border: 1px solid var(--success-border);
}
.val-undervalued .percentile { color: #166534; }
.val-undervalued .signal { color: #166534; }
.val-undervalued .valuation-bar-fill { background: var(--success); }

.val-fair {
  background: var(--warning-bg);
  border: 1px solid var(--warning-border);
}
.val-fair .percentile { color: #854d0e; }
.val-fair .signal { color: #854d0e; }
.val-fair .valuation-bar-fill { background: var(--warning); }

.val-overvalued {
  background: var(--danger-bg);
  border: 1px solid var(--danger-border);
}
.val-overvalued .percentile { color: #991b1b; }
.val-overvalued .signal { color: #991b1b; }
.val-overvalued .valuation-bar-fill { background: var(--danger); }

.val-na {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
}
.val-na .percentile { color: var(--text-muted); }
.val-na .signal { color: var(--text-muted); }

/* ===== DCA Recommendation ===== */
.alloc-item {
  margin-bottom: 10px;
}

.alloc-item:last-child { margin-bottom: 0; }

.alloc-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3px;
  font-size: 0.85rem;
}

.alloc-header .ratio {
  font-weight: 700;
  color: var(--accent);
}

.alloc-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.alloc-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* ===== Fund Cards ===== */
.fund-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.fund-card {
  text-align: center;
  padding: 10px;
  border-radius: var(--radius);
  background: var(--bg-secondary);
}

.fund-card .name {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.fund-card .nav-value {
  font-size: 1.1rem;
  font-weight: 700;
}

.fund-card .nav-change {
  font-size: 0.75rem;
}

/* ===== Simulator ===== */
.sim-input-group {
  margin-bottom: 12px;
}

.sim-input-group label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.sim-input-group input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 1rem;
  font-weight: 600;
  background: var(--bg);
  color: var(--text);
  transition: border-color 0.2s;
}

.sim-input-group input:focus {
  outline: none;
  border-color: var(--accent);
}

.sim-result {
  background: var(--success-bg);
  border: 1px solid var(--success-border);
  border-radius: var(--radius);
  padding: 12px;
  margin-top: 12px;
}

.sim-result-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.sim-result-row:last-child { margin-bottom: 0; }

.sim-result-row .value {
  font-weight: 700;
}

.sim-result-row .positive { color: var(--success); }

.sim-chart-container {
  position: relative;
}

.sim-disclaimer {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 8px;
}

/* ===== Learning Cards ===== */
.learn-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 10px;
}

.learn-card {
  padding: 12px;
  border-radius: var(--radius);
  border-left: 3px solid var(--accent);
}

.learn-card strong {
  display: block;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.learn-card p {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* ===== Checklist ===== */
.checklist label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 0.85rem;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
}

.checklist label:last-child { border-bottom: none; }

.checklist input[type="checkbox"] {
  accent-color: var(--accent);
  width: 16px;
  height: 16px;
}

/* ===== Footer ===== */
.app-footer {
  text-align: center;
  padding: 16px 24px;
  font-size: 0.7rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
  margin-top: 32px;
}

/* ===== Data Notice ===== */
.data-notice {
  background: var(--accent-light);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 10px 14px;
  font-size: 0.8rem;
  color: var(--accent);
  margin-bottom: 16px;
  text-align: center;
}

/* ===== Responsive ===== */
@media (max-width: 480px) {
  .dashboard { padding: 12px; }
  .index-grid { grid-template-columns: repeat(2, 1fr); }
  .valuation-grid { grid-template-columns: repeat(2, 1fr); }
}
```

- [ ] **Step 2: 提交**

```bash
git add web/styles.css
git commit -m "feat: rewrite styles.css with CSS variables and theme system"
```

---

### Task 7: 重写 index.html — 6 区域仪表盘

**Files:**
- Rewrite: `web/index.html`

**目标:** 创建完整的 6 区域单页仪表盘 HTML 结构。

- [ ] **Step 1: 创建完整的 index.html**

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PennyPilot 学生理财工作台</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>

  <nav class="app-nav">
    <a class="nav-brand" href="#">PennyPilot</a>
    <ul class="nav-links">
      <li><a href="#market" class="active">市场概览</a></li>
      <li><a href="#valuation">估值分析</a></li>
      <li><a href="#dca">定投推荐</a></li>
      <li><a href="#simulator">定投模拟</a></li>
      <li><a href="#learning">理财学习</a></li>
      <li><a href="#checklist">检查清单</a></li>
    </ul>
    <button class="theme-toggle" id="themeToggle" aria-label="切换主题">🌙 深色</button>
  </nav>

  <main class="dashboard">

    <div class="data-notice" id="dataNotice" style="display:none;">
      显示的是默认示例数据。运行 <code>python -m finance_monitor.main</code> 获取最新市场数据。
    </div>

    <!-- Section 1: 市场概览 -->
    <section class="section" id="market">
      <div class="section-header">
        <span class="section-label">01 · Market</span>
        <h2 class="section-title">市场概览</h2>
      </div>
      <div class="index-grid" id="indexGrid"></div>
    </section>

    <!-- Section 2: 估值分析 -->
    <section class="section" id="valuation">
      <div class="section-header">
        <span class="section-label">02 · Valuation</span>
        <h2 class="section-title">估值分析</h2>
      </div>
      <div class="valuation-grid" id="valuationGrid"></div>
    </section>

    <!-- Section 3: 定投推荐 -->
    <section class="section" id="dca">
      <div class="section-header">
        <span class="section-label">03 · DCA</span>
        <h2 class="section-title">定投推荐组合</h2>
      </div>
      <div class="dca-grid">
        <div class="card" id="allocCard"></div>
        <div class="card" id="fundCard"></div>
      </div>
    </section>

    <!-- Section 4: 定投模拟器 -->
    <section class="section" id="simulator">
      <div class="section-header">
        <span class="section-label">04 · Simulator</span>
        <h2 class="section-title">定投收益模拟器</h2>
      </div>
      <div class="simulator-grid">
        <div class="card">
          <div class="sim-input-group">
            <label for="simMonthly">每月投入 (元)</label>
            <input type="number" id="simMonthly" min="10" step="10" value="200">
          </div>
          <div class="sim-input-group">
            <label for="simYears">定投年数</label>
            <input type="number" id="simYears" min="1" max="30" step="1" value="3">
          </div>
          <div class="sim-input-group">
            <label for="simRate">预期年化收益</label>
            <input type="number" id="simRate" min="0" max="20" step="0.5" value="7.5">
          </div>
          <div class="sim-result" id="simResult"></div>
        </div>
        <div class="card sim-chart-container">
          <svg id="simChart" viewBox="0 0 500 220" preserveAspectRatio="xMidYMid meet"></svg>
          <p class="sim-disclaimer">假设固定年化收益，实际收益受市场波动影响，仅供参考</p>
        </div>
      </div>
    </section>

    <!-- Section 5 & 6: 学习 + 清单 -->
    <div class="bottom-grid">
      <section class="section" id="learning">
        <div class="section-header">
          <span class="section-label">05 · Learning</span>
          <h2 class="section-title">理财思维训练</h2>
        </div>
        <div class="learn-grid" id="learnGrid"></div>
      </section>

      <section class="section" id="checklist">
        <div class="section-header">
          <span class="section-label">06 · Checklist</span>
          <h2 class="section-title">投资前检查清单</h2>
        </div>
        <div class="card">
          <div class="checklist">
            <label><input type="checkbox"> 这笔钱 3 个月内不会用到</label>
            <label><input type="checkbox"> 我知道产品的风险等级和赎回时间</label>
            <label><input type="checkbox"> 下跌 20% 不会影响生活费</label>
            <label><input type="checkbox"> 我已经写下买入理由和退出条件</label>
            <label><input type="checkbox"> 我了解定投需要坚持 1 年以上</label>
          </div>
        </div>
      </section>
    </div>

  </main>

  <footer class="app-footer">
    投资有风险 · 本工具用于学习和预算演练 · 不构成投资建议
  </footer>

  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 在浏览器中打开验证结构**

Run: 在浏览器中打开 `web/index.html`，验证页面结构正确（无 JS 时只显示骨架）。

- [ ] **Step 3: 提交**

```bash
git add web/index.html
git commit -m "feat: rewrite index.html as 6-section dashboard"
```

---

### Task 8: 重写 app.js — 数据加载、渲染、模拟器

**Files:**
- Rewrite: `web/app.js`

**目标:** 实现 JSON 数据加载、6 个区域的渲染逻辑、主题切换、定投模拟器。

- [ ] **Step 1: 创建完整的 app.js**

```javascript
/* ===== Default Fallback Data ===== */
const DEFAULT_DATA = {
  generated_at: null,
  indices: [
    { name: "沪深300", close: 3914.60, change_pct: 1.23, pe: 14.17, pe_percentile: 22.0, level: "低估", signal: "买入" },
    { name: "中证500", close: 5670.16, change_pct: -0.87, pe: 32.42, pe_percentile: 33.2, level: "合理", signal: "持有" },
    { name: "上证50", close: 2996.57, change_pct: 0.45, pe: 11.46, pe_percentile: 18.1, level: "低估", signal: "买入" },
    { name: "创业板指", close: 2156.00, change_pct: 0.56, pe: 35.20, pe_percentile: 15.0, level: "低估", signal: "买入" },
    { name: "中证1000", close: 6234.00, change_pct: -1.02, pe: 42.10, pe_percentile: 45.0, level: "合理", signal: "持有" },
    { name: "中证红利", close: 5812.00, change_pct: 0.18, pe: 7.80, pe_percentile: 38.0, level: "合理", signal: "持有" },
    { name: "恒生科技", close: 4521.00, change_pct: 2.10, pe: null, pe_percentile: null, level: "无数据", signal: "观望" },
  ],
  funds: [
    { name: "天弘沪深300ETF联接A", code: "000961", nav: 1.7387, change_pct: 1.23, category: "宽基核心" },
    { name: "天弘中证500ETF联接A", code: "000962", nav: 1.6939, change_pct: -0.87, category: "宽基中盘" },
    { name: "华安黄金ETF联接A", code: "000216", nav: 5.872, change_pct: 0.12, category: "黄金对冲" },
    { name: "天弘中证红利ETF联接A", code: "013794", nav: 1.2341, change_pct: 0.18, category: "红利防守" },
    { name: "华夏恒生科技ETF联接A", code: "013402", nav: 0.8912, change_pct: 2.10, category: "港股卫星" },
  ],
  recommendation: {
    risk_profile: "稳健型",
    signal: "买入",
    advice: "整体 PE 分位 24%，建议执行定投",
    monthly_budget: 200,
    allocations: [
      { fund: "天弘沪深300ETF联接A", code: "000961", ratio: 0.40, amount: 80 },
      { fund: "天弘中证500ETF联接A", code: "000962", ratio: 0.20, amount: 40 },
      { fund: "华安黄金ETF联接A", code: "000216", ratio: 0.15, amount: 30 },
      { fund: "天弘中证红利ETF联接A", code: "013794", ratio: 0.15, amount: 30 },
      { fund: "华夏恒生科技ETF联接A", code: "013402", ratio: 0.10, amount: 20 },
    ],
  },
  market_summary: { avg_pe_percentile: 24.4, overall_signal: "买入", overall_advice: "市场处于历史低估区间，适合定投买入" },
};

const LEARN_PROMPTS = [
  { title: "先问钱的用途", prompt: "这笔钱 3 个月内会不会用到？会用到就不要放进波动资产。" },
  { title: "写下买入理由", prompt: "如果不能用一句话说明为什么买，就先观察一周。" },
  { title: "看最大回撤", prompt: "想象账户短期下跌 20%，你会加仓、持有还是睡不着？" },
  { title: "分清收益来源", prompt: "货币基金靠流动性，债基吃利率和信用，权益基金吃企业盈利。" },
];

const ALLOC_COLORS = ["#0284c7", "#7c3aed", "#eab308", "#16a34a", "#dc2626"];

/* ===== Utilities ===== */
const el = (id) => document.getElementById(id);
const yuan = (v) => `${Math.round(v).toLocaleString()} 元`;
const pct = (v) => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;

/* ===== Data Loading ===== */
let appData = null;
let usingFallback = false;

async function loadData() {
  try {
    const res = await fetch("data.json");
    if (!res.ok) throw new Error("not found");
    appData = await res.json();
  } catch {
    appData = DEFAULT_DATA;
    usingFallback = true;
  }
}

/* ===== Theme ===== */
function initTheme() {
  const stored = localStorage.getItem("pp-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = stored || (prefersDark ? "dark" : "light");
  applyTheme(theme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = el("themeToggle");
  btn.textContent = theme === "dark" ? "☀️ 浅色" : "🌙 深色";
  localStorage.setItem("pp-theme", theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
}

/* ===== Section 1: Market Overview ===== */
function renderMarket() {
  const grid = el("indexGrid");
  if (!appData?.indices?.length) {
    grid.innerHTML = '<p style="color:var(--text-muted)">暂无指数数据</p>';
    return;
  }
  grid.innerHTML = appData.indices.map((item) => {
    const isUp = (item.change_pct || 0) >= 0;
    return `
      <div class="card index-card">
        <div class="name">${item.name}</div>
        <div class="value">${item.close != null ? item.close.toLocaleString() : "—"}</div>
        <div class="change ${isUp ? "change-up" : "change-down"}">${pct(item.change_pct)}</div>
      </div>`;
  }).join("");
}

/* ===== Section 2: Valuation ===== */
function renderValuation() {
  const grid = el("valuationGrid");
  if (!appData?.indices?.length) {
    grid.innerHTML = '<p style="color:var(--text-muted)">暂无估值数据</p>';
    return;
  }
  grid.innerHTML = appData.indices.map((item) => {
    const pe = item.pe_percentile;
    if (pe == null) {
      return `
        <div class="card valuation-card val-na">
          <div class="name">${item.name}</div>
          <div class="percentile">—</div>
          <div class="signal">无 PE 数据</div>
        </div>`;
    }
    const cls = pe < 30 ? "val-undervalued" : pe < 70 ? "val-fair" : "val-overvalued";
    const signalText = pe < 30 ? "低估 · 买入" : pe < 70 ? "合理 · 持有" : "高估 · 观望";
    return `
      <div class="card valuation-card ${cls}">
        <div class="name">${item.name}</div>
        <div class="percentile">${pe.toFixed(1)}%</div>
        <div class="signal">${signalText}</div>
        <div class="valuation-bar"><div class="valuation-bar-fill" style="width:${pe}%"></div></div>
      </div>`;
  }).join("");
}

/* ===== Section 3: DCA Recommendation ===== */
function renderDCA() {
  const rec = appData?.recommendation;
  if (!rec) return;

  const allocCard = el("allocCard");
  const colors = ALLOC_COLORS;
  allocCard.innerHTML = `
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">
      推荐配比 · ${rec.risk_profile || "稳健型"} · 月投 ${yuan(rec.monthly_budget || 200)}
    </div>
    ${(rec.allocations || []).map((a, i) => `
      <div class="alloc-item">
        <div class="alloc-header">
          <span>${a.fund}</span>
          <span class="ratio">${(a.ratio * 100).toFixed(0)}%</span>
        </div>
        <div class="alloc-bar">
          <div class="alloc-bar-fill" style="width:${a.ratio * 100}%;background:${colors[i % colors.length]}"></div>
        </div>
      </div>
    `).join("")}
    ${rec.advice ? `<div style="margin-top:12px;font-size:0.8rem;color:var(--text-secondary);">${rec.advice}</div>` : ""}
  `;

  const fundCard = el("fundCard");
  fundCard.innerHTML = `
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">基金实时净值</div>
    <div class="fund-grid">
      ${(appData.funds || []).map((f) => {
        const isUp = (f.change_pct || 0) >= 0;
        return `
          <div class="fund-card">
            <div class="name">${f.name}</div>
            <div class="nav-value">${f.nav != null ? f.nav.toFixed(4) : "—"}</div>
            <div class="nav-change ${isUp ? "change-up" : "change-down"}">${pct(f.change_pct)}</div>
          </div>`;
      }).join("")}
    </div>
  `;
}

/* ===== Section 4: DCA Simulator ===== */
function calcFV(pmt, years, annualRate) {
  const r = annualRate / 100 / 12;
  const n = years * 12;
  if (r === 0) return pmt * n;
  return pmt * ((Math.pow(1 + r, n) - 1) / r);
}

function renderSimulator() {
  const monthly = Math.max(0, Number(el("simMonthly").value) || 0);
  const years = Math.max(1, Number(el("simYears").value) || 1);
  const rate = Math.max(0, Number(el("simRate").value) || 0);
  const totalInvested = monthly * years * 12;
  const fv = calcFV(monthly, years, rate);
  const profit = fv - totalInvested;

  el("simResult").innerHTML = `
    <div class="sim-result-row"><span>总投入</span><span class="value">${yuan(totalInvested)}</span></div>
    <div class="sim-result-row"><span>预估市值</span><span class="value positive">${yuan(fv)}</span></div>
    <div class="sim-result-row"><span>收益</span><span class="value positive">+${yuan(profit)}</span></div>
  `;

  drawSimChart(monthly, years, rate);
}

function drawSimChart(monthly, years, rate) {
  const svg = el("simChart");
  const w = 500, h = 220;
  const pad = { top: 20, right: 20, bottom: 30, left: 50 };
  const cw = w - pad.left - pad.right;
  const ch = h - pad.top - pad.bottom;
  const months = years * 12;
  const step = Math.max(1, Math.floor(months / 60));

  const points = [];
  for (let m = 0; m <= months; m += step) {
    const invested = monthly * m;
    const fv = calcFV(monthly, m / 12, rate);
    points.push({ m, invested, fv });
  }
  if (points[points.length - 1].m !== months) {
    const invested = monthly * months;
    const fv = calcFV(monthly, years, rate);
    points.push({ m: months, invested, fv });
  }

  const maxVal = Math.max(...points.map((p) => p.fv), 1);
  const xScale = (m) => pad.left + (m / months) * cw;
  const yScale = (v) => pad.top + ch - (v / maxVal) * ch;

  let investedPath = points.map((p, i) => `${i === 0 ? "M" : "L"}${xScale(p.m).toFixed(1)},${yScale(p.invested).toFixed(1)}`).join(" ");
  let fvPath = points.map((p, i) => `${i === 0 ? "M" : "L"}${xScale(p.m).toFixed(1)},${yScale(p.fv).toFixed(1)}`).join(" ");

  const investedArea = `${investedPath} L${xScale(months).toFixed(1)},${yScale(0).toFixed(1)} L${xScale(0).toFixed(1)},${yScale(0).toFixed(1)} Z`;

  const gridLines = [0.25, 0.5, 0.75].map((f) => {
    const y = yScale(maxVal * f);
    return `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${w - pad.right}" y2="${y.toFixed(1)}" stroke="var(--border)" stroke-width="1" stroke-dasharray="4"/>`;
  }).join("");

  const yearLabels = [];
  for (let y = 1; y <= years; y++) {
    const x = xScale(y * 12);
    yearLabels.push(`<text x="${x.toFixed(1)}" y="${(h - 5).toFixed(1)}" fill="var(--text-muted)" font-size="10" text-anchor="middle">Y${y}</text>`);
  }

  const yLabels = [0, 0.25, 0.5, 0.75, 1].map((f) => {
    const v = maxVal * f;
    const y = yScale(v);
    const label = v >= 10000 ? `${(v / 10000).toFixed(1)}万` : `${Math.round(v)}`;
    return `<text x="${(pad.left - 6).toFixed(1)}" y="${(y + 3).toFixed(1)}" fill="var(--text-muted)" font-size="10" text-anchor="end">${label}</text>`;
  }).join("");

  svg.innerHTML = `
    ${gridLines}
    ${yLabels}
    ${yearLabels}
    <path d="${investedArea}" fill="var(--accent)" opacity="0.1"/>
    <path d="${investedPath}" fill="none" stroke="var(--accent)" stroke-width="2"/>
    <path d="${fvPath}" fill="none" stroke="var(--success)" stroke-width="2.5"/>
    <circle cx="${xScale(months).toFixed(1)}" cy="${yScale(calcFV(monthly, years, rate)).toFixed(1)}" r="4" fill="var(--success)"/>
    <circle cx="${xScale(months).toFixed(1)}" cy="${yScale(monthly * months).toFixed(1)}" r="4" fill="var(--accent)"/>
    <rect x="${w - 140}" y="5" width="10" height="10" fill="var(--accent)" opacity="0.3" rx="2"/>
    <text x="${w - 126}" y="14" fill="var(--text-muted)" font-size="9">投入本金</text>
    <line x1="${w - 60}" y1="10" x2="${w - 50}" y2="10" stroke="var(--success)" stroke-width="2"/>
    <text x="${w - 46}" y="14" fill="var(--text-muted)" font-size="9">预估市值</text>
  `;
}

/* ===== Section 5: Learning ===== */
function renderLearning() {
  el("learnGrid").innerHTML = LEARN_PROMPTS.map((item, i) => `
    <div class="card learn-card">
      <strong>${i + 1}. ${item.title}</strong>
      <p>${item.prompt}</p>
    </div>
  `).join("");
}

/* ===== Navigation Active State ===== */
function initNavHighlight() {
  const links = document.querySelectorAll(".nav-links a");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((link) => {
            link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
          });
        }
      });
    },
    { rootMargin: "-20% 0px -70% 0px" }
  );
  document.querySelectorAll(".section[id]").forEach((s) => observer.observe(s));
}

/* ===== Init ===== */
async function init() {
  initTheme();
  await loadData();

  if (usingFallback) {
    el("dataNotice").style.display = "block";
  }

  renderMarket();
  renderValuation();
  renderDCA();
  renderSimulator();
  renderLearning();
  initNavHighlight();

  el("themeToggle").addEventListener("click", toggleTheme);
  ["simMonthly", "simYears", "simRate"].forEach((id) => {
    el(id).addEventListener("input", renderSimulator);
  });
}

init();
```

- [ ] **Step 2: 在浏览器中打开验证**

Run: 在浏览器中打开 `web/index.html`（直接双击），验证：
- 6 个区域全部渲染
- 深浅主题切换正常
- 定投模拟器输入变化时图表实时更新
- 默认数据 fallback 显示提示条

- [ ] **Step 3: 提交**

```bash
git add web/app.js
git commit -m "feat: rewrite app.js with JSON loading, theme toggle, DCA simulator"
```

---

### Task 9: 更新测试 — 覆盖新增逻辑

**Files:**
- Modify: `finance_monitor/test_valuation.py`

**目标:** 新增测试覆盖 `json_export` 和扩展后的 catalog。

- [ ] **Step 1: 在 test_valuation.py 末尾新增 json_export 测试**

```python
try:  # pragma: no cover
    from finance_monitor.json_export import export_to_json, DATA_FILE
except ModuleNotFoundError:  # pragma: no cover
    from json_export import export_to_json, DATA_FILE


class TestJsonExport:
    def _make_sample_data(self):
        indices = [
            {"name": "沪深300", "close": 3914.6, "change_pct": 1.23, "date": "2026-05-23"},
        ]
        valuations = [
            {"name": "沪深300", "pe": 14.17, "pe_percentile": 22.0, "level": "低估", "signal": "买入"},
        ]
        funds = [
            {"name": "天弘沪深300ETF联接A", "code": "000961", "nav": 1.7387, "nav_prev": 1.7174, "date": "2026-05-23"},
        ]
        return indices, valuations, funds

    def test_export_creates_json(self, tmp_path, monkeypatch):
        indices, valuations, funds = self._make_sample_data()
        monkeypatch.setattr("finance_monitor.json_export.DATA_FILE", tmp_path / "data.json")
        path = export_to_json(indices, valuations, funds, "稳健型", "买入", "建议定投", 24.4)
        assert path.exists()

        import json
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["indices"]) == 1
        assert len(data["funds"]) == 1
        assert data["recommendation"]["risk_profile"] == "稳健型"
        assert data["market_summary"]["avg_pe_percentile"] == 24.4

    def test_export_indices_have_valuation_fields(self, tmp_path, monkeypatch):
        indices, valuations, funds = self._make_sample_data()
        monkeypatch.setattr("finance_monitor.json_export.DATA_FILE", tmp_path / "data.json")
        path = export_to_json(indices, valuations, funds, "稳健型", "买入", "建议定投", 24.4)

        import json
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        idx = data["indices"][0]
        assert idx["pe"] == 14.17
        assert idx["pe_percentile"] == 22.0
        assert idx["level"] == "低估"
```

- [ ] **Step 2: 运行所有测试**

Run: `python -m pytest finance_monitor/test_valuation.py -v`
Expected: 所有测试 PASS

- [ ] **Step 3: 提交**

```bash
git add finance_monitor/test_valuation.py
git commit -m "test: add json_export tests and update catalog assertions"
```

---

### Task 10: 集成验证 — 端到端测试

**Files:**
- 无文件修改

**目标:** 运行完整 Python 管道，验证 `web/data.json` 生成，浏览器验证前端渲染。

- [ ] **Step 1: 运行 Python 主程序**

Run: `python -m finance_monitor.main`
Expected: 终端输出 7 个指数、5 只基金的表格，最后显示"已生成 web/data.json"

- [ ] **Step 2: 验证 data.json 已生成**

Run: `python -c "import json; d=json.load(open('web/data.json')); print(f'{len(d[\"indices\"])} indices, {len(d[\"funds\"])} funds')"`
Expected: `7 indices, 5 funds`

- [ ] **Step 3: 在浏览器中打开 web/index.html**

- 验证 7 个指数行情卡片显示真实数据
- 验证估值分析区域显示 6 个指数的 PE 分位（恒生科技显示"无数据"）
- 验证定投推荐区域显示 5 只基金的配比和净值
- 验证定投模拟器输入变化时图表实时更新
- 验证深浅主题切换正常
- 验证页面底部无 "显示默认数据" 提示（因为有真实 data.json）

- [ ] **Step 4: 降级测试 — 删除 data.json 后验证 fallback**

Run: `rm web/data.json && echo "deleted"`
然后在浏览器刷新 `web/index.html`，验证：
- 显示 "显示的是默认示例数据" 提示条
- 所有 6 个区域正常渲染（使用默认数据）
- 无 JS 报错

- [ ] **Step 5: 最终提交**

```bash
git add -A
git commit -m "feat: PennyPilot full upgrade - 7 indices, 5 funds, dashboard"
```
