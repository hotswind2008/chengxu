#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import sys

print("="*50)
print("开始运行测试程序...")
print("Python版本:", sys.version)
print("="*50)

root = tk.Tk()
root.title("基本测试")
root.geometry("600x400+100+100")
root.configure(bg='yellow')

# 强制窗口置顶
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)

# 大标题
label = tk.Label(
    root, 
    text="如果你看到这个窗口\n说明tkinter正常工作",
    font=('Arial', 20, 'bold'),
    bg='yellow',
    fg='blue'
)
label.pack(expand=True)

# 按钮
btn = tk.Button(
    root,
    text="点击我关闭窗口",
    font=('Arial', 16, 'bold'),
    bg='red',
    fg='white',
    command=root.destroy,
    padx=30,
    pady=20
)
btn.pack(pady=20)

print("\n窗口应该已经显示")
print("如果看不到窗口，请检查是否被其他窗口遮挡")
print("或者尝试按 Cmd+Tab 切换窗口")
print("="*50)

root.mainloop()

print("程序已关闭")





