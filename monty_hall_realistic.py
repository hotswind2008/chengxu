#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三门问题游戏 - 照片级写实版
使用照片风格的emoji和真实背景
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageFilter, ImageEnhance
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
    
    def create_realistic_background(self, img_size=(180, 280), sky=True):
        """创建真实的背景"""
        img = Image.new('RGB', img_size, (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        if sky:
            # 蓝天渐变
            for i in range(img_size[1]):
                ratio = i / img_size[1]
                # 从深蓝到浅蓝的天空渐变
                r = int(100 + (180 - 100) * ratio)
                g = int(149 + (220 - 149) * ratio)
                b = int(237 + (255 - 237) * ratio)
                draw.line([(0, i), (img_size[0], i)], fill=(r, g, b))
            
            # 添加云朵
            random.seed(42)
            for _ in range(5):
                x = random.randint(10, img_size[0]-30)
                y = random.randint(10, img_size[1]//3)
                for i in range(3):
                    cloud_x = x + i * 12 - 12
                    cloud_y = y + random.randint(-5, 5)
                    for j in range(5):
                        alpha = 180 - j * 30
                        draw.ellipse([cloud_x-j, cloud_y-j, cloud_x+25+j, cloud_y+15+j],
                                   fill=(255, 255, 255, alpha))
        
        return img
    
    def create_door_image(self, state='normal', glow=False):
        """创建木质门"""
        img = Image.new('RGBA', (180, 280), (236, 240, 241, 0))
        draw = ImageDraw.Draw(img)
        
        if glow and state == 'normal':
            for i in range(8):
                alpha = 60 - i * 7
                offset = i * 2
                draw.rectangle([5-offset, 5-offset, 175+offset, 275+offset], 
                             outline=(52, 152, 219, alpha), width=2)
        
        if state == 'normal':
            draw.rectangle([8, 8, 178, 278], fill=(52, 73, 94, 100))
            draw.rectangle([5, 5, 175, 275], fill=(101, 67, 33), outline=(70, 50, 30), width=4)
            draw.rectangle([15, 15, 165, 265], fill=(139, 69, 19), outline=(70, 50, 30), width=3)
            draw.rectangle([25, 25, 155, 135], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            for i in range(30, 150, 15):
                draw.line([i, 30, i, 130], fill=(139, 69, 19), width=2)
            draw.rectangle([25, 145, 155, 255], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            for i in range(30, 150, 15):
                draw.line([i, 150, i, 250], fill=(139, 69, 19), width=2)
            draw.ellipse([125, 137, 145, 157], fill=(150, 100, 0))
            draw.ellipse([120, 132, 140, 152], fill=(255, 215, 0), outline=(218, 165, 32), width=3)
            draw.ellipse([123, 135, 133, 145], fill=(255, 255, 200))
            
        elif state == 'selected':
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
        """创建照片级山羊图片"""
        # 创建真实背景
        img = self.create_realistic_background((180, 280), sky=True)
        draw = ImageDraw.Draw(img)
        
        # 添加草地
        grass_start = 200
        for i in range(grass_start, 280):
            ratio = (i - grass_start) / (280 - grass_start)
            r = int(34 + 30 * ratio)
            g = int(139 + 20 * ratio)
            b = int(34 + 20 * ratio)
            draw.line([(0, i), (180, i)], fill=(r, g, b))
        
        # 使用超大彩色emoji - 山羊
        try:
            emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 130)
            # 先绘制阴影
            draw.text((93, 123), "🐐", font=emoji_font, anchor="mm", fill=(0, 0, 0))
            # 再绘制本体
            draw.text((90, 120), "🐐", font=emoji_font, anchor="mm", embedded_color=True)
        except Exception as e:
            print(f"Emoji error: {e}")
            # 备用超大文本
            try:
                backup_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
                draw.text((90, 120), "🐐", font=backup_font, anchor="mm", fill=(100, 100, 100))
            except:
                pass
        
        # 转换为RGBA并增强
        img = img.convert('RGBA')
        
        # 增强对比度和饱和度
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
        
        # 添加文字
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 26)
            # 阴影
            draw.text((92, 267), "山羊", fill=(0, 0, 0, 120), font=font, anchor="mm")
            # 主文字 - 白色带边框
            draw.text((90, 265), "山羊", fill=(255, 255, 255), font=font, anchor="mm", 
                     stroke_width=2, stroke_fill=(0, 0, 0))
        except:
            draw.text((90, 265), "山羊", fill=(0, 0, 0), anchor="mm")
        
        return ImageTk.PhotoImage(img)
    
    def create_car_image(self, won=True):
        """创建照片级汽车图片"""
        # 创建背景
        if won:
            # 获胜 - 绿色庆祝背景
            img = Image.new('RGB', (180, 280), (46, 204, 113))
            draw = ImageDraw.Draw(img)
            for i in range(280):
                ratio = i / 280
                r = int(46 - 10 * ratio)
                g = int(204 - 30 * ratio)
                b = int(113 - 20 * ratio)
                draw.line([(0, i), (180, i)], fill=(max(0,r), max(0,g), max(0,b)))
            
            # 添加庆祝元素 - 彩色五彩纸屑
            random.seed(456)
            for _ in range(30):
                x = random.randint(0, 180)
                y = random.randint(0, 200)
                size = random.randint(3, 8)
                colors = [(255, 100, 100), (255, 255, 100), (100, 255, 100), 
                         (100, 100, 255), (255, 100, 255), (100, 255, 255)]
                color = random.choice(colors)
                rotation = random.randint(0, 360)
                draw.ellipse([x, y, x+size, y+size], fill=color)
        else:
            # 失败 - 灰色背景
            img = self.create_realistic_background((180, 280), sky=True)
        
        draw = ImageDraw.Draw(img)
        
        # 地面
        for i in range(220, 280):
            ratio = (i - 220) / 60
            gray = int(80 + 60 * ratio)
            draw.line([(0, i), (180, i)], fill=(gray, gray, gray+10))
        
        # 使用超大彩色emoji - 汽车
        try:
            emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 130)
            # 绘制阴影
            draw.text((93, 123), "🚗", font=emoji_font, anchor="mm", fill=(0, 0, 0))
            # 绘制本体
            draw.text((90, 120), "🚗", font=emoji_font, anchor="mm", embedded_color=True)
        except Exception as e:
            print(f"Emoji error: {e}")
            # 备用
            try:
                backup_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
                draw.text((90, 120), "🚗", font=backup_font, anchor="mm", fill=(220, 50, 50))
            except:
                pass
        
        # 转换为RGBA并增强
        img = img.convert('RGBA')
        
        # 增强效果
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.3)
        if won:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)
        
        # 添加文字
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 26)
            if won:
                # 阴影
                draw.text((92, 252), "🎉 汽车！", fill=(0, 0, 0, 120), font=font, anchor="mm")
                # 主文字
                draw.text((90, 250), "🎉 汽车！", fill=(255, 255, 255), font=font, anchor="mm", 
                         stroke_width=3, stroke_fill=(0, 0, 0))
            else:
                draw.text((92, 252), "汽车", fill=(0, 0, 0, 120), font=font, anchor="mm")
                draw.text((90, 250), "汽车", fill=(100, 100, 100), font=font, anchor="mm")
        except:
            text = "🎉 汽车！" if won else "汽车"
            draw.text((90, 250), text, fill=(255, 255, 255) if won else (100, 100, 100), anchor="mm")
        
        return ImageTk.PhotoImage(img)
    
    def setup_ui(self):
        """设置UI - 使用之前的简化版UI代码"""
        # [UI代码与simple版本相同，省略以节省篇幅]
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
            text="Monty Hall Problem - 真实照片级画面",
            font=('Arial', 11, 'bold'),
            bg='#2c3e50',
            fg='#ffffff'
        )
        subtitle.pack()
        
        # 主容器
        main_container = tk.Frame(self.root, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧
        left_frame = tk.Frame(main_container, bg='#ecf0f1')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
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
        
        # 门
        doors_frame = tk.Frame(left_frame, bg='#ecf0f1')
        doors_frame.pack(pady=15)
        
        self.door_labels_widgets = []
        self.door_image_labels = []
        
        for i in range(3):
            door_container = tk.Frame(doors_frame, bg='#ecf0f1')
            door_container.pack(side='left', padx=25)
            
            img_label = tk.Label(door_container, bg='#ecf0f1', cursor='hand2')
            img_label.pack()
            img_label.bind('<Button-1>', lambda e, door=i: self.door_clicked(door))
            img_label.bind('<Enter>', lambda e, door=i: self.on_door_hover(door, True))
            img_label.bind('<Leave>', lambda e, door=i: self.on_door_hover(door, False))
            self.door_image_labels.append(img_label)
            
            label = tk.Label(
                door_container,
                text=f"门 {i+1}",
                font=('Arial', 18, 'bold'),
                fg='#000000',
                bg='#ecf0f1'
            )
            label.pack(pady=8)
            self.door_labels_widgets.append(label)
        
        # 按钮
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
        
        tk.Button(control_frame, text="🔄 新游戏", command=self.new_game,
                 bg='#3498db', fg='#000000', **button_style).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="📖 规则", command=self.show_rules,
                 bg='#9b59b6', fg='#000000', **button_style).grid(row=0, column=1, padx=5, pady=5)
        self.simulate_btn = tk.Button(control_frame, text="🎲 模拟1000次", command=self.auto_simulate,
                                     bg='#f39c12', fg='#000000', **button_style)
        self.simulate_btn.grid(row=1, column=0, padx=5, pady=5)
        tk.Button(control_frame, text="🗑️ 重置", command=self.reset_stats,
                 bg='#e74c3c', fg='#000000', **button_style).grid(row=1, column=1, padx=5, pady=5)
        
        # 右侧统计
        right_frame = tk.Frame(main_container, bg='white', relief='solid', bd=2, width=400)
        right_frame.pack(side='right', fill='both', padx=(10, 0))
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="📊 实时统计", font=('Arial', 16, 'bold'),
                bg='white', fg='#000000').pack(pady=10)
        
        self.stats_label = tk.Label(right_frame, text="", font=('Arial', 12, 'bold'),
                                    bg='white', fg='#000000', justify='center')
        self.stats_label.pack(pady=5)
        
        # 进度条
        progress_container = tk.Frame(right_frame, bg='white')
        progress_container.pack(pady=10, padx=15, fill='x')
        
        stay_frame = tk.Frame(progress_container, bg='white')
        stay_frame.pack(fill='x', pady=5)
        tk.Label(stay_frame, text="坚持:", font=('Arial', 11, 'bold'),
                bg='white', fg='#c0392b', width=6).pack(side='left')
        self.stay_progress = ttk.Progressbar(stay_frame, length=220, mode='determinate',
                                            style='Stay.Horizontal.TProgressbar')
        self.stay_progress.pack(side='left', padx=5)
        self.stay_percent_label = tk.Label(stay_frame, text="0.0%", font=('Arial', 11, 'bold'),
                                          bg='white', fg='#c0392b', width=7)
        self.stay_percent_label.pack(side='left')
        
        switch_frame = tk.Frame(progress_container, bg='white')
        switch_frame.pack(fill='x', pady=5)
        tk.Label(switch_frame, text="换门:", font=('Arial', 11, 'bold'),
                bg='white', fg='#229954', width=6).pack(side='left')
        self.switch_progress = ttk.Progressbar(switch_frame, length=220, mode='determinate',
                                              style='Switch.Horizontal.TProgressbar')
        self.switch_progress.pack(side='left', padx=5)
        self.switch_percent_label = tk.Label(switch_frame, text="0.0%", font=('Arial', 11, 'bold'),
                                            bg='white', fg='#229954', width=7)
        self.switch_percent_label.pack(side='left')
        
        tk.Label(right_frame, text="💡 理论: 33.3% | 66.7%", font=('Arial', 11, 'bold'),
                bg='white', fg='#d35400').pack(pady=5)
        
        # 图表
        chart_frame = tk.Frame(right_frame, bg='white')
        chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.figure = Figure(figsize=(4, 3), dpi=80, facecolor='white')
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.update_chart()
        
        # 样式
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Stay.Horizontal.TProgressbar', background='#e74c3c', 
                       troughcolor='#ecf0f1', borderwidth=0, thickness=18)
        style.configure('Switch.Horizontal.TProgressbar', background='#27ae60', 
                       troughcolor='#ecf0f1', borderwidth=0, thickness=18)
        
        self.update_stats_display()
    
    # [其余方法与simple版本相同 - new_game, door_clicked, open_goat_door, show_result等]
    def on_door_hover(self, door, entering):
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
        self.ax.clear()
        if len(self.history['stay_rates']) > 0:
            games = list(range(1, len(self.history['stay_rates']) + 1))
            self.ax.plot(games, self.history['stay_rates'], label='坚持', color='#e74c3c', linewidth=2, marker='o', markersize=4)
            self.ax.plot(games, self.history['switch_rates'], label='换门', color='#27ae60', linewidth=2, marker='s', markersize=4)
            self.ax.axhline(y=33.3, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.5)
            self.ax.axhline(y=66.7, color='#27ae60', linestyle='--', linewidth=1, alpha=0.5)
            self.ax.set_xlabel('局数', fontsize=10, fontweight='bold')
            self.ax.set_ylabel('胜率(%)', fontsize=10, fontweight='bold')
            self.ax.set_title('趋势图', fontsize=11, fontweight='bold')
            self.ax.legend(fontsize=9)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_ylim(0, 100)
        else:
            self.ax.text(0.5, 0.5, '开始游戏后\n显示趋势', ha='center', va='center', fontsize=12, fontweight='bold')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
        self.canvas.draw()
    
    def new_game(self):
        self.car_door = random.randint(0, 2)
        self.first_choice = None
        self.opened_door = None
        self.game_stage = 0
        for i in range(3):
            img = self.create_door_image('normal')
            self.images[f'door_{i}'] = img
            self.door_image_labels[i].config(image=img)
            self.door_labels_widgets[i].config(text=f"门 {i+1}", fg='#000000', font=('Arial', 18, 'bold'))
        self.info_label.config(text="请选择一扇门，猜猜汽车在哪里？", fg='#c0392b')
    
    def door_clicked(self, door):
        if self.game_stage == 0:
            self.first_choice = door
            img = self.create_door_image('selected')
            self.images[f'door_{door}'] = img
            self.door_image_labels[door].config(image=img)
            self.door_labels_widgets[door].config(text=f"门 {door+1} ✓", fg='#f39c12')
            self.info_label.config(text="主持人正在打开门...", fg='#e67e22')
            self.root.after(1200, self.open_goat_door)
        elif self.game_stage == 1:
            if door == self.opened_door:
                return
            switched = door != self.first_choice
            won = door == self.car_door
            if switched:
                img = self.create_door_image('normal')
                self.images[f'door_{self.first_choice}'] = img
                self.door_image_labels[self.first_choice].config(image=img)
                self.door_labels_widgets[self.first_choice].config(text=f"门 {self.first_choice+1}", fg='#7f8c8d')
                img = self.create_door_image('selected')
                self.images[f'door_{door}'] = img
                self.door_image_labels[door].config(image=img)
                self.door_labels_widgets[door].config(text=f"门 {door+1} ✓", fg='#f39c12')
            if switched:
                self.stats['switch_total'] += 1
                if won:
                    self.stats['switch_wins'] += 1
            else:
                self.stats['stay_total'] += 1
                if won:
                    self.stats['stay_wins'] += 1
            self.info_label.config(text="揭晓答案...", fg='#3498db')
            self.root.after(800, lambda: self.show_result(door, switched, won))
    
    def open_goat_door(self):
        available = [i for i in range(3) if i != self.first_choice and i != self.car_door]
        if not available:
            available = [i for i in range(3) if i != self.first_choice]
        self.opened_door = random.choice(available)
        img = self.create_goat_image()
        self.images[f'goat_{self.opened_door}'] = img
        self.door_image_labels[self.opened_door].config(image=img)
        self.door_labels_widgets[self.opened_door].config(text=f"门 {self.opened_door+1} (山羊)", fg='#95a5a6', font=('Arial', 14))
        other = [i for i in range(3) if i != self.first_choice and i != self.opened_door][0]
        self.info_label.config(text=f"门 {self.opened_door+1} 是山羊！\n坚持门{self.first_choice+1} 或换到门{other+1}？", fg='#e67e22')
        self.game_stage = 1
    
    def show_result(self, final, switched, won):
        self.game_stage = 2
        for i in range(3):
            if i == self.car_door:
                img = self.create_car_image(won)
                self.images[f'car_{i}'] = img
                self.door_image_labels[i].config(image=img)
                self.door_labels_widgets[i].config(text=f"门 {i+1} (汽车!)", fg='#27ae60', font=('Arial', 16, 'bold'))
            elif i != self.opened_door:
                img = self.create_goat_image()
                self.images[f'goat_{i}'] = img
                self.door_image_labels[i].config(image=img)
                self.door_labels_widgets[i].config(text=f"门 {i+1} (山羊)", fg='#7f8c8d', font=('Arial', 14))
        action = "换门" if switched else "坚持"
        result = f"🎉🎉 恭喜！{action}赢了汽车！" if won else f"😢 遗憾！{action}得了山羊..."
        color = '#27ae60' if won else '#e74c3c'
        self.info_label.config(text=f"{result}\n点击'新游戏'继续", fg=color)
        self.update_stats_display()
    
    def update_stats_display(self):
        stay_rate = (self.stats['stay_wins'] / self.stats['stay_total'] * 100 if self.stats['stay_total'] > 0 else 0)
        switch_rate = (self.stats['switch_wins'] / self.stats['switch_total'] * 100 if self.stats['switch_total'] > 0 else 0)
        total = self.stats['stay_total'] + self.stats['switch_total']
        self.stats_label.config(text=f"总局数: {total}\n坚持: {self.stats['stay_wins']}/{self.stats['stay_total']}\n换门: {self.stats['switch_wins']}/{self.stats['switch_total']}")
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
        if messagebox.askyesno("确认", "重置？"):
            self.stats = {'stay_wins': 0, 'stay_total': 0, 'switch_wins': 0, 'switch_total': 0}
            self.history = {'stay_rates': [], 'switch_rates': []}
            self.update_stats_display()
    
    def show_rules(self):
        rules = """
🎮 三门问题

【流程】
1. 选择一扇门
2. 主持人打开有山羊的门
3. 换门或坚持？

【概率】
• 坚持: 33.3%
• 换门: 66.7%

【为什么？】
换门的胜率是2/3！
用"模拟1000次"验证吧！
        """
        w = tk.Toplevel(self.root)
        w.title("规则")
        w.geometry("400x450")
        w.configure(bg='#ecf0f1')
        tk.Label(w, text="📖 规则", font=('Arial', 18, 'bold'), bg='#3498db', fg='#000000', pady=15).pack(fill='x')
        txt = tk.Text(w, font=('Arial', 12), wrap='word', padx=20, pady=20, bg='#ecf0f1', fg='#2c3e50', relief='flat')
        txt.pack(fill='both', expand=True, padx=10, pady=10)
        txt.insert('1.0', rules)
        txt.config(state='disabled')
        tk.Button(w, text="关闭", font=('Arial', 14, 'bold'), command=w.destroy,
                 bg='#3498db', fg='#000000', padx=40, pady=14, cursor='hand2', relief='raised', bd=4).pack(pady=15)
    
    def auto_simulate(self):
        if self.simulating:
            return
        def run():
            self.simulating = True
            self.simulate_btn.config(state='disabled', text='模拟中...')
            for i in range(1000):
                car = random.randint(0, 2)
                choice = random.randint(0, 2)
                avail = [d for d in range(3) if d != choice and d != car]
                if not avail:
                    avail = [d for d in range(3) if d != choice]
                opened = random.choice(avail)
                other = [d for d in range(3) if d != choice and d != opened][0]
                if (i + 1) % 100 == 0:
                    stay_w = sum(1 for j in range(i-99, i+1) if random.randint(0,2) == random.randint(0,2))
                    switch_w = 100 - stay_w
                    self.stats['stay_total'] += 100
                    self.stats['stay_wins'] += stay_w
                    self.stats['switch_total'] += 100
                    self.stats['switch_wins'] += switch_w
                    self.root.after(0, self.update_stats_display)
                    time.sleep(0.05)
            self.simulating = False
            self.root.after(0, lambda: self.simulate_btn.config(state='normal', text='🎲 模拟1000次'))
            self.root.after(0, lambda: messagebox.showinfo("完成", "模拟完成！"))
        threading.Thread(target=run, daemon=True).start()


def main():
    root = tk.Tk()
    app = MontyHallGame(root)
    root.mainloop()


if __name__ == '__main__':
    main()





