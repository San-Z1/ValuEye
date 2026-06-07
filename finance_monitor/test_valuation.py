"""Tests for the valuation and history helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

try:  # pragma: no cover - support both root and package test execution
    from finance_monitor.catalog import (
        build_student_allocation,
        classify_risk_score,
        product_catalog,
    )
    from finance_monitor.demo_data import build_demo_dashboard_data
    from finance_monitor import main as main_module
    from finance_monitor import valuation as valuation_module
    from finance_monitor.insights import build_history_rows, sparkline
    from finance_monitor.json_export import DATA_FILE, export_to_json, validate_dashboard_payload
except ModuleNotFoundError:  # pragma: no cover
    from catalog import build_student_allocation, classify_risk_score, product_catalog
    from demo_data import build_demo_dashboard_data
    import main as main_module
    import valuation as valuation_module
    from insights import build_history_rows, sparkline
    from json_export import DATA_FILE, export_to_json, validate_dashboard_payload

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


class TestCatalog:
    def test_risk_score_classification(self):
        assert classify_risk_score(20)["profile"] == "保守型"
        assert classify_risk_score(45)["profile"] == "稳健型"
        assert classify_risk_score(80)["profile"] == "成长型"

    def test_student_allocation_uses_surplus(self):
        plan = build_student_allocation(1200, 900, 45)
        assert plan["monthly_surplus"] == 300
        assert sum(item["amount"] for item in plan["allocations"]) == 300
        assert "不借钱投资" in plan["guardrail"]

    def test_product_catalog_has_risk_labels(self):
        products = product_catalog()
        assert len(products) >= 6
        assert all("risk_label" in item for item in products)


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
        assert data["schema_version"] == 1
        assert data["recommendation"]["risk_profile"] == "稳健型"
        assert data["recommendation"]["avg_pe_percentile"] == 24.4
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

    def test_validate_dashboard_payload_rejects_missing_fields(self):
        with pytest.raises(ValueError, match="missing fields"):
            validate_dashboard_payload({"schema_version": 1})

    def test_validate_dashboard_payload_rejects_bad_schema_version(self):
        with pytest.raises(ValueError, match="unsupported schema_version"):
            validate_dashboard_payload({
                "schema_version": 999,
                "generated_at": "2026-05-23T10:00:00",
                "indices": [],
                "funds": [],
                "recommendation": {
                    "risk_profile": "稳健型",
                    "signal": "持有",
                    "advice": "测试",
                    "monthly_budget": 200,
                    "allocations": [],
                },
                "market_summary": {},
            })


class TestDemoData:
    def test_demo_dashboard_data_matches_export_schema(self):
        data = build_demo_dashboard_data()
        validate_dashboard_payload(data)

        assert data["schema_version"] == 1
        assert len(data["indices"]) == 7
        assert len(data["funds"]) == 5
        assert data["indices"][0]["name"] == "沪深300"
        assert data["recommendation"]["risk_profile"] == "稳健型"
        assert data["recommendation"]["allocations"][0]["amount"] > 0

    def test_main_demo_data_mode_writes_dashboard_json(self, tmp_path, monkeypatch):
        output = tmp_path / "data.json"
        monkeypatch.setattr(main_module, "DATA_FILE", output)
        monkeypatch.setattr(main_module.sys, "argv", ["finance_monitor.main", "--demo-data"])

        exit_code = main_module.main()

        assert exit_code == 0
        assert Path(output).exists()
        with open(output, encoding="utf-8") as handle:
            data = json.load(handle)
        assert data["schema_version"] == 1
        assert data["indices"][0]["name"] == "沪深300"
