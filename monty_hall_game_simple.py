#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三门问题游戏 - 简化真实版
使用系统emoji表情符号，更真实生动
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import threading
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 配置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False


class MontyHallGame:
    def __init__(self, root):
        self.root = root
        self.root.title("三门问题游戏 - Monty Hall Problem")
        self.root.geometry("1200x900")
        self.root.resizable(False, False)
        self.root.configure(bg='#ecf0f1')
        
        # 游戏状态
        self.car_door = 0
        self.first_choice = None
        self.opened_door = None
        self.game_stage = 0
        self.simulating = False
        self.hovering_door = None
        
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
        
        # 存储图片引用
        self.images = {}
        
        self.setup_ui()
        self.new_game()
    
    def create_door_image(self, state='normal', glow=False):
        """创建门的图片"""
        img = Image.new('RGBA', (180, 280), (236, 240, 241, 0))
        draw = ImageDraw.Draw(img)
        
        # 发光效果
        if glow and state == 'normal':
            for i in range(8):
                alpha = 60 - i * 7
                offset = i * 2
                draw.rectangle([5-offset, 5-offset, 175+offset, 275+offset], 
                             outline=(52, 152, 219, alpha), width=2)
        
        if state == 'normal':
            # 阴影
            draw.rectangle([8, 8, 178, 278], fill=(52, 73, 94, 100))
            # 门框
            draw.rectangle([5, 5, 175, 275], fill=(101, 67, 33), outline=(70, 50, 30), width=4)
            draw.rectangle([15, 15, 165, 265], fill=(139, 69, 19), outline=(70, 50, 30), width=3)
            # 上下门板
            draw.rectangle([25, 25, 155, 135], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            for i in range(30, 150, 15):
                draw.line([i, 30, i, 130], fill=(139, 69, 19), width=2)
            draw.rectangle([25, 145, 155, 255], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            for i in range(30, 150, 15):
                draw.line([i, 150, i, 250], fill=(139, 69, 19), width=2)
            # 门把手
            draw.ellipse([125, 137, 145, 157], fill=(150, 100, 0))
            draw.ellipse([120, 132, 140, 152], fill=(255, 215, 0), outline=(218, 165, 32), width=3)
            draw.ellipse([123, 135, 133, 145], fill=(255, 255, 200))
            
        elif state == 'selected':
            # 发光选中门
            for i in range(6):
                alpha = 120 - i * 20
                draw.rectangle([5-i*3, 5-i*3, 175+i*3, 275+i*3], 
                             outline=(243, 156, 18, alpha), width=4)
            draw.rectangle([5, 5, 175, 275], fill=(243, 156, 18), outline=(230, 126, 34), width=5)
            draw.rectangle([15, 15, 165, 265], fill=(245, 176, 65), outline=(230, 126, 34), width=3)
            draw.rectangle([25, 25, 155, 135], fill=(249, 191, 59), outline=(243, 156, 18), width=3)
            draw.rectangle([25, 145, 155, 255], fill=(249, 191, 59), outline=(243, 156, 18), width=3)
            draw.ellipse([125, 137, 145, 157], fill=(200, 150, 0))
            draw.ellipse([120, 132, 140, 152], fill=(255, 215, 0), outline=(218, 165, 32), width=3)
            draw.ellipse([123, 135, 133, 145], fill=(255, 255, 200))
            # 问号
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 55)
                draw.text((77, 72), "?", fill=(0, 0, 0, 100), font=font, anchor="mm")
                draw.text((75, 70), "?", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=2, stroke_fill=(230, 126, 34))
                draw.text((77, 192), "?", fill=(0, 0, 0, 100), font=font, anchor="mm")
                draw.text((75, 190), "?", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=2, stroke_fill=(230, 126, 34))
            except:
                pass
        
        return ImageTk.PhotoImage(img)
    
    def create_goat_image(self):
        """创建真实的山羊图片 - 使用超大emoji"""
        img = Image.new('RGBA', (180, 280), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 天空渐变背景
        for i in range(240):
            ratio = i / 240
            r = int(135 + (200 - 135) * ratio)
            g = int(206 + (230 - 206) * ratio)
            b = int(250 + (255 - 250) * ratio)
            draw.line([(0, i), (180, i)], fill=(r, g, b))
        
        # 草地
        for i in range(240, 280):
            ratio = (i - 240) / 40
            r = int(46 + 10 * ratio)
            g = int(204 - 20 * ratio)
            b = int(113 - 10 * ratio)
            draw.line([(0, i), (180, i)], fill=(r, g, b))
        
        # 超大emoji山羊
        try:
            emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 140)
            draw.text((90, 120), "🐐", font=emoji_font, anchor="mm", embedded_color=True)
        except:
            # 备用
            try:
                emoji_font = ImageFont.truetype("/System/Library/Fonts/AppleColorEmoji.ttf", 140)
                draw.text((90, 120), "🐐", font=emoji_font, anchor="mm")
            except:
                # 最终备用
                draw.text((90, 120), "🐐", font=None, anchor="mm")
        
        # 文字
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
            draw.text((92, 267), "山羊", fill=(0, 0, 0, 80), font=font, anchor="mm")
            draw.text((90, 265), "山羊", fill=(52, 73, 94), font=font, anchor="mm", 
                     stroke_width=1, stroke_fill=(255, 255, 255))
        except:
            draw.text((90, 265), "山羊", fill=(52, 73, 94), anchor="mm")
        
        return ImageTk.PhotoImage(img)
    
    def create_car_image(self, won=True):
        """创建真实的汽车图片 - 使用超大emoji"""
        if won:
            bg_color = (46, 204, 113)
        else:
            bg_color = (220, 230, 240)
        
        img = Image.new('RGBA', (180, 280), bg_color + (255,))
        draw = ImageDraw.Draw(img)
        
        # 背景渐变
        for i in range(220):
            factor = 1 - (i / 220) * 0.2
            r, g, b = bg_color
            color = (int(r*factor), int(g*factor), int(b*factor))
            draw.line([(0, i), (180, i)], fill=color)
        
        # 地面
        for i in range(220, 280):
            ratio = (i - 220) / 60
            gray = int(100 + 50 * ratio)
            draw.line([(0, i), (180, i)], fill=(gray, gray, gray+10))
        
        if won:
            # 庆祝气球
            random.seed(123)
            for i in range(6):
                x = 15 + i * 28
                y = 15 + random.randint(0, 30)
                balloon_color = [(255, 100, 100), (255, 200, 50), (100, 150, 255), 
                               (255, 150, 200), (150, 255, 150), (255, 180, 100)][i]
                draw.ellipse([x, y, x+15, y+20], fill=balloon_color, outline=(200, 200, 200), width=2)
                draw.ellipse([x+3, y+2, x+10, y+8], fill=(255, 255, 255, 120))
                draw.line([x+7, y+20, x+7, y+35], fill=(150, 150, 150), width=2)
        
        # 超大emoji汽车
        try:
            emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 140)
            draw.text((90, 120), "🚗", font=emoji_font, anchor="mm", embedded_color=True)
        except:
            # 备用
            try:
                emoji_font = ImageFont.truetype("/System/Library/Fonts/AppleColorEmoji.ttf", 140)
                draw.text((90, 120), "🚗", font=emoji_font, anchor="mm")
            except:
                # 最终备用
                draw.text((90, 120), "🚗", font=None, anchor="mm")
        
        # 文字
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
            if won:
                draw.text((91, 252), "🎉 汽车！", fill=(0, 0, 0, 50), font=font, anchor="mm")
                draw.text((90, 250), "🎉 汽车！", fill=(255, 255, 255), font=font, anchor="mm", 
                         stroke_width=2, stroke_fill=(52, 73, 94))
            else:
                draw.text((91, 252), "汽车", fill=(0, 0, 0, 50), font=font, anchor="mm")
                draw.text((90, 250), "汽车", fill=(127, 140, 141), font=font, anchor="mm")
        except:
            text = "🎉 汽车！" if won else "汽车"
            draw.text((90, 250), text, fill=(255, 255, 255) if won else (127, 140, 141), anchor="mm")
        
        return ImageTk.PhotoImage(img)
    
    def setup_ui(self):
        """设置用户界面"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=90)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🚗 三门问题游戏 🐐",
            font=('Arial', 26, 'bold'),
            bg='#2c3e50',
            fg='#f1c40f'
        )
        title_label.pack(pady=10)
        
        subtitle = tk.Label(
            title_frame,
            text="Monty Hall Problem - 换门还是不换？用数据说话！",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        subtitle.pack()
        
        # 创建主容器
        main_container = tk.Frame(self.root, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧游戏区域
        left_frame = tk.Frame(main_container, bg='#ecf0f1')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 说明文字
        self.info_label = tk.Label(
            left_frame,
            text="请选择一扇门，猜猜汽车在哪里？",
            font=('Arial', 15, 'bold'),
            fg='#c0392b',
            bg='#ecf0f1',
            wraplength=700,
            justify='center',
            height=3
        )
        self.info_label.pack(pady=10)
        
        # 门的容器
        doors_frame = tk.Frame(left_frame, bg='#ecf0f1')
        doors_frame.pack(pady=15)
        
        self.door_labels_widgets = []
        self.door_image_labels = []
        
        for i in range(3):
            door_container = tk.Frame(doors_frame, bg='#ecf0f1')
            door_container.pack(side='left', padx=25)
            
            # 图片标签
            img_label = tk.Label(door_container, bg='#ecf0f1', cursor='hand2')
            img_label.pack()
            img_label.bind('<Button-1>', lambda e, door=i: self.door_clicked(door))
            img_label.bind('<Enter>', lambda e, door=i: self.on_door_hover(door, True))
            img_label.bind('<Leave>', lambda e, door=i: self.on_door_hover(door, False))
            self.door_image_labels.append(img_label)
            
            # 门号标签
            label = tk.Label(
                door_container,
                text=f"门 {i+1}",
                font=('Arial', 18, 'bold'),
                fg='#000000',
                bg='#ecf0f1'
            )
            label.pack(pady=8)
            self.door_labels_widgets.append(label)
        
        # 控制按钮区域
        control_frame = tk.Frame(left_frame, bg='#ecf0f1')
        control_frame.pack(pady=15)
        
        button_style = {
            'font': ('Arial', 13, 'bold'),
            'padx': 24,
            'pady': 14,
            'cursor': 'hand2',
            'relief': 'raised',
            'bd': 4
        }
        
        self.new_game_btn = tk.Button(
            control_frame,
            text="🔄 新游戏",
            command=self.new_game,
            bg='#3498db',
            fg='#000000',
            activebackground='#2980b9',
            activeforeground='#000000',
            **button_style
        )
        self.new_game_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.rules_btn = tk.Button(
            control_frame,
            text="📖 游戏规则",
            command=self.show_rules,
            bg='#9b59b6',
            fg='#000000',
            activebackground='#8e44ad',
            activeforeground='#000000',
            **button_style
        )
        self.rules_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.simulate_btn = tk.Button(
            control_frame,
            text="🎲 模拟1000次",
            command=self.auto_simulate,
            bg='#f39c12',
            fg='#000000',
            activebackground='#e67e22',
            activeforeground='#000000',
            **button_style
        )
        self.simulate_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.reset_stats_btn = tk.Button(
            control_frame,
            text="🗑️ 重置统计",
            command=self.reset_stats,
            bg='#e74c3c',
            fg='#000000',
            activebackground='#c0392b',
            activeforeground='#000000',
            **button_style
        )
        self.reset_stats_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # 右侧统计区域
        right_frame = tk.Frame(main_container, bg='white', relief='solid', bd=2, width=400)
        right_frame.pack(side='right', fill='both', padx=(10, 0))
        right_frame.pack_propagate(False)
        
        stats_title = tk.Label(
            right_frame,
            text="📊 实时统计分析",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#000000'
        )
        stats_title.pack(pady=10)
        
        self.stats_label = tk.Label(
            right_frame,
            text="",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#000000',
            justify='center'
        )
        self.stats_label.pack(pady=5)
        
        # 进度条
        progress_container = tk.Frame(right_frame, bg='white')
        progress_container.pack(pady=10, padx=15, fill='x')
        
        stay_frame = tk.Frame(progress_container, bg='white')
        stay_frame.pack(fill='x', pady=5)
        
        tk.Label(
            stay_frame,
            text="坚持:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#c0392b',
            width=6
        ).pack(side='left')
        
        self.stay_progress = ttk.Progressbar(
            stay_frame,
            length=220,
            mode='determinate',
            style='Stay.Horizontal.TProgressbar'
        )
        self.stay_progress.pack(side='left', padx=5)
        
        self.stay_percent_label = tk.Label(
            stay_frame,
            text="0.0%",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#c0392b',
            width=7
        )
        self.stay_percent_label.pack(side='left')
        
        switch_frame = tk.Frame(progress_container, bg='white')
        switch_frame.pack(fill='x', pady=5)
        
        tk.Label(
            switch_frame,
            text="换门:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#229954',
            width=6
        ).pack(side='left')
        
        self.switch_progress = ttk.Progressbar(
            switch_frame,
            length=220,
            mode='determinate',
            style='Switch.Horizontal.TProgressbar'
        )
        self.switch_progress.pack(side='left', padx=5)
        
        self.switch_percent_label = tk.Label(
            switch_frame,
            text="0.0%",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#229954',
            width=7
        )
        self.switch_percent_label.pack(side='left')
        
        # 理论值
        theory_label = tk.Label(
            right_frame,
            text="💡 理论: 坚持33.3% | 换门66.7%",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#d35400'
        )
        theory_label.pack(pady=5)
        
        # 统计图表
        chart_frame = tk.Frame(right_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.figure = Figure(figsize=(4, 3), dpi=80, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.update_chart()
        
        # 配置进度条样式
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Stay.Horizontal.TProgressbar', 
                       background='#e74c3c', 
                       troughcolor='#ecf0f1',
                       borderwidth=0,
                       thickness=18)
        style.configure('Switch.Horizontal.TProgressbar', 
                       background='#27ae60', 
                       troughcolor='#ecf0f1',
                       borderwidth=0,
                       thickness=18)
        
        self.update_stats_display()
    
    def on_door_hover(self, door, entering):
        """门的悬停效果"""
        if self.game_stage < 2 and door != self.opened_door:
            if entering:
                self.hovering_door = door
                if door != self.first_choice:
                    img = self.create_door_image('normal', glow=True)
                    self.images[f'door_{door}_hover'] = img
                    self.door_image_labels[door].config(image=img)
            else:
                self.hovering_door = None
                if door != self.first_choice:
                    img = self.create_door_image('normal')
                    self.images[f'door_{door}'] = img
                    self.door_image_labels[door].config(image=img)
    
    def update_chart(self):
        """更新统计图表"""
        self.ax.clear()
        
        if len(self.history['stay_rates']) > 0:
            games = list(range(1, len(self.history['stay_rates']) + 1))
            self.ax.plot(games, self.history['stay_rates'], 
                        label='坚持原选择', color='#e74c3c', linewidth=2, marker='o', markersize=4)
            self.ax.plot(games, self.history['switch_rates'], 
                        label='换门策略', color='#27ae60', linewidth=2, marker='s', markersize=4)
            
            # 理论线
            self.ax.axhline(y=33.3, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5)
            self.ax.axhline(y=66.7, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5)
            
            self.ax.set_xlabel('游戏局数', fontsize=10, fontweight='bold')
            self.ax.set_ylabel('胜率 (%)', fontsize=10, fontweight='bold')
            self.ax.set_title('胜率趋势图', fontsize=11, fontweight='bold', color='#2c3e50')
            self.ax.legend(fontsize=9, loc='best', frameon=True, shadow=True)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_ylim(0, 100)
        else:
            self.ax.text(0.5, 0.5, '开始游戏后\n将显示胜率趋势', 
                        ha='center', va='center', fontsize=12, color='#2c3e50', fontweight='bold')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
        
        self.canvas.draw()
    
    def new_game(self):
        """开始新游戏"""
        self.car_door = random.randint(0, 2)
        self.first_choice = None
        self.opened_door = None
        self.game_stage = 0
        self.hovering_door = None
        
        # 创建并显示门的图片
        for i, img_label in enumerate(self.door_image_labels):
            img = self.create_door_image('normal')
            self.images[f'door_{i}'] = img
            img_label.config(image=img)
            
            self.door_labels_widgets[i].config(
                text=f"门 {i+1}",
                fg='#000000',
                font=('Arial', 18, 'bold')
            )
        
        self.info_label.config(
            text="请选择一扇门，猜猜汽车在哪里？",
            fg='#c0392b'
        )
    
    def door_clicked(self, door):
        """处理门被点击"""
        if self.game_stage == 0:
            # 第一次选择
            self.first_choice = door
            img = self.create_door_image('selected')
            self.images[f'door_{door}_selected'] = img
            self.door_image_labels[door].config(image=img)
            self.door_labels_widgets[door].config(text=f"门 {door+1} ✓", fg='#f39c12')
            
            self.info_label.config(text="主持人正在打开一扇门...", fg='#e67e22')
            
            # 延迟后主持人打开门
            self.root.after(1200, self.open_goat_door)
            
        elif self.game_stage == 1:
            # 第二次选择
            if door == self.opened_door:
                return
            
            final_choice = door
            switched = (final_choice != self.first_choice)
            won = (final_choice == self.car_door)
            
            # 更新选择标记
            if switched:
                img = self.create_door_image('normal')
                self.images[f'door_{self.first_choice}_back'] = img
                self.door_image_labels[self.first_choice].config(image=img)
                self.door_labels_widgets[self.first_choice].config(
                    text=f"门 {self.first_choice+1}",
                    fg='#7f8c8d'
                )
                
                img = self.create_door_image('selected')
                self.images[f'door_{final_choice}_selected'] = img
                self.door_image_labels[final_choice].config(image=img)
                self.door_labels_widgets[final_choice].config(
                    text=f"门 {final_choice+1} ✓",
                    fg='#f39c12'
                )
            
            # 更新统计
            if switched:
                self.stats['switch_total'] += 1
                if won:
                    self.stats['switch_wins'] += 1
            else:
                self.stats['stay_total'] += 1
                if won:
                    self.stats['stay_wins'] += 1
            
            self.info_label.config(text="正在揭晓答案...", fg='#3498db')
            
            # 延迟显示结果
            self.root.after(800, lambda: self.show_result(final_choice, switched, won))
    
    def open_goat_door(self):
        """主持人打开一扇有山羊的门"""
        available_doors = [i for i in range(3) 
                          if i != self.first_choice and i != self.car_door]
        
        if not available_doors:
            available_doors = [i for i in range(3) 
                              if i != self.first_choice]
        
        self.opened_door = random.choice(available_doors)
        
        # 显示山羊
        img = self.create_goat_image()
        self.images[f'goat_{self.opened_door}'] = img
        self.door_image_labels[self.opened_door].config(image=img)
        self.door_labels_widgets[self.opened_door].config(
            text=f"门 {self.opened_door+1} (山羊)",
            fg='#95a5a6',
            font=('Arial', 14)
        )
        
        # 更新提示
        other_door = [i for i in range(3) 
                     if i != self.first_choice and i != self.opened_door][0]
        
        self.info_label.config(
            text=f"主持人打开了门 {self.opened_door+1}，里面是山羊！🐐\n"
                 f"你可以坚持门 {self.first_choice+1}，或换到门 {other_door+1}\n"
                 f"请点击你的最终选择！",
            fg='#e67e22'
        )
        
        self.game_stage = 1
    
    def show_result(self, final_choice, switched, won):
        """显示游戏结果"""
        self.game_stage = 2
        
        # 显示所有门后的内容
        for i in range(3):
            if i == self.car_door:
                img = self.create_car_image(won)
                self.images[f'car_{i}'] = img
                self.door_image_labels[i].config(image=img)
                self.door_labels_widgets[i].config(
                    text=f"门 {i+1} (汽车!)",
                    fg='#27ae60',
                    font=('Arial', 16, 'bold')
                )
            elif i != self.opened_door:
                img = self.create_goat_image()
                self.images[f'goat_{i}'] = img
                self.door_image_labels[i].config(image=img)
                self.door_labels_widgets[i].config(
                    text=f"门 {i+1} (山羊)",
                    fg='#7f8c8d',
                    font=('Arial', 14)
                )
        
        # 更新提示
        action = "换门" if switched else "坚持原选择"
        if won:
            result = f"🎉🎉 恭喜你！你选择了{action}，赢得了汽车！🚗🚗"
            color = '#27ae60'
        else:
            result = f"😢 很遗憾！你选择了{action}，得到了山羊...🐐"
            color = '#e74c3c'
        
        self.info_label.config(
            text=f"{result}\n点击'新游戏'继续挑战",
            fg=color
        )
        
        self.update_stats_display()
    
    def update_stats_display(self):
        """更新统计显示"""
        stay_rate = (self.stats['stay_wins'] / self.stats['stay_total'] * 100 
                    if self.stats['stay_total'] > 0 else 0)
        switch_rate = (self.stats['switch_wins'] / self.stats['switch_total'] * 100 
                      if self.stats['switch_total'] > 0 else 0)
        
        total_games = self.stats['stay_total'] + self.stats['switch_total']
        
        stats_text = (
            f"总局数: {total_games}\n"
            f"坚持: {self.stats['stay_wins']}/{self.stats['stay_total']}\n"
            f"换门: {self.stats['switch_wins']}/{self.stats['switch_total']}"
        )
        
        self.stats_label.config(text=stats_text)
        
        # 更新进度条
        self.stay_progress['value'] = stay_rate
        self.switch_progress['value'] = switch_rate
        self.stay_percent_label.config(text=f"{stay_rate:.1f}%")
        self.switch_percent_label.config(text=f"{switch_rate:.1f}%")
        
        # 更新历史数据
        if total_games > 0:
            self.history['stay_rates'].append(stay_rate)
            self.history['switch_rates'].append(switch_rate)
            
            # 限制历史数据长度
            if len(self.history['stay_rates']) > 50:
                self.history['stay_rates'] = self.history['stay_rates'][-50:]
                self.history['switch_rates'] = self.history['switch_rates'][-50:]
            
            self.update_chart()
    
    def reset_stats(self):
        """重置统计数据"""
        if messagebox.askyesno("确认重置", "确定要重置所有统计数据吗？"):
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
            messagebox.showinfo("完成", "统计数据已重置！")
    
    def show_rules(self):
        """显示游戏规则"""
        rules = """
