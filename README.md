# 🎓 自动文献追踪助手 (Scholar-Auto-Tracker)

这是一个基于 **GitHub Actions + Python + SerpApi** 实现的自动化文献监控工具。

## 🚀 自动运行机制
* **触发频率**：每周一凌晨 00:00 (UTC) 自动抓取。
* **数据来源**：Google Scholar。
* **处理逻辑**：自动去重、过滤纯引用/书籍、按相关性排序。

## 📊 最新检索结果
> [!TIP]
> 检索到的最新文献会保存在当前仓库的 [papers.md](./papers.md) 文件中。

[点击此处直接查看最新文献列表](./papers.md)

---

## 🛠️ 配置说明
如果你想修改搜索关键词，请编辑 `fetch_papers.py` 中的 `SEARCH_QUERY` 变量。
如果你想修改运行时间，请编辑 `.github/workflows/update.yml` 中的 `cron` 表达式。
