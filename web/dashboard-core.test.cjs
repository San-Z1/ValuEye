const assert = require("node:assert/strict");
const test = require("node:test");

const core = require("./dashboard-core.js");

test("validateDataShape accepts the supported dashboard payload contract", () => {
  const error = core.validateDataShape({
    schema_version: core.SUPPORTED_SCHEMA_VERSION,
    generated_at: "2026-06-08T10:00:00",
    indices: [],
    funds: [],
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
    recommendation: {},
  });

  assert.equal(error, "数据版本不兼容");
});

test("validateDataShape accepts legacy payloads that omit schema_version", () => {
  const error = core.validateDataShape({
    generated_at: "2026-06-08T10:00:00",
    indices: [],
    funds: [],
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
    recommendation: {
      risk_profile: "稳健型",
      monthly_budget: 200,
      allocations: [],
    },
  });

  assert.equal(normalized.schema_version, core.SUPPORTED_SCHEMA_VERSION);
});

test("normalizeData coerces partial numeric fields without throwing", () => {
  const normalized = core.normalizeData({
    schema_version: 1,
    generated_at: "2026-06-08T10:00:00",
    indices: [{ name: "沪深300", close: "3914.6", change_pct: "bad" }],
    funds: [{ name: "样例基金", nav: "1.2345", change_pct: "-0.5" }],
    recommendation: {
      monthly_budget: "300",
      allocations: [{ fund: "样例基金", ratio: "0.4", amount: "120" }],
    },
    market_summary: {},
  });

  assert.equal(normalized.indices[0].close, 3914.6);
  assert.equal(normalized.indices[0].change_pct, null);
  assert.equal(normalized.funds[0].change_pct, -0.5);
  assert.equal(normalized.recommendation.monthly_budget, 300);
  assert.equal(normalized.recommendation.allocations[0].amount, 120);
});

test("buildDataWarning reports stale generated data", () => {
  const now = new Date("2026-06-08T12:00:00Z").getTime();
  const warning = core.buildDataWarning("2026-06-04T11:00:00Z", now);

  assert.match(warning, /超过 4 天未更新/);
});

test("calcFV computes monthly compound future value", () => {
  const value = core.calcFV(200, 3, 7.5);

  assert.equal(Math.round(value), 8046);
});
