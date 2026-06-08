const assert = require("node:assert/strict");
const test = require("node:test");

const core = require("./dashboard-core.js");

test("validateDataShape accepts the supported dashboard payload contract", () => {
  const error = core.validateDataShape({
    schema_version: core.SUPPORTED_SCHEMA_VERSION,
    generated_at: "2026-06-08T10:00:00",
    indices: [],
    funds: [],
    products: [],
    recommendation: {
      risk_profile: "稳健型",
      signal: "持有",
      advice: "测试",
      monthly_budget: 200,
      allocations: [],
    },
    market_summary: {},
  });

  assert.equal(error, "");
});

test("validateDataShape rejects incompatible schema versions", () => {
  const error = core.validateDataShape({
    schema_version: 999,
    indices: [],
    funds: [],
    products: [],
    recommendation: {},
  });

  assert.equal(error, "数据版本不兼容");
});

test("validateDataShape accepts legacy payloads that omit schema_version", () => {
  const error = core.validateDataShape({
    generated_at: "2026-06-08T10:00:00",
    indices: [],
    funds: [],
    products: [
      {
        name: "货币基金",
        category: "现金管理",
        risk: 1,
        risk_label: "低风险",
        liquidity: "T+0/T+1",
        horizon: "随取随用",
        role: "备用金",
        starter_tip: "先放生活费。",
      },
    ],
    recommendation: {
      risk_profile: "稳健型",
      signal: "持有",
      advice: "测试",
      monthly_budget: 200,
      allocations: [],
    },
  });

  assert.equal(error, "");
});

test("normalizeData upgrades legacy payloads to the supported schema version", () => {
  const normalized = core.normalizeData({
    generated_at: "2026-06-08T10:00:00",
    indices: [],
    funds: [],
    products: [
      {
        name: "货币基金",
        category: "现金管理",
        risk: 1,
        risk_label: "低风险",
        liquidity: "T+0/T+1",
        horizon: "随取随用",
        role: "备用金",
        starter_tip: "先放生活费。",
      },
    ],
    recommendation: {
      risk_profile: "稳健型",
      monthly_budget: 200,
      allocations: [],
    },
  });

  assert.equal(normalized.schema_version, core.SUPPORTED_SCHEMA_VERSION);
  assert.equal(normalized.products[0].name, "货币基金");
});

test("normalizeData coerces partial numeric fields without throwing", () => {
  const normalized = core.normalizeData({
    schema_version: 1,
    generated_at: "2026-06-08T10:00:00",
    indices: [{ name: "沪深300", close: "3914.6", change_pct: "bad" }],
    funds: [{ name: "样例基金", nav: "1.2345", change_pct: "-0.5" }],
    products: [{ name: "短债基金", risk: "2", liquidity: "T+1" }],
    recommendation: {
      monthly_budget: "300",
      allocations: [{ fund: "样例基金", ratio: "0.4", amount: "120" }],
    },
    market_summary: {},
  });

  assert.equal(normalized.indices[0].close, 3914.6);
  assert.equal(normalized.indices[0].change_pct, null);
  assert.equal(normalized.funds[0].change_pct, -0.5);
  assert.equal(normalized.products[0].risk, 2);
  assert.equal(normalized.products[0].risk_label, "R2");
  assert.equal(normalized.recommendation.monthly_budget, 300);
  assert.equal(normalized.recommendation.allocations[0].amount, 120);
});

test("buildDataWarning reports stale generated data", () => {
  const now = new Date("2026-06-08T12:00:00Z").getTime();
  const warning = core.buildDataWarning("2026-06-04T11:00:00Z", now);

  assert.match(warning, /超过 4 天未更新/);
});

test("buildDataUrl appends a cache-busting query parameter", () => {
  const url = core.buildDataUrl(1780849800000);

  assert.equal(url, "data.json?v=1780849800000");
});

test("scoreChecklist classifies investment readiness", () => {
  assert.deepEqual(core.scoreChecklist(0, 5), {
    checked: 0,
    total: 5,
    ratio: 0,
    level: "准备不足",
    tone: "danger",
    message: "先补齐现金流、风险等级和退出条件，再考虑买入。",
  });
  assert.equal(core.scoreChecklist(3, 5).level, "基本准备");
  assert.equal(core.scoreChecklist(5, 5).level, "准备充分");
});

test("calcFV computes monthly compound future value", () => {
  const value = core.calcFV(200, 3, 7.5);

  assert.equal(Math.round(value), 8046);
});
