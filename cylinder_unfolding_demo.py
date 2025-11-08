"""
圆柱面展开演示 - 交互式版本
Interactive Cylinder Unfolding Demonstration - 展示圆柱面上的曲线展开到平面后的形状
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button, CheckButtons
from matplotlib.animation import FuncAnimation
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class InteractiveCylinderUnfolding:
    """交互式圆柱面展开演示类"""
    
    def __init__(self, radius=1.0, height=4.0):
        self.radius = radius
        self.height = height
        
        # 创建图形：左侧3D视图，右侧展开平面视图
        self.fig = plt.figure(figsize=(18, 9))
        
        # 3D圆柱面视图
        self.ax_3d = self.fig.add_subplot(121, projection='3d')
        self.ax_3d.set_xlabel('X', fontsize=10)
        self.ax_3d.set_ylabel('Y', fontsize=10)
        self.ax_3d.set_zlabel('Z', fontsize=10)
        self.ax_3d.set_title('圆柱面（3D视图）', fontsize=14, fontweight='bold')
        
        # 展开平面视图
        self.ax_2d = self.fig.add_subplot(122)
        self.ax_2d.set_xlabel('展开长度（弧长）', fontsize=10)
        self.ax_2d.set_ylabel('高度', fontsize=10)
        self.ax_2d.set_title('展开后的平面', fontsize=14, fontweight='bold')
        self.ax_2d.grid(True, alpha=0.3)
        
        # 展开进度（0-1）
        self.unfold_progress = 0.0
        
        # 动画参数
        self.animation_running = False  # 动画是否正在运行
        self.animation_direction = 1  # 动画方向：1=展开，-1=收起
        self.animation_speed = 0.02  # 动画速度（每帧增加的进度）
        self.updating_from_animation = False  # 标志：是否正在从动画更新
        self.anim = None  # FuncAnimation对象
        self.frame_count = 0  # 帧计数器
        
        # 曲线参数
        self.circle_z = self.height * 0.5  # 圆的高度
        self.ellipse_z_center = self.height * 0.5  # 椭圆中心高度
        self.ellipse_amplitude = self.height * 0.3  # 椭圆振幅（正弦曲线的振幅）
        self.helix_turns = 2.0  # 螺旋线圈数
        
        # 存储绘制的对象
        self.cylinder_surface = None
        self.curves_3d = []
        self.curves_2d = []
        
        # 曲线可见性状态
        self.show_circle = True
        self.show_ellipse = True
        self.show_helix = True
        
        # 创建滑块和复选框
        self.create_sliders()
        self.create_checkboxes()
        
        # 初始绘制
        self.update_visualization()
        
        # 显示帮助信息
        self.show_help()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = (
            "\n" + "="*60 + "\n"
            "圆柱面展开交互式演示 - 操作说明\n"
            "="*60 + "\n"
            "滑块控制:\n"
            "  • 展开进度: 控制圆柱面展开的程度 (0=未展开, 1=完全展开)\n"
            "  • 圆的高度: 调整圆在圆柱面上的高度位置\n"
            "  • 椭圆中心: 调整椭圆中心的高度位置\n"
            "  • 椭圆振幅: 调整椭圆展开后正弦曲线的振幅\n"
            "  • 螺旋圈数: 调整螺旋线的圈数\n\n"
            "复选框控制:\n"
            "  • 显示/隐藏圆、椭圆、螺旋线\n\n"
            "自动演示:\n"
            "  • 播放/暂停: 开始或暂停自动展开动画\n"
            "  • 自动演示速度: 控制动画播放速度\n\n"
            "说明:\n"
            "  • 圆展开后是一条水平直线\n"
            "  • 椭圆展开后是正弦曲线（不是直线！）\n"
            "  • 螺旋线展开后是一条斜直线\n"
            "="*60 + "\n"
        )
        print(help_text)
    
    def create_sliders(self):
        """创建交互式滑块"""
        # 调整图形布局，为滑块留出空间
        plt.subplots_adjust(left=0.05, bottom=0.25, right=0.95, top=0.95)
        
        # 展开进度滑块
        ax_unfold = plt.axes([0.15, 0.15, 0.7, 0.02])
        self.slider_unfold = Slider(ax_unfold, '展开进度', 0.0, 1.0, 
                                     valinit=0.0, valstep=0.01)
        self.slider_unfold.on_changed(self.update_unfold)
        
        # 圆的高度滑块
        ax_circle_z = plt.axes([0.15, 0.12, 0.35, 0.02])
        self.slider_circle_z = Slider(ax_circle_z, '圆的高度', 0.1, self.height*0.9, 
                                       valinit=self.circle_z, valstep=0.1)
        self.slider_circle_z.on_changed(self.update_circle_z)
        
        # 椭圆中心高度滑块
        ax_ellipse_center = plt.axes([0.55, 0.12, 0.35, 0.02])
        self.slider_ellipse_center = Slider(ax_ellipse_center, '椭圆中心', 0.1, self.height*0.9, 
                                            valinit=self.ellipse_z_center, valstep=0.1)
        self.slider_ellipse_center.on_changed(self.update_ellipse_center)
        
        # 椭圆振幅滑块
        ax_ellipse_amp = plt.axes([0.15, 0.09, 0.35, 0.02])
        self.slider_ellipse_amp = Slider(ax_ellipse_amp, '椭圆振幅', 0.1, self.height*0.4, 
                                         valinit=self.ellipse_amplitude, valstep=0.1)
        self.slider_ellipse_amp.on_changed(self.update_ellipse_amp)
        
        # 螺旋圈数滑块
        ax_helix_turns = plt.axes([0.55, 0.09, 0.35, 0.02])
        self.slider_helix_turns = Slider(ax_helix_turns, '螺旋圈数', 0.5, 4.0, 
                                          valinit=self.helix_turns, valstep=0.1)
        self.slider_helix_turns.on_changed(self.update_helix_turns)
        
        # 重置按钮
        ax_reset = plt.axes([0.15, 0.05, 0.1, 0.03])
        self.button_reset = Button(ax_reset, '重置')
        self.button_reset.on_clicked(self.reset)
        
        # 保存按钮
        ax_save = plt.axes([0.27, 0.05, 0.1, 0.03])
        self.button_save = Button(ax_save, '保存')
        self.button_save.on_clicked(self.save_image)
        
        # 播放/暂停按钮
        ax_play = plt.axes([0.70, 0.09, 0.1, 0.03])
        self.button_play = Button(ax_play, '播放')
        self.button_play.on_clicked(self.toggle_animation)
        
        # 动画速度滑块
        ax_speed = plt.axes([0.70, 0.12, 0.25, 0.02])
        self.slider_speed = Slider(ax_speed, '自动演示速度', 0.005, 0.05, 
                                     valinit=self.animation_speed, valstep=0.005)
        self.slider_speed.on_changed(self.update_speed)
    
    def create_checkboxes(self):
        """创建复选框控制曲线显示/隐藏"""
        # 复选框位置
        ax_check = plt.axes([0.40, 0.05, 0.25, 0.05])
        
        # 初始状态
        self.checkbox_labels = ['显示圆', '显示椭圆', '显示螺旋线']
        actives = [True, True, True]
        
        self.checkboxes = CheckButtons(ax_check, self.checkbox_labels, actives)
        self.checkboxes.on_clicked(self.toggle_curve)
    
    def toggle_curve(self, label):
        """切换曲线显示状态"""
        if label == self.checkbox_labels[0]:  # '显示圆'
            self.show_circle = not self.show_circle
        elif label == self.checkbox_labels[1]:  # '显示椭圆'
            self.show_ellipse = not self.show_ellipse
        elif label == self.checkbox_labels[2]:  # '显示螺旋线'
            self.show_helix = not self.show_helix
        
        self.update_visualization()
    
    def update_speed(self, val):
        """更新动画速度"""
        self.animation_speed = val
    
    def toggle_animation(self, event):
        """切换动画播放/暂停状态"""
        if self.animation_running:
            # 停止动画
            self.stop_animation()
        else:
            # 开始动画
            self.start_animation()
    
    def animate(self, frame):
        """FuncAnimation 回调函数"""
        if not self.animation_running:
            return []
        
        try:
            # 更新展开进度
            self.unfold_progress += self.animation_direction * self.animation_speed
            
            # 检查边界，改变方向
            if self.unfold_progress >= 1.0:
                self.unfold_progress = 1.0
                self.animation_direction = -1  # 开始收起
            elif self.unfold_progress <= 0.0:
                self.unfold_progress = 0.0
                self.animation_direction = 1  # 开始展开
            
            # 更新界面
            self.updating_from_animation = True
            self.slider_unfold.set_val(self.unfold_progress)
            self.updating_from_animation = False
            self.update_visualization()
            
            # 每100帧打印一次调试信息
            if frame % 100 == 0:
                print(f"动画帧 {frame}: 展开进度={self.unfold_progress:.3f}")
        except Exception as e:
            print(f"动画更新错误: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    def stop_animation(self):
        """停止动画"""
        self.animation_running = False
        self.button_play.label.set_text('播放')
        # 停止FuncAnimation
        if self.anim:
            self.anim.event_source.stop()
            self.anim = None
    
    def start_animation(self):
        """开始自动演示动画"""
        # 先停止之前的动画
        if self.animation_running and self.anim:
            self.stop_animation()
        
        self.animation_running = True
        self.button_play.label.set_text('暂停')
        
        # 停止旧的动画
        if self.anim:
            try:
                self.anim.event_source.stop()
            except:
                pass
            self.anim = None
        
        # 创建新的FuncAnimation
        print("正在创建动画...")
        try:
            self.anim = FuncAnimation(
                self.fig,
                self.animate,
                interval=50,  # 50ms间隔
                blit=False,
                repeat=True,
                cache_frame_data=False
            )
            
            # 确保动画事件源已启动
            if hasattr(self.anim, 'event_source'):
                print(f"动画事件源类型: {type(self.anim.event_source)}")
                if hasattr(self.anim.event_source, 'start'):
                    self.anim.event_source.start()
                    print("已调用 event_source.start()")
                elif hasattr(self.anim.event_source, 'resume'):
                    self.anim.event_source.resume()
                    print("已调用 event_source.resume()")
                else:
                    print(f"event_source 可用方法: {dir(self.anim.event_source)}")
                
                # 检查是否运行
                if hasattr(self.anim.event_source, 'is_running'):
                    print(f"动画是否运行: {self.anim.event_source.is_running()}")
            else:
                print("警告: 动画对象没有 event_source 属性")
            
            # 强制刷新画布
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            
            print(f"动画已启动，展开进度: {self.unfold_progress:.3f}")
        except Exception as e:
            print(f"启动动画时出错: {e}")
            import traceback
            traceback.print_exc()
            self.animation_running = False
            self.button_play.label.set_text('播放')
    
    
    def update_unfold(self, val):
        """更新展开进度"""
        # 如果是从动画更新的，跳过
        if self.updating_from_animation:
            return
        
        # 如果动画正在运行，手动调整滑块会停止动画
        if self.animation_running:
            self.stop_animation()
        
        self.unfold_progress = val
        self.update_visualization()
    
    def update_circle_z(self, val):
        """更新圆的高度"""
        self.circle_z = val
        self.update_visualization()
    
    def update_ellipse_center(self, val):
        """更新椭圆中心高度"""
        self.ellipse_z_center = val
        self.update_visualization()
    
    def update_ellipse_amp(self, val):
        """更新椭圆振幅"""
        self.ellipse_amplitude = val
        self.update_visualization()
    
    def update_helix_turns(self, val):
        """更新螺旋圈数"""
        self.helix_turns = val
        self.update_visualization()
    
    def reset(self, event):
        """重置所有参数"""
        self.unfold_progress = 0.0
        self.circle_z = self.height * 0.5
        self.ellipse_z_center = self.height * 0.5
        self.ellipse_amplitude = self.height * 0.3
        self.helix_turns = 2.0
        
        # 重置可见性
        self.show_circle = True
        self.show_ellipse = True
        self.show_helix = True
        
        self.slider_unfold.set_val(0.0)
        self.slider_circle_z.set_val(self.circle_z)
        self.slider_ellipse_center.set_val(self.ellipse_z_center)
        self.slider_ellipse_amp.set_val(self.ellipse_amplitude)
        self.slider_helix_turns.set_val(self.helix_turns)
        
        # 重置复选框状态
        if hasattr(self, 'checkboxes'):
            for i, label in enumerate(self.checkbox_labels):
                if self.checkboxes.get_status()[i] != True:
                    self.checkboxes.set_active(i)
        
        self.update_visualization()
    
    def save_image(self, event):
        """保存当前图像"""
        filename = 'cylinder_unfolding_interactive.png'
        self.fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"图片已保存: {filename}")
    
    def draw_cylinder_3d(self):
        """绘制3D圆柱面"""
        self.ax_3d.clear()
        self.ax_3d.set_xlabel('X', fontsize=10)
        self.ax_3d.set_ylabel('Y', fontsize=10)
        self.ax_3d.set_zlabel('Z', fontsize=10)
        self.ax_3d.set_title('圆柱面（3D视图）', fontsize=14, fontweight='bold')
        
        # 绘制部分展开的圆柱面
        theta_max = 2 * np.pi * (1 - self.unfold_progress)
        
        if theta_max > 0.1:
            theta = np.linspace(0, theta_max, 50)
            z = np.linspace(0, self.height, 30)
            Theta, Z = np.meshgrid(theta, z)
            X = self.radius * np.cos(Theta)
            Y = self.radius * np.sin(Theta)
            self.ax_3d.plot_surface(X, Y, Z, alpha=0.3, color='lightblue', 
                                   edgecolor='blue', linewidth=0.5)
        
        lim = self.radius * 1.5
        self.ax_3d.set_xlim(-lim, lim)
        self.ax_3d.set_ylim(-lim, lim)
        self.ax_3d.set_zlim(0, self.height)
    
    def draw_circle_on_cylinder(self):
        """在圆柱面上绘制圆，并展开到平面"""
        # 3D视图中的圆
        theta = np.linspace(0, 2 * np.pi * (1 - self.unfold_progress), 100)
        x_circle = self.radius * np.cos(theta)
        y_circle = self.radius * np.sin(theta)
        z_circle = np.full_like(theta, self.circle_z)
        
        line1, = self.ax_3d.plot(x_circle, y_circle, z_circle, 'r-', 
                                linewidth=2.5, label='圆')
        self.curves_3d.append(line1)
        
        # 展开后的曲线（一条水平直线）
        if self.unfold_progress > 0:
            theta_unfolded = np.linspace(0, 2 * np.pi * self.unfold_progress, 100)
            x_unfolded = self.radius * theta_unfolded
            y_unfolded = np.full_like(x_unfolded, self.circle_z)
            
            line2, = self.ax_2d.plot(x_unfolded, y_unfolded, 'r-', 
                                    linewidth=2.5, label='圆展开')
            self.curves_2d.append(line2)
    
    def draw_ellipse_on_cylinder(self):
        """在圆柱面上绘制椭圆，并展开到平面（正弦曲线）"""
        # 3D视图中的椭圆（在圆柱面上是一个倾斜的椭圆）
        # 椭圆的高度随角度变化：z = z_center + amplitude * sin(theta)
        theta = np.linspace(0, 2 * np.pi * (1 - self.unfold_progress), 100)
        z_ellipse = self.ellipse_z_center + self.ellipse_amplitude * np.sin(theta)
        z_ellipse = np.clip(z_ellipse, 0, self.height)
        
        x_ellipse = self.radius * np.cos(theta)
        y_ellipse = self.radius * np.sin(theta)
        
        line1, = self.ax_3d.plot(x_ellipse, y_ellipse, z_ellipse, 'g-', 
                                linewidth=2.5, label='椭圆')
        self.curves_3d.append(line1)
        
        # 展开后的曲线（正弦曲线！）
        if self.unfold_progress > 0:
            theta_unfolded = np.linspace(0, 2 * np.pi * self.unfold_progress, 100)
            x_unfolded = self.radius * theta_unfolded
            # 展开后：y = z_center + amplitude * sin(theta)
            # 因为 x = radius * theta，所以 theta = x / radius
            y_unfolded = self.ellipse_z_center + self.ellipse_amplitude * np.sin(theta_unfolded)
            y_unfolded = np.clip(y_unfolded, 0, self.height)
            
            line2, = self.ax_2d.plot(x_unfolded, y_unfolded, 'g-', 
                                    linewidth=2.5, label='椭圆展开（正弦曲线）')
            self.curves_2d.append(line2)
    
    def draw_helix_on_cylinder(self):
        """在圆柱面上绘制螺旋线，并展开到平面"""
        # 3D视图中的螺旋线
        theta_max = 2 * np.pi * self.helix_turns * (1 - self.unfold_progress)
        theta = np.linspace(0, theta_max, 200)
        
        x_helix = self.radius * np.cos(theta)
        y_helix = self.radius * np.sin(theta)
        z_helix = (self.height / (2 * np.pi * self.helix_turns)) * theta
        z_helix = np.clip(z_helix, 0, self.height)
        
        line1, = self.ax_3d.plot(x_helix, y_helix, z_helix, 'orange', 
                                linewidth=2.5, label='螺旋线')
        self.curves_3d.append(line1)
        
        # 展开后的曲线（一条斜直线）
        if self.unfold_progress > 0:
            theta_unfolded = np.linspace(0, 2 * np.pi * self.helix_turns * self.unfold_progress, 200)
            x_unfolded = self.radius * theta_unfolded
            y_unfolded = (self.height / (2 * np.pi * self.helix_turns)) * theta_unfolded
            y_unfolded = np.clip(y_unfolded, 0, self.height)
            
            line2, = self.ax_2d.plot(x_unfolded, y_unfolded, 'orange', 
                                    linewidth=2.5, label='螺旋线展开')
            self.curves_2d.append(line2)
    
    def update_visualization(self):
        """更新可视化"""
        # 清除之前的曲线
        for curve in self.curves_3d:
            curve.remove()
        for curve in self.curves_2d:
            curve.remove()
        self.curves_3d = []
        self.curves_2d = []
        
        # 清除2D视图
        self.ax_2d.clear()
        self.ax_2d.set_xlabel('展开长度（弧长）', fontsize=10)
        self.ax_2d.set_ylabel('高度', fontsize=10)
        self.ax_2d.set_title('展开后的平面', fontsize=14, fontweight='bold')
        self.ax_2d.grid(True, alpha=0.3)
        
        # 绘制圆柱面
        self.draw_cylinder_3d()
        
        # 绘制各曲线（根据可见性状态）
        if self.show_circle:
            self.draw_circle_on_cylinder()
        if self.show_ellipse:
            self.draw_ellipse_on_cylinder()
        if self.show_helix:
            self.draw_helix_on_cylinder()
        
        # 设置2D视图的范围
        max_x = 2 * np.pi * self.radius * max(1.1, self.helix_turns * 1.1)
        self.ax_2d.set_xlim(-max_x * 0.05, max_x)
        self.ax_2d.set_ylim(-self.height * 0.1, self.height * 1.1)
        
        # 添加图例
        if self.unfold_progress > 0.1:
            self.ax_2d.legend(loc='upper right', fontsize=9)
        
        self.fig.canvas.draw()
    
    def show(self):
        """显示交互式窗口"""
        # 确保动画对象被保存，避免被垃圾回收
        self.fig.canvas.manager.set_window_title('圆柱面展开演示')
        # 将动画对象保存为实例属性，防止被垃圾回收
        if hasattr(self, 'anim') and self.anim:
            self.fig._animation = self.anim  # 保存到figure对象中
        
        # 连接窗口关闭事件
        def on_close(event):
            if self.anim:
                self.anim.event_source.stop()
        
        self.fig.canvas.mpl_connect('close_event', on_close)
        
        plt.show()

def main():
    """主函数"""
    print("=" * 60)
    print("圆柱面展开演示程序 - 交互式版本")
    print("=" * 60)
    
    try:
        demo = InteractiveCylinderUnfolding(radius=1.0, height=4.0)
        print("\n✓ 交互式窗口已打开！")
        print("提示: 使用滑块调整参数，观察曲线的变化")
        print("提示: 点击'播放'按钮开始自动演示\n")
        demo.show()
        
    except Exception as e:
        print(f"\n✗ 运行出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
