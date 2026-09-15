import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKIN_FILE = os.path.join(BASE_DIR, "daily_checkin.json")
MATH_PROBLEMS_FILE = os.path.join(BASE_DIR, "math_problems.json")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"读取 {filepath} 失败: {e}")
        return []

def save_json(filepath, data):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("保存失败", f"无法写入文件 {filepath}: {e}")
        return False

class CheckinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XCPC-Math 每日打卡录入")
        self.root.geometry("520x460")
        self.root.resizable(False, False)

        # 加载现有题目供选择与校验
        self.math_problems = load_json(MATH_PROBLEMS_FILE)
        self.math_id_map = {item['id']: item for item in self.math_problems if 'id' in item}

        frame = ttk.Frame(root, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        self.var_date = tk.StringVar(value=today_str)
        self.var_problem_id = tk.StringVar()
        self.var_preview = tk.StringVar(value="等待选择或输入题目 ID...")

        self._build_ui(frame)

    def _build_ui(self, parent):
        row = 0

        # 打卡日期
        ttk.Label(parent, text="打卡日期:").grid(row=row, column=0, sticky=tk.W, pady=10)
        date_frame = ttk.Frame(parent)
        date_frame.grid(row=row, column=1, sticky=tk.W, pady=10)
        ttk.Entry(date_frame, textvariable=self.var_date, width=15).pack(side=tk.LEFT)
        ttk.Label(date_frame, text=" (格式: YYYY-MM-DD)", foreground="gray").pack(side=tk.LEFT, padx=5)
        row += 1

        # 题目 ID
        ttk.Label(parent, text="题目 ID:").grid(row=row, column=0, sticky=tk.W, pady=10)
        
        # 支持下拉快捷选择已存在的题目 ID，也可直接键盘输入
        id_values = list(self.math_id_map.keys())
        self.cb_id = ttk.Combobox(parent, textvariable=self.var_problem_id, values=id_values, width=35)
        self.cb_id.grid(row=row, column=1, sticky=tk.W, pady=10)
        self.cb_id.bind("<<ComboboxSelected>>", self.on_id_changed)
        self.cb_id.bind("<KeyRelease>", self.on_id_changed)
        row += 1

        # 关联信息预览区
        ttk.Label(parent, text="题目校验:").grid(row=row, column=0, sticky=tk.NW, pady=10)
        preview_box = ttk.Label(parent, textvariable=self.var_preview, foreground="#2980b9", wraplength=320, justify=tk.LEFT)
        preview_box.grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        btn_save = ttk.Button(parent, text="确认打卡", command=self.save_checkin, width=22)
        btn_save.grid(row=row, column=0, columnspan=2, pady=10)

    def on_id_changed(self, event=None):
        pid = self.var_problem_id.get().strip()
        if not pid:
            self.var_preview.set("等待选择或输入题目 ID...")
            return

        if pid in self.math_id_map:
            p = self.math_id_map[pid]
            info = f"✅ 已关联：[{p.get('platform')}] {p.get('contest_name')} - Problem {p.get('problem_id')}\n难度: {p.get('difficulty')} | 分类: {p.get('category')}-{p.get('subcategory')}"
            self.var_preview.set(info)
        else:
            self.var_preview.set("⚠️ 注意：该 ID 尚未在 math_problems.json 中找到，请确保拼写一致。")

    def save_checkin(self):
        date_str = self.var_date.get().strip()
        problem_id = self.var_problem_id.get().strip()

        if not date_str or not problem_id:
            messagebox.showwarning("校验失败", "打卡日期与题目 ID 均为必填项！")
            return

        # 校验日期合法性
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("日期格式错误", "请严格按照 YYYY-MM-DD 输入日期。")
            return

        checkin_data = load_json(CHECKIN_FILE)

        # 查重逻辑：防止同一天重复打卡同一题
        if any(item.get('date') == date_str and item.get('id') == problem_id for item in checkin_data):
            messagebox.showerror("重复打卡", f"在 {date_str} 已经为题目 {problem_id} 打过卡了！")
            return

        new_record = {
            "date": date_str,
            "id": problem_id
        }

        # 自动插入并按日期降序保存
        checkin_data.append(new_record)
        checkin_data.sort(key=lambda x: x.get('date', ''), reverse=True)

        if save_json(CHECKIN_FILE, checkin_data):
            messagebox.showinfo("打卡成功", f"🎉 {date_str} 打卡成功！\n记录已写入 daily_checkin.json")
            self.var_problem_id.set("")
            self.var_preview.set("等待选择或输入题目 ID...")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app = CheckinApp(root)
    root.mainloop()