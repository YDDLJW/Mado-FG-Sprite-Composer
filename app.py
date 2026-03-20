import os
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from composer import compose_images, combine_one


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("窗社或类似游戏引擎立绘合成工具 / FG Composer for Mado-like Engines")

        self.body_files = []
        self.expr_files = []

        self.worker_thread = None
        self.msg_queue = queue.Queue()
        self.is_running = False
        self.preview_photo = None

        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪 / Ready")

        main = tk.Frame(root, padx=10, pady=10)
        main.pack(fill="both", expand=True)

        top = tk.Frame(main)
        top.pack(fill="x", pady=(0, 8))

        tk.Label(top, text="输出路径 / Output Folder").pack(side="left")
        self.output_entry = tk.Entry(top, textvariable=self.output_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.output_btn = tk.Button(top, text="浏览 / Browse", command=self.select_output_dir)
        self.output_btn.pack(side="left")

        mid = tk.Frame(main)
        mid.pack(fill="both", expand=True)

        left = tk.Frame(mid)
        left.pack(side="left", fill="both", expand=False)

        preview_frame = tk.LabelFrame(mid, text="预览 / Preview")
        preview_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

        body_frame = tk.LabelFrame(left, text="身体图片列表 / Body Image List")
        body_frame.pack(fill="both", expand=True)

        body_btn_row = tk.Frame(body_frame)
        body_btn_row.pack(fill="x", pady=(4, 4))
        self.body_btn = tk.Button(body_btn_row, text="添加身体图片（可多选） / Add Body Images (Multi-select)", command=self.select_body_files)
        self.body_btn.pack(side="left", fill="x", expand=True)
        self.body_remove_btn = tk.Button(body_btn_row, text="移除选中 / Remove Selected", command=self.remove_selected_body)
        self.body_remove_btn.pack(side="left", padx=(6, 0))
        self.body_clear_btn = tk.Button(body_btn_row, text="清空列表 / Clear List", command=self.clear_body_list)
        self.body_clear_btn.pack(side="left", padx=(6, 0))

        body_list_row = tk.Frame(body_frame)
        body_list_row.pack(fill="both", expand=True)
        self.body_listbox = tk.Listbox(body_list_row, exportselection=False, width=42)
        self.body_listbox.pack(side="left", fill="both", expand=True)
        body_scroll = tk.Scrollbar(body_list_row, command=self.body_listbox.yview)
        body_scroll.pack(side="left", fill="y")
        self.body_listbox.config(yscrollcommand=body_scroll.set)
        self.body_listbox.bind("<<ListboxSelect>>", self.on_preview_selection_changed)

        expr_frame = tk.LabelFrame(left, text="表情图片列表 / Expression Image List")
        expr_frame.pack(fill="both", expand=True, pady=(10, 0))

        expr_btn_row = tk.Frame(expr_frame)
        expr_btn_row.pack(fill="x", pady=(4, 4))
        self.expr_btn = tk.Button(expr_btn_row, text="添加表情图片（可多选） / Add Expression Images (Multi-select)", command=self.select_expr_files)
        self.expr_btn.pack(side="left", fill="x", expand=True)
        self.expr_remove_btn = tk.Button(expr_btn_row, text="移除选中 / Remove Selected", command=self.remove_selected_expr)
        self.expr_remove_btn.pack(side="left", padx=(6, 0))
        self.expr_clear_btn = tk.Button(expr_btn_row, text="清空列表 / Clear List", command=self.clear_expr_list)
        self.expr_clear_btn.pack(side="left", padx=(6, 0))

        expr_list_row = tk.Frame(expr_frame)
        expr_list_row.pack(fill="both", expand=True)
        self.expr_listbox = tk.Listbox(expr_list_row, exportselection=False, width=42)
        self.expr_listbox.pack(side="left", fill="both", expand=True)
        expr_scroll = tk.Scrollbar(expr_list_row, command=self.expr_listbox.yview)
        expr_scroll.pack(side="left", fill="y")
        self.expr_listbox.config(yscrollcommand=expr_scroll.set)
        self.expr_listbox.bind("<<ListboxSelect>>", self.on_preview_selection_changed)

        self.preview_info_var = tk.StringVar(value="请选择一个身体图片和一个表情图片 / Please select one body image and one expression image")
        tk.Label(preview_frame, textvariable=self.preview_info_var, anchor="w", justify="left").pack(fill="x", padx=8, pady=(8, 4))

        self.preview_canvas = tk.Canvas(preview_frame, bg="#202020", highlightthickness=1, highlightbackground="#666")
        self.preview_canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.preview_canvas.bind("<Configure>", self.on_preview_canvas_resize)

        bottom = tk.Frame(main)
        bottom.pack(fill="x", pady=(10, 0))

        self.export_current_btn = tk.Button(bottom, text="只导出当前预览这一组 / Export Current Preview Only", command=self.export_current_preview, height=2)
        self.export_current_btn.pack(fill="x", pady=(0, 8))

        self.start_btn = tk.Button(bottom, text="开始批量合成 / Start Batch Composition", command=self.start_combine, height=2)
        self.start_btn.pack(fill="x")

        tk.Label(main, textvariable=self.status_var, anchor="w").pack(fill="x", pady=(8, 4))

        log_frame = tk.LabelFrame(main, text="日志 / Log")
        log_frame.pack(fill="both", expand=False, pady=(4, 0))
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")

    def set_running_state(self, running):
        self.is_running = running
        state = "disabled" if running else "normal"
        self.body_btn.config(state=state)
        self.expr_btn.config(state=state)
        self.body_remove_btn.config(state=state)
        self.expr_remove_btn.config(state=state)
        self.body_clear_btn.config(state=state)
        self.expr_clear_btn.config(state=state)
        self.output_btn.config(state=state)
        self.output_entry.config(state=state)
        self.start_btn.config(state=state)
        self.export_current_btn.config(state=state)
        self.status_var.set("处理中... / Processing..." if running else "就绪 / Ready")

    def select_output_dir(self):
        folder = filedialog.askdirectory(title="选择输出目录 / Select Output Folder")
        if folder:
            self.output_var.set(folder)

    def select_body_files(self):
        files = filedialog.askopenfilenames(
            title="选择身体图片 / Select Body Images",
            filetypes=[("PNG 图片 / PNG Images", "*.png"), ("所有文件 / All Files", "*.*")]
        )
        if files:
            added = 0
            for path in files:
                if path not in self.body_files:
                    self.body_files.append(path)
                    self.body_listbox.insert("end", path)
                    added += 1
            self.log(f"添加身体图片 {added} 个 / Added {added} body image(s)")
            if self.body_listbox.size() > 0 and not self.body_listbox.curselection():
                self.body_listbox.selection_set(0)
                self.on_preview_selection_changed()

    def select_expr_files(self):
        files = filedialog.askopenfilenames(
            title="选择表情图片 / Select Expression Images",
            filetypes=[("PNG 图片 / PNG Images", "*.png"), ("所有文件 / All Files", "*.*")]
        )
        if files:
            added = 0
            for path in files:
                if path not in self.expr_files:
                    self.expr_files.append(path)
                    self.expr_listbox.insert("end", path)
                    added += 1
            self.log(f"添加表情图片 {added} 个 / Added {added} expression image(s)")
            if self.expr_listbox.size() > 0 and not self.expr_listbox.curselection():
                self.expr_listbox.selection_set(0)
                self.on_preview_selection_changed()

    def remove_selected_body(self):
        sel = self.body_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        path = self.body_listbox.get(idx)
        if path in self.body_files:
            self.body_files.remove(path)
        self.body_listbox.delete(idx)
        self.on_preview_selection_changed()

    def remove_selected_expr(self):
        sel = self.expr_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        path = self.expr_listbox.get(idx)
        if path in self.expr_files:
            self.expr_files.remove(path)
        self.expr_listbox.delete(idx)
        self.on_preview_selection_changed()

    def clear_body_list(self):
        if self.is_running:
            return
        if self.body_listbox.size() == 0:
            return
        if messagebox.askyesno("确认 / Confirm", "确定清空身体图片列表吗？\nClear the body image list?"):
            self.body_files.clear()
            self.body_listbox.delete(0, "end")
            self.on_preview_selection_changed()

    def clear_expr_list(self):
        if self.is_running:
            return
        if self.expr_listbox.size() == 0:
            return
        if messagebox.askyesno("确认 / Confirm", "确定清空表情图片列表吗？\nClear the expression image list?"):
            self.expr_files.clear()
            self.expr_listbox.delete(0, "end")
            self.on_preview_selection_changed()

    def get_selected_body_path(self):
        sel = self.body_listbox.curselection()
        if not sel:
            return None
        return self.body_listbox.get(sel[0])

    def get_selected_expr_path(self):
        sel = self.expr_listbox.curselection()
        if not sel:
            return None
        return self.expr_listbox.get(sel[0])

    def on_preview_selection_changed(self, event=None):
        self.update_preview()

    def on_preview_canvas_resize(self, event=None):
        self.update_preview()

    def update_preview(self):
        body_path = self.get_selected_body_path()
        expr_path = self.get_selected_expr_path()

        self.preview_canvas.delete("all")
        self.preview_photo = None

        if not body_path or not expr_path:
            self.preview_info_var.set("请选择一个身体图片和一个表情图片 / Please select one body image and one expression image")
            return

        try:
            canvas_img, body_pos, expr_pos = compose_images(body_path, expr_path)

            pw = max(1, self.preview_canvas.winfo_width())
            ph = max(1, self.preview_canvas.winfo_height())

            iw, ih = canvas_img.size
            scale = min((pw - 20) / iw, (ph - 20) / ih)
            scale = min(scale, 1.0)
            nw = max(1, int(iw * scale))
            nh = max(1, int(ih * scale))

            preview_img = canvas_img.resize((nw, nh), Image.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(preview_img)

            x = pw // 2
            y = ph // 2
            self.preview_canvas.create_image(x, y, image=self.preview_photo, anchor="center")

            self.preview_info_var.set(
                f"身体 / Body: {os.path.basename(body_path)}    body=({body_pos['x']},{body_pos['y']})\n"
                f"表情 / Expression: {os.path.basename(expr_path)}    expr=({expr_pos['x']},{expr_pos['y']})"
            )
        except Exception as e:
            self.preview_info_var.set(f"预览失败 / Preview failed: {e}")

    def export_current_preview(self):
        if self.is_running:
            return

        body_path = self.get_selected_body_path()
        expr_path = self.get_selected_expr_path()

        if not body_path or not expr_path:
            messagebox.showerror("错误 / Error", "请先各选择一个身体图片和一个表情图片\nPlease select one body image and one expression image first")
            return

        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误 / Error", "请先填写输出路径\nPlease specify the output folder first")
            return

        os.makedirs(output_dir, exist_ok=True)

        try:
            out_path, body_pos, expr_pos = combine_one(body_path, expr_path, output_dir)
            self.log(
                f"导出当前预览 / Exported current preview: {os.path.basename(body_path)} + {os.path.basename(expr_path)} "
                f"-> {os.path.basename(out_path)} | "
                f"body=({body_pos['x']},{body_pos['y']}), expr=({expr_pos['x']},{expr_pos['y']})"
            )
            messagebox.showinfo("完成 / Done", f"已导出 / Exported:\n{out_path}")
        except Exception as e:
            messagebox.showerror("错误 / Error", f"导出失败 / Export failed:\n{e}")

    def start_combine(self):
        if self.is_running:
            return

        if not self.body_files:
            messagebox.showerror("错误 / Error", "请先选择身体图片\nPlease select body images first")
            return
        if not self.expr_files:
            messagebox.showerror("错误 / Error", "请先选择表情图片\nPlease select expression images first")
            return

        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误 / Error", "请先填写输出路径\nPlease specify the output folder first")
            return

        os.makedirs(output_dir, exist_ok=True)
        self.log_text.delete("1.0", "end")
        self.set_running_state(True)

        self.worker_thread = threading.Thread(
            target=self.combine_worker,
            args=(self.body_files[:], self.expr_files[:], output_dir),
            daemon=True
        )
        self.worker_thread.start()
        self.root.after(100, self.process_queue)

    def combine_worker(self, body_files, expr_files, output_dir):
        count = 0
        fail = 0
        total = len(body_files) * len(expr_files)
        current = 0

        for body in body_files:
            for expr in expr_files:
                current += 1
                try:
                    out_path, body_pos, expr_pos = combine_one(body, expr, output_dir)
                    self.msg_queue.put((
                        "log",
                        f"[{current}/{total}] 完成 / Done: {os.path.basename(body)} + {os.path.basename(expr)} "
                        f"-> {os.path.basename(out_path)} | "
                        f"body=({body_pos['x']},{body_pos['y']}), expr=({expr_pos['x']},{expr_pos['y']})"
                    ))
                    count += 1
                except Exception as e:
                    self.msg_queue.put((
                        "log",
                        f"[{current}/{total}] 失败 / Failed: {os.path.basename(body)} + {os.path.basename(expr)} | {e}"
                    ))
                    fail += 1

        self.msg_queue.put(("done", (count, fail)))

    def process_queue(self):
        try:
            while True:
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self.log(payload)
                elif msg_type == "done":
                    count, fail = payload
                    self.set_running_state(False)
                    self.status_var.set(f"完成 / Finished: 成功 {count} 张，失败 {fail} 张 / Success {count}, Failed {fail}")
                    messagebox.showinfo("完成 / Done", f"成功 {count} 张，失败 {fail} 张\nSuccess {count}, Failed {fail}")
                    return
        except queue.Empty:
            pass

        if self.is_running:
            self.root.after(100, self.process_queue)

    def on_close(self):
        if self.is_running:
            if not messagebox.askyesno("确认 / Confirm", "仍在处理中，确定要关闭吗？\nProcessing is still running. Are you sure you want to close?"):
                return
        self.root.destroy()