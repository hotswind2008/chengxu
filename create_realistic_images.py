#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建真实的山羊和汽车图片
使用大尺寸emoji表情符号
"""

from PIL import Image, ImageDraw, ImageTk, ImageFont
import os

def create_realistic_goat():
    """创建真实的山羊图片 - 使用大表情符号"""
    img = Image.new('RGBA', (180, 280), (135, 206, 250, 255))
    draw = ImageDraw.Draw(img)
    
    # 背景渐变
    for i in range(280):
        ratio = i / 280
        r = int(135 + (200 - 135) * ratio)
        g = int(206 + (240 - 206) * ratio)
        b = int(250 + (255 - 250) * ratio)
        draw.line([(0, i), (180, i)], fill=(r, g, b))
    
    # 使用超大emoji
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 120)
        # 山羊emoji
        draw.text((90, 120), "🐐", font=font, anchor="mm", embedded_color=True)
        
        # 底部文字
        text_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        draw.text((91, 257), "山羊", fill=(0, 0, 0, 80), font=text_font, anchor="mm")
        draw.text((90, 255), "山羊", fill=(52, 73, 94), font=text_font, anchor="mm")
    except:
        # 备用方案
        draw.text((90, 120), "🐐", font=None, anchor="mm")
        draw.text((90, 255), "山羊", font=None, anchor="mm")
    
    return img

def create_realistic_car(won=True):
    """创建真实的汽车图片 - 使用大表情符号"""
    if won:
        bg_color = (46, 204, 113)
    else:
        bg_color = (220, 230, 240)
    
    img = Image.new('RGBA', (180, 280), bg_color + (255,))
    draw = ImageDraw.Draw(img)
    
    # 背景渐变
    for i in range(280):
        factor = 1 - (i / 280) * 0.2
        r, g, b = bg_color
        color = (int(r*factor), int(g*factor), int(b*factor))
        draw.line([(0, i), (180, i)], fill=color)
    
    # 使用超大emoji
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 120)
        # 汽车emoji
        draw.text((90, 120), "🚗", font=font, anchor="mm", embedded_color=True)
        
        # 底部文字
        text_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        if won:
            draw.text((91, 252), "🎉 汽车！", fill=(0, 0, 0, 50), font=text_font, anchor="mm")
            draw.text((90, 250), "🎉 汽车！", fill=(255, 255, 255), font=text_font, anchor="mm", 
                     stroke_width=2, stroke_fill=(52, 73, 94))
        else:
            draw.text((91, 252), "汽车", fill=(0, 0, 0, 50), font=text_font, anchor="mm")
            draw.text((90, 250), "汽车", fill=(127, 140, 141), font=text_font, anchor="mm")
    except Exception as e:
        print(f"Error: {e}")
        # 备用方案
        draw.text((90, 120), "🚗", font=None, anchor="mm")
        draw.text((90, 250), "汽车", font=None, anchor="mm")
    
    return img

if __name__ == '__main__':
    # 测试创建图片
    goat_img = create_realistic_goat()
    goat_img.save('test_goat.png')
    print("Created test_goat.png")
    
    car_img = create_realistic_car(True)
    car_img.save('test_car.png')
    print("Created test_car.png")
