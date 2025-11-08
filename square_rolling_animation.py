"""
正方形在数轴上滚动动画
Square Rolling on Number Line Animation
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patches as patches

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class RollingSquare:
    def __init__(self, side_length=1.0):
        """
        初始化滚动正方形
        
        参数:
        side_length: 正方形边长
        """
        self.side = side_length
        # 正方形的初始中心位置（中心在数轴上方半个边长的位置）
        self.center_x = 0
        self.center_y = side_length / 2
        # 初始角度
        self.angle = 0
        
    def get_vertices(self, center_x, center_y, angle):
        """
        获取正方形的四个顶点坐标
        
        参数:
        center_x, center_y: 中心坐标
        angle: 旋转角度（弧度）
        
        返回:
        vertices: 4x2数组，包含四个顶点坐标
        """
        # 相对于中心的顶点位置（未旋转时）
        half_side = self.side / 2
        vertices = np.array([
            [-half_side, -half_side],
            [half_side, -half_side],
            [half_side, half_side],
            [-half_side, half_side]
        ])
        
        # 旋转矩阵
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])
        
        # 旋转顶点
        rotated_vertices = vertices @ rotation_matrix.T
        
        # 平移到中心位置
        rotated_vertices[:, 0] += center_x
        rotated_vertices[:, 1] += center_y
        
        return rotated_vertices
    
    def roll_to_position(self, target_x):
        """
        计算滚动到目标x位置时的状态
        符合物理规律：正方形绕着接触的底边顶点旋转，每90度换一个支点
        
        参数:
        target_x: 目标x坐标
        
        返回:
        center_x, center_y, angle: 正方形的中心坐标和旋转角度
        """
        # 当前滚动的距离
        distance = target_x
        
        # 确定当前在第几个边的滚动阶段（从0开始）
        edge_num = int(distance / self.side)
        
        # 当前边内的滚动进度（0到1之间）
        progress = (distance / self.side) - edge_num
        
        # 当前接触点的x坐标（这个顶点固定在数轴上）
        contact_x = edge_num * self.side
        
        # 总旋转角度（顺时针为负）
        angle = -(distance / self.side) * (np.pi / 2)
        
        # 中心到顶点的距离（对角线的一半）
        radius = self.side * np.sqrt(2) / 2
        
        # 在一个边的滚动过程中，正方形绕接触点旋转
        # progress=0时：右下角顶点接触地面，中心在接触点的西北方向（135度 = 3π/4）
        # progress=1时：已经旋转了90度，下一个顶点即将接触地面
        
        # 中心相对于接触点的角度（逆时针，从正东方向开始）
        # 初始角度135度（西北方向），随着滚动逆时针旋转
        angle_from_contact = (3 * np.pi / 4) + progress * (np.pi / 2)
        
        # 计算中心坐标
        center_x = contact_x + radius * np.cos(angle_from_contact)
        center_y = radius * np.sin(angle_from_contact)
        
        return center_x, center_y, angle

def create_rolling_square_animation(
    duration=10.0,
    fps=30,
    side_length=1.0,
    speed=1.0,
    output_file='square_rolling.gif'
):
    """
    创建正方形滚动动画
    
    参数:
    duration: 动画时长（秒）
    fps: 帧率
    side_length: 正方形边长
    speed: 滚动速度（单位距离/秒）
    output_file: 输出文件名
    """
    # 创建滚动正方形对象
    square = RollingSquare(side_length=side_length)
    
    # 计算总帧数
    total_frames = int(duration * fps)
    
    # 计算总滚动距离
    total_distance = speed * duration
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 设置数轴范围
    x_margin = 2
    y_margin = 2
    ax.set_xlim(-x_margin, total_distance + x_margin)
    ax.set_ylim(0, side_length * 2 + y_margin)  # y从0开始，不显示数轴下方
    ax.set_aspect('equal')
    
    # 绘制数轴
    ax.axhline(y=0, color='black', linewidth=2, label='数轴')
    
    # 绘制刻度
    tick_spacing = 1.0
    num_ticks = int(total_distance / tick_spacing) + 3
    for i in range(-1, num_ticks):
        x = i * tick_spacing
        ax.plot([x, x], [0, 0.1], 'k-', linewidth=1.5)  # 刻度向上
        ax.text(x, 0.15, f'{x:.1f}', ha='center', va='bottom', fontsize=10)  # 文字在上方
    
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('位置', fontsize=12)
    ax.set_ylabel('高度', fontsize=12)
    ax.set_title('正方形在数轴上滚动', fontsize=14, fontweight='bold')
    
    # 创建正方形补丁对象
    square_patch = patches.Polygon(
        [[0, 0], [1, 0], [1, 1], [0, 1]],
        closed=True,
        edgecolor='blue',
        facecolor='lightblue',
        linewidth=2,
        alpha=0.7
    )
    ax.add_patch(square_patch)
    
    # 创建中心点标记
    center_dot, = ax.plot([], [], 'ro', markersize=8, label='中心点')
    
    # 创建接触点标记
    contact_dot, = ax.plot([], [], 'gs', markersize=10, label='接触点')
    
    # 创建轨迹线
    trajectory_x = []
    trajectory_y = []
    trajectory_line, = ax.plot([], [], 'r--', linewidth=1, alpha=0.5, label='中心轨迹')
    
    # 添加图例
    ax.legend(loc='upper left')
    
    # 添加信息文本
    info_text = ax.text(
        0.02, 0.98, '',
        transform=ax.transAxes,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10
    )
    
    def init():
        """初始化动画"""
        square_patch.set_xy([[0, 0], [1, 0], [1, 1], [0, 1]])
        center_dot.set_data([], [])
        contact_dot.set_data([], [])
        trajectory_line.set_data([], [])
        return square_patch, center_dot, contact_dot, trajectory_line, info_text
    
    def animate(frame):
        """更新每一帧"""
        # 计算当前位置
        t = frame / total_frames
        current_distance = t * total_distance
        
        # 获取正方形状态
        center_x, center_y, angle = square.roll_to_position(current_distance)
        
        # 计算接触点位置
        edge_num = int(current_distance / side_length)
        contact_x = edge_num * side_length
        contact_y = 0
        
        # 获取顶点坐标
        vertices = square.get_vertices(center_x, center_y, angle)
        
        # 更新正方形
        square_patch.set_xy(vertices)
        
        # 更新中心点
        center_dot.set_data([center_x], [center_y])
        
        # 更新接触点
        contact_dot.set_data([contact_x], [contact_y])
        
        # 更新轨迹
        trajectory_x.append(center_x)
        trajectory_y.append(center_y)
        trajectory_line.set_data(trajectory_x, trajectory_y)
        
        # 更新信息文本
        rotation_degrees = np.degrees(angle) % 360
        info_text.set_text(
            f'时间: {t * duration:.2f}s\n'
            f'位置: {current_distance:.2f}\n'
            f'旋转角度: {rotation_degrees:.1f}°\n'
            f'中心高度: {center_y:.2f}'
        )
        
        # 动态调整视图（让正方形始终在视野中）
        if current_distance > 3:
            ax.set_xlim(current_distance - 3, current_distance + 5)
        
        return square_patch, center_dot, contact_dot, trajectory_line, info_text
    
    # 创建动画
    print(f"正在创建动画，共 {total_frames} 帧...")
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
        writer = 'ffmpeg'
        anim.save(output_file, writer=writer, fps=fps, dpi=100)
    
    print(f"动画已保存: {output_file}")
    plt.close()
    
    return anim

def main():
    """主函数"""
    print("=" * 50)
    print("正方形在数轴上滚动动画生成器")
    print("=" * 50)
    
    # 配置参数
    config = {
        'duration': 8.0,          # 动画时长（秒）
        'fps': 30,                 # 帧率
        'side_length': 1.0,        # 正方形边长
        'speed': 2.0,              # 滚动速度（单位/秒）
        'output_file': 'square_rolling.mp4'  # 输出文件
    }
    
    print(f"\n配置参数:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # 创建动画
    try:
        anim = create_rolling_square_animation(**config)
        print("\n✓ 动画生成成功！")
        
    except Exception as e:
        print(f"\n✗ 生成动画时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

