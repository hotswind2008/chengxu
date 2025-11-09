"""
正态分布参数变化演示程序
演示均值(μ)和标准差(σ)对正态分布图形的影响，以及三sigma准则
"""

import sys
import argparse
import os
import matplotlib
# 若外部已通过环境变量指定后端（如 MPLBACKEND=Agg），则尊重不覆盖
_env_backend = os.environ.get('MPLBACKEND')
# 若明确为 Agg，则忽略该设置，避免在 Windows 可执行版中走无界面路径
if _env_backend and _env_backend.lower() == 'agg':
    try:
        del os.environ['MPLBACKEND']
    except Exception:
        pass
    _env_backend = None
if _env_backend is None:
    # Windows 上优先强制 TkAgg，避免选择到不兼容后端
    if sys.platform.startswith('win'):
        try:
            matplotlib.use('TkAgg')
        except Exception:
            pass
    else:
        # macOS / Linux：按优先级尝试
        for _backend in ('MacOSX', 'TkAgg', 'Qt5Agg', 'QtAgg'):
            try:
                matplotlib.use(_backend)
                break
            except Exception:
                continue
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
from matplotlib.widgets import Slider

# 设置中文字体（包含 Windows 常见字体）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'SimSun', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class NormalDistributionDemo:
    """正态分布演示类"""
    
    def __init__(self):
        # 初始参数
        self.mu = 0.0  # 均值
        self.sigma = 1.0  # 标准差
        
        # 固定的x轴范围，用于更好地对比不同sigma下的图形形状
        # 使用固定范围可以更清楚地看出"高瘦"和"矮胖"的区别
        self.fixed_x_range = [-6, 6]  # 固定范围，覆盖大多数情况
        
        # 固定的y轴最大值，保持y轴范围不变，让图形变化
        # 基于最小sigma值（0.1）计算峰值，确保所有情况都能显示
        # 峰值 = 1/(σ√(2π))，当σ=0.1时，峰值最大
        min_sigma = 0.1
        max_peak = 1 / (min_sigma * np.sqrt(2 * np.pi))
        self.fixed_y_max = max_peak * 1.2  # 留20%的余量给标签
        # 动态放大系数：让曲线在不同 σ 下占据更多可视高度，但不超过固定上限
        self.y_scale_factor = 1.8
        
        # 创建图形和子图
        self.default_figsize = (22, 14)
        self.fig = plt.figure(figsize=self.default_figsize)
        self.fig.patch.set_facecolor('#F5F5DC')
        
        # 主图：显示正态分布曲线和三sigma准则
        self.ax_main = plt.subplot(2, 1, 1)
        self.ax_main.set_facecolor('#FFFFFF')
        
        # 创建第二个子图显示CDF（可选）
        self.show_cdf = False
        self.ax_cdf = None
        
        # 三西格玛互动：k 值和是否显示尾部区域
        self.k = 1.0
        self.show_tails = False
        
        # 创建滑块区域
        self.ax_mu = plt.axes([0.15, 0.06, 0.35, 0.03])
        self.ax_sigma = plt.axes([0.55, 0.06, 0.35, 0.03])
        self.ax_k = plt.axes([0.35, 0.015, 0.30, 0.028])
        
        # 创建滑块
        self.slider_mu = Slider(self.ax_mu, '均值 μ', -5.0, 5.0, 
                               valinit=self.mu, valstep=0.1)
        self.slider_sigma = Slider(self.ax_sigma, '标准差 σ', 0.1, 3.0, 
                                   valinit=self.sigma, valstep=0.1)
        self.slider_k = Slider(self.ax_k, 'kσ 范围', 1, 3, valinit=self.k, valstep=1)
        
        # 绑定滑块事件
        self.slider_mu.on_changed(self.update)
        self.slider_sigma.on_changed(self.update)
        self.slider_k.on_changed(self.update)
        
        # 绑定键盘事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 存储绘制的对象
        self.curve = None
        self.fill_regions = []
        self.vertical_lines = []
        self.text_labels = []
        self.prob_text = None
        self._help_shown = False
        
        # 初始化绘制
        self.update(None)
    
    def show_help(self, force=False):
        """显示帮助信息"""
        if force or not self._help_shown:
            self._help_shown = True
            help_text = (
            "\n" + "="*60 + "\n"
            "正态分布参数变化演示 - 操作说明\n"
            "="*60 + "\n"
            "功能说明:\n"
            "  • 拖动上方滑块调整均值(μ)，观察曲线左右移动\n"
            "  • 拖动下方滑块调整标准差(σ)，观察曲线宽窄变化\n"
            "  • 彩色区域显示三sigma准则的覆盖范围:\n"
            "    - 绿色区域: μ±σ (68.27%)\n"
            "    - 黄色区域: μ±2σ (95.45%)\n"
            "    - 橙色区域: μ±3σ (99.73%)\n"
            "  • 垂直虚线标记了μ, μ±σ, μ±2σ, μ±3σ的位置\n\n"
            "键盘快捷键:\n"
            "  • 左/右方向键: μ 减/加 0.1\n"
            "  • 上/下方向键: σ 加/减 0.1\n"
            "  • 't' 键: 切换显示 μ±kσ 之外的尾部区域\n"
            "  • '+' / '=' 键: 放大窗口尺寸\n"
            "  • '-' 键: 缩小窗口尺寸\n"
            "  • 'f' 键: 切换全屏\n"
            "  • 's' 键: 保存当前图片\n"
            "  • 'r' 键: 重置参数到默认值 (μ=0, σ=1)\n"
            "  • 'c' 键: 切换显示累积分布函数(CDF)\n"
            "  • 'h' 键: 显示帮助信息\n"
            "  • 'q' 键: 退出程序\n\n"
            "三sigma准则:\n"
            "  • 68.27%的数据落在μ±σ范围内\n"
            "  • 95.45%的数据落在μ±2σ范围内\n"
            "  • 99.73%的数据落在μ±3σ范围内\n"
            "="*60 + "\n"
            )
            print(help_text, end='', flush=True)
    
    def normal_pdf(self, x, mu=None, sigma=None):
        """计算正态分布概率密度函数"""
        if mu is None:
            mu = self.mu
        if sigma is None:
            sigma = self.sigma
        return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    
    def normal_cdf(self, x, mu=None, sigma=None):
        """计算正态分布累积分布函数（使用误差函数）"""
        if mu is None:
            mu = self.mu
        if sigma is None:
            sigma = self.sigma
        
        # 使用误差函数计算CDF: CDF(x) = 0.5 * (1 + erf((x-μ)/(σ√2)))
        z = (x - mu) / (sigma * np.sqrt(2))
        # 使用math.erf处理标量，numpy的vectorize处理数组
        if np.isscalar(z):
            return 0.5 * (1 + math.erf(z))
        else:
            erf_vec = np.vectorize(math.erf)
            return 0.5 * (1 + erf_vec(z))
    
    def update(self, val):
        """更新图形"""
        # 获取当前参数值
        self.mu = self.slider_mu.val
        self.sigma = self.slider_sigma.val
        
        # 清除之前的绘制
        self.ax_main.clear()
        
        # 使用固定的x轴范围；改变 μ 时，横轴坐标不动，曲线平行移动
        # 这样可以直观看到曲线在固定坐标下的左右平移
        x_min = self.fixed_x_range[0]
        x_max = self.fixed_x_range[1]
        x = np.linspace(x_min, x_max, 1000)
        
        # 计算正态分布概率密度函数
        y = self.normal_pdf(x)
        
        # 计算理论最大概率密度值（在x=μ处）
        # 正态分布在x=μ处的峰值 = 1/(σ√(2π))
        # 当σ减小时，峰值增加（图形变高瘦）
        # 当σ增大时，峰值减小（图形变矮胖）
        theoretical_max = 1 / (self.sigma * np.sqrt(2 * np.pi))
        # 使用动态上限：在不超过固定上限的情况下，放大当前曲线显示高度
        y_max = min(self.fixed_y_max, theoretical_max * self.y_scale_factor)
        
        # 绘制正态分布曲线
        self.curve, = self.ax_main.plot(x, y, 'b-', linewidth=3.0, 
                                        label=f'正态分布 N(μ={self.mu:.2f}, σ={self.sigma:.2f})')
        
        # 当前k值（取整为1/2/3）
        self.k = float(int(self.slider_k.val))
        
        # 计算三sigma准则的关键点
        sigma_points = [
            (self.mu - 3*self.sigma, 'μ-3σ', '#FF6B6B', 0.9973),
            (self.mu - 2*self.sigma, 'μ-2σ', '#FFD93D', 0.9545),
            (self.mu - self.sigma, 'μ-σ', '#6BCF7F', 0.6827),
            (self.mu, 'μ', '#4D96FF', None),
            (self.mu + self.sigma, 'μ+σ', '#6BCF7F', 0.6827),
            (self.mu + 2*self.sigma, 'μ+2σ', '#FFD93D', 0.9545),
            (self.mu + 3*self.sigma, 'μ+3σ', '#FF6B6B', 0.9973),
        ]
        
        # 绘制填充区域（从外到内，避免覆盖）
        # 3σ区域（橙色）
        x_3sigma = np.linspace(self.mu - 3*self.sigma, self.mu + 3*self.sigma, 500)
        y_3sigma = self.normal_pdf(x_3sigma)
        fill_3sigma = self.ax_main.fill_between(x_3sigma, 0, y_3sigma, 
                                                alpha=0.12, color='#FF6B6B', 
                                                label='μ±3σ (99.73%)')
        
        # 2σ区域（黄色）
        x_2sigma = np.linspace(self.mu - 2*self.sigma, self.mu + 2*self.sigma, 500)
        y_2sigma = self.normal_pdf(x_2sigma)
        fill_2sigma = self.ax_main.fill_between(x_2sigma, 0, y_2sigma, 
                                               alpha=0.18, color='#FFD93D', 
                                               label='μ±2σ (95.45%)')
        
        # 1σ区域（绿色）
        x_1sigma = np.linspace(self.mu - self.sigma, self.mu + self.sigma, 500)
        y_1sigma = self.normal_pdf(x_1sigma)
        fill_1sigma = self.ax_main.fill_between(x_1sigma, 0, y_1sigma, 
                                                alpha=0.24, color='#6BCF7F', 
                                                label='μ±σ (68.27%)')
        
        self.fill_regions = [fill_3sigma, fill_2sigma, fill_1sigma]
        
        # 动态 kσ 区域高亮（更醒目）
        k_left = self.mu - self.k * self.sigma
        k_right = self.mu + self.k * self.sigma
        x_k = np.linspace(max(x_min, k_left), min(x_max, k_right), 400)
        if len(x_k) > 1:
            y_k = self.normal_pdf(x_k)
            dyn_color = '#1E4BD1' if int(self.k) == 2 else ('#8A2BE2' if int(self.k) == 3 else '#4D96FF')
            dyn_alpha = 0.42 if int(self.k) == 2 else (0.36 if int(self.k) == 3 else 0.45)
            self.ax_main.fill_between(x_k, 0, y_k, color=dyn_color, alpha=dyn_alpha,
                                      edgecolor=dyn_color, linewidth=1.0,
                                      label=f'当前 μ±{int(self.k)}σ')
            # 在边界画粗线
            self.ax_main.axvline(k_left, color=dyn_color, linewidth=2.8, linestyle='-')
            self.ax_main.axvline(k_right, color=dyn_color, linewidth=2.8, linestyle='-')
            # 在顶部画双向箭头标注宽度 2kσ
            arrow_y = y_max * 0.82
            self.ax_main.annotate('', xy=(k_left, arrow_y), xytext=(k_right, arrow_y),
                                  arrowprops=dict(arrowstyle='<->', color=dyn_color, lw=2.2))
            self.ax_main.text((k_left + k_right)/2.0, arrow_y * 1.02, f'宽度 = {int(self.k)}σ',
                              ha='center', va='bottom', fontsize=11, color=dyn_color, fontweight='bold')
        
        # 可选：高亮尾部（μ±kσ 之外）
        if self.show_tails:
            # 左尾
            if x_min < k_left:
                x_tail_l = np.linspace(x_min, min(k_left, x_max), 300)
                if len(x_tail_l) > 1:
                    y_tail_l = self.normal_pdf(x_tail_l)
                    self.ax_main.fill_between(x_tail_l, 0, y_tail_l, color='#FF6B6B', alpha=0.18)
            # 右尾
            if x_max > k_right:
                x_tail_r = np.linspace(max(k_right, x_min), x_max, 300)
                if len(x_tail_r) > 1:
                    y_tail_r = self.normal_pdf(x_tail_r)
                    self.ax_main.fill_between(x_tail_r, 0, y_tail_r, color='#FF6B6B', alpha=0.18)

        # 若 k=3，突出显示与 k=2 的增量区域（2σ~3σ），使用明显颜色填充曲线下方
        if int(self.k) == 3:
            inc_left_l = self.mu - 3*self.sigma
            inc_left_r = self.mu - 2*self.sigma
            inc_right_l = self.mu + 2*self.sigma
            inc_right_r = self.mu + 3*self.sigma
            # 左侧带（曲线下）
            x_band_l = np.linspace(max(x_min, inc_left_l), min(x_max, inc_left_r), 300)
            if len(x_band_l) > 1:
                y_band_l = self.normal_pdf(x_band_l)
                self.ax_main.fill_between(x_band_l, 0, y_band_l, color='#FF8C00', alpha=0.38,
                                          label='k=3 增量区 (2σ→3σ)')
            # 右侧带（曲线下）
            x_band_r = np.linspace(max(x_min, inc_right_l), min(x_max, inc_right_r), 300)
            if len(x_band_r) > 1:
                y_band_r = self.normal_pdf(x_band_r)
                self.ax_main.fill_between(x_band_r, 0, y_band_r, color='#FF8C00', alpha=0.38)
        
        # 绘制垂直虚线标记关键点
        self.vertical_lines = []
        self.text_labels = []
        for x_val, label, color, prob in sigma_points:
            if label == 'μ':
                # 均值用粗实线
                line = self.ax_main.axvline(x_val, color=color, linestyle='-', 
                                           linewidth=2.5, alpha=0.8, zorder=10)
            else:
                # 其他用虚线
                line = self.ax_main.axvline(x_val, color=color, linestyle='--', 
                                           linewidth=2, alpha=0.7, zorder=9)
            self.vertical_lines.append(line)
            
            # 添加标签（使用固定y_max，放在坐标轴内）
            if label == 'μ':
                text = self.ax_main.text(x_val, y_max * 0.95, label, 
                                        ha='center', va='bottom',
                                        fontsize=12, fontweight='bold',
                                        color=color, zorder=11)
                # 在竖线附近标注 μ 的数值
                mu_value_text = f"μ={self.mu:.2f}"
                self.ax_main.text(x_val, y_max * 0.06, mu_value_text,
                                  ha='center', va='bottom', fontsize=11,
                                  fontweight='bold', color=color, zorder=11,
                                  bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                            edgecolor=color, alpha=0.75))
            else:
                text = self.ax_main.text(x_val, y_max * 0.90, label, 
                                        ha='center', va='bottom',
                                        fontsize=10, color=color, zorder=11)
            self.text_labels.append(text)
        
        # 设置图形属性
        # y轴范围：使用固定范围，保持不变
        self.ax_main.set_xlim(x_min, x_max)
        self.ax_main.set_ylim(0, y_max)
        self.ax_main.set_xlabel('x', fontsize=14)
        self.ax_main.set_ylabel('概率密度 f(x)', fontsize=14)
        self.ax_main.set_title(f'正态分布 N(μ={self.mu:.2f}, σ={self.sigma:.2f}) 与三sigma准则', 
                              fontsize=16, fontweight='bold', pad=15)
        self.ax_main.tick_params(labelsize=13)
        self.ax_main.grid(True, alpha=0.3, linestyle='--')
        self.ax_main.legend(loc='upper right', fontsize=11, framealpha=0.9)
        
        # 计算动态 kσ 覆盖率与与 k-1 的差值
        prob_k = float(self.normal_cdf(self.mu + self.k * self.sigma) -
                       self.normal_cdf(self.mu - self.k * self.sigma))
        prev_k = int(self.k) - 1 if int(self.k) > 1 else None
        delta_text = ''
        if prev_k is not None:
            prob_prev = float(self.normal_cdf(self.mu + prev_k * self.sigma) -
                              self.normal_cdf(self.mu - prev_k * self.sigma))
            delta_text = f"增量 Δ(±{prev_k}σ→±{int(self.k)}σ) = {(prob_k-prob_prev)*100:.2f}%\n"
        
        # 添加参数与概率说明文本
        prob_text = (
            f"参数: μ={self.mu:.2f}, σ={self.sigma:.2f}\n"
            f"三sigma准则概率:\n"
            f"  P(μ-σ ≤ X ≤ μ+σ) = 68.27%\n"
            f"  P(μ-2σ ≤ X ≤ μ+2σ) = 95.45%\n"
            f"  P(μ-3σ ≤ X ≤ μ+3σ) = 99.73%\n"
            f"当前 μ±{int(self.k)}σ 覆盖率 = {prob_k*100:.2f}%\n"
            f"{delta_text}"
            f"峰值: {theoretical_max:.4f}"
        )
        self.prob_text = self.ax_main.text(0.02, 0.98, prob_text,
                                           transform=self.ax_main.transAxes,
                                           fontsize=10,
                                           verticalalignment='top',
                                           bbox=dict(boxstyle='round', 
                                                    facecolor='wheat', 
                                                    alpha=0.8),
                                           zorder=12)
        
        # 如果启用CDF显示，添加第二个子图
        if self.show_cdf:
            # 清除或创建CDF子图（避免影响滑动条 Axes）
            if self.ax_cdf is None or (self.ax_cdf not in self.fig.axes):
                self.ax_cdf = self.fig.add_subplot(2, 1, 2)
            else:
                self.ax_cdf.clear()
            
            # 计算CDF
            cdf_y = self.normal_cdf(x)
            
            # 绘制CDF曲线
            self.ax_cdf.plot(x, cdf_y, 'r-', linewidth=2.5, 
                            label=f'累积分布函数 CDF')
            
            # 标记关键点
            for x_val, label, color, prob in sigma_points:
                if prob is not None:
                    cdf_val = self.normal_cdf(x_val)
                    self.ax_cdf.plot(x_val, cdf_val, 'o', color=color, 
                                    markersize=8, zorder=10)
            
            self.ax_cdf.set_xlim(x_min, x_max)
            self.ax_cdf.set_ylim(0, 1)
            self.ax_cdf.set_xlabel('x', fontsize=13)
            self.ax_cdf.set_ylabel('累积概率 F(x)', fontsize=13)
            self.ax_cdf.set_title('累积分布函数 (CDF)', 
                                 fontsize=14, fontweight='bold')
            self.ax_cdf.tick_params(labelsize=12)
            self.ax_cdf.grid(True, alpha=0.3, linestyle='--')
            self.ax_cdf.legend(loc='lower right', fontsize=10, framealpha=0.9)
            
            # 调整布局：放大主图窗口区域，保持整体窗口尺寸不变
            self.ax_main.set_position([0.07, 0.34, 0.90, 0.60])  # left, bottom, width, height
            self.ax_cdf.set_position([0.07, 0.22, 0.90, 0.12])
        else:
            # 如果关闭CDF，移除第二个子图（不影响滑动条 Axes）
            if self.ax_cdf is not None and (self.ax_cdf in self.fig.axes):
                self.fig.delaxes(self.ax_cdf)
            self.ax_cdf = None
            # 放大主图窗口区域，保持整体窗口尺寸不变
            self.ax_main.set_position([0.07, 0.16, 0.90, 0.78])
        
        # 重新绘制
        self.fig.canvas.draw_idle()
    
    def on_key(self, event):
        """处理键盘事件"""
        key = event.key.lower()
        
        if key == 's':
            filename = f'normal_distribution_mu{self.mu:.2f}_sigma{self.sigma:.2f}.png'
            self.fig.savefig(filename, dpi=300, facecolor='#F5F5DC', bbox_inches='tight')
            print(f"图片已保存: {filename}")
        elif key == 'r':
            self.slider_mu.set_val(0.0)
            self.slider_sigma.set_val(1.0)
            print("已重置参数: μ=0.0, σ=1.0")
        elif key == 'c':
            self.show_cdf = not self.show_cdf
            self.update(None)
            status = "开启" if self.show_cdf else "关闭"
            print(f"累积分布函数(CDF)显示已{status}")
        elif key in ('left', 'right'):
            step = self.slider_mu.valstep or 0.1
            delta = -step if key == 'left' else step
            new_mu = float(np.clip(self.mu + delta, self.slider_mu.valmin, self.slider_mu.valmax))
            self.slider_mu.set_val(round(new_mu, 2))
            print(f"μ -> {self.slider_mu.val:.2f}")
        elif key in ('down', 'up'):
            step = self.slider_sigma.valstep or 0.1
            delta = step if key == 'up' else -step
            new_sigma = float(np.clip(self.sigma + delta, self.slider_sigma.valmin, self.slider_sigma.valmax))
            self.slider_sigma.set_val(round(new_sigma, 2))
            print(f"σ -> {self.slider_sigma.val:.2f}")
        elif key == 't':
            self.show_tails = not self.show_tails
            self.update(None)
            status = "开启" if self.show_tails else "关闭"
            print(f"尾部区域显示已{status}")
        elif key in ('+', '='):
            w, h = self.fig.get_size_inches()
            self.fig.set_size_inches(w * 1.12, h * 1.12, forward=True)
            self.fig.canvas.draw_idle()
            print(f"窗口尺寸 -> {self.fig.get_size_inches()[0]:.1f} x {self.fig.get_size_inches()[1]:.1f} in")
        elif key == '-':
            w, h = self.fig.get_size_inches()
            self.fig.set_size_inches(w / 1.12, h / 1.12, forward=True)
            self.fig.canvas.draw_idle()
            print(f"窗口尺寸 -> {self.fig.get_size_inches()[0]:.1f} x {self.fig.get_size_inches()[1]:.1f} in")
        elif key == 'f':
            manager = getattr(self.fig.canvas, "manager", None)
            toggle = getattr(manager, "full_screen_toggle", None) if manager is not None else None
            if callable(toggle):
                toggle()
            else:
                # 后备方案：将窗口放大到默认尺寸的1.4倍
                w, h = self.default_figsize
                self.fig.set_size_inches(w * 1.4, h * 1.4, forward=True)
            self.fig.canvas.draw_idle()
        elif key == 'h':
            self.show_help(force=True)
        elif key == 'q':
            plt.close(self.fig)
            print("退出程序")
    
    def show(self):
        """显示交互式窗口"""
        plt.subplots_adjust(bottom=0.15)
        plt.show()

