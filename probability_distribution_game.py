"""
概率分布学习游戏
帮助学生理解0-1分布（伯努利分布）、二项分布和泊松分布
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy import stats
import random
from fractions import Fraction

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class ProbabilityDistributionGame:
    """概率分布学习游戏类"""
    
    def __init__(self):
        self.score = 0
        self.total_questions = 0
        self.current_distribution = None  # 'bernoulli', 'binomial', 'poisson'
        self.current_question = None
        self.level = 1
        self.answer_input = ""  # 当前输入的答案
        self.show_answer = False  # 是否显示答案
        
        # 创建主窗口
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.patch.set_facecolor('#F0F8FF')
        
        # 创建子图布局
        self.gs = self.fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 主可视化区域（左上，2x2）
        self.ax_main = self.fig.add_subplot(self.gs[0:2, 0:2])
        
        # 控制面板（右上）
        self.ax_control = self.fig.add_subplot(self.gs[0:2, 2])
        self.ax_control.axis('off')
        
        # 题目区域（底部）
        self.ax_question = self.fig.add_subplot(self.gs[2, :])
        self.ax_question.axis('off')
        
        # 绑定键盘事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 显示主菜单
        self.show_main_menu()
        
    def show_main_menu(self):
        """显示主菜单"""
        self.ax_main.clear()
        self.ax_main.axis('off')
        
        title_text = "概率分布学习游戏"
        subtitle_text = "选择要学习的分布类型"
        
        self.ax_main.text(0.5, 0.7, title_text, 
                         ha='center', va='center',
                         fontsize=32, fontweight='bold',
                         color='#2E86AB', transform=self.ax_main.transAxes)
        
        self.ax_main.text(0.5, 0.5, subtitle_text,
                         ha='center', va='center',
                         fontsize=18, color='#666666',
                         transform=self.ax_main.transAxes)
        
        # 显示选项
        options = [
            "1. 0-1分布（伯努利分布）",
            "2. 二项分布",
            "3. 泊松分布",
            "4. 随机练习",
            "按 'q' 退出"
        ]
        
        y_positions = [0.35, 0.25, 0.15, 0.05, -0.05]
        for i, (option, y_pos) in enumerate(zip(options, y_positions)):
            color = '#4169E1' if i < 4 else '#999999'
            self.ax_main.text(0.5, y_pos, option,
                            ha='center', va='center',
                            fontsize=16, color=color,
                            transform=self.ax_main.transAxes)
        
        # 显示得分信息
        self.update_control_panel()
        self.update_question_panel("按数字键 1-4 选择分布类型，或按 'q' 退出")
        self.fig.canvas.draw()
    
    def update_control_panel(self):
        """更新控制面板"""
        self.ax_control.clear()
        self.ax_control.axis('off')
        
        info_text = f"""
得分: {self.score}
正确率: {self.get_accuracy():.1f}%
等级: {self.level}
题目数: {self.total_questions}

