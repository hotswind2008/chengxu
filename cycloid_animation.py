"""
旋轮线动画
Cycloid Animation - 圆在直线上滚动时，圆上一点描绘的轨迹
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class RollingCircle:
    def __init__(self, radius=1.0):
        """
        初始化滚动圆
        
        参数:
        radius: 圆的半径
        """
        self.radius = radius
        
    def get_circle_position(self, theta):
        """
        计算圆滚动到角度theta时的中心位置
        
        参数:
        theta: 旋转角度（弧度）
        
        返回:
        center_x, center_y: 圆的中心坐标
        """
        # 圆在直线上滚动，中心始终在半径高度
        center_x = self.radius * theta
        center_y = self.radius
        return center_x, center_y
    
    def get_trace_point(self, theta):
        """
        计算圆上一点（开始时在底部）在角度theta时的位置
        这是旋轮线轨迹上的点
        
        参数:
        theta: 旋转角度（弧度）
        
        返回:
        x, y: 轨迹点的坐标
        """
        # 旋轮线参数方程
        x = self.radius * (theta - np.sin(theta))
        y = self.radius * (1 - np.cos(theta))
        return x, y

def create_cycloid_animation(
    duration=10.0,
    fps=30,
    radius=1.0,
    cycles=3,
    output_file='cycloid_animation.mp4',
    show_trace=True,
    trace_point_angle=0
):
    """
    创建旋轮线动画
    
    参数:
    duration: 动画时长（秒）
    fps: 帧率
    radius: 圆的半径
    cycles: 旋转的周期数（一个周期是2π）
    output_file: 输出文件名
    show_trace: 是否显示轨迹
    trace_point_angle: 轨迹点的角度（0表示底部，π/2表示右侧，π表示顶部）
    """
    # 创建滚动圆对象
    circle = RollingCircle(radius=radius)
    
    # 计算总帧数
    total_frames = int(duration * fps)
    
    # 计算总旋转角度
    total_theta = cycles * 2 * np.pi
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 设置坐标轴范围
    x_range = total_theta * radius + radius * 4
    y_range = radius * 4
    ax.set_xlim(-radius * 2, x_range)
    ax.set_ylim(-radius * 0.5, y_range)
    ax.set_aspect('equal')
    
    # 绘制直线（地面）
    ax.axhline(y=0, color='black', linewidth=2.5, label='地面', zorder=1)
    
    # 绘制网格
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    
    # 设置标题和标签
    ax.set_xlabel('位置 (x)', fontsize=12)
    ax.set_ylabel('高度 (y)', fontsize=12)
    ax.set_title('旋轮线动画 (Cycloid Animation)', fontsize=16, fontweight='bold')
    
    # 创建圆对象
    circle_patch = patches.Circle(
        (0, radius),
        radius,
        edgecolor='blue',
        facecolor='lightblue',
        linewidth=2.5,
        alpha=0.6,
        zorder=3
    )
    ax.add_patch(circle_patch)
    
    # 创建圆心标记
    center_dot, = ax.plot([], [], 'bo', markersize=8, label='圆心', zorder=4)
    
    # 创建圆心到轨迹点的连线
    center_line, = ax.plot([], [], 'g--', linewidth=1.5, alpha=0.5, label='半径', zorder=2)
    
    # 创建轨迹点标记
    trace_dot, = ax.plot([], [], 'ro', markersize=10, label='轨迹点', zorder=5)
    
    # 创建旋轮线轨迹
    trajectory_x = []
    trajectory_y = []
    trajectory_line, = ax.plot([], [], 'r-', linewidth=2.5, alpha=0.8, label='旋轮线轨迹', zorder=2)
    
    # 添加图例
    ax.legend(loc='upper left', fontsize=10)
    
    # 存储所有theta值用于绘制完整轨迹线（预计算）
    all_theta = np.linspace(0, total_theta, total_frames)
    full_trajectory_x = []
    full_trajectory_y = []
    for theta in all_theta:
        x, y = circle.get_trace_point(theta)
        full_trajectory_x.append(x)
        full_trajectory_y.append(y)
    
    def init():
        """初始化动画"""
        circle_patch.center = (0, radius)
        center_dot.set_data([], [])
        center_line.set_data([], [])
        trace_dot.set_data([], [])
        trajectory_line.set_data([], [])
        return circle_patch, center_dot, center_line, trace_dot, trajectory_line
    
    def animate(frame):
        """更新每一帧"""
        # 计算当前角度
        t = frame / total_frames
        theta = t * total_theta
        
        # 获取圆心位置
        center_x, center_y = circle.get_circle_position(theta)
        
        # 更新圆的位置
        circle_patch.center = (center_x, center_y)
        
        # 获取轨迹点位置
        trace_x, trace_y = circle.get_trace_point(theta)
        
        # 计算轨迹点相对于圆心的角度（用于绘制连线）
        # 在旋轮线中，轨迹点初始在底部（角度为-π/2），然后随圆旋转
        relative_angle = theta - np.pi / 2
        
        # 绘制从圆心到轨迹点的连线
        center_line.set_data([center_x, trace_x], [center_y, trace_y])
        
        # 更新圆心标记
        center_dot.set_data([center_x], [center_y])
        
        # 更新轨迹点标记
        trace_dot.set_data([trace_x], [trace_y])
        
        # 更新轨迹（累积历史轨迹）
        if show_trace:
            trajectory_x.append(trace_x)
            trajectory_y.append(trace_y)
            trajectory_line.set_data(trajectory_x, trajectory_y)
        else:
            # 显示完整轨迹线（淡色）
            trajectory_line.set_data(full_trajectory_x[:frame+1], full_trajectory_y[:frame+1])
            trajectory_line.set_alpha(0.3)
        
        # 动态调整视图（让圆始终在视野中心附近）
        if center_x > radius * 3:
            view_center_x = center_x
            ax.set_xlim(view_center_x - radius * 6, view_center_x + radius * 4)
        
        return circle_patch, center_dot, center_line, trace_dot, trajectory_line
    
    # 创建动画
    print(f"正在创建旋轮线动画，共 {total_frames} 帧...")
    print(f"圆半径: {radius}, 周期数: {cycles}")
    
    anim = FuncAnimation(
        fig,
        animate,
        init_func=init,
        frames=total_frames,
        interval=1000/fps,
        blit=True
    )
    
    # 保存动画
    print(f"正在保存动画到 {output_file}...")
    if output_file.endswith('.gif'):
        writer = PillowWriter(fps=fps)
        anim.save(output_file, writer=writer)
    elif output_file.endswith('.mp4'):
        # 尝试使用ffmpeg，如果失败则使用pillow
        try:
            writer = 'ffmpeg'
            anim.save(output_file, writer=writer, fps=fps, dpi=100, bitrate=1800)
        except Exception as e:
            print(f"使用ffmpeg失败，尝试使用pillow: {e}")
            if output_file.endswith('.mp4'):
                output_file = output_file.replace('.mp4', '.gif')
            writer = PillowWriter(fps=fps)
            anim.save(output_file, writer=writer)
    
    print(f"动画已保存: {output_file}")
    plt.close()
    
    return anim

def main():
    """主函数"""
    print("=" * 60)
    print("旋轮线动画生成器 (Cycloid Animation Generator)")
    print("=" * 60)
    
    # 配置参数
    config = {
        'duration': 30.0,              # 动画时长（秒）
        'fps': 30,                     # 帧率
        'radius': 1.0,                 # 圆的半径
        'cycles': 3,                   # 旋转的周期数
        'output_file': 'cycloid_animation.mp4',  # 输出文件
        'show_trace': True,            # 显示累积轨迹
        'trace_point_angle': 0         # 轨迹点角度（0=底部）
    }
    
    print(f"\n配置参数:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # 创建动画
    try:
        anim = create_cycloid_animation(**config)
        print("\n✓ 动画生成成功！")
        print(f"✓ 输出文件: {config['output_file']}")
        
    except Exception as e:
        print(f"\n✗ 生成动画时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

