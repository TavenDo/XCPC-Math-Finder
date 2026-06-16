import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# 强制绑定脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "video_solutions.json")

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

class VideoSolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XCPC 题解录入工具")
        self.root.geometry("450x250")
        self.root.resizable(False, False)

        frame = ttk.Frame(root, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        self.var_title = tk.StringVar()
        self.var_url = tk.StringVar()

        self._build_ui(frame)

    def _build_ui(self, parent):
        row = 0
        
        ttk.Label(parent, text="题解标题:").grid(row=row, column=0, sticky=tk.W, pady=10)
        ttk.Entry(parent, textvariable=self.var_title, width=35).grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1

        ttk.Label(parent, text="B站链接:").grid(row=row, column=0, sticky=tk.W, pady=10)
        ttk.Entry(parent, textvariable=self.var_url, width=35).grid(row=row, column=1, sticky=tk.W, pady=10)
        row += 1

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1

        btn_save = ttk.Button(parent, text="保存至题解库", command=self.save_entry, width=20)
        btn_save.grid(row=row, column=0, columnspan=2, pady=10)

    def save_entry(self):
        title = self.var_title.get().strip()
        url = self.var_url.get().strip()

        if not title or not url:
            messagebox.showwarning("校验失败", "标题和链接均为必填项！")
            return

        data = load_data()

        # 查重逻辑：防止同一个 B 站视频被重复录入
        if any(item.get('url') == url for item in data):
            messagebox.showerror("重复错误", "该 B 站链接已存在于题解库中！")
            return

        new_video = {
            "title": title,
            "url": url
        }

        data.append(new_video)
        if save_data(data):
            messagebox.showinfo("录入成功", f"《{title}》已成功归档！")
            # 录入成功后全部清空，方便粘贴下一个
            self.var_title.set("")
            self.var_url.set("")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app = VideoSolutionApp(root)
    root.mainloop()