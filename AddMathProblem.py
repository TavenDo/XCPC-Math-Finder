import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

# 核心修复：强制绑定脚本所在目录，防止因 IDE 运行路径问题导致文件保存到别处
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "math_problems.json")

# 更新：只保留四个大方向，去掉博弈论
CATEGORIES = ["计数问题", "纯数论", "线性代数", "概率与期望"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
# 更新：只保留 Codeforces 和 QOJ
PLATFORMS = ["Codeforces", "QOJ"]

def load_data():
    if not os.path.exists(FILE_PATH):
        return []
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            # 兼容空文件或内容不合法的情况
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

class MathProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XCPC Math Finder 录入工具")
        self.root.geometry("450x500")
        self.root.resizable(False, False)

        frame = ttk.Frame(root, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        self.var_platform = tk.StringVar(value="Codeforces")
        self.var_contest_name = tk.StringVar()
        self.var_contest_url = tk.StringVar()
        self.var_problem_id = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_subcategory = tk.StringVar()
        self.var_difficulty = tk.StringVar()

        self._build_ui(frame)

    def _build_ui(self, parent):
        row = 0
        
        ttk.Label(parent, text="平    台:").grid(row=row, column=0, sticky=tk.W, pady=8)
        cb_platform = ttk.Combobox(parent, textvariable=self.var_platform, values=PLATFORMS, state="readonly", width=33)
        cb_platform.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="比赛名称:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_contest_name, width=35).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="比赛链接:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_contest_url, width=35).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="题    号:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_problem_id, width=35).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="题目大类:").grid(row=row, column=0, sticky=tk.W, pady=8)
        cb_category = ttk.Combobox(parent, textvariable=self.var_category, values=CATEGORIES, state="readonly", width=33)
        cb_category.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="细分小类:").grid(row=row, column=0, sticky=tk.W, pady=8)
        ttk.Entry(parent, textvariable=self.var_subcategory, width=35).grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Label(parent, text="难    度:").grid(row=row, column=0, sticky=tk.W, pady=8)
        cb_diff = ttk.Combobox(parent, textvariable=self.var_difficulty, values=DIFFICULTIES, state="readonly", width=33)
        cb_diff.grid(row=row, column=1, sticky=tk.W, pady=8)
        row += 1

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        btn_save = ttk.Button(parent, text="保存至题库", command=self.save_entry, width=20)
        btn_save.grid(row=row, column=0, columnspan=2, pady=10)

    def save_entry(self):
        platform = self.var_platform.get().strip()
        c_name = self.var_contest_name.get().strip()
        c_url = self.var_contest_url.get().strip()
        p_id = self.var_problem_id.get().strip().upper()
        category = self.var_category.get().strip()
        subcat = self.var_subcategory.get().strip()
        diff = self.var_difficulty.get().strip()

        if not all([platform, c_name, c_url, p_id, category, subcat, diff]):
            messagebox.showwarning("校验失败", "所有字段均为必填项，请补充完整！")
            return

        try:
            raw_contest_id = c_url.rstrip('/').split('/')[-1]
            unique_id = f"{platform}_{raw_contest_id}_{p_id}"
        except:
            unique_id = f"{platform}_{int(datetime.datetime.now().timestamp())}_{p_id}"

        data = load_data()

        if any(item.get('id') == unique_id for item in data):
            messagebox.showerror("重复错误", f"题库中已存在 ID 为 {unique_id} 的题目！")
            return

        new_problem = {
            "id": unique_id,
            "platform": platform,
            "contest_name": c_name,
            "contest_url": c_url,
            "problem_id": p_id,
            "category": category,
            "subcategory": subcat,
            "difficulty": diff,
            "status": False 
        }

        data.append(new_problem)
        if save_data(data):
            messagebox.showinfo("录入成功", f"题目 {p_id} 已成功保存！\n文件路径: {FILE_PATH}")
            self.var_problem_id.set("")
            self.var_subcategory.set("")
            self.var_difficulty.set("")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app = MathProblemApp(root)
    root.mainloop()