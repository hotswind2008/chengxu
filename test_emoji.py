#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试emoji显示"""

import tkinter as tk
from tkinter import font as tkfont

root = tk.Tk()
root.title("Emoji测试")
root.geometry("400x400")
root.configure(bg='white')

# 测试不同大小的emoji
sizes = [20, 40, 60, 80, 100]
emojis = ["🐐", "🚗", "🚪"]

y_pos = 20
for size in sizes:
    label = tk.Label(root, text=f"大小{size}: 🐐 🚗 🚪", 
                    font=('Arial', size), bg='white')
    label.pack(pady=10)

tk.Label(root, text="如果上面显示正常，\n说明系统支持emoji",
        font=('Arial', 14), bg='white', fg='blue').pack(pady=20)

root.mainloop()
