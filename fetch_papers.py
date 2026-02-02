import os
import re
import sys
import time
from datetime import datetime
from serpapi import GoogleSearch
from googletrans import Translator

# ================= 配置区域 =================
SEARCH_QUERY = 'optimization (Muon OR Gluon OR Shampoo OR "linear minimization oracle" OR LMO)'
YEAR_LOW = datetime.now().year - 2
YEAR_HIGH = datetime.now().year
FILE_NAME = "papers.md"
# ===========================================

def clean_text(text):
    if not text: return "N/A"
    return text.replace("\n", " ").replace("|", "｜").strip()

def translate_to_zh(text):
    """将英文摘要翻译为中文"""
    if not text or text == "N/A":
        return "暂无摘要"
    try:
        # 实例化翻译器
        translator = Translator()
        # 尝试翻译
        result = translator.translate(text, dest='zh-cn')
        return result.text
    except Exception as e:
        print(f"翻译记录时出现小插曲: {e}")
        return "（翻译暂时不可用）"

def load_existing_links(file_path):
    """读取旧文件，提取已存在的论文链接防止重复"""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        return set(re.findall(r'\[查看详情\]\((https?://[^\s)]+)\)', content))

def fetch_scholar_data():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print("错误: 环境变量 SERPAPI_KEY 未设置")
        sys.exit(1)

    params = {
        "engine": "google_scholar",
        "q": SEARCH_QUERY,
        "as_ylo": YEAR_LOW,
        "as_yhi": YEAR_HIGH,
        "num": "5",  # 每次抓取前20条
        "hl": "zh-CN",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        return search.get_dict().get("organic_results", [])
    except Exception as e:
        print(f"SerpApi 请求失败: {e}")
        return []

def main():
    print(f"🚀 启动自动化追踪任务: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    existing_links = load_existing_links(FILE_NAME)
    raw_papers = fetch_scholar_data()
    
    if not raw_papers:
        print("💡 未检索到新内容。")
        return

    new_rows = []
    for item in raw_papers:
        link = item.get("link")
        title = item.get("title", "Untitled")
        
        # 基础过滤
        if not link or "[CITATION]" in title.upper() or "[B]" in title.upper():
            continue
        # 增量去重
        if link in existing_links:
            continue
            
        print(f"📝 正在处理新文献: {title[:50]}...")
        
        # 获取并翻译摘要
        snippet_en = item.get("snippet", "")
        snippet_zh = translate_to_zh(snippet_en)
        
        # 格式化数据（支持 Markdown 换行排版）
        clean_title = clean_text(title)
        year_info = item.get("publication_info", {}).get("summary", "N/A")
        
        # 排版优化：中文在前，英文在后并缩小
        combined_snippet = f"{clean_text(snippet_zh)}<br><small>原文: {clean_text(snippet_en)}</small>"
        
        row = f"| {year_info} | **{clean_title}** | {combined_snippet} | [查看详情]({link}) |"
        new_rows.append(row)
        
        # 稍微暂停防止翻译接口请求过快
        time.sleep(0.5)

    if not new_rows:
        print("💡 检索到的文献库中均已存在。")
        return

    # 构建文件内容
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    table_header = "| 发表时间/来源 | 论文题目 | 摘要 (中/英) | 链接 |\n| :--- | :--- | :--- | :--- |\n"
    title_section = f"# 🎓 自动文献追踪报告\n\n> 最后更新: `{timestamp}` | 搜索词: `{SEARCH_QUERY}`\n\n"

    if not os.path.exists(FILE_NAME):
        final_content = title_section + table_header + "\n".join(new_rows)
    else:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            old_lines = f.readlines()
        
        # 定位表格内容开始的行
        header_index = 0
        for i, line in enumerate(old_lines):
            if "| :--- |" in line:
                header_index = i + 1
                break
        
        old_rows_part = "".join(old_lines[header_index:]) if header_index > 0 else ""
        final_content = title_section + table_header + "\n".join(new_rows) + "\n" + old_rows_part

    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"✨ 任务完成! 本次新增 {len(new_rows)} 篇文献。")

if __name__ == "__main__":
    main()

    




