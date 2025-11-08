#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试显示问题
"""

import tkinter as tk
from tkinter import Canvas
import platform

def test_display():
    root = tk.Tk()
    root.title("显示测试")
    root.geometry("800x600")
    root.configure(bg='lightblue')
    
    # 测试1: 标题
    tk.Label(root, text="测试1: 这是标题", font=('Arial', 24, 'bold'), 
             bg='lightblue', fg='red').pack(pady=10)
    
    # 测试2: 普通文本
    tk.Label(root, text="测试2: 这是普通文本", font=('Arial', 16), 
             bg='lightblue').pack(pady=10)
    
    # 测试3: Frame
    frame = tk.Frame(root, bg='yellow', width=600, height=100)
    frame.pack(pady=10)
    frame.pack_propagate(False)
    tk.Label(frame, text="测试3: 这是一个Frame", font=('Arial', 14), 
             bg='yellow').pack(expand=True)
    
    # 测试4: Canvas绘图
    canvas_frame = tk.Frame(root, bg='lightblue')
    canvas_frame.pack(pady=10)
    
    tk.Label(canvas_frame, text="测试4: Canvas绘图", font=('Arial', 14),
             bg='lightblue').pack()
    
    canvas = Canvas(canvas_frame, width=200, height=200, bg='white')
    canvas.pack()
    
    # 绘制一个简单的矩形
    canvas.create_rectangle(20, 20, 180, 180, fill='green', outline='black', width=3)
    canvas.create_oval(60, 60, 140, 140, fill='red', outline='black', width=2)
    canvas.create_text(100, 100, text="Canvas", font=('Arial', 16, 'bold'))
    
    # 测试5: 按钮
    button_frame = tk.Frame(root, bg='lightblue')
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="按钮1", font=('Arial', 12), 
              bg='#3498db', fg='white', padx=20, pady=10).pack(side='left', padx=5)
    tk.Button(button_frame, text="按钮2", font=('Arial', 12), 
              bg='#e74c3c', fg='white', padx=20, pady=10).pack(side='left', padx=5)
    tk.Button(button_frame, text="按钮3", font=('Arial', 12), 
              bg='#2ecc71', fg='white', padx=20, pady=10).pack(side='left', padx=5)
    
    # 系统信息
    info = f"系统: {platform.system()}\n"
    info += f"Python版本: {platform.python_version()}\n"
    info += f"屏幕: {root.winfo_screenwidth()}x{root.winfo_screenheight()}"
    
    tk.Label(root, text=info, font=('Arial', 10), bg='lightblue', 
             justify='left').pack(pady=10)
    
    # 退出按钮
    tk.Button(root, text="关闭窗口", font=('Arial', 14, 'bold'),
              command=root.destroy, bg='orange', padx=30, pady=15).pack(pady=20)
    
    print("窗口已创建，所有组件应该可见")
    print(f"系统: {platform.system()}")
    print(f"窗口大小: 800x600")
    
    root.mainloop()

if __name__ == '__main__':
    test_display()





