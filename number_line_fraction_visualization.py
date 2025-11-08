"""
数轴分数可视化 - 简化交互式版本
两个端点互为倒数，拖动一个端点时另一个自动更新
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from fractions import Fraction

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class ReciprocalNumberLine:
    """互为倒数的数轴可视化类"""
    
    def __init__(self, start_num=0, end_num=4, initial_value=0.3, figsize=(14, 6)):
        self.start_num = start_num
        self.end_num = end_num
        self.line_y = 0.5
        self.interval_color = 'red'
        
        # 两个端点：第一个端点和它的倒数
        self.point1_value = initial_value
        self.point2_value = 1.0 / initial_value if initial_value != 0 else None
        
        # 当前正在拖动的点索引（None表示没有拖动）
        self.dragging = None
        self.drag_tolerance = 0.15  # 拖动容差
        
        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.patch.set_facecolor('#F5F5DC')
        self.ax.set_facecolor('#F5F5DC')
        
        # 存储绘制的对象
        self.point1_dot = None
        self.point2_dot = None
        self.point1_label = None
        self.point2_label = None
        self.interval_rect = None
        self.interval_lines = []
        
        # 帮助信息显示标志
        self._help_shown = False
        
        # 绑定事件
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 初始化绘制
        self.draw_number_line()
        self.update_visualization()
        
        # 显示帮助信息（只显示一次）
        self.show_help()
    
    def show_help(self, force=False):
        """显示帮助信息"""
        # 只在首次显示或强制显示时打印帮助信息，避免重复打印
        if force or not self._help_shown:
            help_text = (
                "\n" + "="*60 + "\n"
                "互为倒数的数轴可视化 - 操作说明\n"
                "="*60 + "\n"
                "鼠标操作:\n"
                "  • 左键拖动端点: 移动端点，另一个端点会自动更新为倒数\n"
                "  • 拖动时端点颜色会变为橙色提示\n\n"
                "键盘快捷键:\n"
                "  • 's' 键: 保存当前图片\n"
                "  • 'r' 键: 重置到初始值 (0.3 和 10/3)\n"
                "  • 'h' 键: 显示帮助信息\n"
                "  • 'q' 键: 退出程序\n\n"
                "说明: 两个端点始终互为倒数关系\n"
                "="*60 + "\n"
            )
            print(help_text, end='', flush=True)
            self._help_shown = True
    
    def draw_number_line(self):
        """绘制数轴"""
        margin = 0.5
        self.ax.set_xlim(self.start_num - margin, self.end_num + margin)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_aspect('equal')
        
        # 绘制主数轴线
        self.ax.plot([self.start_num - margin, self.end_num + margin], 
                     [self.line_y, self.line_y], 
                     'k-', linewidth=2, zorder=1)
        
        # 绘制整数标记和刻度
        for i in range(self.start_num, self.end_num + 1):
            # 整数刻度线
            self.ax.plot([i, i], [self.line_y - 0.08, self.line_y + 0.08], 
                        'k-', linewidth=1.5, zorder=2)
            # 整数圆点
            self.ax.plot(i, self.line_y, 'ko', markersize=6, zorder=3)
            # 整数标签
            self.ax.text(i, self.line_y + 0.15, str(i), 
                        ha='center', va='bottom', fontsize=14, fontweight='bold', zorder=4)
        
        # 绘制小数刻度（十分位）
        for i in range(self.start_num, self.end_num):
            for j in range(1, 10):
                x_pos = i + j / 10.0
                if self.start_num <= x_pos <= self.end_num:
                    self.ax.plot([x_pos, x_pos], [self.line_y - 0.04, self.line_y + 0.04], 
                                'k-', linewidth=0.8, alpha=0.6, zorder=1)
        
        self.ax.axis('off')
    
    def parse_fraction(self, value):
        """将数值转换为分数标签，确保显示准确的分数"""
        try:
            # 使用更高的精度来找到精确的分数表示
            frac = Fraction(value).limit_denominator(10000)
            # 验证这个分数是否接近原值
            if abs(float(frac) - value) < 1e-8:
                if frac.denominator != 1:
                    return f"{frac.numerator}/{frac.denominator}"
                else:
                    return str(int(value))
            else:
                # 如果无法精确表示，显示更多小数位以确保精度
                return f"{value:.6f}".rstrip('0').rstrip('.')
        except:
            return f"{value:.6f}".rstrip('0').rstrip('.')
    
    def update_visualization(self):
        """更新可视化"""
        # 清除之前的绘制
        if self.point1_dot:
            if isinstance(self.point1_dot, list):
                for item in self.point1_dot:
                    item.remove()
            else:
                self.point1_dot.remove()
        if self.point2_dot:
            if isinstance(self.point2_dot, list):
                for item in self.point2_dot:
                    item.remove()
            else:
                self.point2_dot.remove()
        if self.point1_label:
            self.point1_label.remove()
        if self.point2_label:
            self.point2_label.remove()
        if self.interval_rect:
            self.interval_rect.remove()
        for line in self.interval_lines:
            line.remove()
        
        self.interval_lines = []
        
        # 确保point1_value在范围内
        if self.point1_value < self.start_num:
            self.point1_value = self.start_num
        if self.point1_value > self.end_num:
            self.point1_value = self.end_num
        
        # 强制确保两个端点始终互为倒数关系（每次更新都重新计算）
        if self.point1_value != 0:
            # 始终根据point1重新计算point2的倒数，确保精确的倒数关系
            self.point2_value = 1.0 / self.point1_value
            # 验证倒数关系
            product = self.point1_value * self.point2_value
            if abs(product - 1.0) > 1e-10:
                # 如果乘积不是1，重新计算以确保精度
                self.point2_value = 1.0 / self.point1_value
        else:
            # 如果point1为0，避免除零错误
            self.point2_value = None
        
        # 重新绘制数轴
        self.ax.clear()
        self.draw_number_line()
        
        # 确定区间范围
        if self.point2_value is not None:
            min_val = min(self.point1_value, self.point2_value)
            max_val = max(self.point1_value, self.point2_value)
            
            # 绘制区间高亮（只显示数轴上方部分）
            rect_width = max_val - min_val
            rect_height = 0.5  # 只显示数轴上方的高度
            rect_x = min_val
            rect_y = self.line_y  # 从数轴开始向上
            
            # 绘制虚线矩形（只显示数轴上方）
            self.interval_rect = patches.Rectangle(
                (rect_x, rect_y), rect_width, rect_height,
                linewidth=2.5, linestyle='--', 
                edgecolor=self.interval_color, facecolor='none',
                zorder=0
            )
            self.ax.add_patch(self.interval_rect)
            
            # 绘制从端点到矩形框上方边缘的虚线（只绘制上方）
            for val in [self.point1_value, self.point2_value]:
                line1, = self.ax.plot([val, val], 
                                     [self.line_y, rect_y + rect_height], 
                                     linestyle='--', linewidth=2, 
                                     color=self.interval_color, 
                                     alpha=0.7, zorder=0)
                self.interval_lines.append(line1)
        
        # 验证倒数关系（用于调试和确保正确性）
        if self.point2_value is not None:
            product = self.point1_value * self.point2_value
            if abs(product - 1.0) > 1e-9:
                # 如果乘积不是1，强制重新计算以确保精确的倒数关系
                self.point2_value = 1.0 / self.point1_value
                # 调试输出
                new_product = self.point1_value * self.point2_value
                print(f"修正倒数关系: point1={self.point1_value:.10f}, point2={self.point2_value:.10f}, 乘积={new_product:.10f}")
        
        # 绘制端点1
        dot_color1 = 'orange' if self.dragging == 1 else 'red'
        dot1_outline, = self.ax.plot(self.point1_value, self.line_y, 'ko', markersize=14, zorder=5)
        dot1_fill, = self.ax.plot(self.point1_value, self.line_y, 'o', color=dot_color1, markersize=10, zorder=6)
        self.point1_dot = [dot1_outline, dot1_fill]
        
        label1_text = self.parse_fraction(self.point1_value)
        text_y = self.line_y - 0.35
        self.point1_label = self.ax.text(self.point1_value, text_y, label1_text, 
                                         ha='center', va='center',
                                         fontsize=13, fontweight='bold',
                                         bbox=dict(boxstyle='round,pad=0.3', 
                                                  facecolor='#FFFFE0',
                                                  edgecolor='black',
                                                  linewidth=1,
                                                  alpha=0.9),
                                         zorder=7)
        
        # 绘制端点2（如果存在且有效）
        if self.point2_value is not None:
            # 再次确保倒数关系
            expected_point2 = 1.0 / self.point1_value
            if abs(self.point2_value - expected_point2) > 1e-9:
                self.point2_value = expected_point2
            
            dot_color2 = 'orange' if self.dragging == 2 else 'blue'
            dot2_outline, = self.ax.plot(self.point2_value, self.line_y, 'ko', markersize=14, zorder=5)
            dot2_fill, = self.ax.plot(self.point2_value, self.line_y, 'o', color=dot_color2, markersize=10, zorder=6)
            self.point2_dot = [dot2_outline, dot2_fill]
            
            label2_text = self.parse_fraction(self.point2_value)
            self.point2_label = self.ax.text(self.point2_value, text_y, label2_text, 
                                             ha='center', va='center',
                                             fontsize=13, fontweight='bold',
                                             bbox=dict(boxstyle='round,pad=0.3', 
                                                      facecolor='#FFFFE0',
                                                      edgecolor='black',
                                                      linewidth=1,
                                                      alpha=0.9),
                                             zorder=7)
        
        self.fig.canvas.draw()
    
    def on_press(self, event):
        """处理鼠标按下事件"""
        if event.inaxes != self.ax:
            return
        
        # 检查是否点击在端点附近
        if abs(event.ydata - self.line_y) < self.drag_tolerance:
            dist_to_point1 = abs(event.xdata - self.point1_value)
            dist_to_point2 = abs(event.xdata - self.point2_value) if self.point2_value is not None else float('inf')
            
            if dist_to_point1 < self.drag_tolerance and dist_to_point1 < dist_to_point2:
                self.dragging = 1
            elif dist_to_point2 < self.drag_tolerance:
                self.dragging = 2
            else:
                # 点击在数轴上但没有点，拖动端点1
                self.dragging = 1
                self.point1_value = max(self.start_num, min(self.end_num, event.xdata))
                self.update_visualization()
    
    def on_motion(self, event):
        """处理鼠标移动事件"""
        if self.dragging is None or event.inaxes != self.ax:
            return
        
        if abs(event.ydata - self.line_y) < self.drag_tolerance * 2:
            if self.dragging == 1:
                # 拖动端点1，更新端点2为其倒数
                new_value = max(self.start_num, min(self.end_num, event.xdata))
                if new_value != 0:  # 避免除零
                    self.point1_value = new_value
                    # point2会在update_visualization中自动更新为倒数
                    self.update_visualization()
            elif self.dragging == 2 and self.point2_value is not None:
                # 拖动端点2，更新端点1为其倒数
                new_value = max(self.start_num, min(self.end_num, event.xdata))
                if new_value != 0:
                    # 先计算如果point2=new_value，point1会是多少
                    potential_point1 = 1.0 / new_value
                    # 如果point1在范围内，直接使用
                    if self.start_num <= potential_point1 <= self.end_num:
                        self.point2_value = new_value
                        self.point1_value = potential_point1
                    else:
                        # 如果point1超出范围，调整point2使得point1在边界上且两者互为倒数
                        if potential_point1 < self.start_num:
                            # point1太小，让它等于start_num，然后计算对应的point2
                            self.point1_value = self.start_num
                            self.point2_value = 1.0 / self.point1_value
                        elif potential_point1 > self.end_num:
                            # point1太大，让它等于end_num，然后计算对应的point2
                            self.point1_value = self.end_num
                            self.point2_value = 1.0 / self.point1_value
                    self.update_visualization()
    
    def on_release(self, event):
        """处理鼠标释放事件"""
        self.dragging = None
        if self.point1_value != 0:
            self.update_visualization()
    
    def on_key(self, event):
        """处理键盘事件"""
        key = event.key.lower()
        
        if key == 's':
            filename = 'number_line_reciprocal.png'
            self.fig.savefig(filename, dpi=300, facecolor='#F5F5DC', bbox_inches='tight')
            print(f"图片已保存: {filename}")
        elif key == 'r':
            self.point1_value = 0.3
            # point2会在update_visualization中自动更新为倒数
            self.update_visualization()
            print(f"已重置到初始值: point1={self.point1_value:.3f}, point2={self.point2_value:.3f} (互为倒数)")
        elif key == 'h':
            self.show_help(force=True)
        elif key == 'q':
            plt.close(self.fig)
            print("退出程序")
    
    def show(self):
        """显示交互式窗口"""
        plt.show()

def main():
    """主函数"""
    print("=" * 60)
    print("互为倒数的数轴可视化生成器")
    print("=" * 60)
    
    try:
        app = ReciprocalNumberLine(start_num=0, end_num=4, initial_value=0.3, figsize=(14, 6))
        
        print("\n✓ 交互式窗口已打开！")
        print("提示: 拖动红色或蓝色端点来改变区间\n")
        
        app.show()
        
    except Exception as e:
        print(f"\n✗ 运行程序时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
