import requests
import json
import os
import time
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone

FILE_PATH = "recent_xcpc_contests.json"

def load_existing_data():
    if not os.path.exists(FILE_PATH):
        return {}
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["id"]: item for item in data}
    except Exception as e:
        print(f"读取旧数据失败: {e}")
        return {}

def fetch_cf_contests():
    print("🌍 正在连接 Codeforces API...")
    url = "https://codeforces.com/api/contest.list?gym=true"
    
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    results = []
                    for contest in data["result"]:
                        name = contest.get("name", "")
                        is_xcpc = "ICPC" in name or "CCPC" in name
                        is_recent = any(year in name for year in ["2023", "2024", "2025", "2026"])
                        
                        if is_xcpc and is_recent:
                            results.append({
                                "id": f"CF_{contest['id']}",
                                "platform": "Codeforces",
                                "name": name,
                                "url": f"https://codeforces.com/gym/{contest['id']}",
                                "timestamp": contest.get("startTimeSeconds", 0),
                                "duration": contest.get("durationSeconds", 0)
                            })
                    return results
        except requests.exceptions.RequestException as e:
            print(f"⚠️ 第 {attempt + 1} 次请求 CF 失败: {e}")
            time.sleep(3)
            
    print("❌ CF 抓取彻底失败。")
    return []

def fetch_qoj_contests():
    print("🌍 正在解析 QOJ 网页数据并推算时间戳...")
    url = "https://qoj.ac/contests"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: 
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # 🌟 状态初始化：默认第一个没有年份的比赛为 2026 年
        current_year = 2026
        
        for link in soup.find_all('a'):
            href = link.get('href', '')
            name = link.text.strip()
            
            if href.startswith('/contest/') and any(kw in name for kw in ["ICPC", "CCPC", "Universal Cup"]):
                raw_id = href.split('/')[-1]
                
                # 🌟 正则表达式：寻找名称中类似 2023, 2024 这样的四位年份
                year_match = re.search(r'(20\d{2})', name)
                
                if year_match:
                    # 如果找到了年份，更新当前的状态记忆
                    current_year = int(year_match.group(1))
                # 如果没找到，current_year 就会自然继承上一次循环的年份（或者初始的 2026）
                
                # 🌟 将推算出的年份的 1月1日 转换为标准时间戳 (UTC)
                dt = datetime(current_year, 1, 1, tzinfo=timezone.utc)
                timestamp = int(dt.timestamp())
                
                results.append({
                    "id": f"QOJ_{raw_id}",
                    "platform": "QOJ",
                    "name": name,
                    "url": f"https://qoj.ac{href}",
                    "timestamp": timestamp,  # 注入动态生成的智能时间戳
                    "duration": 18000
                })
                
        # 去重并返回
        return list({item['id']: item for item in results}.values())
        
    except Exception as e:
        print(f"❌ QOJ 抓取异常: {e}")
        return []

def main():
    existing_dict = load_existing_data()
    print(f"📦 本地已加载 {len(existing_dict)} 条历史记录。")

    all_fetched_data = fetch_cf_contests() + fetch_qoj_contests()
    
    added_count = 0
    for item in all_fetched_data:
        contest_id = item["id"]
        if contest_id not in existing_dict:
            existing_dict[contest_id] = item
            added_count += 1
            print(f"✨ 新增: [{item['platform']}] {item['name']}")

    if added_count > 0:
        final_list = list(existing_dict.values())
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        print(f"\n✅ 更新完成！新增 {added_count} 场，总计：{len(final_list)} 场。")
    else:
        print("\n✅ 已经是最新数据，保护手动修改内容，未做任何覆写。")

if __name__ == "__main__":
    main()