快捷键:
- 1: 0-1分布
- 2: 二项分布
- 3: 泊松分布
- 4: 随机练习
- n: 下一题
- r: 重新开始
- q: 退出
        """
        
        self.ax_control.text(0.05, 0.95, info_text,
                            ha='left', va='top',
                            fontsize=11, family='monospace',
                            transform=self.ax_control.transAxes,
                            bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.8))
    
    def update_question_panel(self, text=None):
        """更新题目面板"""
        self.ax_question.clear()
        self.ax_question.axis('off')
        
        if text is None and self.current_question:
            question_text = f"题目: {self.current_question['question']}\n\n"
            if self.show_answer:
                question_text += f"✓ 正确答案: {self.current_question['correct_answer']:.4f}\n\n"
            else:
                question_text += f"已输入: {self.answer_input if self.answer_input else '(未输入)'}\n\n"
                question_text += "提示: 直接输入数字（如 0.25），然后按回车提交答案\n"
                question_text += "按 's' 显示答案，按 'n' 下一题"
            text = question_text
        
        if text:
            self.ax_question.text(0.5, 0.5, text,
                                 ha='center', va='center',
                                 fontsize=13, wrap=True,
                                 transform=self.ax_question.transAxes,
                                 bbox=dict(boxstyle='round', facecolor='#FFFACD', alpha=0.9))
    
    def get_accuracy(self):
        """计算正确率"""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100
    
    def generate_bernoulli_question(self):
        """生成0-1分布题目"""
        p = round(random.uniform(0.1, 0.9), 2)
        question_type = random.choice(['probability', 'expectation', 'variance'])
        
        if question_type == 'probability':
            outcome = random.choice([0, 1])
            correct_answer = p if outcome == 1 else (1 - p)
            question = f"0-1分布：P={p:.2f}，求 P(X={outcome}) = ?"
            return {
                'type': 'bernoulli',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'p': p}
            }
        elif question_type == 'expectation':
            correct_answer = p
            question = f"0-1分布：P={p:.2f}，求 E(X) = ?"
            return {
                'type': 'bernoulli',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'p': p}
            }
        else:  # variance
            correct_answer = p * (1 - p)
            question = f"0-1分布：P={p:.2f}，求 Var(X) = ?"
            return {
                'type': 'bernoulli',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'p': p}
            }
    
    def generate_binomial_question(self):
        """生成二项分布题目"""
        n = random.randint(5, 20)
        p = round(random.uniform(0.2, 0.8), 2)
        question_type = random.choice(['probability', 'expectation', 'variance'])
        
        if question_type == 'probability':
            k = random.randint(0, min(n, 10))
            correct_answer = stats.binom.pmf(k, n, p)
            question = f"二项分布：n={n}, p={p:.2f}，求 P(X={k}) = ?"
            return {
                'type': 'binomial',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'n': n, 'p': p, 'k': k}
            }
        elif question_type == 'expectation':
            correct_answer = n * p
            question = f"二项分布：n={n}, p={p:.2f}，求 E(X) = ?"
            return {
                'type': 'binomial',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'n': n, 'p': p}
            }
        else:  # variance
            correct_answer = n * p * (1 - p)
            question = f"二项分布：n={n}, p={p:.2f}，求 Var(X) = ?"
            return {
                'type': 'binomial',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'n': n, 'p': p}
            }
    
    def generate_poisson_question(self):
        """生成泊松分布题目"""
        lam = round(random.uniform(1, 10), 2)
        question_type = random.choice(['probability', 'expectation', 'variance'])
        
        if question_type == 'probability':
            k = random.randint(0, int(lam * 2) + 2)
            correct_answer = stats.poisson.pmf(k, lam)
            question = f"泊松分布：λ={lam:.2f}，求 P(X={k}) = ?"
            return {
                'type': 'poisson',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'lam': lam, 'k': k}
            }
        elif question_type == 'expectation':
            correct_answer = lam
            question = f"泊松分布：λ={lam:.2f}，求 E(X) = ?"
            return {
                'type': 'poisson',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'lam': lam}
            }
        else:  # variance
            correct_answer = lam
            question = f"泊松分布：λ={lam:.2f}，求 Var(X) = ?"
            return {
                'type': 'poisson',
                'question': question,
                'correct_answer': round(correct_answer, 4),
                'params': {'lam': lam}
            }
    
    def visualize_distribution(self, dist_type, params):
        """可视化分布"""
        self.ax_main.clear()
        
        if dist_type == 'bernoulli':
            self._visualize_bernoulli(params)
        elif dist_type == 'binomial':
            self._visualize_binomial(params)
        elif dist_type == 'poisson':
            self._visualize_poisson(params)
        
        self.fig.canvas.draw()
    
    def _visualize_bernoulli(self, params):
        """可视化0-1分布"""
        p = params['p']
        
        # 概率质量函数
        x = [0, 1]
        pmf = [1 - p, p]
        
        self.ax_main.bar(x, pmf, width=0.3, color=['#FF6B6B', '#4ECDC4'], 
                         alpha=0.7, edgecolor='black', linewidth=2)
        
        # 添加数值标签
        for i, (xi, prob) in enumerate(zip(x, pmf)):
            self.ax_main.text(xi, prob + 0.02, f'{prob:.3f}',
                            ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        # 添加理论值
        self.ax_main.axhline(y=p, xmin=0.25, xmax=0.75, color='red', 
                            linestyle='--', linewidth=2, alpha=0.5, label=f'E(X)={p:.3f}')
        self.ax_main.axhline(y=p*(1-p), xmin=0.1, xmax=0.9, color='blue',
                            linestyle='--', linewidth=2, alpha=0.5, label=f'Var(X)={p*(1-p):.3f}')
        
        self.ax_main.set_xlim(-0.5, 1.5)
        self.ax_main.set_ylim(0, max(pmf) * 1.3)
        self.ax_main.set_xlabel('X (结果)', fontsize=14, fontweight='bold')
        self.ax_main.set_ylabel('概率 P(X)', fontsize=14, fontweight='bold')
        self.ax_main.set_title(f'0-1分布（伯努利分布）: p={p:.2f}', 
                              fontsize=16, fontweight='bold', pad=15)
        self.ax_main.set_xticks([0, 1])
        self.ax_main.set_xticklabels(['失败 (0)', '成功 (1)'])
        self.ax_main.grid(True, alpha=0.3)
        self.ax_main.legend(loc='upper right', fontsize=10)
    
    def _visualize_binomial(self, params):
        """可视化二项分布"""
        n = params['n']
        p = params['p']
        
        # 概率质量函数
        x = np.arange(0, n + 1)
        pmf = stats.binom.pmf(x, n, p)
        
        # 绘制柱状图
        colors = plt.cm.viridis(np.linspace(0, 1, len(x)))
        bars = self.ax_main.bar(x, pmf, color=colors, alpha=0.7, 
                               edgecolor='black', linewidth=1.5)
        
        # 标注最高概率的点
        max_idx = np.argmax(pmf)
        bars[max_idx].set_color('#FF6B6B')
        bars[max_idx].set_alpha(1.0)
        
        # 添加理论值线
        E_X = n * p
        Var_X = n * p * (1 - p)
        self.ax_main.axvline(x=E_X, color='red', linestyle='--', 
                            linewidth=2, alpha=0.7, label=f'E(X)={E_X:.2f}')
        
        # 添加标准差区间
        std = np.sqrt(Var_X)
        self.ax_main.axvspan(max(0, E_X - std), min(n, E_X + std), 
                            alpha=0.2, color='green', label=f'±1σ区间')
        
        self.ax_main.set_xlim(-0.5, n + 0.5)
        self.ax_main.set_ylim(0, max(pmf) * 1.2)
        self.ax_main.set_xlabel('X (成功次数)', fontsize=14, fontweight='bold')
        self.ax_main.set_ylabel('概率 P(X)', fontsize=14, fontweight='bold')
        self.ax_main.set_title(f'二项分布: n={n}, p={p:.2f}', 
                              fontsize=16, fontweight='bold', pad=15)
        self.ax_main.grid(True, alpha=0.3, axis='y')
        self.ax_main.legend(loc='upper right', fontsize=10)
    
    def _visualize_poisson(self, params):
        """可视化泊松分布"""
        lam = params['lam']
        
        # 概率质量函数（显示足够的范围）
        max_x = int(lam * 3) + 5
        x = np.arange(0, max_x + 1)
        pmf = stats.poisson.pmf(x, lam)
        
        # 绘制柱状图
        colors = plt.cm.plasma(np.linspace(0, 1, len(x)))
        bars = self.ax_main.bar(x, pmf, color=colors, alpha=0.7,
                               edgecolor='black', linewidth=1.5)
        
        # 标注最高概率的点
        max_idx = np.argmax(pmf)
        bars[max_idx].set_color('#FF6B6B')
        bars[max_idx].set_alpha(1.0)
        
        # 添加理论值线
        E_X = lam
        self.ax_main.axvline(x=E_X, color='red', linestyle='--',
                            linewidth=2, alpha=0.7, label=f'E(X)=Var(X)={lam:.2f}')
        
        # 添加标准差区间
        std = np.sqrt(lam)
        self.ax_main.axvspan(max(0, E_X - std), E_X + std,
                            alpha=0.2, color='green', label=f'±1σ区间')
        
        self.ax_main.set_xlim(-0.5, max_x + 0.5)
        self.ax_main.set_ylim(0, max(pmf) * 1.2)
        self.ax_main.set_xlabel('X (事件发生次数)', fontsize=14, fontweight='bold')
        self.ax_main.set_ylabel('概率 P(X)', fontsize=14, fontweight='bold')
        self.ax_main.set_title(f'泊松分布: λ={lam:.2f}', 
                              fontsize=16, fontweight='bold', pad=15)
        self.ax_main.grid(True, alpha=0.3, axis='y')
        self.ax_main.legend(loc='upper right', fontsize=10)
    
    def start_practice(self, dist_type=None):
        """开始练习"""
        if dist_type is None:
            dist_type = random.choice(['bernoulli', 'binomial', 'poisson'])
        
        self.current_distribution = dist_type
        
        # 生成题目
        if dist_type == 'bernoulli':
            self.current_question = self.generate_bernoulli_question()
        elif dist_type == 'binomial':
            self.current_question = self.generate_binomial_question()
        elif dist_type == 'poisson':
            self.current_question = self.generate_poisson_question()
        
        # 显示可视化
        self.visualize_distribution(dist_type, self.current_question['params'])
        
        # 重置答案输入状态
        self.answer_input = ""
        self.show_answer = False
        
        # 显示题目
        self.update_question_panel()
        self.update_control_panel()
        
        print(f"\n{'='*60}")
        print(f"题目: {self.current_question['question']}")
        print(f"{'='*60}")
        print("提示: 在图形窗口中直接输入数字，然后按回车提交答案")
        print("或按 's' 显示答案，按 'n' 下一题")
    
    def check_answer(self, user_answer_str=None):
        """检查答案"""
        if user_answer_str is None:
            user_answer_str = self.answer_input
        
        if not user_answer_str or not user_answer_str.strip():
            print("请输入答案！")
            return False
        
        try:
            user_answer = float(user_answer_str.strip())
            correct_answer = self.current_question['correct_answer']
            tolerance = 0.01  # 允许的误差范围（放宽到0.01以便更容易答对）
            
            self.total_questions += 1
            
            if abs(user_answer - correct_answer) < tolerance:
                self.score += 1
                feedback = f"✓ 正确！答案是 {correct_answer:.4f}"
                self.update_level()
                print(f"\n{feedback}")
            else:
                feedback = f"✗ 错误。正确答案是 {correct_answer:.4f}，你的答案是 {user_answer:.4f}"
                print(f"\n{feedback}")
            
            # 更新控制面板
            self.update_control_panel()
            
            # 显示反馈
            feedback_text = f"{feedback}\n\n按 'n' 进入下一题"
            self.update_question_panel(feedback_text)
            
            # 清空输入
            self.answer_input = ""
            
            return abs(user_answer - correct_answer) < tolerance
            
        except ValueError:
            print("请输入有效的数字！")
            return False
    
    def update_level(self):
        """更新等级"""
        if self.total_questions > 0:
            accuracy = self.get_accuracy()
            if accuracy >= 90:
                self.level = max(self.level, 5)
            elif accuracy >= 80:
                self.level = max(self.level, 4)
            elif accuracy >= 70:
                self.level = max(self.level, 3)
            elif accuracy >= 60:
                self.level = max(self.level, 2)
            else:
                self.level = max(self.level, 1)
    
    def on_key(self, event):
        """处理键盘事件"""
        key = event.key
        
        if key == 'q':
            plt.close(self.fig)
            print("\n游戏结束！")
            print(f"最终得分: {self.score}/{self.total_questions}")
            if self.total_questions > 0:
                print(f"正确率: {self.get_accuracy():.1f}%")
            print(f"等级: {self.level}")
        
        elif key == '1':
            self.start_practice('bernoulli')
        
        elif key == '2':
            self.start_practice('binomial')
        
        elif key == '3':
            self.start_practice('poisson')
        
        elif key == '4':
            self.start_practice()  # 随机选择
        
        elif key == 'n':
            if self.current_question:
                self.start_practice(self.current_distribution)
            else:
                print("请先选择一个分布类型！")
        
        elif key == 's':
            if self.current_question:
                self.show_answer = True
                print(f"\n{'='*60}")
                print(f"💡 正确答案: {self.current_question['correct_answer']:.4f}")
                print(f"{'='*60}\n")
                self.update_question_panel()
        
        elif key == 'r':
            self.score = 0
            self.total_questions = 0
            self.level = 1
            self.current_question = None
            self.current_distribution = None
            self.answer_input = ""
            self.show_answer = False
            self.show_main_menu()
            print("\n游戏已重置！")
        
        elif key == 'enter' or key == '\r':
            # 提交答案
            if self.current_question and self.answer_input:
                self.check_answer()
        
        elif key == 'backspace':
            # 删除最后一个字符
            if self.answer_input:
                self.answer_input = self.answer_input[:-1]
                if self.current_question:
                    self.update_question_panel()
        
        elif key.isdigit() or key == '.' or key == '-':
            # 输入数字
            if self.current_question:
                self.answer_input += key
                self.update_question_panel()
        
        elif key == 'h':
            # 显示帮助
            self.show_help()
    
    def show(self):
        """显示窗口"""
        plt.show()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
{'='*60}
概率分布学习游戏 - 操作说明
{'='*60}

选择分布类型:
  1 - 0-1分布（伯努利分布）
  2 - 二项分布
  3 - 泊松分布
  4 - 随机练习

答题操作:
  - 直接输入数字（如：0.25, 5, 3.1416）
  - 按回车提交答案
  - 按退格键删除输入
  - 按 's' 显示正确答案
  - 按 'n' 进入下一题

其他操作:
  - 按 'r' 重置游戏
  - 按 'h' 显示帮助
  - 按 'q' 退出游戏

{'='*60}
        """
        print(help_text)
    
    def run_interactive(self):
        """运行交互式模式"""
        print("\n" + "="*60)
        print("概率分布学习游戏")
        print("="*60)
        self.show_help()
        print("\n提示: 在图形窗口中操作，直接输入数字即可答题！")
        print("="*60 + "\n")
        
        self.show()

def main():
    """主函数"""
    try:
        game = ProbabilityDistributionGame()
        game.run_interactive()
    except Exception as e:
        print(f"\n✗ 运行程序时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
