# 三门问题游戏 - 打包说明

## 📦 快速打包

### Windows 系统
1. **双击运行** `一键打包.bat`
2. 等待打包完成
3. 在 `dist` 文件夹找到 `三门问题游戏.exe`

### macOS 系统
1. 打开终端，进入项目目录
2. 运行：`chmod +x 一键打包.sh`
3. 运行：`./一键打包.sh`
4. 在 `dist` 文件夹找到可执行文件

---

## 🔧 手动打包（如果一键打包失败）

### 第一步：安装依赖
```bash
# Windows
pip install pyinstaller pillow matplotlib

# macOS/Linux
pip3 install pyinstaller pillow matplotlib
```

### 第二步：打包命令
```bash
# Windows
pyinstaller --name=三门问题游戏 --onefile --windowed --clean monty_hall_windows.py

# macOS/Linux
pyinstaller --name=三门问题游戏 --onefile --windowed --clean monty_hall_windows.py
```

### 第三步：查找结果
- 可执行文件在 `dist` 目录下
- Windows: `dist\三门问题游戏.exe`
- macOS: `dist/三门问题游戏`

---

## 💡 重要说明

### 1. 关于 Windows 和 macOS 的兼容性
`monty_hall_windows.py` 已经实现了**跨平台自适应**：

- **Windows**: 使用 `Segoe UI Emoji` 和 `Microsoft YaHei` 字体
- **macOS**: 使用 `Apple Color Emoji` 和 `Arial` 字体
- **自动检测**: 程序会自动识别运行的系统并调整字体和大小

### 2. 关于 Emoji 显示
- **Windows**: emoji 会使用 Windows 系统的 emoji 样式（扁平化设计）
- **macOS**: emoji 会使用 macOS 系统的 emoji 样式（更立体）
- **这是正常的**：不同系统的 emoji 风格本来就不同

### 3. 如果 emoji 显示为方框
**在 Windows 上**，如果看到方框：
- 确保 Windows 10/11 是最新版本
- 检查是否安装了 emoji 字体
- 可能需要重启电脑

**解决方案**：程序已自动配置最佳字体，通常不会出现问题。

### 4. 打包后文件大小
- Windows EXE: 约 50-80 MB（因为包含了 Python 和所有依赖）
- macOS APP: 约 60-90 MB
- 这是正常的，因为打包了整个运行环境

### 5. 打包注意事项
- **必须在目标系统上打包**：
  - 想要 Windows EXE，必须在 Windows 上打包
  - 想要 macOS APP，必须在 macOS 上打包
- **首次打包较慢**：需要下载和编译，大约 2-5 分钟
- **再次打包较快**：如果修改代码后重新打包，只需 30 秒-1 分钟

---

## 🐛 常见问题

### Q: 打包后双击没反应？
A: 这是正常的，程序可能需要几秒钟启动。如果等待 10 秒后仍无反应，请在命令行运行查看错误信息。

### Q: Windows Defender 报毒？
A: 这是误报。PyInstaller 打包的程序经常被误报。可以添加信任或发送给微软分析。

### Q: 打包失败提示找不到模块？
A: 运行 `pip install pyinstaller pillow matplotlib` 重新安装依赖。

### Q: 游戏运行正常，但打包后出错？
A: 在命令行运行打包后的程序，查看具体错误信息：
```bash
# Windows
dist\三门问题游戏.exe

# macOS
./dist/三门问题游戏
```

### Q: 想减小文件大小？
A: 可以移除 `--onefile` 参数，会生成一个文件夹（包含多个文件），大小会小一些，但分发时需要打包整个文件夹。

---

## 📱 分发给其他人

### Windows
1. 将 `dist\三门问题游戏.exe` 发送给别人
2. 对方**不需要**安装 Python
3. 对方**不需要**安装任何依赖
4. 直接双击即可运行

### macOS
1. 将 `dist/三门问题游戏` 发送给别人
2. 对方可能需要在"系统设置 > 隐私与安全性"中允许运行
3. 或者在终端运行：`xattr -cr 三门问题游戏` 移除隔离属性

---

## 🎮 游戏说明

这是一个**蒙提霍尔问题**（Monty Hall Problem）的互动游戏：

### 游戏规则
1. 有 3 扇门，其中 1 扇后面有汽车 🚗，2 扇后面有山羊 🐐
2. 你先选择一扇门
3. 主持人会打开另外一扇有山羊的门
4. 你可以选择**坚持原选择**或**换门**
5. 看看哪种策略更容易获胜！

### 概率理论
- **坚持原选择**：获胜概率 33.3%
- **换门**：获胜概率 66.7%
- **换门策略是最优的！**

游戏会实时显示统计数据和趋势图，帮助你验证这个违反直觉的概率结论。

---

## 📊 文件说明

- `monty_hall_windows.py` - 游戏主程序（跨平台优化版）
- `一键打包.bat` - Windows 一键打包脚本
- `一键打包.sh` - macOS/Linux 一键打包脚本
- `打包说明README.md` - 本文档

---

## 🔄 更新日志

### v3.0 - Windows 兼容版（当前版本）
- ✅ 跨平台自动适配（Windows/macOS）
- ✅ 系统字体自动选择
- ✅ Emoji 大小自适应
- ✅ 中文字体完美支持
- ✅ 统计图表显示优化

### v2.0 - 最终版
- ✅ 使用系统原生 emoji
- ✅ 大门尺寸优化
- ✅ 颜色对比度增强

### v1.0 - 初始版本
- ✅ 基本游戏功能
- ✅ 实时统计
- ✅ 图表显示

---

## 📞 技术支持

如有问题，请检查：
1. Python 版本（建议 3.8+）
2. 依赖是否安装完整
3. 系统是否支持 tkinter（通常默认支持）

祝你游戏愉快！🎉





