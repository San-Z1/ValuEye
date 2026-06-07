/* ===== Default Fallback Data ===== */
const DEFAULT_DATA = {
  schema_version: 1,
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
const SUPPORTED_SCHEMA_VERSION = 1;

/* ===== Utilities ===== */
const el = (id) => document.getElementById(id);
const yuan = (v) => `${Math.round(v).toLocaleString()} 元`;
const pct = (v) => v == null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;
const asNumber = (value, fallback = null) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
};
const asArray = (value) => Array.isArray(value) ? value : [];
const daysSince = (isoDate) => {
  if (!isoDate) return null;
  const generated = new Date(isoDate);
  if (Number.isNaN(generated.getTime())) return null;
  return Math.floor((Date.now() - generated.getTime()) / 86400000);
};
const formatGeneratedAt = (isoDate) => {
  if (!isoDate) return "当前为示例数据";
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) return "数据时间不可用";
  return `数据生成时间：${date.toLocaleString("zh-CN", { hour12: false })}`;
};

/* ===== Data Loading ===== */
let appData = null;
let usingFallback = false;
let dataWarning = "";

function validateDataShape(data) {
  if (!data || typeof data !== "object") return "数据格式为空";
  if (data.schema_version !== SUPPORTED_SCHEMA_VERSION) return "数据版本不兼容";
  if (!Array.isArray(data.indices)) return "指数数据格式错误";
  if (!Array.isArray(data.funds)) return "基金数据格式错误";
  if (!data.recommendation || typeof data.recommendation !== "object") return "推荐数据格式错误";
  return "";
}

function normalizeData(data) {
  const recommendation = data.recommendation || {};
  return {
    schema_version: SUPPORTED_SCHEMA_VERSION,
    generated_at: data.generated_at || null,
    indices: asArray(data.indices).map((item) => ({
      name: item.name || "未知指数",
      close: asNumber(item.close),
      change_pct: asNumber(item.change_pct),
      pe: asNumber(item.pe),
      pe_percentile: asNumber(item.pe_percentile),
      level: item.level || "无数据",
      signal: item.signal || "观望",
    })),
    funds: asArray(data.funds).map((item) => ({
      name: item.name || "未知基金",
      code: item.code || "",
      nav: asNumber(item.nav),
      change_pct: asNumber(item.change_pct),
      category: item.category || "",
    })),
    recommendation: {
      risk_profile: recommendation.risk_profile || "稳健型",
      signal: recommendation.signal || "持有",
      advice: recommendation.advice || "",
      monthly_budget: asNumber(recommendation.monthly_budget, 200),
      allocations: asArray(recommendation.allocations).map((item) => ({
        fund: item.fund || "未命名基金",
        code: item.code || "",
        ratio: asNumber(item.ratio, 0),
        amount: asNumber(item.amount, 0),
      })),
    },
    market_summary: data.market_summary || {},
  };
}

async function loadData() {
  try {
    const res = await fetch("data.json");
    if (!res.ok) throw new Error("not found");
    const loaded = await res.json();
    const shapeError = validateDataShape(loaded);
    if (shapeError) throw new Error(shapeError);
    appData = normalizeData(loaded);
    const staleDays = daysSince(appData.generated_at);
    if (staleDays != null && staleDays > 3) {
      dataWarning = `数据已超过 ${staleDays} 天未更新。建议重新运行 python -m finance_monitor.main。`;
    }
  } catch (error) {
    appData = DEFAULT_DATA;
    usingFallback = true;
    dataWarning = `显示默认示例数据：${error.message || "无法读取 data.json"}。`;
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
  if (dataWarning) {
    el("dataNotice").textContent = dataWarning;
    el("dataNotice").style.display = "block";
  }
  el("dataTimestamp").textContent = formatGeneratedAt(appData.generated_at);

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
