import os
import re
import sys
from datetime import datetime
from serpapi import GoogleSearch

# ================= 配置区域 =================
SEARCH_QUERY = 'optimization convergence (Muon OR Gluon OR Shampoo OR "linear minimization oracle" OR LMO)'
YEAR_LOW = datetime.now().year - 2
YEAR_HIGH = datetime.now().year
FILE_NAME = "papers.md"
# ===========================================

def clean_text(text):
    if not text: return "N/A"
    return text.replace("\n", " ").replace("|", "｜").strip()

def load_existing_links(file_path):
    """从已有的 md 文件中提取所有链接，防止重复记录"""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        # 匹配 Markdown 格式中的链接 [查看详情](URL)
        return set(re.findall(r'\[查看详情\]\((https?://[^\s)]+)\)', content))

def fetch_scholar_data():
    """获取数据，默认获取前20条结果"""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("错误: 未找到环境变量 SERPAPI_KEY")
        sys.exit(1)

    params = {
        "engine": "google_scholar",
        "q": SEARCH_QUERY,
        "as_ylo": YEAR_LOW,
        "as_yhi": YEAR_HIGH,
        "num": "20",  # 扩大单次检索量
        "hl": "zh-CN",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])
    except Exception as e:
        print(f"API 请求失败: {e}")
        return []

def main():
    print(f"🚀 开始增量检索: {SEARCH_QUERY}...")
    
    # 1. 加载旧数据，防止重复
    existing_links = load_existing_links(FILE_NAME)
    print(f"📁 库中已存在文献: {len(existing_links)} 篇")

    # 2. 抓取新数据
    raw_papers = fetch_scholar_data()
    if not raw_papers:
        print("💡 未发现任何结果。")
        return

    # 3. 过滤出真正的新文献
    new_rows = []
    for item in raw_papers:
        link = item.get("link")
        title = item.get("title", "Untitled")
        
        # 过滤逻辑：无链接、纯引用、图书、已存在
        if not link or "[CITATION]" in title.upper() or "[B]" in title.upper():
            continue
        if link in existing_links:
            continue
            
        # 格式化数据
        clean_title = clean_text(title)
        year = item.get("publication_info", {}).get("summary", "N/A")
        snippet = clean_text(item.get("snippet", ""))
        
        row = f"| {year} | **{clean_title}** | {snippet} | [查看详情]({link}) |"
        new_rows.append(row)

    if not new_rows:
        print("💡 检索到的文献已全部存在，无需更新。")
        return

    # 4. 组装最终内容（置顶新文献）
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    table_header = "| 发表时间/来源 | 论文题目 | 摘要摘要 | 链接 |\n| :--- | :--- | :--- | :--- |\n"
    title_section = f"# 🎓 自动文献追踪报告\n\n> **最后更新**: `{timestamp}` | **搜索词**: `{SEARCH_QUERY}`\n\n"

    if not os.path.exists(FILE_NAME):
        # 第一次创建文件
        final_content = title_section + table_header + "\n".join(new_rows)
    else:
        # 读取旧文件内容，保留表头，插入新行
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
        
        # 寻找表格开始的位置（即 | :--- | 之后的一行）
        header_index = 0
        for i, line in enumerate(old_lines):
            if "| :--- |" in line:
                header_index = i + 1
                break
        
        # 重新拼接：新的标题 + 表头 + 新行 + 旧行
        header_part = title_section + table_header
        old_rows_part = "".join(old_lines[header_index:]) if header_index > 0 else ""
        final_content = header_part + "\n".join(new_rows) + "\n" + old_rows_part

    # 5. 写入文件
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"✅ 成功! 本次新增 {len(new_rows)} 篇文献。")

if __name__ == "__main__":
    main()
    





