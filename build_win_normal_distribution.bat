@echo off
setlocal

REM 打包正态分布演示程序为 Windows 可执行文件
REM 使用方法：双击本脚本，或在命令行中执行

cd /d "%~dp0"

echo ============================================================
echo 正态分布参数变化演示 - Windows 打包
echo ============================================================

REM 1) 安装依赖（包含 matplotlib 与 pyinstaller）
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 2) 使用 PyInstaller 打包
REM 说明：
REM  -w / --windowed        不显示控制台窗口
REM  --clean                清理临时构建文件
REM  --noconfirm            覆盖上一次构建产物
REM  --collect-data         收集 matplotlib 的运行数据（字体、样式等）
REM  --collect-submodules   收集 matplotlib 及其后端子模块
REM  --hidden-import        确保 TkAgg 后端所需的 tkinter 被收集
pyinstaller ^
  --noconfirm --clean -w ^
  --name normal_distribution_demo ^
  --collect-data matplotlib ^
  --collect-submodules matplotlib ^
  --collect-submodules matplotlib.backends ^
  --hidden-import=tkinter ^
  normal_distribution_demo.py

echo.
echo 打包完成！
echo 目录：dist\normal_distribution_demo\
echo 可执行文件：dist\normal_distribution_demo\normal_distribution_demo.exe
echo.
echo 若双击无界面，请在 Windows 设置中确认图形后端支持（一般默认即可）。
echo 需要中文字体显示，请在系统中安装如「SimHei」或「Microsoft YaHei」字体。
echo.
pause


