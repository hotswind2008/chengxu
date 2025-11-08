#!/bin/bash

echo "============================================="
echo "   三门问题游戏 - macOS APP 一键打包"
echo "============================================="
echo ""

echo "[1/3] 检查并安装依赖..."
pip3 install pyinstaller pillow matplotlib
echo ""

echo "[2/3] 清理旧文件..."
rm -rf build dist "三门问题游戏.spec" "三门问题游戏.app"
echo ""

echo "[3/3] 开始打包..."
python3 -m PyInstaller --name=三门问题游戏 \
    --onefile \
    --windowed \
    --clean \
    --noconfirm \
    monty_hall_canvas.py

echo ""
echo "============================================="
if [ -f "dist/三门问题游戏" ]; then
    echo "   ✓ 打包成功！"
    echo ""
    echo "   可执行文件位置: dist/三门问题游戏"
    echo "   文件大小: $(du -h 'dist/三门问题游戏' | cut -f1)"
else
    echo "   ✗ 打包失败！"
    echo "   请检查错误信息"
fi
echo "============================================="
echo ""
