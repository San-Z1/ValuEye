"""Tests for the valuation and history helpers."""

from __future__ import annotations

import json
import os
import tempfile

try:  # pragma: no cover - support both root and package test execution
    from finance_monitor import valuation as valuation_module
    from finance_monitor.insights import build_history_rows, sparkline
except ModuleNotFoundError:  # pragma: no cover
    import valuation as valuation_module
    from insights import build_history_rows, sparkline

judge_valuation = valuation_module.judge_valuation
calculate_monthly_plan = valuation_module.calculate_monthly_plan
save_history = valuation_module.save_history


class TestJudgeValuation:
    def test_none_returns_unknown(self):
        result = judge_valuation(None)
        assert result["level"] == "未知"
        assert result["signal"] == "观望"

    def test_below_undervalued(self):
        result = judge_valuation(29.9)
        assert result["level"] == "低估"
        assert result["signal"] == "买入"

    def test_exactly_at_undervalued_boundary(self):
        result = judge_valuation(30.0)
        assert result["level"] == "合理"

    def test_mid_range(self):
        result = judge_valuation(50.0)
        assert result["level"] == "合理"
        assert result["signal"] == "持有"

    def test_exactly_at_overvalued_boundary(self):
        result = judge_valuation(70.0)
        assert result["level"] == "高估"

    def test_above_overvalued(self):
        result = judge_valuation(70.1)
        assert result["level"] == "高估"
        assert result["signal"] == "观望"

    def test_zero(self):
        result = judge_valuation(0.0)
        assert result["level"] == "低估"

    def test_hundred(self):
        result = judge_valuation(100.0)
        assert result["level"] == "高估"


class TestCalculateMonthlyPlan:
    def test_none_input(self):
        plan = calculate_monthly_plan(None)
        assert plan["budget"] == 200.0
        assert "定投" in plan["action"]

    def test_low_valuation(self):
        plan = calculate_monthly_plan(20.0)
        assert "全额定投" in plan["action"]

    def test_normal_valuation(self):
        plan = calculate_monthly_plan(50.0)
        assert "正常定投" in plan["action"]

    def test_high_valuation(self):
        plan = calculate_monthly_plan(80.0)
        assert "暂停定投" in plan["action"]

    def test_budget_split(self):
        plan = calculate_monthly_plan(50.0)
        assert plan["fund_amount"] == 160.0
        assert plan["savings_amount"] == 40.0


class TestSaveHistory:
    def _make_tmp_history(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({}, handle)
        return path

    def test_basic_save(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr(valuation_module, "HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)

            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            assert len(data["沪深300"]) == 1
            assert data["沪深300"][0]["pe"] == 14.17
        finally:
            os.unlink(path)

    def test_dedup_same_day(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr(valuation_module, "HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)
            save_history("沪深300", 23.0, 14.20, 4920.0)

            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            assert len(data["沪深300"]) == 1
            assert data["沪深300"][0]["pe"] == 14.20
        finally:
            os.unlink(path)

    def test_different_indices_independent(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr(valuation_module, "HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)
            save_history("中证500", 33.2, 32.42, 8670.16)

            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            assert len(data["沪深300"]) == 1
            assert len(data["中证500"]) == 1
        finally:
            os.unlink(path)

    def test_corrupted_file_creates_backup(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{invalid json")

            monkeypatch.setattr(valuation_module, "HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)

            assert os.path.exists(path + ".bak")
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            assert len(data["沪深300"]) == 1
        finally:
            os.unlink(path)
            if os.path.exists(path + ".bak"):
                os.unlink(path + ".bak")


class TestInsights:
    def test_sparkline_constant_series(self):
        assert sparkline([1, 1, 1]) == "▅▅▅"

    def test_build_history_rows(self):
        history = {
            "沪深300": [
                {"date": "2026-05-13", "close": 4800, "pe_percentile": 24.0},
                {"date": "2026-05-14", "close": 4914.5971, "pe_percentile": 22.0},
            ]
        }
        rows = build_history_rows(history, ["沪深300"], window=7)
        assert rows[0]["name"] == "沪深300"
        assert rows[0]["trend"] == "走强"
        assert rows[0]["close_change_pct"] > 0
