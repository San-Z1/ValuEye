"""valuation.py 核心逻辑测试"""

import json
import os
import tempfile

import pytest

# 测试前设置 config，避免依赖真实配置
os.environ.setdefault("_TEST_MODE", "1")

from valuation import judge_valuation, calculate_monthly_plan, save_history


class TestJudgeValuation:
    """judge_valuation 边界条件测试"""

    def test_none_returns_unknown(self):
        result = judge_valuation(None)
        assert result["level"] == "未知"
        assert result["signal"] == "观望"

    def test_below_undervalued(self):
        result = judge_valuation(29.9)
        assert result["level"] == "低估"
        assert result["signal"] == "买入"

    def test_exactly_at_undervalued_boundary(self):
        # 30 不算低估（< 30 才算）
        result = judge_valuation(30.0)
        assert result["level"] == "合理"

    def test_mid_range(self):
        result = judge_valuation(50.0)
        assert result["level"] == "合理"
        assert result["signal"] == "持有"

    def test_exactly_at_overvalued_boundary(self):
        # 70 属于高估（>= 70）
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
    """calculate_monthly_plan 不同场景测试"""

    def test_none_input(self):
        plan = calculate_monthly_plan(None)
        assert plan["budget"] == 200.0
        assert "正常定投" in plan["action"]

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
        assert plan["fund_amount"] == 160.0  # 200 * 0.8
        assert plan["savings_amount"] == 40.0  # 200 * 0.2


class TestSaveHistory:
    """save_history 去重与原子写入测试"""

    def _make_tmp_history(self):
        """创建临时 history 文件，返回路径"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return path

    def test_basic_save(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr("valuation.HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)

            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert len(data["沪深300"]) == 1
            assert data["沪深300"][0]["pe"] == 14.17
        finally:
            os.unlink(path)

    def test_dedup_same_day(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr("valuation.HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)
            save_history("沪深300", 23.0, 14.20, 4920.0)

            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # 同一天只保留最后一条
            assert len(data["沪深300"]) == 1
            assert data["沪深300"][0]["pe"] == 14.20
        finally:
            os.unlink(path)

    def test_different_indices_independent(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            monkeypatch.setattr("valuation.HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)
            save_history("中证500", 33.2, 32.42, 8670.16)

            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert len(data["沪深300"]) == 1
            assert len(data["中证500"]) == 1
        finally:
            os.unlink(path)

    def test_corrupted_file_creates_backup(self, monkeypatch):
        path = self._make_tmp_history()
        try:
            # 写入损坏数据
            with open(path, "w") as f:
                f.write("{invalid json")

            monkeypatch.setattr("valuation.HISTORY_FILE", path)
            save_history("沪深300", 22.0, 14.17, 4914.6)

            # 应该创建了备份
            assert os.path.exists(path + ".bak")
            # 新数据正常写入
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            assert len(data["沪深300"]) == 1
        finally:
            os.unlink(path)
            if os.path.exists(path + ".bak"):
                os.unlink(path + ".bak")