🎮 三门问题游戏规则

【背景故事】
你参加一个游戏节目，面前有三扇门。
其中一扇门后面是汽车🚗，另外两扇门后面是山羊🐐。

【游戏流程】
1️⃣ 你选择一扇门（但不打开）
2️⃣ 主持人知道哪扇门后面是汽车，他会打开剩余两扇门中有山羊的一扇
3️⃣ 主持人问你：要坚持原来的选择，还是换到另一扇未打开的门？
4️⃣ 你做出最终选择并打开门

【关键问题】
换门会提高获胜概率吗？

【概率分析】
• 坚持原选择：获胜概率 = 1/3 ≈ 33.3%
• 换门策略：获胜概率 = 2/3 ≈ 66.7%

【为什么换门更好？】
初始选中汽车的概率是1/3，选中山羊的概率是2/3。
当你选中山羊时（2/3概率），主持人必然打开另一只山羊，
此时换门必定获得汽车！
所以换门的获胜概率是2/3。

【验证方法】
1. 多玩几局，观察"实时统计分析"中的胜率趋势图
2. 使用"模拟1000次"功能进行大量实验
3. 你会看到换门策略的胜率确实接近66.7%！

这个反直觉的结果正是三门问题的精髓所在！
        """
        
        rules_window = tk.Toplevel(self.root)
        rules_window.title("游戏规则说明")
        rules_window.geometry("580x720")
        rules_window.resizable(False, False)
        rules_window.configure(bg='#ecf0f1')
        
        title = tk.Label(
            rules_window,
            text="📖 三门问题 - 游戏规则",
            font=('Arial', 18, 'bold'),
            bg='#3498db',
            fg='#000000',
            pady=15
        )
        title.pack(fill='x')
        
        text_widget = tk.Text(
            rules_window,
            font=('Arial', 12),
            wrap='word',
            padx=25,
            pady=20,
            bg='#ecf0f1',
            fg='#2c3e50',
            relief='flat'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', rules)
        text_widget.config(state='disabled')
        
        close_btn = tk.Button(
            rules_window,
            text="关闭",
            font=('Arial', 14, 'bold'),
            command=rules_window.destroy,
            bg='#3498db',
            fg='#000000',
            padx=40,
            pady=14,
            cursor='hand2',
            relief='raised',
            bd=4,
            activebackground='#2980b9',
            activeforeground='#000000'
        )
        close_btn.pack(pady=15)
    
    def auto_simulate(self):
        """自动模拟多局游戏"""
        if self.simulating:
            messagebox.showwarning("提示", "模拟正在进行中，请稍候...")
            return
        
        def run_simulation():
            self.simulating = True
            self.simulate_btn.config(state='disabled', text='模拟中...')
            
            rounds = 1000
            stay_wins = 0
            switch_wins = 0
            
            for i in range(rounds):
                car_door = random.randint(0, 2)
                first_choice = random.randint(0, 2)
                
                available_doors = [d for d in range(3) 
                                  if d != first_choice and d != car_door]
                if not available_doors:
                    available_doors = [d for d in range(3) if d != first_choice]
                opened_door = random.choice(available_doors)
                
                other_door = [d for d in range(3) 
                             if d != first_choice and d != opened_door][0]
                
                if first_choice == car_door:
                    stay_wins += 1
                
                if other_door == car_door:
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
            self.root.after(0, lambda: self.simulate_btn.config(
                state='normal', 
                text='🎲 模拟1000次'
            ))
            
            final_stay_rate = self.stats['stay_wins']/self.stats['stay_total']*100
            final_switch_rate = self.stats['switch_wins']/self.stats['switch_total']*100
            
            self.root.after(0, lambda: messagebox.showinfo(
                "模拟完成", 
                f"已完成{rounds}次模拟！\n\n"
                f"坚持原选择胜率: {final_stay_rate:.2f}%\n"
                f"换门策略胜率: {final_switch_rate:.2f}%\n\n"
                f"理论值: 33.3% vs 66.7%\n"
                f"误差: {abs(final_stay_rate-33.3):.2f}% vs {abs(final_switch_rate-66.7):.2f}%\n\n"
                "看！实验结果接近理论值！"
            ))
        
        thread = threading.Thread(target=run_simulation, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    app = MontyHallGame(root)
    root.mainloop()


if __name__ == '__main__':
    main()
