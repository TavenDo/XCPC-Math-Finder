import requests
import json
import os
import time

# 定义你的数据文件路径
FILE_PATH = "recent_xcpc_contests.json"

def load_existing_data():
    """读取现有的JSON文件，转为以ID为键的字典，方便去重"""
    if not os.path.exists(FILE_PATH):
        return {}
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 转成字典结构: {"CF_104869": {比赛信息}, "QOJ_1234": {比赛信息}}
            return {item["id"]: item for item in data}
    except Exception as e:
        print(f"读取旧数据失败: {e}")
        return {}

def fetch_cf_contests():
    print("正在连接 Codeforces API...")
    url = "https://codeforces.com/api/contest.list?gym=true"
    
    # 设置最大重试次数为 3 次
    for attempt in range(3):
        try:
            # 将超时时间延长到 30 秒
            response = requests.get(url, timeout=30)
            
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
                                "url": f"https://codeforces.com/gym/{contest['id']}"
                            })
                    return results
            
            print(f"CF 返回状态异常，状态码: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            print(f"第 {attempt + 1} 次请求 CF 失败: {e}")
            if attempt < 2:
                print("等待 3 秒后重试...")
                time.sleep(3) # 休息3秒再试
                
    print("CF 抓取彻底失败，请检查网络或代理设置。")
    return []

def fetch_qoj_contests():
    """
    抓取 QOJ 比赛的预留接口。
    注意：QOJ 目前没有官方 JSON API，后续可能需要用到 BeautifulSoup 库来解析网页HTML。
    这里先搭好架构，返回空列表。
    """
    print("正在获取 QOJ 数据 (功能开发中)...")
    results = []
    # 未来你写好爬虫后，添加到 results 里的格式如下：
    # results.append({
    #     "id": "QOJ_1234",
    #     "platform": "QOJ",
    #     "name": "2023 ICPC Hangzhou",
    #     "url": "https://qoj.ac/contest/1234"
    # })
    return results

def main():
    # 1. 加载旧数据 (保护你手动修改过的中文名)
    existing_dict = load_existing_data()
    print(f"本地已加载 {len(existing_dict)} 条历史记录。")

    # 2. 获取各大平台的新数据
    cf_data = fetch_cf_contests()
    qoj_data = fetch_qoj_contests()
    
    # 将所有平台抓到的数据合并到一起
    all_fetched_data = cf_data + qoj_data

    # 3. 增量去重合并 (只增不改原则)
    added_count = 0
    for item in all_fetched_data:
        contest_id = item["id"]
        # 如果这个 ID 在本地数据里找不到，说明是新比赛
        if contest_id not in existing_dict:
            existing_dict[contest_id] = item
            added_count += 1
            print(f"✨ 发现新比赛并添加: [{item['platform']}] {item['name']}")

    # 4. 判断并保存
    if added_count > 0:
        # 把字典重新剥离成列表
        final_list = list(existing_dict.values())
        # 写回文件
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        print(f"\n✅ 更新完成！本次新增了 {added_count} 场比赛。总计靶场池：{len(final_list)} 场。")
    else:
        print("\n✅ 检查完毕！当前已经是最新数据，没有发现新比赛，未做任何修改。")

if __name__ == "__main__":
    main()