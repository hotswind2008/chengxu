#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三门问题（Monty Hall Problem）游戏 - 终极优化版
添加动画效果、悬停高亮、实时统计图表和丰富的交互体验
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
        
        # 历史数据用于绘图
        self.history = {
            'stay_rates': [],
            'switch_rates': []
        }
        
        # 存储图片引用
        self.images = {}
        
        # 动画相关
        self.animation_running = False
        
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
            # 门框外框
            draw.rectangle([5, 5, 175, 275], fill=(101, 67, 33), outline=(70, 50, 30), width=4)
            # 门板背景
            draw.rectangle([15, 15, 165, 265], fill=(139, 69, 19), outline=(70, 50, 30), width=3)
            
            # 上门板
            draw.rectangle([25, 25, 155, 135], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            # 木纹效果
            for i in range(30, 150, 15):
                draw.line([i, 30, i, 130], fill=(139, 69, 19), width=2)
            for i in range(35, 125, 20):
                draw.arc([i-5, 40, i+15, 70], start=30, end=150, fill=(139, 69, 19), width=1)
            
            # 下门板
            draw.rectangle([25, 145, 155, 255], fill=(160, 82, 45), outline=(101, 67, 33), width=3)
            # 木纹效果
            for i in range(30, 150, 15):
                draw.line([i, 150, i, 250], fill=(139, 69, 19), width=2)
            for i in range(35, 125, 20):
                draw.arc([i-5, 165, i+15, 195], start=30, end=150, fill=(139, 69, 19), width=1)
            
            # 门把手（金色，立体）
            draw.ellipse([125, 137, 145, 157], fill=(150, 100, 0))
            draw.ellipse([120, 132, 140, 152], fill=(255, 215, 0), outline=(218, 165, 32), width=3)
            draw.ellipse([123, 135, 133, 145], fill=(255, 255, 200))
            draw.ellipse([125, 137, 130, 142], fill=(255, 255, 220))
            
        elif state == 'selected':
            # 发光的选中门
            for i in range(6):
                alpha = 120 - i * 20
                draw.rectangle([5-i*3, 5-i*3, 175+i*3, 275+i*3], 
                             outline=(243, 156, 18, alpha), width=4)
            
            # 门框
            draw.rectangle([5, 5, 175, 275], fill=(243, 156, 18), outline=(230, 126, 34), width=5)
            draw.rectangle([15, 15, 165, 265], fill=(245, 176, 65), outline=(230, 126, 34), width=3)
            
            # 上门板
            draw.rectangle([25, 25, 155, 135], fill=(249, 191, 59), outline=(243, 156, 18), width=3)
            # 下门板  
            draw.rectangle([25, 145, 155, 255], fill=(249, 191, 59), outline=(243, 156, 18), width=3)
            
            # 门把手
            draw.ellipse([125, 137, 145, 157], fill=(200, 150, 0))
            draw.ellipse([120, 132, 140, 152], fill=(255, 215, 0), outline=(218, 165, 32), width=3)
            draw.ellipse([123, 135, 133, 145], fill=(255, 255, 200))
            
            # 大问号
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 55)
            except:
                font = None
            
            if font:
                # 问号阴影
                draw.text((77, 72), "?", fill=(0, 0, 0, 100), font=font, anchor="mm")
                # 问号主体
                draw.text((75, 70), "?", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=2, stroke_fill=(230, 126, 34))
                
                draw.text((77, 192), "?", fill=(0, 0, 0, 100), font=font, anchor="mm")
                draw.text((75, 190), "?", fill=(255, 255, 255), font=font, anchor="mm", stroke_width=2, stroke_fill=(230, 126, 34))
        
        return ImageTk.PhotoImage(img)
    
    def create_goat_image(self):
        """创建真实的山羊图片 - 使用大emoji"""
        img = Image.new('RGBA', (180, 280), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 背景 - 天空渐变
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
        
        # 使用超大emoji山羊
        try:
            # 尝试使用Apple Color Emoji字体
            emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 100)
            draw.text((90, 130), "🐐", font=emoji_font, anchor="mm", embedded_color=True)
        except:
            # 备用方案：使用常规字体
            try:
                emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 80)
                draw.text((90, 130), "🐐", font=emoji_font, anchor="mm")
            except:
                pass
        
        # 山羊身体 - 多层次渐变
        # 外层阴影
        draw.ellipse([52, 152, 132, 215], fill=(100, 110, 115, 60))
        # 主体
        for i in range(5):
            offset = i * 2
            color_shift = i * 8
            draw.ellipse([50+offset, 150+offset, 130-offset, 210-offset], 
                        fill=(200-color_shift, 205-color_shift, 210-color_shift))
        draw.ellipse([50, 150, 130, 210], outline=(120, 130, 135), width=3)
        
        # 毛发纹理
        for angle in range(30, 150, 15):
            import math
            cx, cy = 90, 180
            x1 = cx + 35 * math.cos(math.radians(angle))
            y1 = cy + 25 * math.sin(math.radians(angle))
            x2 = cx + 25 * math.cos(math.radians(angle))
            y2 = cy + 18 * math.sin(math.radians(angle))
            draw.line([x1, y1, x2, y2], fill=(170, 175, 180), width=2)
        
        # 山羊脖子
        draw.ellipse([65, 135, 115, 160], fill=(210, 215, 220), outline=(120, 130, 135), width=2)
        
        # 山羊头 - 更立体
        # 头部阴影
        draw.ellipse([63, 93, 123, 153], fill=(180, 185, 190))
        # 头部多层次
        for i in range(4):
            offset = i
            draw.ellipse([60+offset, 90+offset, 120-offset, 150-offset], 
                        fill=(240-i*5, 245-i*5, 250-i*5))
        draw.ellipse([60, 90, 120, 150], outline=(120, 130, 135), width=3)
        
        # 脸颊腮红
        draw.ellipse([65, 125, 75, 135], fill=(255, 182, 193, 80))
        draw.ellipse([105, 125, 115, 135], fill=(255, 182, 193, 80))
        
        # 左耳 - 更精致
        draw.polygon([68, 100, 53, 72, 62, 75, 73, 94], fill=(200, 205, 210), outline=(120, 130, 135), width=2)
        draw.polygon([66, 96, 58, 78, 70, 92], fill=(255, 192, 203))
        draw.arc([60, 80, 70, 92], start=200, end=340, fill=(180, 180, 180), width=1)
        
        # 右耳
        draw.polygon([112, 100, 127, 72, 118, 75, 107, 94], fill=(200, 205, 210), outline=(120, 130, 135), width=2)
        draw.polygon([114, 96, 122, 78, 110, 92], fill=(255, 192, 203))
        draw.arc([110, 80, 120, 92], start=200, end=340, fill=(180, 180, 180), width=1)
        
        # 角 - 螺旋状
        # 左角
        for i in range(5):
            y_offset = i * 4
            width = 6 - i
            draw.line([70-i, 94-y_offset, 58-i*2, 72-y_offset], fill=(60-i*2, 70-i*2, 80-i*2), width=width)
        draw.line([58, 72, 54, 68], fill=(40, 50, 60), width=3)
        # 角纹理
        for i in range(3):
            draw.arc([58-i*3, 72-i*8, 70-i*3, 94-i*8], start=180, end=270, fill=(80, 85, 90), width=1)
        
        # 右角
        for i in range(5):
            y_offset = i * 4
            width = 6 - i
            draw.line([110+i, 94-y_offset, 122+i*2, 72-y_offset], fill=(60-i*2, 70-i*2, 80-i*2), width=width)
        draw.line([122, 72, 126, 68], fill=(40, 50, 60), width=3)
        # 角纹理
        for i in range(3):
            draw.arc([110+i*3, 72-i*8, 122+i*3, 94-i*8], start=270, end=360, fill=(80, 85, 90), width=1)
        
        # 眼睛 - 超可爱
        # 左眼
        draw.ellipse([66, 104, 88, 126], fill=(255, 255, 255), outline=(40, 40, 40), width=3)
        draw.ellipse([71, 109, 85, 123], fill=(139, 69, 19))  # 棕色瞳孔
        draw.ellipse([74, 112, 82, 120], fill=(0, 0, 0))
        draw.ellipse([75, 113, 79, 117], fill=(255, 255, 255))  # 高光1
        draw.ellipse([79, 116, 81, 118], fill=(255, 255, 255, 150))  # 高光2
        # 眼睫毛
        for i in range(3):
            x = 70 + i * 6
            draw.line([x, 104, x-2, 100], fill=(40, 40, 40), width=2)
        
        # 右眼
        draw.ellipse([92, 104, 114, 126], fill=(255, 255, 255), outline=(40, 40, 40), width=3)
        draw.ellipse([95, 109, 109, 123], fill=(139, 69, 19))
        draw.ellipse([98, 112, 106, 120], fill=(0, 0, 0))
        draw.ellipse([99, 113, 103, 117], fill=(255, 255, 255))
        draw.ellipse([101, 116, 103, 118], fill=(255, 255, 255, 150))
        # 眼睫毛
        for i in range(3):
            x = 96 + i * 6
            draw.line([x, 104, x+2, 100], fill=(40, 40, 40), width=2)
        
        # 眉毛
        draw.arc([68, 100, 86, 108], start=180, end=360, fill=(100, 100, 100), width=2)
        draw.arc([94, 100, 112, 108], start=180, end=360, fill=(100, 100, 100), width=2)
        
        # 鼻子 - 更立体
        draw.ellipse([83, 128, 97, 142], fill=(160, 170, 175), outline=(120, 130, 135), width=2)
        draw.ellipse([85, 130, 90, 135], fill=(80, 85, 90))
        draw.ellipse([90, 130, 95, 135], fill=(80, 85, 90))
        # 鼻子高光
        draw.ellipse([86, 137, 91, 140], fill=(200, 210, 215))
        
        # 嘴巴 - 微笑
        draw.arc([70, 135, 110, 160], start=0, end=180, fill=(60, 60, 60), width=4)
        # 嘴角
        draw.line([78, 147, 73, 153], fill=(60, 60, 60), width=3)
        draw.line([102, 147, 107, 153], fill=(60, 60, 60), width=3)
        # 舌头
        draw.arc([85, 145, 95, 153], start=0, end=180, fill=(255, 150, 150), width=2)
        
        # 胡须
        # 左边
        draw.line([65, 132, 40, 130], fill=(180, 180, 180), width=2)
        draw.line([65, 135, 38, 138], fill=(180, 180, 180), width=2)
        draw.line([65, 138, 40, 145], fill=(180, 180, 180), width=2)
        # 右边
        draw.line([115, 132, 140, 130], fill=(180, 180, 180), width=2)
        draw.line([115, 135, 142, 138], fill=(180, 180, 180), width=2)
        draw.line([115, 138, 140, 145], fill=(180, 180, 180), width=2)
        
        # 腿 - 更立体
        legs = [(55, 205, 65, 240), (62, 205, 72, 240), (108, 205, 118, 240), (115, 205, 125, 240)]
        for x1, y1, x2, y2 in legs:
            # 阴影
            draw.rectangle([x1+2, y1+2, x2+2, y2], fill=(110, 120, 125))
            # 主体渐变
            for i in range(x2-x1):
                color = 150 + int((i/(x2-x1)) * 30)
                draw.line([x1+i, y1, x1+i, y2], fill=(color, color+10, color+15), width=1)
            draw.rectangle([x1, y1, x2, y2], outline=(110, 120, 125), width=2)
            # 蹄子
            draw.ellipse([x1-1, y2-5, x2+1, y2+2], fill=(50, 60, 70), outline=(30, 40, 50), width=2)
            # 蹄子分叉
            draw.line([x1+(x2-x1)//2, y2-3, x1+(x2-x1)//2, y2], fill=(70, 80, 90), width=1)
        
        # 尾巴 - 更毛茸茸
        for i in range(3):
            draw.arc([127+i*2, 162+i*3, 147+i*2, 192+i*3], start=270, end=90, 
                    fill=(150-i*10, 155-i*10, 160-i*10), width=5-i)
        # 尾巴末端毛球
        draw.ellipse([138, 175, 150, 187], fill=(190, 195, 200), outline=(140, 145, 150), width=2)
        for _ in range(10):
            x = 144 + random.randint(-4, 4)
            y = 181 + random.randint(-4, 4)
            draw.line([144, 181, x, y], fill=(180, 185, 190), width=1)
        
        # 铃铛项圈
        draw.rectangle([75, 148, 105, 153], fill=(255, 100, 100), outline=(200, 50, 50), width=2)
        draw.ellipse([87, 151, 93, 158], fill=(255, 215, 0), outline=(218, 165, 32), width=2)
        draw.arc([88, 152, 92, 157], start=45, end=135, fill=(255, 255, 255), width=1)
        
        # 文字
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        except:
            font = None
        
        if font:
            # 文字阴影
            draw.text((92, 267), "山羊", fill=(0, 0, 0, 80), font=font, anchor="mm")
            draw.text((90, 265), "山羊", fill=(52, 73, 94), font=font, anchor="mm", 
                     stroke_width=1, stroke_fill=(255, 255, 255))
        
        return ImageTk.PhotoImage(img)
    
    def create_car_image(self, won=True):
        """创建精美的汽车图片"""
        import math
        import random
        
        if won:
            bg_color = (46, 204, 113)
        else:
            bg_color = (220, 230, 240)
        
        img = Image.new('RGBA', (180, 280), bg_color + (255,))
        draw = ImageDraw.Draw(img)
        
        # 背景渐变 - 天空或庆祝背景
        for i in range(220):
            factor = 1 - (i / 220) * 0.2
            r, g, b = bg_color
            color = (int(r*factor), int(g*factor), int(b*factor))
            draw.line([(0, i), (180, i)], fill=color)
        
        # 地面 - 真实质感
        for i in range(220, 280):
            ratio = (i - 220) / 60
            gray = int(100 + 50 * ratio)
            draw.line([(0, i), (180, i)], fill=(gray, gray, gray+10))
        
        if won:
            # 庆祝气球和彩带
            random.seed(123)
            for i in range(6):
                x = 15 + i * 28
                y = 15 + random.randint(0, 30)
                # 气球
                balloon_color = [(255, 100, 100), (255, 200, 50), (100, 150, 255), 
                               (255, 150, 200), (150, 255, 150), (255, 180, 100)][i]
                draw.ellipse([x, y, x+15, y+20], fill=balloon_color, outline=(200, 200, 200), width=2)
                draw.ellipse([x+3, y+2, x+10, y+8], fill=(255, 255, 255, 120))
                draw.line([x+7, y+20, x+7, y+35], fill=(150, 150, 150), width=2)
            
            # 彩带
            for i in range(8):
                x = 10 + i * 22
                for j in range(3):
                    y = 40 + j * 20
                    color = [(255, 200, 0), (255, 100, 150), (100, 200, 255)][j % 3]
                    draw.arc([x-8, y, x+8, y+15], start=0, end=180, fill=color, width=3)
                    draw.arc([x-2, y+10, x+14, y+25], start=180, end=360, fill=color, width=3)
        
        # 地面阴影 - 更柔和
        for i in range(5):
            alpha = 30 - i * 5
            draw.ellipse([40-i*2, 218+i, 145+i*2, 235+i], fill=(0, 0, 0, alpha))
        
        # 车身底部阴影
        draw.rectangle([35, 157, 148, 198], fill=(80, 30, 30, 40))
        
        # 车身主体 - 超级跑车设计
        # 车身底盘（多层渐变）
        for i in range(8):
            offset = i
            r = 231 - i * 5
            g = 76 - i * 3
            b = 60 - i * 2
            draw.rectangle([30+offset, 150+offset, 145-offset, 192-offset], 
                          fill=(r, g, b))
        draw.rectangle([30, 150, 145, 192], outline=(150, 40, 30), width=4)
        
        # 车身高光带
        draw.rectangle([35, 153, 140, 158], fill=(255, 150, 120, 200))
        draw.rectangle([35, 180, 140, 185], fill=(200, 60, 45, 150))
        
        # 车身侧线（运动感）
        for i in range(3):
            y = 160 + i * 8
            draw.line([32, y, 143, y], fill=(180, 55, 40), width=2)
        
        # 车顶（更流线型）
        car_top = [55, 150, 52, 108, 65, 95, 90, 88, 115, 95, 128, 108, 125, 150]
        draw.polygon(car_top, fill=(180, 50, 40), outline=(140, 35, 28), width=3)
        
        # 车顶渐变高光
        for i in range(15):
            offset = i
            alpha = 200 - i * 10
            draw.polygon([58+offset, 147-offset*2, 62+offset, 108-offset, 
                         88-offset, 98-offset, 88-offset, 147-offset*2], 
                        fill=(255, 100, 80, max(0, alpha)))
        
        # 前挡风玻璃（镜面反光效果）
        draw.polygon([58, 147, 68, 103, 90, 93, 90, 147], 
                    fill=(60, 160, 230), outline=(40, 120, 180), width=3)
        # 玻璃反光
        draw.polygon([60, 145, 70, 108, 88, 98, 88, 145], fill=(150, 200, 255, 100))
        draw.polygon([62, 140, 72, 115, 80, 110, 80, 140], fill=(200, 230, 255, 120))
        # 云朵反射
        draw.ellipse([70, 115, 80, 125], fill=(255, 255, 255, 80))
        
        # 后挡风玻璃
        draw.polygon([92, 147, 90, 93, 112, 103, 122, 147], 
                    fill=(60, 160, 230), outline=(40, 120, 180), width=3)
        draw.polygon([94, 145, 92, 98, 110, 108, 120, 145], fill=(150, 200, 255, 100))
        draw.polygon([98, 140, 96, 110, 106, 115, 108, 140], fill=(200, 230, 255, 120))
        
        # 窗框
        draw.line([90, 93, 90, 147], fill=(40, 40, 40), width=5)
        draw.line([90, 95, 90, 145], fill=(80, 80, 80), width=3)
        
        # 车门分隔和细节线条
        draw.line([90, 150, 90, 192], fill=(140, 35, 28), width=4)
        # 车门把手位置凹陷
        draw.arc([68, 165, 80, 175], start=180, end=360, fill=(160, 45, 35), width=2)
        draw.arc([100, 165, 112, 175], start=180, end=360, fill=(160, 45, 35), width=2)
        
        # 前车灯 - LED 大灯（发光）
        # 外发光
        for i in range(4):
            draw.ellipse([130-i*2, 160-i*2, 151+i*2, 181+i*2], 
                        fill=(255, 220, 100, 30-i*7))
        # 主灯
        draw.ellipse([132, 162, 149, 179], fill=(250, 240, 200), outline=(230, 180, 50), width=3)
        draw.ellipse([134, 164, 147, 177], fill=(255, 250, 220))
        # 内部反光
        draw.ellipse([135, 165, 143, 173], fill=(255, 255, 255))
        draw.ellipse([137, 167, 141, 171], fill=(255, 255, 240))
        # LED 灯珠效果
        for i in range(3):
            draw.ellipse([136+i*3, 166, 138+i*3, 168], fill=(255, 255, 255))
        
        # 后车灯 - 红色尾灯
        draw.ellipse([31, 162, 48, 179], fill=(150, 30, 30), outline=(100, 20, 20), width=3)
        draw.ellipse([33, 164, 46, 177], fill=(220, 50, 50))
        draw.ellipse([35, 166, 44, 175], fill=(255, 100, 100))
        draw.arc([36, 168, 43, 173], start=45, end=135, fill=(255, 200, 200), width=2)
        
        # 进气格栅（前脸）
        draw.rectangle([135, 170, 150, 180], fill=(40, 40, 40), outline=(20, 20, 20), width=2)
        for i in range(4):
            y = 172 + i * 2
            draw.line([137, y, 148, y], fill=(60, 60, 60), width=1)
        
        # 保险杠 - 运动型
        draw.polygon([135, 185, 155, 185, 152, 192, 138, 192], 
                    fill=(180, 180, 185), outline=(120, 120, 125), width=2)
        draw.polygon([25, 185, 45, 185, 42, 192, 28, 192], 
                    fill=(180, 180, 185), outline=(120, 120, 125), width=2)
        
        # 前轮 - 超级运动轮胎
        # 轮胎阴影
        draw.ellipse([44, 186, 83, 225], fill=(20, 20, 20, 80))
        # 轮胎外圈
        draw.ellipse([42, 184, 81, 223], fill=(30, 30, 30), outline=(20, 20, 20), width=4)
        # 轮胎纹理
        for i in range(8):
            angle = i * 45
            x1 = 61.5 + 18 * math.cos(math.radians(angle))
            y1 = 203.5 + 18 * math.sin(math.radians(angle))
            x2 = 61.5 + 21 * math.cos(math.radians(angle))
            y2 = 203.5 + 21 * math.sin(math.radians(angle))
            draw.line([x1, y1, x2, y2], fill=(50, 50, 50), width=3)
        # 轮毂 - 运动型五辐
        draw.ellipse([50, 192, 73, 215], fill=(160, 160, 165), outline=(120, 120, 125), width=3)
        draw.ellipse([54, 196, 69, 211], fill=(200, 200, 205))
        # 轮毂辐条
        for angle in range(0, 360, 72):
            x1 = 61.5 + 12 * math.cos(math.radians(angle))
            y1 = 203.5 + 12 * math.sin(math.radians(angle))
            x2 = 61.5 + 5 * math.cos(math.radians(angle))
            y2 = 203.5 + 5 * math.sin(math.radians(angle))
            draw.line([x1, y1, x2, y2], fill=(140, 140, 145), width=4)
        # 轮毂中心
        draw.ellipse([58, 200, 65, 207], fill=(220, 220, 230), outline=(180, 180, 190), width=2)
        
        # 后轮
        draw.ellipse([97, 186, 136, 225], fill=(20, 20, 20, 80))
        draw.ellipse([95, 184, 134, 223], fill=(30, 30, 30), outline=(20, 20, 20), width=4)
        for i in range(8):
            angle = i * 45
            x1 = 114.5 + 18 * math.cos(math.radians(angle))
            y1 = 203.5 + 18 * math.sin(math.radians(angle))
            x2 = 114.5 + 21 * math.cos(math.radians(angle))
            y2 = 203.5 + 21 * math.sin(math.radians(angle))
            draw.line([x1, y1, x2, y2], fill=(50, 50, 50), width=3)
        draw.ellipse([103, 192, 126, 215], fill=(160, 160, 165), outline=(120, 120, 125), width=3)
        draw.ellipse([107, 196, 122, 211], fill=(200, 200, 205))
        for angle in range(0, 360, 72):
            x1 = 114.5 + 12 * math.cos(math.radians(angle))
            y1 = 203.5 + 12 * math.sin(math.radians(angle))
            x2 = 114.5 + 5 * math.cos(math.radians(angle))
            y2 = 203.5 + 5 * math.sin(math.radians(angle))
            draw.line([x1, y1, x2, y2], fill=(140, 140, 145), width=4)
        draw.ellipse([111, 200, 118, 207], fill=(220, 220, 230), outline=(180, 180, 190), width=2)
        
        # 刹车卡钳（运动细节）
        draw.rectangle([66, 200, 72, 207], fill=(255, 50, 50), outline=(200, 30, 30), width=2)
        draw.rectangle([119, 200, 125, 207], fill=(255, 50, 50), outline=(200, 30, 30), width=2)
        
        # 车顶装饰 - 天线
        draw.rectangle([87, 83, 93, 88], fill=(100, 100, 105), outline=(70, 70, 75), width=1)
        draw.ellipse([85, 80, 95, 85], fill=(220, 80, 65), outline=(180, 60, 50), width=2)
        draw.ellipse([87, 81, 93, 84], fill=(255, 120, 100))
        
        # 排气管 - 双出排气
        for x_offset in [0, 8]:
            x = 140 + x_offset
            draw.ellipse([x, 183, x+8, 191], fill=(80, 80, 85), outline=(50, 50, 55), width=2)
            draw.ellipse([x+1, 184, x+7, 190], fill=(50, 50, 55))
            draw.ellipse([x+2, 185, x+6, 189], fill=(30, 30, 35))
            if won:
                # 排气烟雾
                for i in range(3):
                    smoke_x = x + 8 + i * 4
                    smoke_y = 186 - i * 2
                    draw.ellipse([smoke_x, smoke_y, smoke_x+6, smoke_y+4], 
                                fill=(200, 200, 200, 80-i*20))
        
        # 车门把手 - 隐藏式
        draw.ellipse([72, 168, 78, 174], fill=(200, 200, 205), outline=(160, 160, 165), width=2)
        draw.ellipse([73, 169, 77, 173], fill=(220, 220, 230))
        
        draw.ellipse([102, 168, 108, 174], fill=(200, 200, 205), outline=(160, 160, 165), width=2)
        draw.ellipse([103, 169, 107, 173], fill=(220, 220, 230))
        
        # 后视镜 - 流线型
        # 左后视镜
        draw.polygon([52, 120, 48, 115, 50, 110, 54, 115], fill=(180, 50, 40), outline=(140, 35, 28), width=2)
        draw.ellipse([46, 113, 54, 121], fill=(80, 180, 250), outline=(50, 150, 220), width=2)
        draw.ellipse([47, 114, 53, 120], fill=(150, 210, 255, 120))
        
        # 右后视镜
        draw.polygon([128, 120, 132, 115, 130, 110, 126, 115], fill=(180, 50, 40), outline=(140, 35, 28), width=2)
        draw.ellipse([126, 113, 134, 121], fill=(80, 180, 250), outline=(50, 150, 220), width=2)
        draw.ellipse([127, 114, 133, 120], fill=(150, 210, 255, 120))
        
        # 车顶扰流板
        draw.polygon([125, 104, 130, 104, 132, 108, 125, 108], 
                    fill=(160, 45, 35), outline=(120, 30, 25), width=2)
        
        # 车标（红色跑车标志）
        draw.ellipse([85, 175, 95, 185], fill=(255, 215, 0), outline=(218, 165, 32), width=2)
        draw.text((90, 180), "S", font=None, fill=(200, 50, 40), anchor="mm")
        
        # 文字
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        except:
            font = None
        
        if font:
            if won:
                draw.text((91, 252), "🎉 汽车！", fill=(0, 0, 0, 50), font=font, anchor="mm")
                draw.text((90, 250), "🎉 汽车！", fill=(255, 255, 255), font=font, anchor="mm", 
                         stroke_width=2, stroke_fill=(52, 73, 94))
            else:
                draw.text((91, 252), "汽车", fill=(0, 0, 0, 50), font=font, anchor="mm")
                draw.text((90, 250), "汽车", fill=(127, 140, 141), font=font, anchor="mm")
        
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
        
        # 创建主容器（左右分栏）
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