import os
import sys
import tkinter as tk
from app import App


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(resource_path("assets/icon.ico"))
    app = App(root)
    root.geometry("1280x820")
    root.mainloop()