def main():
    """主函数"""
    print("=" * 60)
    print("正态分布参数变化演示程序")
    print("=" * 60)

    # 命令行参数：便于在无GUI环境生成图片
    parser = argparse.ArgumentParser(description='正态分布参数变化演示')
    parser.add_argument('--save', action='store_true', help='保存当前图像并退出')
    parser.add_argument('--mu', type=float, default=None, help='设置均值 μ')
    parser.add_argument('--sigma', type=float, default=None, help='设置标准差 σ (0.1-3.0)')
    parser.add_argument('--k', type=int, choices=[1,2,3], default=None, help='设置 kσ 范围 (1/2/3)')
    parser.add_argument('--tails', action='store_true', help='显示 μ±kσ 之外的尾部区域')
    args = parser.parse_args()
    
    try:
        app = NormalDistributionDemo()

        # 覆盖参数（如传入）
        if args.mu is not None:
            app.slider_mu.set_val(float(np.clip(args.mu, app.slider_mu.valmin, app.slider_mu.valmax)))
        if args.sigma is not None:
            app.slider_sigma.set_val(float(np.clip(args.sigma, app.slider_sigma.valmin, app.slider_sigma.valmax)))
        if args.k is not None:
            app.slider_k.set_val(args.k)
        if args.tails:
            app.show_tails = True
            app.update(None)

        backend = plt.get_backend().lower()

        # 如指定 --save 或处于无GUI后端(严格等于 agg) 则保存并退出
        if args.save or (backend == 'agg'):
            outfile = 'normal_distribution.png'
            app.fig.savefig(outfile, dpi=300, facecolor='#F5F5DC', bbox_inches='tight')
            if backend == 'agg':
                print(f"\n当前环境未启用图形界面（backend={backend}），已保存静态图片: {outfile}")
                print("如需交互式窗口，请在本机终端运行: python normal_distribution_demo.py\n")
            else:
                print(f"\n已保存图片: {outfile}")
            return

        # 仅在交互模式下显示一次帮助信息
        app.show_help()
        print("\n✓ 交互式窗口已打开！")
        print("提示: 拖动滑块或用方向键调整参数\n")
        app.show()
        
    except Exception as e:
        print(f"\n✗ 运行程序时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 在无控制台的打包环境下，弹出图形化错误提示（尽量不影响非GUI环境）
        try:
            import tkinter as _tk
            from tkinter import messagebox as _mb
            _root = _tk.Tk()
            _root.withdraw()
            _mb.showerror("程序错误", f"运行出错：{e}\n\n详情已打印到日志/控制台。")
            _root.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    main()

