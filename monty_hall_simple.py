#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三门问题游戏 - 简化布局版
优化布局确保所有内容完整显示
"""

import tkinter as tk
from tkinter import messagebox, ttk, Canvas
import random
import threading
import time
import platform
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class MontyHallGame:
    def __init__(self, root):
        self.root = root
        self.root.title("三门问题游戏")
        
        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 设置窗口大小为屏幕的80%
        window_width = min(1400, int(screen_width * 0.9))
        window_height = min(950, int(screen_height * 0.9))
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#ecf0f1')
        
        # 检测操作系统
        self.os_type = platform.system()
        
        # 配置字体
        if self.os_type == 'Windows':
            self.text_font = ('Microsoft YaHei', 11, 'bold')
            self.title_font = ('Microsoft YaHei', 24, 'bold')
            self.info_font = ('Microsoft YaHei', 14, 'bold')
            self.button_font = ('Microsoft YaHei', 12, 'bold')
            self.door_label_font = ('Microsoft YaHei', 18, 'bold')
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
        else:
            self.text_font = ('Arial', 12, 'bold')
            self.title_font = ('Arial', 24, 'bold')
            self.info_font = ('Arial', 15, 'bold')
            self.button_font = ('Arial', 13, 'bold')
            self.door_label_font = ('Arial', 20, 'bold')
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'STHeiti', 'Arial']
        
        plt.rcParams['axes.unicode_minus'] = False
        
        # 游戏状态
        self.car_door = 0
        self.first_choice = None
        self.opened_door = None
        self.game_stage = 0
        self.simulating = False
        
        # 统计数据
        self.stats = {
            'stay_wins': 0,
            'stay_total': 0,
            'switch_wins': 0,
            'switch_total': 0
        }
        
        # 历史数据
        self.history = {
            'stay_rates': [],
            'switch_rates': []
        }
        
        self.setup_ui()
        self.new_game()
    
    def draw_door(self, canvas):
        """绘制门"""
        canvas.delete('all')
        w, h = 200, 280
        
        # 门板
        canvas.create_rectangle(5, 5, w-5, h-5, fill='#8b4513', outline='#654321', width=4)
        canvas.create_rectangle(15, 15, w-15, h-15, fill='#a0522d', outline='#654321', width=2)
        
        # 门板装饰
        canvas.create_rectangle(25, 25, w//2-5, h//2-5, fill='#8b4513', outline='#654321', width=2)
        canvas.create_rectangle(w//2+5, 25, w-25, h//2-5, fill='#8b4513', outline='#654321', width=2)
        canvas.create_rectangle(25, h//2+5, w//2-5, h-25, fill='#8b4513', outline='#654321', width=2)
        canvas.create_rectangle(w//2+5, h//2+5, w-25, h-25, fill='#8b4513', outline='#654321', width=2)
        
        # 门把手
        canvas.create_oval(w-50, h//2-8, w-35, h//2+8, fill='#ffd700', outline='#b8860b', width=2)
    
    def draw_car(self, canvas):
        """绘制汽车"""
        canvas.delete('all')
        w, h = 200, 280
        x_center, y_center = w//2, h//2
        
        # 车身
        canvas.create_rectangle(x_center-60, y_center-15, x_center+60, y_center+25, 
                               fill='#e74c3c', outline='#c0392b', width=3)
        # 车顶
        canvas.create_polygon(x_center-45, y_center-15, x_center-35, y_center-40,
                             x_center+35, y_center-40, x_center+45, y_center-15,
                             fill='#e74c3c', outline='#c0392b', width=3)
        # 车窗
        canvas.create_polygon(x_center-40, y_center-13, x_center-33, y_center-35,
                             x_center-5, y_center-35, x_center-5, y_center-13,
                             fill='#3498db', outline='#2980b9', width=2)
        canvas.create_polygon(x_center+5, y_center-13, x_center+5, y_center-35,
                             x_center+33, y_center-35, x_center+40, y_center-13,
                             fill='#3498db', outline='#2980b9', width=2)
        # 车轮
        canvas.create_oval(x_center-50, y_center+15, x_center-30, y_center+35,
                          fill='#2c3e50', outline='#000000', width=2)
        canvas.create_oval(x_center+30, y_center+15, x_center+50, y_center+35,
                          fill='#2c3e50', outline='#000000', width=2)
        # 车轮中心
        canvas.create_oval(x_center-45, y_center+20, x_center-35, y_center+30,
                          fill='#95a5a6', outline='#7f8c8d', width=1)
        canvas.create_oval(x_center+35, y_center+20, x_center+45, y_center+30,
                          fill='#95a5a6', outline='#7f8c8d', width=1)
        # 车灯
        canvas.create_oval(x_center-58, y_center+3, x_center-52, y_center+12,
                          fill='#f1c40f', outline='#f39c12', width=1)
        canvas.create_oval(x_center+52, y_center+3, x_center+58, y_center+12,
                          fill='#f1c40f', outline='#f39c12', width=1)
        # 文字
        canvas.create_text(x_center, y_center+60, text='汽车', 
                          font=(self.door_label_font[0], 16, 'bold'), fill='#27ae60')
    
    def draw_goat(self, canvas):
        """绘制山羊"""
        canvas.delete('all')
        w, h = 200, 280
        x_center, y_center = w//2, h//2
        
        # 身体
        canvas.create_oval(x_center-35, y_center-5, x_center+35, y_center+35,
                          fill='#ecf0f1', outline='#95a5a6', width=3)
        # 头部
        canvas.create_oval(x_center-22, y_center-30, x_center+22, y_center+8,
                          fill='#ecf0f1', outline='#95a5a6', width=3)
        # 耳朵
        canvas.create_polygon(x_center-20, y_center-28, x_center-26, y_center-40,
                             x_center-16, y_center-32, fill='#ecf0f1', outline='#95a5a6', width=2)
        canvas.create_polygon(x_center+20, y_center-28, x_center+26, y_center-40,
                             x_center+16, y_center-32, fill='#ecf0f1', outline='#95a5a6', width=2)
        # 角
        canvas.create_line(x_center-18, y_center-28, x_center-22, y_center-45,
                          fill='#7f8c8d', width=3)
        canvas.create_line(x_center+18, y_center-28, x_center+22, y_center-45,
                          fill='#7f8c8d', width=3)
        # 眼睛
        canvas.create_oval(x_center-13, y_center-20, x_center-7, y_center-14,
                          fill='#2c3e50', outline='#2c3e50', width=1)
        canvas.create_oval(x_center+7, y_center-20, x_center+13, y_center-14,
                          fill='#2c3e50', outline='#2c3e50', width=1)
        # 鼻子
        canvas.create_oval(x_center-4, y_center-8, x_center+4, y_center-3,
                          fill='#34495e', outline='#2c3e50', width=1)
        # 嘴巴
        canvas.create_arc(x_center-8, y_center-8, x_center+8, y_center+3,
                         start=180, extent=180, style='arc', outline='#2c3e50', width=2)
        # 腿
        canvas.create_rectangle(x_center-30, y_center+30, x_center-24, y_center+50,
                               fill='#bdc3c7', outline='#95a5a6', width=2)
        canvas.create_rectangle(x_center-12, y_center+30, x_center-6, y_center+50,
                               fill='#bdc3c7', outline='#95a5a6', width=2)
        canvas.create_rectangle(x_center+6, y_center+30, x_center+12, y_center+50,
                               fill='#bdc3c7', outline='#95a5a6', width=2)
        canvas.create_rectangle(x_center+24, y_center+30, x_center+30, y_center+50,
                               fill='#bdc3c7', outline='#95a5a6', width=2)
        # 尾巴
        canvas.create_line(x_center+33, y_center+8, x_center+43, y_center-2,
                          fill='#7f8c8d', width=3)
        # 文字
        canvas.create_text(x_center, y_center+68, text='山羊',
                          font=(self.door_label_font[0], 16, 'bold'), fill='#95a5a6')
    
    def setup_ui(self):
        """设置用户界面"""
        # 顶部标题
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(fill='x')
        
        tk.Label(
            title_frame,
            text="三门问题游戏",
            font=self.title_font,
            bg='#2c3e50',
            fg='#f1c40f',
            pady=10
        ).pack()
        
        tk.Label(
            title_frame,
            text=f"Monty Hall Problem - {self.os_type}",
            font=('Arial', 10, 'bold'),
            bg='#2c3e50',
            fg='#ffffff',
            pady=5
        ).pack()
        
        # 主容器 - 使用Grid布局
        main_frame = tk.Frame(self.root, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 配置grid权重
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧游戏区
        left_frame = tk.Frame(main_frame, bg='#ecf0f1')
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # 说明文字
        self.info_label = tk.Label(
            left_frame,
            text="请选择一扇门，猜猜汽车在哪里？",
            font=self.info_font,
            fg='#c0392b',
            bg='#ecf0f1',
            wraplength=700,
            justify='center'
        )
        self.info_label.pack(pady=10)
        
        # 门的容器
        doors_frame = tk.Frame(left_frame, bg='#ecf0f1')
        doors_frame.pack(pady=15)
        
        self.door_containers = []
        self.door_frames = []
        self.door_canvases = []
        self.door_labels = []
        
        for i in range(3):
            container = tk.Frame(doors_frame, bg='#ecf0f1')
            container.pack(side='left', padx=15)
            self.door_containers.append(container)
            
            door_frame = tk.Frame(
                container,
                bg='#8b4513',
                relief='raised',
                bd=5,
                width=220,
                height=300
            )
            door_frame.pack()
            door_frame.pack_propagate(False)
            self.door_frames.append(door_frame)
            
            canvas = Canvas(
                door_frame,
                width=200,
                height=280,
                bg='#a0522d',
                highlightthickness=0,
                cursor='hand2'
            )
            canvas.place(relx=0.5, rely=0.5, anchor='center')
            canvas.bind('<Button-1>', lambda e, door=i: self.door_clicked(door))
            canvas.bind('<Enter>', lambda e, door=i: self.on_hover(door, True))
            canvas.bind('<Leave>', lambda e, door=i: self.on_hover(door, False))
            self.door_canvases.append(canvas)
            self.draw_door(canvas)
            
            label = tk.Label(
                container,
                text=f"门 {i+1}",
                font=self.door_label_font,
                fg='#000000',
                bg='#ecf0f1'
            )
            label.pack(pady=8)
            self.door_labels.append(label)
        
        # 控制按钮
        control_frame = tk.Frame(left_frame, bg='#ecf0f1')
        control_frame.pack(pady=15)
        
        button_style = {
            'font': self.button_font,
            'padx': 20,
            'pady': 12,
            'cursor': 'hand2',
            'relief': 'raised',
            'bd': 3
        }
        
        tk.Button(control_frame, text="🔄 新游戏", command=self.new_game,
                 bg='#3498db', fg='#000000', activebackground='#2980b9',
                 **button_style).grid(row=0, column=0, padx=6, pady=6)
        
        tk.Button(control_frame, text="📖 规则", command=self.show_rules,
                 bg='#9b59b6', fg='#000000', activebackground='#8e44ad',
                 **button_style).grid(row=0, column=1, padx=6, pady=6)
        
        self.simulate_btn = tk.Button(
            control_frame, text="🎲 模拟1000次", command=self.auto_simulate,
            bg='#f39c12', fg='#000000', activebackground='#e67e22',
            **button_style
        )
        self.simulate_btn.grid(row=1, column=0, padx=6, pady=6)
        
        tk.Button(control_frame, text="🗑️ 重置", command=self.reset_stats,
                 bg='#e74c3c', fg='#000000', activebackground='#c0392b',
                 **button_style).grid(row=1, column=1, padx=6, pady=6)
        
        # 右侧统计区
        right_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=2)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="📊 实时统计",
            font=(self.text_font[0], 14, 'bold'),
            bg='white',
            fg='#000000',
            pady=10
        ).pack()
        
        self.stats_label = tk.Label(
            right_frame,
            text="",
            font=self.text_font,
            bg='white',
            fg='#000000',
            justify='center'
        )
        self.stats_label.pack(pady=5)
        
        # 进度条
        progress_frame = tk.Frame(right_frame, bg='white')
        progress_frame.pack(pady=10, padx=15, fill='x')
        
        stay_frame = tk.Frame(progress_frame, bg='white')
        stay_frame.pack(fill='x', pady=5)
        
        tk.Label(stay_frame, text="坚持:", font=self.text_font,
                bg='white', fg='#c0392b', width=5).pack(side='left')
        
        self.stay_progress = ttk.Progressbar(
            stay_frame, length=180, mode='determinate',
            style='Stay.Horizontal.TProgressbar'
        )
        self.stay_progress.pack(side='left', padx=5)
        
        self.stay_percent_label = tk.Label(
            stay_frame, text="0.0%", font=self.text_font,
            bg='white', fg='#c0392b', width=6
        )
        self.stay_percent_label.pack(side='left')
        
        switch_frame = tk.Frame(progress_frame, bg='white')
        switch_frame.pack(fill='x', pady=5)
        
        tk.Label(switch_frame, text="换门:", font=self.text_font,
                bg='white', fg='#229954', width=5).pack(side='left')
        
        self.switch_progress = ttk.Progressbar(
            switch_frame, length=180, mode='determinate',
            style='Switch.Horizontal.TProgressbar'
        )
        self.switch_progress.pack(side='left', padx=5)
        
        self.switch_percent_label = tk.Label(
            switch_frame, text="0.0%", font=self.text_font,
            bg='white', fg='#229954', width=6
        )
        self.switch_percent_label.pack(side='left')
        
        tk.Label(
            right_frame,
            text="💡 理论: 坚持33.3% | 换门66.7%",
            font=(self.text_font[0], 10, 'bold'),
            bg='white',
            fg='#d35400',
            wraplength=280
        ).pack(pady=8)
        
        # 图表
        chart_frame = tk.Frame(right_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.figure = Figure(figsize=(3.5, 2.8), dpi=80, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.update_chart()
        
        # 样式
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Stay.Horizontal.TProgressbar', 
                       background='#e74c3c', troughcolor='#ecf0f1',
                       borderwidth=0, thickness=18)
        style.configure('Switch.Horizontal.TProgressbar', 
                       background='#27ae60', troughcolor='#ecf0f1',
                       borderwidth=0, thickness=18)
        
        self.update_stats_display()
    
    def on_hover(self, door, entering):
        """悬停效果"""
        if self.game_stage < 2 and door != self.opened_door:
            if entering:
                self.door_frames[door].config(bg='#a0522d', relief='sunken')
            else:
                if door == self.first_choice:
                    self.door_frames[door].config(bg='#f39c12', relief='sunken')
                else:
                    self.door_frames[door].config(bg='#8b4513', relief='raised')
    
    def update_chart(self):
        """更新图表"""
        self.ax.clear()
        
        if len(self.history['stay_rates']) > 0:
            games = list(range(1, len(self.history['stay_rates']) + 1))
            self.ax.plot(games, self.history['stay_rates'], 
                        label='坚持', color='#e74c3c', linewidth=2, marker='o', markersize=4)
            self.ax.plot(games, self.history['switch_rates'], 
                        label='换门', color='#27ae60', linewidth=2, marker='s', markersize=4)
            
            self.ax.axhline(y=33.3, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5)
            self.ax.axhline(y=66.7, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5)
            
            self.ax.set_xlabel('局数', fontsize=9, fontweight='bold')
            self.ax.set_ylabel('胜率(%)', fontsize=9, fontweight='bold')
            self.ax.set_title('胜率趋势', fontsize=10, fontweight='bold')
            self.ax.legend(fontsize=8, loc='best')
            self.ax.grid(True, alpha=0.3, linestyle='--')
            self.ax.set_ylim(0, 100)
        else:
            self.ax.text(0.5, 0.5, '开始游戏后\n显示趋势图', 
                        ha='center', va='center', fontsize=11, color='#2c3e50')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
        
        self.canvas.draw()
    
    def new_game(self):
        """开始新游戏"""
        self.car_door = random.randint(0, 2)
        self.first_choice = None
        self.opened_door = None
        self.game_stage = 0
        
        for i in range(3):
            self.draw_door(self.door_canvases[i])
            self.door_frames[i].config(bg='#8b4513', relief='raised')
            self.door_labels[i].config(text=f"门 {i+1}", fg='#000000')
        
        self.info_label.config(text="请选择一扇门，猜猜汽车在哪里？", fg='#c0392b')
    
    def door_clicked(self, door):
        """门被点击"""
        if self.game_stage == 0:
            self.first_choice = door
            self.door_frames[door].config(bg='#f39c12', relief='sunken')
            self.door_labels[door].config(text=f"门 {door+1} ✓", fg='#f39c12')
            self.info_label.config(text="主持人正在打开一扇门...", fg='#e67e22')
            self.root.after(1200, self.open_goat_door)
            
        elif self.game_stage == 1:
            if door == self.opened_door:
                return
            
            switched = (door != self.first_choice)
            won = (door == self.car_door)
            
            if switched:
                self.door_frames[self.first_choice].config(bg='#8b4513', relief='raised')
                self.door_labels[self.first_choice].config(text=f"门 {self.first_choice+1}", fg='#7f8c8d')
                self.door_frames[door].config(bg='#f39c12', relief='sunken')
                self.door_labels[door].config(text=f"门 {door+1} ✓", fg='#f39c12')
            
            if switched:
                self.stats['switch_total'] += 1
                if won:
                    self.stats['switch_wins'] += 1
            else:
                self.stats['stay_total'] += 1
                if won:
                    self.stats['stay_wins'] += 1
            
            self.info_label.config(text="正在揭晓答案...", fg='#3498db')
            self.root.after(800, lambda: self.show_result(door, switched, won))
    
    def open_goat_door(self):
        """主持人打开山羊门"""
        available = [i for i in range(3) if i != self.first_choice and i != self.car_door]
        if not available:
            available = [i for i in range(3) if i != self.first_choice]
        
        self.opened_door = random.choice(available)
        
        self.draw_goat(self.door_canvases[self.opened_door])
        self.door_frames[self.opened_door].config(bg='#95a5a6', relief='flat')
        
        other = [i for i in range(3) if i != self.first_choice and i != self.opened_door][0]
        self.info_label.config(
            text=f"主持人打开了门{self.opened_door+1}是山羊！\n坚持门{self.first_choice+1} 或 换到门{other+1}？",
            fg='#e67e22'
        )
        
        self.game_stage = 1
    
    def show_result(self, final, switched, won):
        """显示结果"""
        self.game_stage = 2
        
        for i in range(3):
            if i == self.car_door:
                self.draw_car(self.door_canvases[i])
                self.door_frames[i].config(
                    bg='#27ae60' if won else '#e74c3c',
                    relief='flat'
                )
                self.door_labels[i].config(text=f"门{i+1}(汽车!)", fg='#27ae60')
            elif i != self.opened_door:
                self.draw_goat(self.door_canvases[i])
                self.door_frames[i].config(bg='#95a5a6', relief='flat')
                self.door_labels[i].config(text=f"门{i+1}(山羊)", fg='#7f8c8d')
        
        action = "换门" if switched else "坚持"
        if won:
            result = f"🎉 恭喜！{action}策略赢得汽车！"
            color = '#27ae60'
        else:
            result = f"遗憾！{action}策略得到山羊..."
            color = '#e74c3c'
        
        self.info_label.config(text=f"{result}\n点击'新游戏'继续", fg=color)
        self.update_stats_display()
    
    def update_stats_display(self):
        """更新统计"""
        stay_rate = (self.stats['stay_wins'] / self.stats['stay_total'] * 100 
                    if self.stats['stay_total'] > 0 else 0)
        switch_rate = (self.stats['switch_wins'] / self.stats['switch_total'] * 100 
                      if self.stats['switch_total'] > 0 else 0)
        
        total = self.stats['stay_total'] + self.stats['switch_total']
        
        self.stats_label.config(
            text=f"总局数: {total}\n坚持: {self.stats['stay_wins']}/{self.stats['stay_total']}\n换门: {self.stats['switch_wins']}/{self.stats['switch_total']}"
        )
        
        self.stay_progress['value'] = stay_rate
        self.switch_progress['value'] = switch_rate
        self.stay_percent_label.config(text=f"{stay_rate:.1f}%")
        self.switch_percent_label.config(text=f"{switch_rate:.1f}%")
        
        if total > 0:
            self.history['stay_rates'].append(stay_rate)
            self.history['switch_rates'].append(switch_rate)
            
            if len(self.history['stay_rates']) > 50:
                self.history['stay_rates'] = self.history['stay_rates'][-50:]
                self.history['switch_rates'] = self.history['switch_rates'][-50:]
            
            self.update_chart()
    
    def reset_stats(self):
        """重置统计"""
        if messagebox.askyesno("确认", "确定重置统计数据吗？"):
            self.stats = {
                'stay_wins': 0,
                'stay_total': 0,
                'switch_wins': 0,
                'switch_total': 0
            }
            self.history = {
                'stay_rates': [],
                'switch_rates': []
            }
            self.update_stats_display()
            messagebox.showinfo("完成", "统计已重置！")
    
    def show_rules(self):
        """显示规则"""
        messagebox.showinfo(
            "游戏规则",
            "【三门问题】\n\n"
            "1. 选择一扇门\n"
            "2. 主持人打开一扇有山羊的门\n"
            "3. 选择坚持或换门\n\n"
            "【概率分析】\n"
            "坚持: 33.3%\n"
            "换门: 66.7%\n\n"
            "换门策略胜率更高！"
        )
    
    def auto_simulate(self):
        """自动模拟"""
        if self.simulating:
            messagebox.showwarning("提示", "模拟进行中...")
            return
        
        def run():
            self.simulating = True
            self.simulate_btn.config(state='disabled', text='模拟中...')
            
            rounds = 1000
            stay_wins = 0
            switch_wins = 0
            
            for i in range(rounds):
                car = random.randint(0, 2)
                choice = random.randint(0, 2)
                
                avail = [d for d in range(3) if d != choice and d != car]
                if not avail:
                    avail = [d for d in range(3) if d != choice]
                opened = random.choice(avail)
                
                other = [d for d in range(3) if d != choice and d != opened][0]
                
                if choice == car:
                    stay_wins += 1
                if other == car:
                    switch_wins += 1
                
                if (i + 1) % 100 == 0:
                    self.stats['stay_total'] += 100
                    self.stats['stay_wins'] += stay_wins
                    self.stats['switch_total'] += 100
                    self.stats['switch_wins'] += switch_wins
                    
                    self.root.after(0, self.update_stats_display)
                    
                    stay_wins = 0
                    switch_wins = 0
                    time.sleep(0.05)
            
            self.simulating = False
            self.root.after(0, lambda: self.simulate_btn.config(state='normal', text='🎲 模拟1000次'))
            
            final_stay = self.stats['stay_wins'] / self.stats['stay_total'] * 100
            final_switch = self.stats['switch_wins'] / self.stats['switch_total'] * 100
            
            self.root.after(0, lambda: messagebox.showinfo(
                "模拟完成", 
                f"完成{rounds}次模拟！\n\n"
                f"坚持胜率: {final_stay:.2f}%\n"
                f"换门胜率: {final_switch:.2f}%\n\n"
                f"理论值: 33.3% vs 66.7%"
            ))
        
        threading.Thread(target=run, daemon=True).start()


def main():
    root = tk.Tk()
    app = MontyHallGame(root)
    root.mainloop()


if __name__ == '__main__':
    main()





