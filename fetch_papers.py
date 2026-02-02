import os
import re
import sys
from datetime import datetime
from serpapi import GoogleSearch

# ================= 配置区域 =================
# 建议通过环境变量设置，或在此直接修改

SEARCH_QUERY = 'optimization (Muon OR Gluon OR Shampoo OR "linear minimization oracle" OR LMO)' 
YEAR_LOW = datetime.now().year - 2  # 默认搜索去年到今年
YEAR_HIGH = datetime.now().year
FILE_NAME = "papers.md"
# ===========================================

def clean_text(text):
    """清理字符串中的换行符和特殊Markdown字符，防止破坏表格结构"""
    if not text:
        return "N/A"
    return text.replace("\n", " ").replace("|", "｜").strip()

def is_valid_result(item):
    """基础过滤逻辑：剔除无链接、纯引用、图书"""
    title = item.get("title", "").upper()
    link = item.get("link")
    
    # 过滤掉没有链接的结果
    if not link:
        return False
    # 过滤掉 Google Scholar 标记为 [CITATION] 或 [B] (Book) 的项
    if "[CITATION]" in title or "[B]" in title:
        return False
    return True

def fetch_scholar_data():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("错误: 未找到环境变量 SERPAPI_KEY")
        sys.exit(1)

    params = {
        "engine": "google_scholar",
        "q": SEARCH_QUERY,
        "as_ylo": YEAR_LOW,
        "as_yhi": YEAR_HIGH,
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

def process_to_markdown(papers):
    """核心处理逻辑：去重、过滤、排序、格式化"""
    seen_titles = set()
    final_list = []

    for item in papers:
        if not is_valid_result(item):
            continue
            
        # 简单去重逻辑：基于标题字符
        title = item.get("title")
        title_slug = re.sub(r'\W+', '', title).lower()
        if title_slug in seen_titles:
            continue
        seen_titles.add(title_slug)

        # 提取信息
        pub_info = item.get("publication_info", {}).get("summary", "N/A")
        snippet = clean_text(item.get("snippet", ""))
        link = item.get("link")

        final_list.append({
            "year": pub_info,
            "title": clean_text(title),
            "snippet": snippet,
            "link": link
        })

    # 生成 Markdown 内容
    header = f"# 自动化文献追踪报告\n\n"
    header += f"> **搜索词**: `{SEARCH_QUERY}` | **时间范围**: {YEAR_LOW}-{YEAR_HIGH} | **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    table_header = "| 发表时间/来源 | 论文题目 | 摘要摘要 | 链接 |\n| :--- | :--- | :--- | :--- |\n"
    
    rows = []
    for p in final_list:
        row = f"| {p['year']} | **{p['title']}** | {p['snippet']} | [查看详情]({p['link']}) |"
        rows.append(row)

    if not rows:
        return header + " 本次运行未检索到符合条件的文献。"
    
    return header + table_header + "\n".join(rows)

def main():
    print(f"开始检索: {SEARCH_QUERY}...")
    raw_papers = fetch_scholar_data()
    
    if not raw_papers:
        print("未发现新结果。")
        return

    md_output = process_to_markdown(raw_papers)
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(md_output)
    
    print(f" 成功! 文献已整理至 {FILE_NAME}，共 {len(raw_papers)} 项。")

if __name__ == "__main__":
    main()


    

