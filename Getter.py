import requests
import json

def fetch_xcpc_contests():
    print("正在连接 Codeforces API...")
    # CF Gym 比赛列表的官方 API
    url = "https://codeforces.com/api/contest.list?gym=true"
    
    # 发送网络请求获取数据
    response = requests.get(url)
    
    # 检查网络请求是否成功 (状态码 200 表示成功)
    if response.status_code != 200:
        print("请求失败，请检查网络（可能是国内访问 CF 不稳定，可以尝试开代理）")
        return

    # 将获取到的文本转换为 Python 的字典（JSON格式）
    data = response.json()
    
    if data["status"] != "OK":
        print("API 返回数据异常")
        return

    all_contests = data["result"]
    xcpc_contests = []
    
    print(f"成功获取到 {len(all_contests)} 场 Gym 比赛，正在筛选...")

    # 遍历所有比赛，进行规则筛选
    for contest in all_contests:
        name = contest.get("name", "")
        # CF 里的 startTimeSeconds 是时间戳，我们先简单用比赛名称中的年份来过滤
        # 寻找名称中包含 ICPC 或 CCPC，并且包含近三年年份的比赛
        is_xcpc = "ICPC" in name or "CCPC" in name
        is_recent = "2023" in name or "2024" in name or "2025" in name or "2026" in name
        
        if is_xcpc and is_recent:
            xcpc_contests.append({
                "id": contest["id"],
                "name": name,
                "url": f"https://codeforces.com/gym/{contest['id']}"
            })

    # 将筛选后的结果保存到本地的 JSON 文件中
    with open("recent_xcpc_contests.json", "w", encoding="utf-8") as f:
        json.dump(xcpc_contests, f, ensure_ascii=False, indent=4)
        
    print(f"筛选完成！共找到 {len(xcpc_contests)} 场 XCPC 比赛，已保存到 recent_xcpc_contests.json")

# 运行函数
if __name__ == "__main__":
    fetch_xcpc_contests()