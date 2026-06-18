import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
import re

# 强制绑定脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "recent_xcpc_contests.json")

PLATFORMS = ["Codeforces", "QOJ", "Luogu", "Nowcoder", "HDU", "PTA", "Other"]
DURATIONS_HOURS = {"5 小时 (标准 XCPC)": 18000, "4 小时": 14400, "3 小时": 10800, "2 小时": 7200, "未知/无限": 0}

def load_data():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"解析 JSON 失败: {e}")
        return []

def save_data(data):
    try:
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("写入失败", f"无法保存文件: {e}")
        return False

class ContestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XCPC 比赛录入工具")
        self.root.geometry("480x420")
        self.root.resizable(False, False)

        frame = ttk.Frame(root, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        self.var_platform = tk.StringVar(value="Codeforces")
        self.var_name = tk.StringVar()
        self.var_url = tk.StringVar()
        
        # 默认日期设为今天
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        self.var_date = tk.StringVar(value=today_str)
        self.var_duration = tk.StringVar(value="5 小时 (标准 XCPC)")

        self._build_ui(frame)

    def _build_ui(self, parent):
        row = 0
        
        ttk.Label(parent, text="平    台:").grid(row=row, column=0, sticky=tk.W, pady=8)
        cb_platform = ttk.Combobox(parent, textvariable=self.var_platform, values=PLATFORMS, state="readonly", width=35)
        cb_platform.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="比赛名称:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_name, width=37).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="比赛链接:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_url, width=37).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="比赛日期:").grid(row=row, column=0, sticky=tk.W, pady=8)
        date_frame = ttk.Frame(parent)
        date_frame.grid(row=row, column=1, sticky=tk.W, pady=8)
        ttk.Entry(date_frame, textvariable=self.var_date, width=15).pack(side=tk.LEFT)
        ttk.Label(date_frame, text=" (格式: YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=5)
        row += 1

        ttk.Label(parent, text="比赛时长:").grid(row=row, column=0, sticky=tk.W, pady=8)
        cb_dur = ttk.Combobox(parent, textvariable=self.var_duration, values=list(DURATIONS_HOURS.keys()), state="readonly", width=35)
        cb_dur.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        btn_save = ttk.Button(parent, text="保存至比赛库", command=self.save_entry, width=20)
        btn_save.grid(row=row, column=0, columnspan=2, pady=10)

    def generate_id(self, platform, url):
        """尝试从链接中智能提取唯一ID"""
        if platform == "QOJ" and "qoj.ac/contest/" in url:
            match = re.search(r'contest/(\d+)', url)
            if match:
                return f"QOJ_{match.group(1)}"
        elif platform == "Codeforces" and "codeforces.com/gym/" in url:
            match = re.search(r'gym/(\d+)', url)
            if match:
                return f"CF_{match.group(1)}"
        
        # 兜底：平台 + 当前时间戳
        return f"{platform}_{int(datetime.datetime.now().timestamp())}"

    def save_entry(self):
        platform = self.var_platform.get().strip()
        name = self.var_name.get().strip()
        url = self.var_url.get().strip()
        date_str = self.var_date.get().strip()
        duration_label = self.var_duration.get().strip()

        if not all([platform, name, url, date_str, duration_label]):
            messagebox.showwarning("校验失败", "所有字段均为必填项！")
            return

        # 校验并解析日期为 UTC 时间戳
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            timestamp = int(dt.timestamp())
        except ValueError:
            messagebox.showerror("格式错误", "日期格式不正确，请严格按照 YYYY-MM-DD 输入（例：2023-11-25）。")
            return

        duration_seconds = DURATIONS_HOURS.get(duration_label, 18000)
        unique_id = self.generate_id(platform, url)

        data = load_data()

        # 查重逻辑
        if any(item.get('id') == unique_id for item in data):
            messagebox.showerror("重复错误", f"题库中已存在 ID 为 {unique_id} 的比赛！")
            return

        new_contest = {
            "id": unique_id,
            "platform": platform,
            "name": name,
            "url": url,
            "timestamp": timestamp,
            "duration": duration_seconds
        }

        # 增量插入，前台会自动按时间戳降序渲染
        data.append(new_contest)
        if save_data(data):
            messagebox.showinfo("录入成功", f"比赛《{name}》已成功归档！")
            # 清空名称和链接，保留平台和日期以备连续录入同一时间的比赛
            self.var_name.set("")
            self.var_url.set("")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app = ContestApp(root)
    root.mainloop()