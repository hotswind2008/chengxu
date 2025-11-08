"""
概率分布学习游戏 - 增强版
帮助学生通过游戏化方式掌握0-1分布、二项分布、泊松分布
包含关卡、成就、动画等丰富的游戏化元素
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider, RadioButtons
import numpy as np
import random
from collections import defaultdict
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ProbabilityDistributionGameEnhanced:
    """增强版概率分布学习游戏类"""
    
    def __init__(self):
        # 游戏状态
        self.distribution_type = 'bernoulli'  # 'bernoulli', 'binomial', 'poisson'
        self.game_mode = 'learn'  # 'learn': 学习模式, 'practice': 练习模式, 'challenge': 挑战模式
        
        # 得分系统
        self.score = 0
        self.total_questions = 0
        self.correct_streak = 0  # 连续答对次数
        self.level = 1  # 当前关卡
        self.exp = 0  # 经验值
        
        # 成就系统
        self.achievements = {
            'first_simulation': False,
            'first_correct': False,
            'streak_5': False,
            'streak_10': False,
            'master_bernoulli': False,
            'master_binomial': False,
            'master_poisson': False,
            'simulation_master': False,  # 1000次模拟
        }
        
        # 分布参数
        self.p_bernoulli = 0.5
        self.n_binomial = 10
        self.p_binomial = 0.5
        self.lambda_poisson = 3
        
        # 模拟数据
        self.simulation_results = []
        self.simulation_count = 0
        self.simulation_history = []  # 每次模拟的详细记录
        
        # 练习模式
        self.current_question = None
        self.question_answer = None
        self.question_type = None  # 'probability', 'expectation', 'variance'
        self.user_answer = None
        self.show_answer = False
        
        # 动画效果
        self.animation_frame = 0
        self.highlight_bar_idx = None
        
        # 创建图形界面
        self.fig = plt.figure(figsize=(18, 11))
        self.fig.patch.set_facecolor('#E8F4F8')
        
        # 创建子图布局
        self.setup_layout()
        
        # 创建控件
        self.create_controls()
        
        # 绑定事件
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # 初始化显示
        self.update_all_displays()
        self.show_welcome_message()
    
    def setup_layout(self):
        """设置布局"""
        # 主分布图（左上，大）
        self.ax_main = plt.subplot2grid((5, 4), (0, 0), colspan=2, rowspan=2)
        
        # 模拟结果图（左下）
        self.ax_sim = plt.subplot2grid((5, 4), (2, 0), colspan=2, rowspan=1)
        
        # 信息面板（右上）
        self.ax_info = plt.subplot2grid((5, 4), (0, 2), rowspan=2)
        self.ax_info.axis('off')
        
        # 问题面板（中右）
        self.ax_question = plt.subplot2grid((5, 4), (2, 2), rowspan=1)
        self.ax_question.axis('off')
        
        # 统计面板（右下）
        self.ax_stats = plt.subplot2grid((5, 4), (3, 2), rowspan=1)
        self.ax_stats.axis('off')
        
        # 成就面板（最下）
        self.ax_achievements = plt.subplot2grid((5, 4), (4, 0), colspan=4, rowspan=1)
        self.ax_achievements.axis('off')
    
    def create_controls(self):
        """创建控制按钮和滑块"""
        # 分布类型选择按钮（顶部）
        btn_width = 0.12
        btn_height = 0.04
        spacing = 0.015
        
        ax_btn_bernoulli = plt.axes([0.05, 0.93, btn_width, btn_height])
        ax_btn_binomial = plt.axes([0.05 + btn_width + spacing, 0.93, btn_width, btn_height])
        ax_btn_poisson = plt.axes([0.05 + 2*(btn_width + spacing), 0.93, btn_width, btn_height])
        
        self.btn_bernoulli = Button(ax_btn_bernoulli, '0-1分布', color='#FFE5B4', hovercolor='#FFD700')
        self.btn_binomial = Button(ax_btn_binomial, '二项分布', color='#B4E5FF', hovercolor='#87CEEB')
        self.btn_poisson = Button(ax_btn_poisson, '泊松分布', color='#D4FFD4', hovercolor='#90EE90')
        
        self.btn_bernoulli.on_clicked(lambda x: self.set_distribution('bernoulli'))
        self.btn_binomial.on_clicked(lambda x: self.set_distribution('binomial'))
        self.btn_poisson.on_clicked(lambda x: self.set_distribution('poisson'))
        
        # 模式选择按钮
        ax_btn_learn = plt.axes([0.45, 0.93, 0.08, btn_height])
        ax_btn_practice = plt.axes([0.54, 0.93, 0.08, btn_height])
        ax_btn_challenge = plt.axes([0.63, 0.93, 0.08, btn_height])
        
        self.btn_learn = Button(ax_btn_learn, '学习', color='lightgreen', hovercolor='green')
        self.btn_practice = Button(ax_btn_practice, '练习', color='lightyellow', hovercolor='yellow')
        self.btn_challenge = Button(ax_btn_challenge, '挑战', color='lightcoral', hovercolor='red')
        
        self.btn_learn.on_clicked(lambda x: self.set_game_mode('learn'))
        self.btn_practice.on_clicked(lambda x: self.set_game_mode('practice'))
        self.btn_challenge.on_clicked(lambda x: self.set_game_mode('challenge'))
        
        # 模拟按钮
        ax_btn_sim1 = plt.axes([0.73, 0.93, 0.06, btn_height])
        ax_btn_sim100 = plt.axes([0.80, 0.93, 0.06, btn_height])
        ax_btn_reset = plt.axes([0.87, 0.93, 0.06, btn_height])
        
        self.btn_sim1 = Button(ax_btn_sim1, '模拟1次', color='#FFB6C1', hovercolor='#FF69B4')
        self.btn_sim100 = Button(ax_btn_sim100, '模拟100次', color='#98FB98', hovercolor='#32CD32')
        self.btn_reset = Button(ax_btn_reset, '重置', color='lightgray', hovercolor='gray')
        
        self.btn_sim1.on_clicked(lambda x: self.run_simulation(1))
        self.btn_sim100.on_clicked(lambda x: self.run_simulation(100))
        self.btn_reset.on_clicked(lambda x: self.reset_simulation())
        
        # 创建参数滑块
        self.update_sliders()
    
    def update_sliders(self):
        """更新滑块控件"""
        # 清除旧的滑块
        for attr in ['slider_p_bernoulli', 'slider_n_binomial', 'slider_p_binomial', 'slider_lambda_poisson']:
            if hasattr(self, attr):
                getattr(self, attr).ax.remove()
        
        slider_y = 0.88
        slider_height = 0.02
        
        if self.distribution_type == 'bernoulli':
            ax_slider = plt.axes([0.05, slider_y, 0.4, slider_height])
            self.slider_p_bernoulli = Slider(ax_slider, '概率 p', 0.01, 0.99, 
                                            valinit=self.p_bernoulli, valfmt='%.2f',
                                            valstep=0.01)
            self.slider_p_bernoulli.on_changed(self.update_bernoulli_params)
        
        elif self.distribution_type == 'binomial':
            ax_slider_n = plt.axes([0.05, slider_y, 0.18, slider_height])
            ax_slider_p = plt.axes([0.25, slider_y, 0.18, slider_height])
            
            self.slider_n_binomial = Slider(ax_slider_n, '试验次数 n', 1, 50, 
                                           valinit=self.n_binomial, valfmt='%d', valstep=1)
            self.slider_p_binomial = Slider(ax_slider_p, '成功概率 p', 0.01, 0.99, 
                                            valinit=self.p_binomial, valfmt='%.2f', valstep=0.01)
            
            self.slider_n_binomial.on_changed(self.update_binomial_params)
            self.slider_p_binomial.on_changed(self.update_binomial_params)
        
        elif self.distribution_type == 'poisson':
            ax_slider = plt.axes([0.05, slider_y, 0.4, slider_height])
            self.slider_lambda_poisson = Slider(ax_slider, '参数 λ', 0.1, 10.0, 
                                               valinit=self.lambda_poisson, valfmt='%.2f',
                                               valstep=0.1)
            self.slider_lambda_poisson.on_changed(self.update_poisson_params)
    
    def set_distribution(self, dist_type):
        """设置分布类型"""
        self.distribution_type = dist_type
        self.update_sliders()
        self.reset_simulation()
        if self.game_mode == 'practice':
            self.generate_question()
        self.update_all_displays()
        self.check_achievement_unlock()
    
    def set_game_mode(self, mode):
        """设置游戏模式"""
        self.game_mode = mode
        if mode == 'practice':
            self.generate_question()
        self.update_all_displays()
    
    def update_bernoulli_params(self, val):
        """更新伯努利分布参数"""
        self.p_bernoulli = self.slider_p_bernoulli.val
        if self.game_mode == 'practice':
            self.generate_question()
        self.update_all_displays()
    
    def update_binomial_params(self, val):
        """更新二项分布参数"""
        self.n_binomial = int(self.slider_n_binomial.val)
        self.p_binomial = self.slider_p_binomial.val
        if self.game_mode == 'practice':
            self.generate_question()
        self.update_all_displays()
    
    def update_poisson_params(self, val):
        """更新泊松分布参数"""
        self.lambda_poisson = self.slider_lambda_poisson.val
        if self.game_mode == 'practice':
            self.generate_question()
        self.update_all_displays()
    
    def calculate_probability(self, k):
        """计算概率值"""
        if self.distribution_type == 'bernoulli':
            if k == 0:
                return 1 - self.p_bernoulli
            elif k == 1:
                return self.p_bernoulli
            return 0
        
        elif self.distribution_type == 'binomial':
            if k < 0 or k > self.n_binomial:
                return 0
            # 使用组合数计算：C(n,k) * p^k * (1-p)^(n-k)
            if k == 0:
                return (1 - self.p_binomial) ** self.n_binomial
            prob = 1.0
            for i in range(k):
                prob *= (self.n_binomial - i) / (i + 1)
            prob *= (self.p_binomial ** k) * ((1 - self.p_binomial) ** (self.n_binomial - k))
            return prob
        
        elif self.distribution_type == 'poisson':
            if k < 0:
                return 0
            # P(X=k) = (λ^k * e^(-λ)) / k!
            prob = np.exp(-self.lambda_poisson)
            for i in range(k):
                prob *= self.lambda_poisson / (i + 1)
            return prob
        
        return 0
    
    def calculate_expectation(self):
        """计算期望值"""
        if self.distribution_type == 'bernoulli':
            return self.p_bernoulli
        elif self.distribution_type == 'binomial':
            return self.n_binomial * self.p_binomial
        elif self.distribution_type == 'poisson':
            return self.lambda_poisson
        return 0
    
    def calculate_variance(self):
        """计算方差"""
        if self.distribution_type == 'bernoulli':
            return self.p_bernoulli * (1 - self.p_bernoulli)
        elif self.distribution_type == 'binomial':
            return self.n_binomial * self.p_binomial * (1 - self.p_binomial)
        elif self.distribution_type == 'poisson':
            return self.lambda_poisson
        return 0
    
    def run_simulation(self, num_trials=1):
        """运行模拟"""
        for _ in range(num_trials):
            if self.distribution_type == 'bernoulli':
                result = 1 if random.random() < self.p_bernoulli else 0
            elif self.distribution_type == 'binomial':
                success_count = sum(1 for _ in range(self.n_binomial) 
                                  if random.random() < self.p_binomial)
                result = success_count
            elif self.distribution_type == 'poisson':
                result = np.random.poisson(self.lambda_poisson)
            else:
                result = 0
            
            self.simulation_results.append(result)
            self.simulation_count += 1
        
        # 解锁成就
        if not self.achievements['first_simulation']:
            self.achievements['first_simulation'] = True
            self.show_achievement_message("🎉 成就解锁：首次模拟！")
        
        if self.simulation_count >= 1000 and not self.achievements['simulation_master']:
            self.achievements['simulation_master'] = True
            self.show_achievement_message("🏆 成就解锁：模拟大师！完成1000次模拟")
        
        self.update_all_displays()
    
    def reset_simulation(self):
        """重置模拟结果"""
        self.simulation_results = []
        self.simulation_count = 0
        self.update_all_displays()
    
    def generate_question(self):
        """生成问题"""
        question_types = ['probability', 'expectation', 'variance']
        self.question_type = random.choice(question_types)
        self.show_answer = False
        
        if self.distribution_type == 'bernoulli':
            if self.question_type == 'probability':
                k = random.choice([0, 1])
                self.question_answer = self.calculate_probability(k)
                self.current_question = (
                    f"📊 概率计算题\n\n"
                    f"在0-1分布中，成功概率 p = {self.p_bernoulli:.2f}\n"
                    f"请问 P(X = {k}) = ?\n\n"
                    f"（请输入0到1之间的小数，保留4位小数）"
                )
            elif self.question_type == 'expectation':
                self.question_answer = self.calculate_expectation()
                self.current_question = (
                    f"📊 期望值计算题\n\n"
                    f"在0-1分布中，成功概率 p = {self.p_bernoulli:.2f}\n"
                    f"请问 E(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
            else:  # variance
                self.question_answer = self.calculate_variance()
                self.current_question = (
                    f"📊 方差计算题\n\n"
                    f"在0-1分布中，成功概率 p = {self.p_bernoulli:.2f}\n"
                    f"请问 Var(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
        
        elif self.distribution_type == 'binomial':
            if self.question_type == 'probability':
                k = random.randint(0, min(self.n_binomial, 15))
                self.question_answer = self.calculate_probability(k)
                self.current_question = (
                    f"📊 概率计算题\n\n"
                    f"在二项分布中，n = {self.n_binomial}，p = {self.p_binomial:.2f}\n"
                    f"请问 P(X = {k}) = ?\n\n"
                    f"（请输入0到1之间的小数，保留4位小数）"
                )
            elif self.question_type == 'expectation':
                self.question_answer = self.calculate_expectation()
                self.current_question = (
                    f"📊 期望值计算题\n\n"
                    f"在二项分布中，n = {self.n_binomial}，p = {self.p_binomial:.2f}\n"
                    f"请问 E(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
            else:  # variance
                self.question_answer = self.calculate_variance()
                self.current_question = (
                    f"📊 方差计算题\n\n"
                    f"在二项分布中，n = {self.n_binomial}，p = {self.p_binomial:.2f}\n"
                    f"请问 Var(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
        
        elif self.distribution_type == 'poisson':
            if self.question_type == 'probability':
                k = random.randint(0, min(int(self.lambda_poisson * 4), 20))
                self.question_answer = self.calculate_probability(k)
                self.current_question = (
                    f"📊 概率计算题\n\n"
                    f"在泊松分布中，λ = {self.lambda_poisson:.2f}\n"
                    f"请问 P(X = {k}) = ?\n\n"
                    f"（请输入0到1之间的小数，保留4位小数）"
                )
            elif self.question_type == 'expectation':
                self.question_answer = self.calculate_expectation()
                self.current_question = (
                    f"📊 期望值计算题\n\n"
                    f"在泊松分布中，λ = {self.lambda_poisson:.2f}\n"
                    f"请问 E(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
            else:  # variance
                self.question_answer = self.calculate_variance()
                self.current_question = (
                    f"📊 方差计算题\n\n"
                    f"在泊松分布中，λ = {self.lambda_poisson:.2f}\n"
                    f"请问 Var(X) = ?\n\n"
                    f"（请输入数字，保留4位小数）"
                )
        
        self.update_all_displays()
    
    def check_answer(self, user_answer):
        """检查答案"""
        try:
            user_val = float(user_answer)
            correct = abs(user_val - self.question_answer) < 0.0001
            
            if correct:
                self.score += 1
                self.correct_streak += 1
                self.exp += 10
                self.total_questions += 1
                
                # 检查成就
                if not self.achievements['first_correct']:
                    self.achievements['first_correct'] = True
                    self.show_achievement_message("🎉 成就解锁：首次答对！")
                
                if self.correct_streak == 5 and not self.achievements['streak_5']:
                    self.achievements['streak_5'] = True
                    self.show_achievement_message("🔥 成就解锁：连续答对5题！")
                
                if self.correct_streak == 10 and not self.achievements['streak_10']:
                    self.achievements['streak_10'] = True
                    self.show_achievement_message("🏆 成就解锁：连续答对10题！")
                
                # 检查掌握成就
                if self.distribution_type == 'bernoulli' and not self.achievements['master_bernoulli']:
                    if self.score >= 10:
                        self.achievements['master_bernoulli'] = True
                        self.show_achievement_message("⭐ 成就解锁：0-1分布大师！")
                
                return True, "✅ 回答正确！"
            else:
                self.correct_streak = 0
                self.total_questions += 1
                return False, f"❌ 回答错误。正确答案：{self.question_answer:.4f}"
        except ValueError:
            return False, "❌ 请输入有效的数字"
    
    def show_achievement_message(self, message):
        """显示成就消息"""
        print(f"\n{'='*60}")
        print(message)
        print(f"{'='*60}\n")
    
    def check_achievement_unlock(self):
        """检查成就解锁"""
        # 分布掌握成就基于得分检查，在check_answer中处理
        pass
    
    def show_welcome_message(self):
        """显示欢迎消息"""
        print("\n" + "="*70)
        print("🎮 概率分布学习游戏 - 增强版")
        print("="*70)
        print("\n📚 学习三种重要的概率分布：")
        print("  • 0-1分布（伯努利分布）：两种结果的随机试验")
        print("  • 二项分布：n次独立重复试验中成功的次数")
        print("  • 泊松分布：单位时间内随机事件发生的次数")
        print("\n🎯 游戏模式：")
        print("  • 学习模式：调整参数，观察分布变化")
        print("  • 练习模式：回答问题，提升技能")
        print("  • 挑战模式：高难度题目，测试掌握程度")
        print("\n⌨️  键盘快捷键：")
        print("  • 'n' - 生成新问题（练习模式）")
        print("  • 's' - 显示答案")
        print("  • 'h' - 显示帮助")
        print("  • 'q' - 快速模拟100次")
        print("="*70 + "\n")
    
    def update_all_displays(self):
        """更新所有显示"""
        self.draw_distribution()
        self.draw_simulation()
        self.draw_info()
        self.draw_question()
        self.draw_stats()
        self.draw_achievements()
        self.fig.canvas.draw()
    
    def draw_distribution(self):
        """绘制概率分布"""
        self.ax_main.clear()
        self.ax_main.set_facecolor('#FFFFFF')
        
        if self.distribution_type == 'bernoulli':
            x = [0, 1]
            y = [self.calculate_probability(0), self.calculate_probability(1)]
            colors = ['#87CEEB', '#FF6B6B']
            
            bars = self.ax_main.bar(x, y, width=0.4, color=colors, 
                                   edgecolor='black', linewidth=2.5, alpha=0.8)
            
            # 添加概率标签
            for i, (xi, yi) in enumerate(zip(x, y)):
                self.ax_main.text(xi, yi + max(y) * 0.05, f'{yi:.3f}', 
                                ha='center', va='bottom', fontsize=12, fontweight='bold')
                # 添加事件说明
                event_label = '失败' if i == 0 else '成功'
                self.ax_main.text(xi, -max(y) * 0.1, event_label, 
                                ha='center', va='top', fontsize=10, style='italic')
            
            self.ax_main.set_xlim(-0.6, 1.6)
            self.ax_main.set_ylim(0, max(y) * 1.3)
            self.ax_main.set_xticks([0, 1])
            self.ax_main.set_xlabel('随机变量 X', fontsize=13, fontweight='bold')
            self.ax_main.set_ylabel('概率 P(X)', fontsize=13, fontweight='bold')
            self.ax_main.set_title('0-1分布（伯努利分布）', fontsize=15, fontweight='bold', pad=15, color='#FF6B6B')
            self.ax_main.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # 添加期望和方差标注
            expectation = self.calculate_expectation()
            variance = self.calculate_variance()
            info_text = f'E(X) = {expectation:.3f}\nVar(X) = {variance:.3f}'
            self.ax_main.text(0.98, 0.98, info_text, transform=self.ax_main.transAxes,
                            ha='right', va='top', fontsize=10,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        elif self.distribution_type == 'binomial':
            x = list(range(self.n_binomial + 1))
            y = [self.calculate_probability(k) for k in x]
            
            # 使用渐变色
            colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(x)))
            bars = self.ax_main.bar(x, y, width=0.7, color=colors, 
                                   edgecolor='navy', linewidth=1.5, alpha=0.8)
            
            self.ax_main.set_xlim(-0.5, self.n_binomial + 0.5)
            self.ax_main.set_ylim(0, max(y) * 1.2)
            self.ax_main.set_xlabel('成功次数 k', fontsize=13, fontweight='bold')
            self.ax_main.set_ylabel('概率 P(X=k)', fontsize=13, fontweight='bold')
            self.ax_main.set_title(f'二项分布 (n={self.n_binomial}, p={self.p_binomial:.2f})', 
                                  fontsize=15, fontweight='bold', pad=15, color='#4169E1')
            self.ax_main.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # 标记最可能值
            max_idx = np.argmax(y)
            self.ax_main.axvline(max_idx, color='red', linestyle='--', linewidth=2, alpha=0.6)
            self.ax_main.text(max_idx, max(y) * 1.1, f'最可能值: {max_idx}', 
                            ha='center', fontsize=10, fontweight='bold', color='red')
            
            # 添加期望和方差
            expectation = self.calculate_expectation()
            variance = self.calculate_variance()
            info_text = f'E(X) = {expectation:.2f}\nVar(X) = {variance:.2f}'
            self.ax_main.text(0.98, 0.98, info_text, transform=self.ax_main.transAxes,
                            ha='right', va='top', fontsize=10,
                            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        elif self.distribution_type == 'poisson':
            max_k = max(20, int(self.lambda_poisson * 4))
            x = list(range(max_k + 1))
            y = [self.calculate_probability(k) for k in x]
            
            # 使用渐变色
            colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(x)))
            bars = self.ax_main.bar(x, y, width=0.7, color=colors, 
                                   edgecolor='darkgreen', linewidth=1.5, alpha=0.8)
            
            self.ax_main.set_xlim(-0.5, min(max_k + 0.5, 30))
            self.ax_main.set_ylim(0, max(y) * 1.2)
            self.ax_main.set_xlabel('事件发生次数 k', fontsize=13, fontweight='bold')
            self.ax_main.set_ylabel('概率 P(X=k)', fontsize=13, fontweight='bold')
            self.ax_main.set_title(f'泊松分布 (λ={self.lambda_poisson:.2f})', 
                                  fontsize=15, fontweight='bold', pad=15, color='#228B22')
            self.ax_main.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # 标记参数值附近
            lambda_int = int(self.lambda_poisson)
            if lambda_int < len(y):
                self.ax_main.axvline(lambda_int, color='red', linestyle='--', linewidth=2, alpha=0.6)
                self.ax_main.text(lambda_int, max(y) * 1.1, f'λ={self.lambda_poisson:.2f}', 
                                ha='center', fontsize=10, fontweight='bold', color='red')
            
            # 添加期望和方差（泊松分布期望=方差=λ）
            expectation = self.calculate_expectation()
            variance = self.calculate_variance()
            info_text = f'E(X) = Var(X) = {expectation:.2f}'
            self.ax_main.text(0.98, 0.98, info_text, transform=self.ax_main.transAxes,
                            ha='right', va='top', fontsize=10,
                            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    def draw_simulation(self):
        """绘制模拟结果"""
        self.ax_sim.clear()
        self.ax_sim.set_facecolor('#F8F8F8')
        
        if len(self.simulation_results) == 0:
            self.ax_sim.text(0.5, 0.5, '点击"模拟"按钮开始随机模拟', 
                           ha='center', va='center', fontsize=12,
                           transform=self.ax_sim.transAxes, style='italic')
            self.ax_sim.set_title('模拟结果', fontsize=12, fontweight='bold')
            return
        
        # 统计频率
        unique, counts = np.unique(self.simulation_results, return_counts=True)
        frequencies = counts / len(self.simulation_results)
        
        if self.distribution_type == 'bernoulli':
            x_all = [0, 1]
            y_all = [frequencies[list(unique).index(0)] if 0 in unique else 0,
                    frequencies[list(unique).index(1)] if 1 in unique else 0]
            colors = ['#87CEEB', '#FF6B6B']
            self.ax_sim.bar(x_all, y_all, width=0.4, color=colors, 
                          edgecolor='black', linewidth=2, alpha=0.7)
            self.ax_sim.set_xlim(-0.6, 1.6)
            self.ax_sim.set_xticks([0, 1])
        else:
            self.ax_sim.bar(unique, frequencies, width=0.6, color='steelblue', 
                          edgecolor='navy', linewidth=1.5, alpha=0.7)
            self.ax_sim.set_xlim(-0.5, max(unique) + 0.5)
        
        # 计算样本均值和方差
        sample_mean = np.mean(self.simulation_results)
        sample_var = np.var(self.simulation_results)
        theoretical_mean = self.calculate_expectation()
        theoretical_var = self.calculate_variance()
        
        self.ax_sim.set_xlabel('观测值', fontsize=11, fontweight='bold')
        self.ax_sim.set_ylabel('频率', fontsize=11, fontweight='bold')
        title = f'模拟结果 (共{self.simulation_count}次) | '
        title += f'样本均值: {sample_mean:.3f} (理论: {theoretical_mean:.3f})'
        self.ax_sim.set_title(title, fontsize=11, fontweight='bold')
        self.ax_sim.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加理论分布曲线（用于对比）
        if len(self.simulation_results) >= 10:  # 样本足够大时才显示
            if self.distribution_type == 'bernoulli':
                x_theory = [0, 1]
                y_theory = [self.calculate_probability(0), self.calculate_probability(1)]
            elif self.distribution_type == 'binomial':
                x_theory = list(range(self.n_binomial + 1))
                y_theory = [self.calculate_probability(k) for k in x_theory]
            else:  # poisson
                max_k = max(unique) if len(unique) > 0 else 10
                x_theory = list(range(max_k + 1))
                y_theory = [self.calculate_probability(k) for k in x_theory]
            
            self.ax_sim.plot(x_theory, y_theory, 'r--', linewidth=2, alpha=0.6, label='理论分布')
            self.ax_sim.legend(fontsize=9)
    
    def draw_info(self):
        """显示分布信息"""
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        if self.distribution_type == 'bernoulli':
            info_text = (
                "📖 0-1分布（伯努利分布）\n\n"
                "定义：\n"
                "• 只有两种可能结果\n"
                "  成功(X=1) 或 失败(X=0)\n\n"
                "参数：\n"
                f"• p = {self.p_bernoulli:.2f} (成功概率)\n\n"
                "概率质量函数：\n"
                f"• P(X=0) = {self.calculate_probability(0):.3f}\n"
                f"• P(X=1) = {self.calculate_probability(1):.3f}\n\n"
                "数学性质：\n"
                f"• E(X) = p = {self.calculate_expectation():.3f}\n"
                f"• Var(X) = p(1-p) = {self.calculate_variance():.3f}\n\n"
                "实际应用：\n"
                "• 抛硬币\n"
                "• 是否下雨\n"
                "• 产品质量合格与否"
            )
            bg_color = '#FFF8DC'
        
        elif self.distribution_type == 'binomial':
            info_text = (
                "📖 二项分布\n\n"
                "定义：\n"
                "• n次独立重复试验\n"
                "• 每次成功概率为p\n"
                "• X表示成功次数\n\n"
                "参数：\n"
                f"• n = {self.n_binomial} (试验次数)\n"
                f"• p = {self.p_binomial:.2f} (成功概率)\n\n"
                "概率质量函数：\n"
                f"• P(X=k) = C(n,k)·p^k·(1-p)^(n-k)\n\n"
                "数学性质：\n"
                f"• E(X) = np = {self.calculate_expectation():.2f}\n"
                f"• Var(X) = np(1-p) = {self.calculate_variance():.2f}\n\n"
                "实际应用：\n"
                "• 多次抛硬币\n"
                "• 产品质量检测\n"
                "• 调查问卷分析"
            )
            bg_color = '#E6F3FF'
        
        elif self.distribution_type == 'poisson':
            info_text = (
                "📖 泊松分布\n\n"
                "定义：\n"
                "• 描述单位时间内\n"
                "  随机事件发生次数\n"
                "• 事件独立且概率很小\n\n"
                "参数：\n"
                f"• λ = {self.lambda_poisson:.2f}\n"
                "  (平均发生次数)\n\n"
                "概率质量函数：\n"
                f"• P(X=k) = (λ^k)e^(-λ)/k!\n\n"
                "数学性质：\n"
                f"• E(X) = λ = {self.calculate_expectation():.2f}\n"
                f"• Var(X) = λ = {self.calculate_variance():.2f}\n\n"
                "实际应用：\n"
                "• 每小时电话数\n"
                "• 网站访问量\n"
                "• 放射性衰变\n"
                "• 交通事故数"
            )
            bg_color = '#F0FFF0'
        
        self.ax_info.text(0.05, 0.95, info_text, transform=self.ax_info.transAxes,
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.8,
                                 edgecolor='black', linewidth=1.5))
    
    def draw_question(self):
        """显示问题"""
        self.ax_question.clear()
        self.ax_question.axis('off')
        
        if self.game_mode == 'practice' and self.current_question:
            question_text = self.current_question
            
            if self.show_answer and self.question_answer is not None:
                question_text += f"\n\n💡 正确答案：{self.question_answer:.4f}"
            
            self.ax_question.text(0.05, 0.5, question_text, 
                                 transform=self.ax_question.transAxes,
                                 fontsize=11, verticalalignment='center',
                                 bbox=dict(boxstyle='round', facecolor='#FFFACD', 
                                         alpha=0.9, edgecolor='orange', linewidth=2))
        else:
            mode_text = {
                'learn': '📚 学习模式：调整参数滑块，观察分布变化',
                'practice': '✏️  练习模式：回答问题提升技能',
                'challenge': '⚔️  挑战模式：高难度题目测试'
            }
            self.ax_question.text(0.5, 0.5, mode_text.get(self.game_mode, ''),
                                 transform=self.ax_question.transAxes,
                                 ha='center', va='center', fontsize=12,
                                 bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.7))
    
    def draw_stats(self):
        """显示统计信息"""
        self.ax_stats.clear()
        self.ax_stats.axis('off')
        
        accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        
        stats_text = (
            f"📊 得分统计\n"
            f"得分：{self.score}/{self.total_questions}\n"
            f"正确率：{accuracy:.1f}%\n"
            f"连续答对：{self.correct_streak}题\n"
            f"经验值：{self.exp} XP\n"
            f"等级：Lv.{self.level}\n\n"
            f"⌨️  快捷键\n"
            f"'n' - 新问题\n"
            f"'s' - 显示答案\n"
            f"'q' - 快速模拟100次"
        )
        
        self.ax_stats.text(0.05, 0.95, stats_text, transform=self.ax_stats.transAxes,
                          fontsize=10, verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='#E0E0E0', alpha=0.8,
                                  edgecolor='gray', linewidth=1.5))
    
    def draw_achievements(self):
        """显示成就"""
        self.ax_achievements.clear()
        self.ax_achievements.axis('off')
        
        achievement_names = {
            'first_simulation': '🎯 首次模拟',
            'first_correct': '✅ 首次答对',
            'streak_5': '🔥 连续5题',
            'streak_10': '🏆 连续10题',
            'master_bernoulli': '⭐ 0-1分布大师',
            'master_binomial': '⭐ 二项分布大师',
            'master_poisson': '⭐ 泊松分布大师',
            'simulation_master': '🎖️ 模拟大师',
        }
        
        achievement_text = "🏅 成就系统："
        x_pos = 0.02
        spacing = 0.12
        
        for i, (key, name) in enumerate(achievement_names.items()):
            status = "✓" if self.achievements[key] else "○"
            color = 'green' if self.achievements[key] else 'gray'
            achievement_text = f"{status} {name}"
            
            self.ax_achievements.text(x_pos + i * spacing, 0.5, achievement_text,
                                     transform=self.ax_achievements.transAxes,
                                     fontsize=9, color=color, ha='left',
                                     bbox=dict(boxstyle='round', facecolor='white', 
                                             alpha=0.7 if self.achievements[key] else 0.3,
                                             edgecolor=color, linewidth=1))
    
    def on_key(self, event):
        """处理键盘事件"""
        if event.key == 'n':
            if self.game_mode == 'practice':
                self.generate_question()
                self.update_all_displays()
        elif event.key == 's':
            if self.game_mode == 'practice' and self.question_answer is not None:
                self.show_answer = True
                print(f"\n{'='*60}")
                print(f"💡 正确答案：{self.question_answer:.4f}")
                print(f"{'='*60}\n")
                self.update_all_displays()
        elif event.key == 'q':
            self.run_simulation(100)
            print(f"\n⚡ 已进行100次批量模拟！当前共{self.simulation_count}次模拟。\n")
        elif event.key == 'h':
            self.show_welcome_message()
        elif event.key.isdigit() and self.game_mode == 'practice':
            # 简单的答案输入（需要更完善的输入系统）
            print(f"\n提示：请输入完整答案后按回车（当前功能需完善）")
    
    def show(self):
        """显示窗口"""
        plt.show()

def main():
    """主函数"""
    print("\n" + "="*70)
    print("🎮 概率分布学习游戏 - 增强版")
    print("="*70)
    print("\n正在启动游戏...")
    print("="*70 + "\n")
    
    try:
        game = ProbabilityDistributionGameEnhanced()
        game.show()
    except Exception as e:
        print(f"\n✗ 运行程序时出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

