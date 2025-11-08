@echo off
chcp 65001
echo =============================================
echo    三门问题游戏 - Windows EXE 一键打包
echo =============================================
echo.

echo [1/3] 检查并安装依赖...
pip install pyinstaller pillow matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

echo [2/3] 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "三门问题游戏.spec" del "三门问题游戏.spec"
echo.

echo [3/3] 开始打包...
python -m PyInstaller --name=三门问题游戏 ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    monty_hall_canvas.py

echo.
echo =============================================
if exist "dist\三门问题游戏.exe" (
    echo    ✓ 打包成功！
    echo.
    echo    可执行文件位置: dist\三门问题游戏.exe
    echo    文件大小: 
    dir "dist\三门问题游戏.exe" | find "三门问题游戏.exe"
) else (
    echo    ✗ 打包失败！
    echo    请检查错误信息
)
echo =============================================
echo.
pause
