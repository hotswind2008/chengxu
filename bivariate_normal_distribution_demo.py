"""
二维正态分布演示程序
支持通过滑块交互调整参数 μx, μy, σx, σy, 相关系数 ρ，并展示三维表面图 (PDF)。
在无GUI环境下可使用 --save 直接输出图片。
"""

import sys
import argparse
import os
import matplotlib

# 在 --save 模式下强制使用 Agg 后端，避免初始化 GUI
_force_agg = ('--save' in sys.argv)
_env_backend = os.environ.get('MPLBACKEND')
if _force_agg:
    try:
        matplotlib.use('Agg')
    except Exception:
        pass
elif _env_backend is None:
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

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - 激活3D投影
from matplotlib import colors

# 设置中文字体（包含 Windows 常见字体）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'SimSun', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 170  # 提升交互窗口清晰度


class BivariateNormalDistributionDemo:
    """二维正态分布交互演示"""

    def __init__(self):
        # 初始参数
        self.mu_x = 0.0
        self.mu_y = 0.0
        self.sigma_x = 1.0
        self.sigma_y = 1.0
        self.rho = 0.0  # 相关系数

        # 网格与范围：固定可视化范围，便于对比参数变化
        self.grid_limit = 6.0
        # 双轨渲染：预览(低开销) + 高清(高质量)
        self.grid_size_full = 360
        self.grid_size_preview = 56    # 进一步降低预览网格，保持三维
        self.rcount_full = 220         # 高清采样
        self.rcount_preview = 36       # 更轻预览采样（三维）
        self.preview_delay_ms = 160    # 滑动停止后延时再渲染高清
        self.preview_coalesce_ms = 80  # 合并频繁滑动事件，降低重绘频率
        self.fast_mode = True          # 默认开启“极速模式”：优先流畅性
        self.use_2d_preview = False    # 不使用2D热力图预览，预览也保持三维

        # 预估最大峰值（在 ρ=0、σx/σy 最小时取得）用于设定表面图 z 轴上限
        self.min_sigma = 0.2
        self.max_pdf_peak_scale = 2.2  # 上限放宽，让夸张后更不易被截断
        self.rho_max_abs = 0.95  # 相关系数允许的绝对值上界，用于计算全局z上限
        self.fix_z_axis = True  # 默认固定Z轴，便于观察“高瘦/矮胖”对比
        self.show_wireframe = True  # 默认叠加网格线增强可见性
        # 视觉增强参数
        self.height_exaggeration = 5.0  # 垂直夸张系数，让曲面更“高”
        self.color_map_name = 'turbo'  # 更鲜艳的色图
        self.color_gamma = 0.6  # PowerNorm gamma (<1 提升中低值对比)
        # Z 轴上限参考（与夸张系数解耦，使夸张真正放大曲面）
        self.rho_ref_for_limit = 0.0  # 用 ρ=0 估算全局上限，更贴近日常使用

        # 建图
        self.default_figsize = (30, 18)  # 放大窗口尺寸
        self.fig = plt.figure(figsize=self.default_figsize)
        self.fig.patch.set_facecolor('#F5F5DC')

        # 子图：仅展示3D表面
        self.ax3d = self.fig.add_subplot(1, 1, 1, projection='3d')
        self.ax3d.set_facecolor('#FFFFFF')
        # 填充更大可视区域并设置更接近的视角与比例
        try:
            self.ax3d.set_box_aspect((1.0, 1.0, 1.8))
        except Exception:
            pass
        self.ax3d.view_init(elev=28, azim=-55)
        try:
            self.ax3d.dist = 4.2
        except Exception:
            pass
        self.ax3d.set_position([0.05, 0.14, 0.92, 0.82])  # left, bottom, width, height
        # 叠加一个2D Axes用于“极速预览”的 imshow（与3D同位置，默认隐藏）
        self.ax2d = self.fig.add_axes(self.ax3d.get_position())
        self.ax2d.set_facecolor('#FFFFFF')
        self.ax2d.set_visible(False)
        self.img = None
        # 已绘制对象的句柄（避免每次清空坐标轴导致刻度抖动）
        self.surface = None
        self.wire = None
        # 关闭自动缩放，防止参数变化时坐标轴自动调整
        try:
            self.ax3d.set_autoscale_on(False)
        except Exception:
            pass
        try:
            self.ax2d.set_autoscale_on(False)
        except Exception:
            pass

        # 滑块区域
        # 两排布局：第一排 μx, μy, ρ；第二排 σx, σy 与重置按钮
        self.ax_mux = plt.axes([0.12, 0.07, 0.28, 0.03])
        self.ax_muy = plt.axes([0.46, 0.07, 0.28, 0.03])
        self.ax_rho = plt.axes([0.80, 0.07, 0.12, 0.03])

        self.ax_sigx = plt.axes([0.12, 0.02, 0.28, 0.03])
        self.ax_sigy = plt.axes([0.46, 0.02, 0.28, 0.03])
        self.ax_reset = plt.axes([0.80, 0.02, 0.12, 0.035])

        # 滑块控件
        self.slider_mux = Slider(self.ax_mux, 'μx', -5.0, 5.0, valinit=self.mu_x, valstep=0.1)
        self.slider_muy = Slider(self.ax_muy, 'μy', -5.0, 5.0, valinit=self.mu_y, valstep=0.1)
        self.slider_rho = Slider(self.ax_rho, 'ρ', -0.95, 0.95, valinit=self.rho, valstep=0.01)
        self.slider_sigx = Slider(self.ax_sigx, 'σx', self.min_sigma, 3.0, valinit=self.sigma_x, valstep=0.05)
        self.slider_sigy = Slider(self.ax_sigy, 'σy', self.min_sigma, 3.0, valinit=self.sigma_y, valstep=0.05)
        self.btn_reset = Button(self.ax_reset, '重置', color='#EEEEEE', hovercolor='#DDDDDD')

        # 事件绑定（滑动时先渲染预览，稍后再渲染高清）
        self.slider_mux.on_changed(self.on_slider_changed)
        self.slider_muy.on_changed(self.on_slider_changed)
        self.slider_rho.on_changed(self.on_slider_changed)
        self.slider_sigx.on_changed(self.on_slider_changed)
        self.slider_sigy.on_changed(self.on_slider_changed)
        self.btn_reset.on_clicked(self.on_reset_clicked)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        # 预览→高清 定时器
        self._finalize_timer = self.fig.canvas.new_timer(interval=self.preview_delay_ms)
        self._finalize_timer.add_callback(self._render_high_quality)
        # 合并预览定时器
        self._preview_timer = self.fig.canvas.new_timer(interval=self.preview_coalesce_ms)
        self._preview_timer.add_callback(self._render_preview)

        # 初始化计算网格
        self.X_full, self.Y_full = self._make_grid(self.grid_limit, self.grid_size_full)
        self.X_preview, self.Y_preview = self._make_grid(self.grid_limit, self.grid_size_preview)

        # 计算全局固定 z 轴上限：在参数范围内的理论最大峰值再乘以裕量系数
        # 峰值最大出现在 σx=σy=min_sigma 且 |ρ| 最大处
        # 为了让曲面在常用范围内更“高”，使用 ρ=0 估算上限，且不乘夸张系数
        self.global_z_max = (self._theoretical_peak(self.min_sigma, self.min_sigma, self.rho_ref_for_limit)
                             * self.max_pdf_peak_scale)
        # 预置固定刻度
        self.fixed_xticks = np.arange(-self.grid_limit, self.grid_limit + 1e-9, 2.0)
        self.fixed_yticks = np.arange(-self.grid_limit, self.grid_limit + 1e-9, 2.0)
        # 5 个 z 轴刻度：0, 25%, 50%, 75%, 100%（仅在固定Z轴时使用）
        self.fixed_zticks = np.linspace(0.0, self.global_z_max, 5)
        # 初始化固定坐标轴范围与刻度（一次性设置，后续不随参数改变）
        self.ax3d.set_xlim(-self.grid_limit, self.grid_limit)
        self.ax3d.set_ylim(-self.grid_limit, self.grid_limit)
        self.ax3d.set_xticks(self.fixed_xticks)
        self.ax3d.set_yticks(self.fixed_yticks)
        if self.fix_z_axis:
            self.ax3d.set_zlim(0.0, self.global_z_max)
            self.ax3d.set_zticks(self.fixed_zticks)
        # 2D 预览轴同样固定范围/刻度
        self.ax2d.set_xlim(-self.grid_limit, self.grid_limit)
        self.ax2d.set_ylim(-self.grid_limit, self.grid_limit)
        self.ax2d.set_xticks(self.fixed_xticks)
        self.ax2d.set_yticks(self.fixed_yticks)

        # 首次绘制（高清）
        self._draw_all(quality='high')

    def _make_grid(self, limit: float, size: int):
        axis = np.linspace(-limit, limit, size)
        X, Y = np.meshgrid(axis, axis)
        return X, Y

    def _bivariate_normal_pdf(self, X, Y, mu_x, mu_y, sigma_x, sigma_y, rho):
        """计算二维正态分布概率密度函数值"""
        one_minus_rho2 = 1.0 - rho * rho
        if one_minus_rho2 <= 1e-8:
            one_minus_rho2 = 1e-8
        norm = 1.0 / (2.0 * np.pi * sigma_x * sigma_y * np.sqrt(one_minus_rho2))
        x_std = (X - mu_x) / sigma_x
        y_std = (Y - mu_y) / sigma_y
        expo = -0.5 * (1.0 / one_minus_rho2) * (x_std**2 - 2.0 * rho * x_std * y_std + y_std**2)
        Z = norm * np.exp(expo)
        return Z

    def _theoretical_peak(self, sigma_x, sigma_y, rho):
        """返回给定参数下的理论峰值（在均值处）"""
        one_minus_rho2 = max(1e-8, 1.0 - rho * rho)
        return 1.0 / (2.0 * np.pi * sigma_x * sigma_y * np.sqrt(one_minus_rho2))

    def _draw_all(self, quality='high'):
        """重绘3D图。quality: 'preview' 或 'high'"""
        # 在极速模式下，将高清也降级为预览以保证流畅
        effective_quality = 'preview' if (self.fast_mode and quality == 'high') else quality
        # 移除旧的绘图对象，但不清空坐标轴，保持刻度/范围稳定
        if self.surface is not None:
            try:
                self.surface.remove()
            except Exception:
                pass
            self.surface = None
        if self.wire is not None:
            try:
                self.wire.remove()
            except Exception:
                pass
            self.wire = None

        # 当前参数
        self.mu_x = self.slider_mux.val
        self.mu_y = self.slider_muy.val
        self.sigma_x = self.slider_sigx.val
        self.sigma_y = self.slider_sigy.val
        self.rho = self.slider_rho.val

        # 选择网格与采样粒度
        if effective_quality == 'preview':
            X, Y = self.X_preview, self.Y_preview
            rcount = self.rcount_preview
            ccount = self.rcount_preview
            antialiased = False
            shade = False
            show_wire = False  # 预览关闭网格线以提速
        else:
            X, Y = self.X_full, self.Y_full
            rcount = self.rcount_full
            ccount = self.rcount_full
            antialiased = True
            shade = True
            show_wire = self.show_wireframe

        Z = self._bivariate_normal_pdf(X, Y, self.mu_x, self.mu_y,
                                       self.sigma_x, self.sigma_y, self.rho)

        # 先计算当前应使用的 Z 上限（用于颜色归一化与坐标轴范围）
        peak = self._theoretical_peak(self.sigma_x, self.sigma_y, self.rho)
        if self.fix_z_axis:
            zmax_for_view = self.global_z_max
        else:
            zmax_for_view = min(self.global_z_max, peak * self.max_pdf_peak_scale)
            zmax_for_view = max(zmax_for_view, 0.15)

        # 垂直夸张 & 颜色归一化（增强对比/鲜艳度）
        Z_plot = np.clip(Z * self.height_exaggeration, 0.0, zmax_for_view)
        if effective_quality == 'preview':
            norm = None  # 预览使用默认线性映射，进一步提速
        else:
            norm = colors.PowerNorm(gamma=self.color_gamma, vmin=0.0, vmax=zmax_for_view)
        # 极速预览（可选2D热力图，当前关闭，保持三维）
        if effective_quality == 'preview' and self.fast_mode and self.use_2d_preview:
            # 保持与3D相同的显示区域
            self.ax2d.set_position(self.ax3d.get_position())
            extent = [-self.grid_limit, self.grid_limit, -self.grid_limit, self.grid_limit]
            if self.img is None:
                self.img = self.ax2d.imshow(Z_plot, extent=extent, origin='lower',
                                            cmap=self.color_map_name, vmin=0.0, vmax=zmax_for_view,
                                            interpolation='nearest', aspect='equal')
            else:
                self.img.set_data(Z_plot)
                self.img.set_clim(0.0, zmax_for_view)
            # 固定坐标轴与刻度
            self.ax2d.set_title(f'二维正态分布（预览模式）\nμ=({self.mu_x:.2f},{self.mu_y:.2f}), '
                                f'σ=({self.sigma_x:.2f},{self.sigma_y:.2f}), ρ={self.rho:.2f}',
                                fontsize=14, pad=14, fontweight='bold')
            self.ax2d.set_xlabel('x', fontsize=12)
            self.ax2d.set_ylabel('y', fontsize=12)
            # 切换可见性：隐藏3D，仅显示2D
            self.ax3d.set_visible(False)
            self.ax2d.set_visible(True)
            self.fig.canvas.draw_idle()
            return
        # 3D 表面（高清或非极速预览）
        self.ax2d.set_visible(False)
        self.ax3d.set_visible(True)
        self.surface = self.ax3d.plot_surface(X, Y, Z_plot,
                                              cmap=self.color_map_name,
                                              norm=norm,
                                              rcount=rcount, ccount=ccount,
                                              linewidth=0,
                                              antialiased=antialiased,
                                              shade=shade,
                                              alpha=1.0)
        # 可选叠加网格线以提升可见性
        if show_wire:
            try:
                self.wire = self.ax3d.plot_wireframe(X, Y, Z_plot, rstride=18, cstride=18,
                                                      color='k', linewidth=0.25, alpha=0.14)
            except Exception:
                pass
        # Z 轴：若固定则使用全局上限与固定刻度（反复设置确保稳定）
        if self.fix_z_axis:
            self.ax3d.set_zlim(0.0, self.global_z_max)
            self.ax3d.set_zticks(self.fixed_zticks)
        else:
            # 防止 zmax 过小导致看起来像平面
            self.ax3d.set_zlim(0.0, zmax_for_view)
            # 根据当前上限动态设置 5 个刻度
            self.ax3d.set_zticks(np.linspace(0.0, zmax_for_view, 5))
        self.ax3d.set_title(f'二维正态分布 PDF 表面\nμ=({self.mu_x:.2f},{self.mu_y:.2f}), '
                            f'σ=({self.sigma_x:.2f},{self.sigma_y:.2f}), ρ={self.rho:.2f}',
                            fontsize=14, pad=14, fontweight='bold')
        self.ax3d.set_xlabel('x', fontsize=12)
        self.ax3d.set_ylabel('y', fontsize=12)
        self.ax3d.set_zlabel('f(x, y)', fontsize=12)

        # 统一绘制
        self.fig.canvas.draw_idle()

    # 事件与交互
    def update(self, _):
        # 兼容旧调用：直接高清
        self._draw_all(quality='high')

    def on_slider_changed(self, _):
        # 仅安排预览和高清的定时器，避免每次滑动都重绘
        try:
            if self._finalize_timer.is_running():
                self._finalize_timer.stop()
        except Exception:
            pass
        try:
            if self._preview_timer.is_running():
                self._preview_timer.stop()
        except Exception:
            pass
        try:
            self._preview_timer.start()
        except Exception:
            # 个别后端可能不支持 is_running 判定，直接忽略
            pass
        try:
            self._finalize_timer.start()
        except Exception:
            # 个别后端可能不支持 is_running 判定，直接忽略
            pass

    def _render_high_quality(self):
        try:
            self._finalize_timer.stop()
        except Exception:
            pass
        self._draw_all(quality='high')

    def on_mouse_release(self, _event):
        # 鼠标释放时，立刻切回高清渲染
        self._render_high_quality()
    
    def _render_preview(self):
        try:
            self._preview_timer.stop()
        except Exception:
            pass
        self._draw_all(quality='preview')

    def on_reset_clicked(self, _event):
        self.slider_mux.set_val(0.0)
        self.slider_muy.set_val(0.0)
        self.slider_sigx.set_val(1.0)
        self.slider_sigy.set_val(1.0)
        self.slider_rho.set_val(0.0)

    def on_key(self, event):
        key = event.key.lower()
        if key == 's':
            fname = (f"bivariate_normal_mu({self.mu_x:.2f},{self.mu_y:.2f})_"
                     f"sigma({self.sigma_x:.2f},{self.sigma_y:.2f})_rho({self.rho:.2f}).png")
            self.fig.savefig(fname, dpi=300, facecolor='#F5F5DC', bbox_inches='tight')
            print(f"图片已保存: {fname}")
        elif key == 'r':
            self.on_reset_clicked(None)
        elif key in ('+', '='):
            w, h = self.fig.get_size_inches()
            self.fig.set_size_inches(w * 1.12, h * 1.12, forward=True)
            self.fig.canvas.draw_idle()
        elif key == '-':
            w, h = self.fig.get_size_inches()
            self.fig.set_size_inches(w / 1.12, h / 1.12, forward=True)
            self.fig.canvas.draw_idle()
        elif key == 'f':
            manager = getattr(self.fig.canvas, "manager", None)
            toggle = getattr(manager, "full_screen_toggle", None) if manager is not None else None
            if callable(toggle):
                toggle()
            else:
                w, h = self.default_figsize
                self.fig.set_size_inches(w * 1.35, h * 1.35, forward=True)
            self.fig.canvas.draw_idle()
        elif key == 'q':
            plt.close(self.fig)
        elif key == 'z':
            # 切换是否固定 Z 轴
            self.fix_z_axis = not self.fix_z_axis
            self._render_high_quality()
            print(f"Z轴固定: {'是' if self.fix_z_axis else '否'}")
        elif key == 'w':
            # 切换网格线
            self.show_wireframe = not self.show_wireframe
            self._render_high_quality()
            print(f"网格线: {'显示' if self.show_wireframe else '隐藏'}")
        elif key == 'p':
            # 切换极速模式（降低分辨率与DPI以提升流畅度）
            self.fast_mode = not self.fast_mode
            try:
                self.fig.set_dpi(120 if self.fast_mode else 170)
            except Exception:
                pass
            self._render_high_quality()
            print(f"极速模式: {'开启(更流畅)' if self.fast_mode else '关闭(更精细)'}")
        elif key in ('1', '2', '3'):
            # 性能预设：1=超流畅 2=均衡 3=高清
            preset = key
            if preset == '1':
                self.grid_size_preview = 56
                self.rcount_preview = 40
                self.preview_coalesce_ms = 90
                self.preview_delay_ms = 220
                self.fast_mode = True
                try:
                    self.fig.set_dpi(110)
                except Exception:
                    pass
            elif preset == '2':
                self.grid_size_preview = 72
                self.rcount_preview = 48
                self.preview_coalesce_ms = 80
                self.preview_delay_ms = 160
                self.fast_mode = True
                try:
                    self.fig.set_dpi(120)
                except Exception:
                    pass
            else:
                self.grid_size_preview = 100
                self.rcount_preview = 70
                self.preview_coalesce_ms = 60
                self.preview_delay_ms = 140
                self.fast_mode = False
                try:
                    self.fig.set_dpi(170)
                except Exception:
                    pass
            # 更新计时器间隔
            try:
                self._preview_timer.interval = self.preview_coalesce_ms
            except Exception:
                pass
            try:
                self._finalize_timer.interval = self.preview_delay_ms
            except Exception:
                pass
            self._render_high_quality()
            print(f"性能预设切换为 {preset}（'1'超流畅 / '2'均衡 / '3'高清）")

    def show(self):
        plt.subplots_adjust(left=0.05, right=0.96, bottom=0.12, top=0.90)
        plt.show()


