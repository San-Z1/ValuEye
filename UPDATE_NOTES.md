# 🚀 迭代更新笔记 (Update Notes)
- **✨ 核心功能升级**：新增近 7 日历史趋势展示、sparkline 走势摘要、学生资金分层、风险画像、热门理财选项地图、理财任务卡、定投模拟器，以及零构建静态前端工作台。前端现在支持 `web/data.json` schema 校验、数据过期提醒、默认示例数据兜底、无缓存刷新、理财产品地图展示和投资前准备度评分。新增 `python -m finance_monitor.main --demo-data`，可在无网络时生成课堂演示数据。
- **🛠️ 架构与代码重构**：项目主线整理为 `finance_monitor/` 包结构，拆出 `history.py`、`insights.py`、`catalog.py` 和 `json_export.py`，让主流程只负责编排。前端拆分为 `dashboard-core.js` 与 `app.js`，核心数据归一化、schema 校验和复利计算可以用 Node 独立测试。
- **🐛 细节与健壮性优化**：补充 BaoStock / akshare 获取失败时的兜底处理，历史文件损坏时自动备份，JSON 导出前强制校验数据契约，前端在数据缺失、版本不兼容或数据超过 3 天未更新时给出明确提示，并兼容旧版本地 `data.json`。测试覆盖估值边界、历史趋势、风险画像、资金分层、JSON 导出、离线演示数据和前端核心逻辑。
- **💡 架构师建议**：下一步可以把 `web/` 发布到 GitHub Pages；增加 `--export-dashboard` 或 `--offline-demo` 参数，方便课堂演示；继续扩展产品库，加入债券久期、回撤、费率、赎回规则等字段；后续可增加“理财任务卡”和“错题本式风险复盘”，让学生从看结果升级为训练决策过程。
