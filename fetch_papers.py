import os
import re
import sys
from datetime import datetime
from serpapi import GoogleSearch

# ================= 配置区域 =================
SEARCH_QUERY = 'optimization (Muon OR Gluon OR Shampoo OR "linear minimization oracle" OR LMO)'
YEAR_LOW = datetime.now().year - 2 
YEAR_HIGH = datetime.now().year
FILE_NAME = "papers.md"
# ===========================================

def clean_text(text):
    if not text: return "N/A"
    return text.replace("\n", " ").replace("|", "｜").strip()

def load_existing_links(file_path):
    """从已有的 md 文件中提取所有链接，防止重复"""
    if not os.path.exists(file_path): 
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        return set(re.findall(r'\[查看详情\]\((https?://[^\s)]+)\)', content))

def fetch_scholar_data():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("错误: 未找到 SERPAPI_KEY")
        sys.exit(1)

    params = {
        "engine": "google_scholar",
        "q": SEARCH_QUERY,
        "as_ylo": YEAR_LOW,
        "as_yhi": YEAR_HIGH,
        "num": "30",
        "hl": "zh-CN",
        "api_key": api_key
    }
    try:
        search = GoogleSearch(params)
        return search.get_dict().get("organic_results", [])
    except Exception as e:
        print(f"请求失败: {e}")
        return []

def main():
    print(f"启动任务: {datetime.now().strftime('%Y-%m-%d')}")
    existing_links = load_existing_links(FILE_NAME)
    raw_papers = fetch_scholar_data()
    
    if not raw_papers:
        print("未发现新结果。")
        return

    processed_list = []
    for item in raw_papers:
        link = item.get("link")
        title = item.get("title", "Untitled")
        
        # 过滤广告和重复
        if not link or "[CITATION]" in title.upper() or link in existing_links:
            continue
            
        # 提取日期
        pub_info = item.get("publication_info", {}).get("summary", "")
        # date_match = re.search(r'(\d{4}[年/-]\d{1,2}[月/-]\d{1,2})', pub_info)
        # date_str = date_match.group(1) if date_match else f"{YEAR_HIGH}-01-01"

        processed_list.append({
            "date": pub_info,
            "title": clean_text(title),
            "snippet": clean_text(item.get("snippet", "No snippet available")),
            "link": link
        })

    if not processed_list:
        print("检索到的文献已在记录中。")
        return

    # 排序：由远到近（时间升序）
    processed_list.sort(key=lambda x: x['date'], reverse=False)

    # 生成 Markdown 表格行
    new_rows = [f"| {p['date']} | **{p['title']}** | {p['snippet']} | [Paper]({p['link']}) |" for p in processed_list]

    # 写入逻辑
    if not os.path.exists(FILE_NAME):
        header = f"# 文献追踪历史\n\n> 搜索词: `{SEARCH_QUERY}`\n\n| 日期 | 标题 | 摘要片段 | 链接 |\n| :--- | :--- | :--- | :--- |\n"
        content = header + "\n".join(new_rows)
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        # 追加到文件末尾
        with open(FILE_NAME, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(new_rows))
    
    print(f"更新 {len(new_rows)} 篇文献")

if __name__ == "__main__":
    main()









