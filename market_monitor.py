#!/usr/bin/env python3
"""
大学生理财助手 - 市场监控脚本
功能：监控A股核心指数估值，提供定投建议
作者：Claude Code
版本：1.0.0
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import time
import sys

class MarketMonitor:
    def __init__(self):
        self.indices = {
            "沪深300": "000300.SH",
            "科创50": "000688.SH",
            "中证500": "000905.SH"
        }

        # 基金配置 - 更适合大学生的选择
        self.funds = [
            {"name": "华夏沪深300ETF", "code": "510330", "nav": 4.256, "pe_percentile": 35, "min_investment": 10},
            {"name": "易方达中证500ETF", "code": "510580", "nav": 2.893, "pe_percentile": 28, "min_investment": 10},
            {"name": "南方科创50ETF", "code": "588080", "nav": 1.456, "pe_percentile": 65, "min_investment": 10}
        ]

    def get_market_data(self) -> Dict:
        """获取市场数据 - 使用Yahoo Finance API"""
        data = {}

        print("🔍 正在获取市场数据...")

        for name, code in self.indices.items():
            try:
                # 这里使用Yahoo Finance作为示例
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    result = response.json()
                    if 'chart' in result and 'result' in result['chart']:
                        meta = result['chart']['result'][0]['meta']
                        data[name] = {
                            'current_price': meta['regularMarketPrice'],
                            'previous_close': meta['previousClose'],
                            'change_percent': ((meta['regularMarketPrice'] - meta['previousClose']) / meta['previousClose']) * 100
                        }
                        print(f"✅ 成功获取{name}数据")
                else:
                    print(f"❌ 获取{name}数据失败，状态码：{response.status_code}")

            except Exception as e:
                print(f"❌ 获取{name}数据失败: {e}")

        return data

    def generate_investment_advice(self, pe_percentile: float) -> str:
        """生成投资建议"""
        if pe_percentile < 20:
            return "🟢 强烈建议买入 - 市场处于历史低估区域"
        elif pe_percentile < 40:
            return "🟡 建议定投 - 市场估值合理偏低"
        elif pe_percentile < 60:
            return "🟠 继续持有 - 市场估值适中"
        elif pe_percentile < 80:
            return "🔴 谨慎操作 - 市场估值偏高"
        else:
            return "⚫ 建议止盈 - 市场处于高估区域"

    def calculate_monthly_investment(self, monthly_budget: float = 200.0) -> Dict:
        """计算每月投资分配"""
        # 80%定投 + 20%余额宝策略
        fund_allocation = monthly_budget * 0.8
        balance_baby = monthly_budget * 0.2

        # 分配到不同基金
        fund_amount = fund_allocation / len(self.funds)

        return {
            "总预算": monthly_budget,
            "基金投资总额": fund_allocation,
            "余额宝储备": balance_baby,
            "单只基金金额": fund_amount,
            "建议操作": f"每月定投{len(self.funds)}只基金，每只{fund_amount:.2f}元"
        }

    def print_market_report(self):
        """打印市场报告"""
        print("\n" + "🌟" * 30)
        print(f"📊 大学生理财市场晨报 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("🌟" * 30)

        # 获取指数数据
        market_data = self.get_market_data()

        print("\n【📈 核心指数表现】")
        print("-" * 50)
        if market_data:
            for name, data in market_data.items():
                change_emoji = "📈" if data['change_percent'] > 0 else "📉"
                print(f"{name:12} | 现价: {data['current_price']:8.2f} | "
                      f"{change_emoji} {data['change_percent']:+6.2f}%")
        else:
            print("⚠️  今日市场数据获取失败，使用模拟数据")
            # 模拟数据
            print("沪深300      | 现价:  3985.23 | 📈  +1.25%")
            print("科创50       | 现价:  1056.78 | 📉  -0.85%")
            print("中证500      | 现价:  6123.45 | 📈  +0.62%")

        # 获取基金数据
        print("\n【🎯 基金估值分析】")
        print("-" * 70)
        print(f"{'基金名称':15} {'净值':>8} {'PE分位':>8} {'投资建议':>25}")
        print("-" * 70)

        for fund in self.funds:
            advice = self.generate_investment_advice(fund['pe_percentile'])
            print(f"{fund['name']:15} {fund['nav']:8.3f} "
                  f"{fund['pe_percentile']:8.1f}% {advice:>25}")

        # 投资分配建议
        investment_plan = self.calculate_monthly_investment()

        print("\n【💰 本月投资计划】")
        print("-" * 50)
        print(f"每月总预算: {investment_plan['总预算']:.2f}元")
        print(f"基金投资: {investment_plan['基金投资总额']:.2f}元")
        print(f"余额宝储备: {investment_plan['余额宝储备']:.2f}元")
        print(f"操作建议: {investment_plan['建议操作']}")

        # 整体市场建议
        print("\n【📋 今日操作建议】")
        print("-" * 50)
        avg_pe_percentile = sum(f['pe_percentile'] for f in self.funds) / len(self.funds)
        overall_advice = self.generate_investment_advice(avg_pe_percentile)
        print(f"整体市场PE分位: {avg_pe_percentile:.1f}%")
        print(f"市场状态: {overall_advice}")

        # 具体操作建议
        if "建议买入" in overall_advice or "建议定投" in overall_advice:
            print("\n✅ 建议执行本月定投计划")
            print("📝 操作步骤：")
            print("  1. 将40元转入余额宝")
            print("  2. 用160元进行基金定投")
            print("  3. 每只基金定投约53元")
        else:
            print("\n⏸️ 建议暂停定投，观望为主")
            print("📝 操作步骤：")
            print("  1. 将200元全部转入余额宝")
            print("  2. 等待更好的入场时机")
            print("  3. 继续学习理财知识")

        print("\n" + "🌟" * 30)
        print("💡 温馨提示：")
        print("  • 投资有风险，决策需谨慎")
        print("  • 历史表现不代表未来收益")
        print("  • 坚持定投，无视短期波动")
        print("  • 建议长期持有3-5年")
        print("🌟" * 30 + "\n")

def main():
    """主函数"""
    print("🚀 启动大学生理财监控系统...")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        monitor = MarketMonitor()
        monitor.print_market_report()

        print("\n✅ 理财监控完成！")
        print("="*50)

    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        print("请检查网络连接或API配置")
        sys.exit(1)

if __name__ == "__main__":
    main()