const {
  DEFAULT_DATA,
  LEARN_PROMPTS,
  validateDataShape,
  normalizeData,
  buildDataWarning,
  formatGeneratedAt,
  calcFV,
} = window.PennyPilotCore;

const ALLOC_COLORS = ["#0284c7", "#7c3aed", "#eab308", "#16a34a", "#dc2626"];

const el = (id) => document.getElementById(id);
const yuan = (value) => `${Math.round(value).toLocaleString()} 元`;
const pct = (value) => value == null ? "-" : `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;

let appData = null;
let usingFallback = false;
let dataWarning = "";

async function loadData() {
  try {
    const response = await fetch("data.json");
    if (!response.ok) throw new Error("无法读取 data.json");

    const loaded = await response.json();
    const shapeError = validateDataShape(loaded);
    if (shapeError) throw new Error(shapeError);

    appData = normalizeData(loaded);
    dataWarning = buildDataWarning(appData.generated_at);
  } catch (error) {
    appData = DEFAULT_DATA;
    usingFallback = true;
    dataWarning = `显示默认示例数据：${error.message || "数据加载失败"}。`;
  }
}

function initTheme() {
  const stored = localStorage.getItem("pp-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(stored || (prefersDark ? "dark" : "light"));
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const button = el("themeToggle");
  button.textContent = theme === "dark" ? "☀ 浅色" : "☾ 深色";
  localStorage.setItem("pp-theme", theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
}

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
        <div class="value">${item.close != null ? item.close.toLocaleString() : "-"}</div>
        <div class="change ${isUp ? "change-up" : "change-down"}">${pct(item.change_pct)}</div>
      </div>`;
  }).join("");
}

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
          <div class="percentile">-</div>
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

function renderDCA() {
  const rec = appData?.recommendation;
  if (!rec) return;

  el("allocCard").innerHTML = `
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">
      推荐配比 · ${rec.risk_profile || "稳健型"} · 月投 ${yuan(rec.monthly_budget || 200)}
    </div>
    ${(rec.allocations || []).map((item, index) => `
      <div class="alloc-item">
        <div class="alloc-header">
          <span>${item.fund}</span>
          <span class="ratio">${(item.ratio * 100).toFixed(0)}%</span>
        </div>
        <div class="alloc-bar">
          <div class="alloc-bar-fill" style="width:${item.ratio * 100}%;background:${ALLOC_COLORS[index % ALLOC_COLORS.length]}"></div>
        </div>
      </div>
    `).join("")}
    ${rec.advice ? `<div style="margin-top:12px;font-size:0.8rem;color:var(--text-secondary);">${rec.advice}</div>` : ""}
  `;

  el("fundCard").innerHTML = `
    <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:12px;">基金实时净值</div>
    <div class="fund-grid">
      ${(appData.funds || []).map((fund) => {
        const isUp = (fund.change_pct || 0) >= 0;
        return `
          <div class="fund-card">
            <div class="name">${fund.name}</div>
            <div class="nav-value">${fund.nav != null ? fund.nav.toFixed(4) : "-"}</div>
            <div class="nav-change ${isUp ? "change-up" : "change-down"}">${pct(fund.change_pct)}</div>
          </div>`;
      }).join("")}
    </div>
  `;
}

function renderSimulator() {
  const monthly = Math.max(0, Number(el("simMonthly").value) || 0);
  const years = Math.max(1, Number(el("simYears").value) || 1);
  const rate = Math.max(0, Number(el("simRate").value) || 0);
  const totalInvested = monthly * years * 12;
  const futureValue = calcFV(monthly, years, rate);
  const profit = futureValue - totalInvested;

  el("simResult").innerHTML = `
    <div class="sim-result-row"><span>总投入</span><span class="value">${yuan(totalInvested)}</span></div>
    <div class="sim-result-row"><span>预计市值</span><span class="value positive">${yuan(futureValue)}</span></div>
    <div class="sim-result-row"><span>收益</span><span class="value positive">+${yuan(profit)}</span></div>
  `;

  drawSimChart(monthly, years, rate);
}

