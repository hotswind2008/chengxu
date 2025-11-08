#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包三门问题游戏为Windows exe文件
使用 PyInstaller
"""

import os
import sys
import subprocess

def build_exe():
    """打包为exe文件"""
    
    print("=" * 60)
    print("三门问题游戏 - 打包为Windows EXE")
    print("=" * 60)
    print()
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")
    
    print()
    
    # PyInstaller 命令
    cmd = [
        'pyinstaller',
        '--name=三门问题游戏',
        '--onefile',  # 打包成单个exe文件
        '--windowed',  # 不显示控制台窗口
        '--icon=NONE',  # 没有图标（可以添加.ico文件）
        '--clean',  # 清理临时文件
        '--add-data', 'monty_hall_final.py:.',  # 添加源文件
        'monty_hall_final.py'
    ]
    
    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("✓ 打包成功！")
        print("=" * 60)
        print()
        print("可执行文件位置: dist/三门问题游戏.exe")
        print()
        print("注意事项：")
        print("1. exe文件在 dist 文件夹中")
        print("2. 可以直接双击运行")
        print("3. 需要Windows系统支持emoji显示")
        print("4. 首次运行可能需要几秒钟启动")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")
        return False
    
    return True

if __name__ == '__main__':
    build_exe()





