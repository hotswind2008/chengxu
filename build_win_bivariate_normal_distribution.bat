@echo off
setlocal
chcp 65001

REM 二维正态分布演示 - Windows EXE 打包脚本
REM 使用方法：双击本脚本，或在命令行中执行

cd /d "%~dp0"

echo ============================================================
echo 二维正态分布演示 - Windows 打包
echo ============================================================
echo.

echo [1/2] 安装依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.

echo [2/2] 开始打包...
REM 说明：
REM  -w / --windowed        不显示控制台窗口
REM  --clean                清理临时构建文件
REM  --noconfirm            覆盖上一次构建产物
REM  --collect-data         收集 matplotlib 的运行数据（字体、样式等）
REM  --collect-submodules   收集 matplotlib 及其后端子模块
REM  --hidden-import        确保 TkAgg 后端所需的 tkinter 被收集
pyinstaller ^
  --noconfirm --clean -w ^
  --name bivariate_normal_distribution_demo ^
  --collect-data matplotlib ^
  --collect-submodules matplotlib ^
  --collect-submodules matplotlib.backends ^
  --hidden-import=tkinter ^
  bivariate_normal_distribution_demo.py

echo.
if exist "dist\\bivariate_normal_distribution_demo\\bivariate_normal_distribution_demo.exe" (
  echo ✓ 打包完成！
  echo 可执行文件：dist\bivariate_normal_distribution_demo\bivariate_normal_distribution_demo.exe
) else (
  echo ✗ 打包失败，请检查上方日志。
)
echo.
echo 提示：
echo - 若双击无界面，请在 Windows 中确认图形后端支持（默认 TkAgg）。
echo - 如需單文件 EXE，可在上方命令中加入 --onefile。
echo - 需要中文字体显示，请在系统安装「Microsoft YaHei」或「SimHei」。
echo.
pause


