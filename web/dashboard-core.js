(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.PennyPilotCore = api;
})(typeof globalThis !== "undefined" ? globalThis : window, function () {
  const SUPPORTED_SCHEMA_VERSION = 1;

  const DEFAULT_DATA = {
    schema_version: SUPPORTED_SCHEMA_VERSION,
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
      advice: "整体 PE 分位 24%，建议执行定投。",
      monthly_budget: 200,
      allocations: [
        { fund: "天弘沪深300ETF联接A", code: "000961", ratio: 0.40, amount: 80 },
        { fund: "天弘中证500ETF联接A", code: "000962", ratio: 0.20, amount: 40 },
        { fund: "华安黄金ETF联接A", code: "000216", ratio: 0.15, amount: 30 },
        { fund: "天弘中证红利ETF联接A", code: "013794", ratio: 0.15, amount: 30 },
        { fund: "华夏恒生科技ETF联接A", code: "013402", ratio: 0.10, amount: 20 },
      ],
    },
    market_summary: {
      avg_pe_percentile: 24.4,
      overall_signal: "买入",
      overall_advice: "市场处于历史低估区间，适合定投买入",
    },
  };

  const LEARN_PROMPTS = [
    { title: "先问钱的用途", prompt: "这笔钱 3 个月内会不会用到？会用到就不要放进波动资产。" },
    { title: "写下买入理由", prompt: "如果不能用一句话说明为什么买，就先观察一周。" },
    { title: "看最大回撤", prompt: "想象账户短期下跌 20%，你会加仓、持有还是睡不着？" },
    { title: "分清收益来源", prompt: "货币基金靠流动性，债基吃利率和信用，权益基金吃企业盈利。" },
  ];

  const asNumber = (value, fallback = null) => {
    const number = Number(value);
    return Number.isFinite(number) ? number : fallback;
  };

  const asArray = (value) => Array.isArray(value) ? value : [];

  const daysSince = (isoDate, now = Date.now()) => {
    if (!isoDate) return null;
    const generated = new Date(isoDate);
    if (Number.isNaN(generated.getTime())) return null;
    return Math.floor((now - generated.getTime()) / 86400000);
  };

  const formatGeneratedAt = (isoDate) => {
    if (!isoDate) return "当前为示例数据";
    const date = new Date(isoDate);
    if (Number.isNaN(date.getTime())) return "数据时间不可用";
    return `数据生成时间：${date.toLocaleString("zh-CN", { hour12: false })}`;
  };

  function validateDataShape(data) {
    if (!data || typeof data !== "object") return "数据格式为空";
    if (
      data.schema_version != null
      && data.schema_version !== SUPPORTED_SCHEMA_VERSION
    ) {
      return "数据版本不兼容";
    }
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

  function buildDataWarning(generatedAt, now = Date.now()) {
    const staleDays = daysSince(generatedAt, now);
    if (staleDays != null && staleDays > 3) {
      return `数据已超过 ${staleDays} 天未更新。建议重新运行 python -m finance_monitor.main。`;
    }
    return "";
  }

  function buildDataUrl(now = Date.now()) {
    return `data.json?v=${encodeURIComponent(String(now))}`;
  }

  function calcFV(pmt, years, annualRate) {
    const r = annualRate / 100 / 12;
    const n = years * 12;
    if (r === 0) return pmt * n;
    return pmt * ((Math.pow(1 + r, n) - 1) / r);
  }

  return {
    DEFAULT_DATA,
    LEARN_PROMPTS,
    SUPPORTED_SCHEMA_VERSION,
    asNumber,
    asArray,
    daysSince,
    formatGeneratedAt,
    validateDataShape,
    normalizeData,
    buildDataWarning,
    buildDataUrl,
    calcFV,
  };
});