function drawSimChart(monthly, years, rate) {
  const svg = el("simChart");
  const w = 500;
  const h = 220;
  const pad = { top: 20, right: 20, bottom: 30, left: 50 };
  const cw = w - pad.left - pad.right;
  const ch = h - pad.top - pad.bottom;
  const months = years * 12;
  const step = Math.max(1, Math.floor(months / 60));
  const points = [];

  for (let month = 0; month <= months; month += step) {
    points.push({
      month,
      invested: monthly * month,
      futureValue: calcFV(monthly, month / 12, rate),
    });
  }
  if (points[points.length - 1].month !== months) {
    points.push({
      month: months,
      invested: monthly * months,
      futureValue: calcFV(monthly, years, rate),
    });
  }

  const maxValue = Math.max(...points.map((point) => point.futureValue), 1);
  const xScale = (month) => pad.left + (month / months) * cw;
  const yScale = (value) => pad.top + ch - (value / maxValue) * ch;
  const pathFor = (key) => points
    .map((point, index) => `${index === 0 ? "M" : "L"}${xScale(point.month).toFixed(1)},${yScale(point[key]).toFixed(1)}`)
    .join(" ");

  const investedPath = pathFor("invested");
  const valuePath = pathFor("futureValue");
  const investedArea = `${investedPath} L${xScale(months).toFixed(1)},${yScale(0).toFixed(1)} L${xScale(0).toFixed(1)},${yScale(0).toFixed(1)} Z`;
  const gridLines = [0.25, 0.5, 0.75].map((factor) => {
    const y = yScale(maxValue * factor);
    return `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${w - pad.right}" y2="${y.toFixed(1)}" stroke="var(--border)" stroke-width="1" stroke-dasharray="4"/>`;
  }).join("");
  const yearLabels = Array.from({ length: years }, (_, index) => {
    const year = index + 1;
    const x = xScale(year * 12);
    return `<text x="${x.toFixed(1)}" y="${(h - 5).toFixed(1)}" fill="var(--text-muted)" font-size="10" text-anchor="middle">Y${year}</text>`;
  }).join("");
  const yLabels = [0, 0.25, 0.5, 0.75, 1].map((factor) => {
    const value = maxValue * factor;
    const y = yScale(value);
    const label = value >= 10000 ? `${(value / 10000).toFixed(1)}万` : `${Math.round(value)}`;
    return `<text x="${(pad.left - 6).toFixed(1)}" y="${(y + 3).toFixed(1)}" fill="var(--text-muted)" font-size="10" text-anchor="end">${label}</text>`;
  }).join("");

  svg.innerHTML = `
    ${gridLines}
    ${yLabels}
    ${yearLabels}
    <path d="${investedArea}" fill="var(--accent)" opacity="0.1"/>
    <path d="${investedPath}" fill="none" stroke="var(--accent)" stroke-width="2"/>
    <path d="${valuePath}" fill="none" stroke="var(--success)" stroke-width="2.5"/>
    <circle cx="${xScale(months).toFixed(1)}" cy="${yScale(calcFV(monthly, years, rate)).toFixed(1)}" r="4" fill="var(--success)"/>
    <circle cx="${xScale(months).toFixed(1)}" cy="${yScale(monthly * months).toFixed(1)}" r="4" fill="var(--accent)"/>
    <rect x="${w - 140}" y="5" width="10" height="10" fill="var(--accent)" opacity="0.3" rx="2"/>
    <text x="${w - 126}" y="14" fill="var(--text-muted)" font-size="9">投入本金</text>
    <line x1="${w - 60}" y1="10" x2="${w - 50}" y2="10" stroke="var(--success)" stroke-width="2"/>
    <text x="${w - 46}" y="14" fill="var(--text-muted)" font-size="9">预计市值</text>
  `;
}

function renderLearning() {
  el("learnGrid").innerHTML = LEARN_PROMPTS.map((item, index) => `
    <div class="card learn-card">
      <strong>${index + 1}. ${item.title}</strong>
      <p>${item.prompt}</p>
    </div>
  `).join("");
}

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
    { rootMargin: "-20% 0px -70% 0px" },
  );
  document.querySelectorAll(".section[id]").forEach((section) => observer.observe(section));
}

async function init() {
  initTheme();
  await loadData();

  if (usingFallback || dataWarning) {
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
