import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "math_problems.json")
WORK_FILE_PATH = os.path.join(BASE_DIR, "Math_work.json")

CATEGORIES = ["计数问题", "纯数论", "线性代数", "概率与期望", "Ad-hoc"]
DIFFICULTIES = ["Template", "Easy", "Medium", "Hard"]
PLATFORMS = ["Codeforces", "QOJ", "Luogu"]

def load_data(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"解析 JSON 失败 ({filepath}): {e}")
        return []

def save_data(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("写入失败", f"无法保存文件 ({filepath}): {e}")
        return False

class MathProblemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XCPC Math Finder 录入工具")
        self.root.geometry("480x650")
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
        
        ttk.Label(parent, text="平    台:").grid(row=row, column=0, sticky=tk.W, pady=6)
        cb_platform = ttk.Combobox(parent, textvariable=self.var_platform, values=PLATFORMS, state="readonly", width=33)
        cb_platform.grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="比赛名称:").grid(row=row, column=0, sticky=tk.W, pady=6)
        ttk.Entry(parent, textvariable=self.var_contest_name, width=35).grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="比赛链接:").grid(row=row, column=0, sticky=tk.W, pady=6)
        ttk.Entry(parent, textvariable=self.var_contest_url, width=35).grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="题    号:").grid(row=row, column=0, sticky=tk.W, pady=6)
        ttk.Entry(parent, textvariable=self.var_problem_id, width=35).grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="题目大类:").grid(row=row, column=0, sticky=tk.W, pady=6)
        cb_category = ttk.Combobox(parent, textvariable=self.var_category, values=CATEGORIES, state="readonly", width=33)
        cb_category.grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="细分小类:").grid(row=row, column=0, sticky=tk.W, pady=6)
        ttk.Entry(parent, textvariable=self.var_subcategory, width=35).grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Label(parent, text="难    度:").grid(row=row, column=0, sticky=tk.W, pady=6)
        cb_diff = ttk.Combobox(parent, textvariable=self.var_difficulty, values=DIFFICULTIES, state="readonly", width=33)
        cb_diff.grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        # 思维路径输入区（多行文本框）
        ttk.Label(parent, text="思维路径:").grid(row=row, column=0, sticky=tk.NW, pady=6)
        self.txt_thinking = tk.Text(parent, width=35, height=6, font=("Segoe UI", 9))
        self.txt_thinking.grid(row=row, column=1, sticky=tk.W, pady=6)
        row += 1

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)
        row += 1

        btn_save = ttk.Button(parent, text="保存至题库", command=self.save_entry, width=20)
        btn_save.grid(row=row, column=0, columnspan=2, pady=8)

    def save_entry(self):
        platform = self.var_platform.get().strip()
        c_name = self.var_contest_name.get().strip()
        c_url = self.var_contest_url.get().strip()
        p_id = self.var_problem_id.get().strip().upper()
        category = self.var_category.get().strip()
        subcat = self.var_subcategory.get().strip()
        diff = self.var_difficulty.get().strip()
        thinking = self.txt_thinking.get("1.0", tk.END).strip()

        if not all([platform, c_name, c_url, p_id, category, subcat, diff]):
            messagebox.showwarning("校验失败", "除思维路径外，其余基本字段均为必填项！")
            return

        try:
            raw_contest_id = c_url.rstrip('/').split('/')[-1]
            unique_id = f"{platform}_{raw_contest_id}_{p_id}"
        except Exception:
            unique_id = f"{platform}_{int(datetime.datetime.now().timestamp())}_{p_id}"

        problems_data = load_data(FILE_PATH)

        if any(item.get('id') == unique_id for item in problems_data):
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

        problems_data.append(new_problem)
        if not save_data(FILE_PATH, problems_data):
            return

        # 若填写了思维路径，更新/追加到 Math_work.json
        if thinking:
            work_data = load_data(WORK_FILE_PATH)
            matched = False
            for item in work_data:
                if item.get("id") == unique_id:
                    item["thinking"] = thinking
                    matched = True
                    break
            if not matched:
                work_data.append({
                    "id": unique_id,
                    "thinking": thinking
                })
            save_data(WORK_FILE_PATH, work_data)

        messagebox.showinfo("录入成功", f"题目 {p_id} 已成功保存！\n思维路径状态: {'已记录' if thinking else '未填写'}")
        self.var_problem_id.set("")
        self.var_subcategory.set("")
        self.var_difficulty.set("")
        self.txt_thinking.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app = MathProblemApp(root)
    root.mainloop()