def main():
    print("=" * 60)
    print("二维正态分布演示程序")
    print("=" * 60)

    parser = argparse.ArgumentParser(description='二维正态分布参数演示')
    parser.add_argument('--save', action='store_true', help='保存当前图像并退出')
    parser.add_argument('--mux', type=float, default=None, help='设置 μx')
    parser.add_argument('--muy', type=float, default=None, help='设置 μy')
    parser.add_argument('--sigmax', type=float, default=None, help='设置 σx (0.2-3.0)')
    parser.add_argument('--sigmay', type=float, default=None, help='设置 σy (0.2-3.0)')
    parser.add_argument('--rho', type=float, default=None, help='设置相关系数 ρ (-0.95~0.95)')
    parser.add_argument('--grid', type=int, default=None, help='可选：设置网格尺寸，默认160')
    args = parser.parse_args()

    try:
        app = BivariateNormalDistributionDemo()

        # 覆盖参数
        if args.mux is not None:
            app.slider_mux.set_val(float(np.clip(args.mux, -5.0, 5.0)))
        if args.muy is not None:
            app.slider_muy.set_val(float(np.clip(args.muy, -5.0, 5.0)))
        if args.sigmax is not None:
            app.slider_sigx.set_val(float(np.clip(args.sigmax, app.min_sigma, 3.0)))
        if args.sigmay is not None:
            app.slider_sigy.set_val(float(np.clip(args.sigmay, app.min_sigma, 3.0)))
        if args.rho is not None:
            app.slider_rho.set_val(float(np.clip(args.rho, -0.95, 0.95)))
        if args.grid is not None and args.grid >= 40:
            app.grid_size_full = int(max(args.grid, app.grid_size_preview))
            app.X_full, app.Y_full = app._make_grid(app.grid_limit, app.grid_size_full)
            app._render_high_quality()

        backend = plt.get_backend().lower()
        if args.save or (backend == 'agg'):
            outfile = 'bivariate_normal_distribution.png'
            app.fig.savefig(outfile, dpi=300, facecolor='#F5F5DC', bbox_inches='tight')
            if backend == 'agg':
                print(f"\n当前环境未启用图形界面（backend={backend}），已保存静态图片: {outfile}")
                print("如需交互式窗口，请在本机终端运行: python bivariate_normal_distribution_demo.py\n")
            else:
                print(f"\n已保存图片: {outfile}")
            return

        print("\n✓ 交互式窗口已打开！")
        print("提示: 拖动滑块或按 r 重置，s 保存，f 全屏，q 退出\n")
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


