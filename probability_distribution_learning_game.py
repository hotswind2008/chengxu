"""
概率分布学习游戏 - 交互式教育游戏
帮助学生通过游戏化方式掌握0-1分布、二项分布、泊松分布
包含学习模式、练习模式、挑战模式和模拟实验
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import random
from datetime import datetime
import json
import math

# 设置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class ProbabilityDistributionGame:
    """概率分布学习游戏主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("概率分布学习游戏 - 0-1分布、二项分布、泊松分布")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#F5F5F5')
        
        # 游戏状态
        self.current_distribution = 'bernoulli'  # 'bernoulli', 'binomial', 'poisson'
        self.game_mode = 'learn'  # 'learn', 'practice', 'challenge', 'simulation'
        
        # 得分系统
        self.score = 0
        self.total_questions = 0
        self.correct_streak = 0
        self.max_streak = 0
        self.level = 1
        self.exp = 0
        
        # 成就系统
        self.achievements = {
            'first_correct': False,
            'streak_5': False,
            'streak_10': False,
            'master_bernoulli': False,
            'master_binomial': False,
            'master_poisson': False,
            'simulation_100': False,
            'perfect_score': False,
        }
        
        # 分布参数
        self.p_bernoulli = 0.5
        self.n_binomial = 10
        self.p_binomial = 0.5
        self.lambda_poisson = 3.0
        
        # 模拟数据
        self.simulation_results = []
        self.simulation_count = 0
        
        # 练习模式
        self.current_question = None
        self.user_answer = ""
        self.show_hint = False
        
        # 答题历史
        self.answer_history = []  # 存储每次答题的记录
        
        # 挑战模式
        self.challenge_time_left = 60
        self.challenge_questions = []
        self.challenge_current_q = 0
        self.challenge_timer = None
        self.challenge_score = 0
        
        # 创建界面
        self.create_widgets()
        
        # 强制更新窗口以确保所有控件都已创建
        self.root.update_idletasks()
        self.root.update()
        
        # 初始化显示图表
        self.update_all_displays()
        
        # 如果是练习模式，自动生成一道题目
        if self.game_mode == 'practice':
            self.root.after(300, lambda: self.generate_question())  # 延迟300ms确保界面完全创建
        
        # 绑定键盘快捷键
        self.root.bind('<Return>', lambda e: self.check_answer())
        self.root.bind('<Control-s>', lambda e: self.save_figure())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<F2>', lambda e: self.show_statistics())
        self.root.focus_set()  # 设置焦点以接收键盘事件
        
    def create_widgets(self):
        """创建GUI控件"""
        # 顶部工具栏
        toolbar_frame = tk.Frame(self.root, bg='#2C3E50', height=60)
        toolbar_frame.pack(fill=tk.X, padx=0, pady=0)
        toolbar_frame.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(toolbar_frame, text="📊 概率分布学习游戏", 
                              font=('Arial', 18, 'bold'), bg='#2C3E50', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # 模式选择
        mode_frame = tk.Frame(toolbar_frame, bg='#2C3E50')
        mode_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(mode_frame, text="模式:", font=('Arial', 10), bg='#2C3E50', fg='white').pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value='learn')
        modes = [('学习', 'learn'), ('练习', 'practice'), ('挑战', 'challenge'), ('模拟', 'simulation')]
        for text, value in modes:
            tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=value,
                          command=self.on_mode_change, font=('Arial', 10),
                          bg='#2C3E50', fg='white', selectcolor='#34495E',
                          activebackground='#34495E', activeforeground='white').pack(side=tk.LEFT, padx=5)
        
        # 分布选择
        dist_frame = tk.Frame(toolbar_frame, bg='#2C3E50')
        dist_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(dist_frame, text="分布:", font=('Arial', 10), bg='#2C3E50', fg='white').pack(side=tk.LEFT, padx=5)
        self.dist_var = tk.StringVar(value='bernoulli')
        distributions = [('0-1分布', 'bernoulli'), ('二项分布', 'binomial'), ('泊松分布', 'poisson')]
        for text, value in distributions:
            tk.Radiobutton(dist_frame, text=text, variable=self.dist_var, value=value,
                          command=self.on_distribution_change, font=('Arial', 10),
                          bg='#2C3E50', fg='white', selectcolor='#34495E',
                          activebackground='#34495E', activeforeground='white').pack(side=tk.LEFT, padx=5)
        
        # 得分显示
        self.score_label = tk.Label(toolbar_frame, text="得分: 0/0 | 连击: 0 | 等级: 1",
                                    font=('Arial', 11, 'bold'), bg='#2C3E50', fg='#3498DB')
        self.score_label.pack(side=tk.RIGHT, padx=20)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg='#F5F5F5')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：控制面板和参数设置
        left_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.config(width=350)
        
        # 参数控制区域
        self.create_parameter_controls(left_panel)
        
        # 中间：图表显示区域
        chart_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 创建matplotlib图表
        self.fig = Figure(figsize=(10, 8), facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 工具栏
        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()
        
        # 创建子图
        self.ax_dist = self.fig.add_subplot(2, 1, 1)
        self.ax_sim = self.fig.add_subplot(2, 1, 2)
        
        # 初始化时显示空图表提示
        self.ax_dist.text(0.5, 0.5, '选择分布类型开始学习', 
                         ha='center', va='center', fontsize=14, 
                         transform=self.ax_dist.transAxes, color='gray')
        self.ax_dist.set_title('概率分布图', fontsize=14, fontweight='bold')
        self.ax_sim.text(0.5, 0.5, '点击"运行模拟"开始模拟实验', 
                        ha='center', va='center', fontsize=14, 
                        transform=self.ax_sim.transAxes, color='gray')
        self.ax_sim.set_title('模拟实验结果', fontsize=12, fontweight='bold')
        
        # 确保图表初始可见
        self.fig.tight_layout()
        self.canvas.draw()
        self.canvas.flush_events()
        
        # 右侧：信息面板
        right_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_panel.config(width=400)
        
        # 理论说明
        theory_frame = tk.LabelFrame(right_panel, text="📚 理论说明", font=('Arial', 12, 'bold'),
                                    bg='white', fg='#2C3E50')
        theory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.theory_text = scrolledtext.ScrolledText(theory_frame, wrap=tk.WORD, 
                                                     font=('Arial', 10), bg='#FAFAFA',
                                                     relief=tk.FLAT, padx=10, pady=10)
        self.theory_text.pack(fill=tk.BOTH, expand=True)
        
        # 练习/挑战区域
        self.practice_frame = tk.LabelFrame(right_panel, text="🎯 练习", font=('Arial', 12, 'bold'),
                                           bg='white', fg='#2C3E50')
        self.practice_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.create_practice_widgets()
        
        # 成就显示
        achievement_frame = tk.LabelFrame(right_panel, text="🏆 成就", font=('Arial', 12, 'bold'),
                                         bg='white', fg='#2C3E50')
        achievement_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.achievement_text = tk.Text(achievement_frame, height=8, wrap=tk.WORD,
                                       font=('Arial', 9), bg='#FAFAFA', relief=tk.FLAT)
        self.achievement_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.achievement_text.config(state=tk.DISABLED)
        
    def create_parameter_controls(self, parent):
        """创建参数控制控件"""
        # 0-1分布参数
        bernoulli_frame = tk.LabelFrame(parent, text="0-1分布参数", font=('Arial', 11, 'bold'),
                                       bg='white', fg='#E74C3C')
        bernoulli_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(bernoulli_frame, text="概率 p:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10, pady=5)
        self.p_bernoulli_var = tk.DoubleVar(value=0.5)
        self.p_bernoulli_scale = tk.Scale(bernoulli_frame, from_=0.0, to=1.0, resolution=0.01,
                                          orient=tk.HORIZONTAL, variable=self.p_bernoulli_var,
                                          command=self.on_parameter_change, bg='white')
        self.p_bernoulli_scale.pack(fill=tk.X, padx=10, pady=5)
        self.p_bernoulli_label = tk.Label(bernoulli_frame, text="p = 0.50", font=('Arial', 10, 'bold'),
                                          bg='white', fg='#E74C3C')
        self.p_bernoulli_label.pack(pady=5)
        
        # 二项分布参数
        binomial_frame = tk.LabelFrame(parent, text="二项分布参数", font=('Arial', 11, 'bold'),
                                      bg='white', fg='#3498DB')
        binomial_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(binomial_frame, text="试验次数 n:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10, pady=5)
        self.n_binomial_var = tk.IntVar(value=10)
        self.n_binomial_scale = tk.Scale(binomial_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                         variable=self.n_binomial_var, command=self.on_parameter_change,
                                         bg='white')
        self.n_binomial_scale.pack(fill=tk.X, padx=10, pady=5)
        self.n_binomial_label = tk.Label(binomial_frame, text="n = 10", font=('Arial', 10, 'bold'),
                                         bg='white', fg='#3498DB')
        self.n_binomial_label.pack(pady=5)
        
        tk.Label(binomial_frame, text="成功概率 p:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10, pady=5)
        self.p_binomial_var = tk.DoubleVar(value=0.5)
        self.p_binomial_scale = tk.Scale(binomial_frame, from_=0.0, to=1.0, resolution=0.01,
                                        orient=tk.HORIZONTAL, variable=self.p_binomial_var,
                                        command=self.on_parameter_change, bg='white')
        self.p_binomial_scale.pack(fill=tk.X, padx=10, pady=5)
        self.p_binomial_label = tk.Label(binomial_frame, text="p = 0.50", font=('Arial', 10, 'bold'),
                                         bg='white', fg='#3498DB')
        self.p_binomial_label.pack(pady=5)
        
        # 泊松分布参数
        poisson_frame = tk.LabelFrame(parent, text="泊松分布参数", font=('Arial', 11, 'bold'),
                                     bg='white', fg='#9B59B6')
        poisson_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(poisson_frame, text="参数 λ:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10, pady=5)
        self.lambda_poisson_var = tk.DoubleVar(value=3.0)
        self.lambda_poisson_scale = tk.Scale(poisson_frame, from_=0.1, to=20.0, resolution=0.1,
                                            orient=tk.HORIZONTAL, variable=self.lambda_poisson_var,
                                            command=self.on_parameter_change, bg='white')
        self.lambda_poisson_scale.pack(fill=tk.X, padx=10, pady=5)
        self.lambda_poisson_label = tk.Label(poisson_frame, text="λ = 3.00", font=('Arial', 10, 'bold'),
                                             bg='white', fg='#9B59B6')
        self.lambda_poisson_label.pack(pady=5)
        
        # 操作按钮
        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="🎲 运行模拟", command=self.run_simulation,
                 font=('Arial', 11, 'bold'), bg='#2ECC71', fg='white',
                 relief=tk.RAISED, bd=3, padx=20, pady=10,
                 activebackground='#27AE60', activeforeground='white').pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="🔄 重置模拟", command=self.reset_simulation,
                 font=('Arial', 11), bg='#95A5A6', fg='white',
                 relief=tk.RAISED, bd=2, padx=20, pady=10,
                 activebackground='#7F8C8D', activeforeground='white').pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="💾 保存图表", command=self.save_figure,
                 font=('Arial', 11), bg='#3498DB', fg='white',
                 relief=tk.RAISED, bd=2, padx=20, pady=10,
                 activebackground='#2980B9', activeforeground='white').pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="📊 查看统计", command=self.show_statistics,
                 font=('Arial', 11), bg='#9B59B6', fg='white',
                 relief=tk.RAISED, bd=2, padx=20, pady=10,
                 activebackground='#8E44AD', activeforeground='white').pack(fill=tk.X, pady=5)
        
        tk.Button(button_frame, text="❓ 帮助", command=self.show_help,
                 font=('Arial', 11), bg='#95A5A6', fg='white',
                 relief=tk.RAISED, bd=2, padx=20, pady=10,
                 activebackground='#7F8C8D', activeforeground='white').pack(fill=tk.X, pady=5)
        
    def create_practice_widgets(self):
        """创建练习模式控件"""
        # 使用Text widget来显示题目，这样可以更好地显示长文本
        question_frame = tk.Frame(self.practice_frame, bg='white')
        question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(question_frame, text="题目:", font=('Arial', 10, 'bold'), bg='white').pack(anchor=tk.W, pady=(0, 5))
        
        self.question_text = tk.Text(question_frame, height=3, wrap=tk.WORD, 
                                     font=('Arial', 11), bg='#FAFAFA', 
                                     relief=tk.FLAT, padx=8, pady=8,
                                     fg='#2C3E50', state=tk.DISABLED)
        self.question_text.pack(fill=tk.BOTH, expand=True)
        
        # 兼容旧的question_label引用
        self.question_label = self.question_text
        
        answer_frame = tk.Frame(self.practice_frame, bg='white')
        answer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(answer_frame, text="答案:", font=('Arial', 10, 'bold'), bg='white').pack(side=tk.LEFT, padx=5)
        self.answer_entry = tk.Entry(answer_frame, font=('Arial', 12), width=15)
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        button_frame = tk.Frame(self.practice_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="✓ 提交答案", command=self.check_answer,
                 font=('Arial', 10, 'bold'), bg='#2ECC71', fg='white',
                 relief=tk.RAISED, bd=2, padx=15, pady=8,
                 activebackground='#27AE60').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="💡 提示", command=self.show_hint_answer,
                 font=('Arial', 10), bg='#F39C12', fg='white',
                 relief=tk.RAISED, bd=2, padx=15, pady=8,
                 activebackground='#E67E22').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(button_frame, text="➡️ 下一题", command=self.generate_question,
                 font=('Arial', 10), bg='#3498DB', fg='white',
                 relief=tk.RAISED, bd=2, padx=15, pady=8,
                 activebackground='#2980B9').pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.feedback_label = tk.Label(self.practice_frame, text="", font=('Arial', 10),
                                       bg='white', fg='#2C3E50')
        self.feedback_label.pack(pady=5)
        
        # 挑战模式计时器显示
        self.challenge_timer_label = tk.Label(self.practice_frame, text="", font=('Arial', 12, 'bold'),
                                             bg='white', fg='#E74C3C')
        self.challenge_timer_label.pack(pady=5)
        
    def on_mode_change(self):
        """模式切换"""
        # 如果从挑战模式切换出来，停止计时器
        if self.game_mode == 'challenge' and self.challenge_timer:
            self.root.after_cancel(self.challenge_timer)
            self.challenge_timer = None
            self.challenge_timer_label.config(text="")
            
        self.game_mode = self.mode_var.get()
        self.update_all_displays()
        if self.game_mode == 'practice':
            # 切换到练习模式时自动生成题目
            self.root.after(100, self.generate_question)  # 延迟确保界面更新完成
        elif self.game_mode == 'challenge':
            self.start_challenge()
        elif self.game_mode == 'simulation':
            # 模拟模式下重置一些显示
            if hasattr(self, 'question_text'):
                self.question_text.config(state=tk.NORMAL)
                self.question_text.delete(1.0, tk.END)
                self.question_text.insert(1.0, "模拟模式：运行模拟实验观察结果")
                self.question_text.config(state=tk.DISABLED, fg='#7F8C8D')
            elif hasattr(self, 'question_label'):
                self.question_label.config(text="模拟模式：运行模拟实验观察结果", fg='#7F8C8D')
            if hasattr(self, 'feedback_label'):
                self.feedback_label.config(text="")
        elif self.game_mode == 'learn':
            # 学习模式下清空题目
            if hasattr(self, 'question_text'):
                self.question_text.config(state=tk.NORMAL)
                self.question_text.delete(1.0, tk.END)
                self.question_text.insert(1.0, "学习模式：调整参数观察分布变化")
                self.question_text.config(state=tk.DISABLED, fg='#7F8C8D')
            elif hasattr(self, 'question_label'):
                self.question_label.config(text="学习模式：调整参数观察分布变化", fg='#7F8C8D')
            if hasattr(self, 'feedback_label'):
                self.feedback_label.config(text="")
            
    def on_distribution_change(self):
        """分布类型切换"""
        self.current_distribution = self.dist_var.get()
        self.update_all_displays()
        if self.game_mode == 'practice':
            self.generate_question()
            
    def on_parameter_change(self, value=None):
        """参数变化"""
        self.p_bernoulli = self.p_bernoulli_var.get()
        self.n_binomial = self.n_binomial_var.get()
        self.p_binomial = self.p_binomial_var.get()
        self.lambda_poisson = self.lambda_poisson_var.get()
        
        # 更新标签
        self.p_bernoulli_label.config(text=f"p = {self.p_bernoulli:.2f}")
        self.n_binomial_label.config(text=f"n = {self.n_binomial}")
        self.p_binomial_label.config(text=f"p = {self.p_binomial:.2f}")
        self.lambda_poisson_label.config(text=f"λ = {self.lambda_poisson:.2f}")
        
        self.update_all_displays()
        
    def update_all_displays(self):
        """更新所有显示"""
        self.draw_distribution()
        self.draw_simulation()
        self.update_theory_text()
        self.update_score_display()
        self.update_achievements()
        
    def draw_distribution(self):
        """绘制理论概率分布"""
        self.ax_dist.clear()
        
        if self.current_distribution == 'bernoulli':
            x = [0, 1]
            y = [1 - self.p_bernoulli, self.p_bernoulli]
            colors = ['#E74C3C', '#2ECC71']
            bars = self.ax_dist.bar(x, y, width=0.6, color=colors, edgecolor='black', linewidth=2, alpha=0.8)
            self.ax_dist.set_xlim(-0.5, 1.5)
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xticks([0, 1])
            self.ax_dist.set_xlabel('随机变量 X', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'0-1分布（伯努利分布）p = {self.p_bernoulli:.2f}', 
                                  fontsize=14, fontweight='bold', color='#E74C3C')
            
            for i, (xi, yi) in enumerate(zip(x, y)):
                self.ax_dist.text(xi, yi + max(y) * 0.05, f'{yi:.3f}', 
                                ha='center', va='bottom', fontsize=11, fontweight='bold')
            self.ax_dist.grid(True, alpha=0.3)
            
        elif self.current_distribution == 'binomial':
            n = self.n_binomial
            p = self.p_binomial
            x = np.arange(0, n + 1)
            # 计算二项分布概率：C(n,k) * p^k * (1-p)^(n-k)
            y = np.array([math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k)) for k in x])
            
            bars = self.ax_dist.bar(x, y, width=0.8, color='#3498DB', edgecolor='black', linewidth=1.5, alpha=0.7)
            self.ax_dist.set_xlim(-0.5, n + 0.5)
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xlabel('成功次数 k', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X=k)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'二项分布 B(n={n}, p={p:.2f})', 
                                  fontsize=14, fontweight='bold', color='#3498DB')
            
            # 标注最大值
            max_idx = np.argmax(y)
            self.ax_dist.plot([max_idx], [y[max_idx]], 'ro', markersize=10)
            self.ax_dist.text(max_idx, y[max_idx] + max(y) * 0.05, 
                            f'最大值: P({max_idx})={y[max_idx]:.3f}',
                            ha='center', va='bottom', fontsize=10, fontweight='bold', color='red')
            self.ax_dist.grid(True, alpha=0.3)
            
        elif self.current_distribution == 'poisson':
            lam = self.lambda_poisson
            x_max = max(15, int(lam * 3))
            x = np.arange(0, x_max + 1)
            # 计算泊松分布概率：λ^k * e^(-λ) / k!
            y = np.array([(lam ** k) * math.exp(-lam) / math.factorial(k) for k in x])
            
            bars = self.ax_dist.bar(x, y, width=0.8, color='#9B59B6', edgecolor='black', linewidth=1.5, alpha=0.7)
            self.ax_dist.set_xlim(-0.5, x_max + 0.5)
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xlabel('事件发生次数 k', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X=k)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'泊松分布 P(λ={lam:.2f})', 
                                  fontsize=14, fontweight='bold', color='#9B59B6')
            
            # 标注期望值
            self.ax_dist.axvline(lam, color='red', linestyle='--', linewidth=2, alpha=0.7)
            self.ax_dist.text(lam, max(y) * 0.9, f'E(X)=λ={lam:.2f}',
                            ha='center', va='bottom', fontsize=10, fontweight='bold', color='red')
            self.ax_dist.grid(True, alpha=0.3)
        
        # 确保图表正确显示
        try:
            self.fig.tight_layout()
            self.canvas.draw()
            # 强制刷新canvas显示
            self.canvas.get_tk_widget().update_idletasks()
            self.root.update_idletasks()
        except Exception as e:
            print(f"绘制分布图时出错: {e}")
            import traceback
            traceback.print_exc()
        
    def draw_simulation(self):
        """绘制模拟结果"""
        self.ax_sim.clear()
        
        if len(self.simulation_results) == 0:
            self.ax_sim.text(0.5, 0.5, '点击"运行模拟"开始模拟实验', 
                           ha='center', va='center', fontsize=14, 
                           transform=self.ax_sim.transAxes, color='gray')
            self.ax_sim.set_xlabel('')
            self.ax_sim.set_ylabel('')
            self.ax_sim.set_title('模拟实验结果', fontsize=12, fontweight='bold')
        else:
            if self.current_distribution == 'bernoulli':
                counts = [self.simulation_results.count(0), self.simulation_results.count(1)]
                x = [0, 1]
                bars = self.ax_sim.bar(x, counts, width=0.6, color=['#E74C3C', '#2ECC71'], 
                                      edgecolor='black', linewidth=2, alpha=0.7)
                self.ax_sim.set_xticks([0, 1])
                self.ax_sim.set_xlabel('结果', fontsize=11)
                self.ax_sim.set_ylabel('频数', fontsize=11)
                
                # 显示频率
                total = len(self.simulation_results)
                for i, (xi, count) in enumerate(zip(x, counts)):
                    freq = count / total
                    self.ax_sim.text(xi, count + total * 0.02, f'{count}\n({freq:.3f})',
                                   ha='center', va='bottom', fontsize=10, fontweight='bold')
                    
            elif self.current_distribution == 'binomial':
                max_val = max(self.simulation_results) if self.simulation_results else self.n_binomial
                bins = np.arange(-0.5, max_val + 1.5, 1)
                counts, _ = np.histogram(self.simulation_results, bins=bins)
                x = np.arange(0, len(counts))
                
                bars = self.ax_sim.bar(x, counts, width=0.8, color='#3498DB', 
                                      edgecolor='black', linewidth=1.5, alpha=0.7)
                self.ax_sim.set_xlabel('成功次数', fontsize=11)
                self.ax_sim.set_ylabel('频数', fontsize=11)
                
            elif self.current_distribution == 'poisson':
                max_val = max(self.simulation_results) if self.simulation_results else int(self.lambda_poisson * 3)
                bins = np.arange(-0.5, max_val + 1.5, 1)
                counts, _ = np.histogram(self.simulation_results, bins=bins)
                x = np.arange(0, len(counts))
                
                bars = self.ax_sim.bar(x, counts, width=0.8, color='#9B59B6', 
                                      edgecolor='black', linewidth=1.5, alpha=0.7)
                self.ax_sim.set_xlabel('事件发生次数', fontsize=11)
                self.ax_sim.set_ylabel('频数', fontsize=11)
            
            total = len(self.simulation_results)
            mean_val = np.mean(self.simulation_results)
            var_val = np.var(self.simulation_results)
            
            self.ax_sim.set_title(f'模拟结果 (n={total}) | 均值={mean_val:.3f} | 方差={var_val:.3f}', 
                                 fontsize=11, fontweight='bold')
            self.ax_sim.grid(True, alpha=0.3)
        
        try:
            self.fig.tight_layout()
            self.canvas.draw()
            # 强制刷新canvas显示
            self.canvas.get_tk_widget().update_idletasks()
            self.root.update_idletasks()
        except Exception as e:
            print(f"绘制模拟结果时出错: {e}")
            import traceback
            traceback.print_exc()
        
    def update_theory_text(self):
        """更新理论说明文本"""
        self.theory_text.config(state=tk.NORMAL)
        self.theory_text.delete(1.0, tk.END)
        
        if self.current_distribution == 'bernoulli':
            text = """
【0-1分布（伯努利分布）】

定义：
0-1分布是一次伯努利试验的结果，只有两种可能：成功（1）或失败（0）。

概率质量函数：
P(X=1) = p
P(X=0) = 1-p

其中 p 是成功概率，0 ≤ p ≤ 1。

数学期望：E(X) = p
方差：Var(X) = p(1-p)

应用场景：
• 抛硬币（正面或反面）
• 投篮（命中或未命中）
• 产品质量检验（合格或不合格）

特点：
• 最简单的离散分布
• 只有两个可能的取值
• 是二项分布的特殊情况（n=1）
"""
        elif self.current_distribution == 'binomial':
            text = """
【二项分布】

定义：
二项分布是n次独立伯努利试验中成功次数的分布。

概率质量函数：
P(X=k) = C(n,k) · p^k · (1-p)^(n-k)

其中：
• n：试验次数
• k：成功次数 (0 ≤ k ≤ n)
• p：每次试验成功概率
• C(n,k) = n!/(k!(n-k)!)：组合数

数学期望：E(X) = np
方差：Var(X) = np(1-p)

应用场景：
• 抛n次硬币，出现正面的次数
• 抽查n件产品，不合格品的数量
• n次射击的命中次数

特点：
• n次独立重复试验
• 每次试验结果只有两种可能
• 成功概率p保持不变
"""
        else:  # poisson
            text = """
【泊松分布】

定义：
泊松分布描述在固定时间或空间内，事件发生次数的概率分布。

概率质量函数：
P(X=k) = (λ^k · e^(-λ)) / k!

其中：
• λ（lambda）：单位时间内事件发生的平均次数
• k：事件发生的次数（k = 0, 1, 2, ...）
• e ≈ 2.71828：自然常数

数学期望：E(X) = λ
方差：Var(X) = λ
（泊松分布的期望和方差相等！）

应用场景：
• 单位时间内收到的邮件数量
• 单位面积内缺陷的数量
• 商店每小时接待的顾客数
• 放射性物质的衰变次数

特点：
• 是二项分布的极限情况（n→∞, p→0, np=λ）
• 适合描述稀有事件
• 期望和方差都等于λ
"""
        
        self.theory_text.insert(1.0, text.strip())
        self.theory_text.config(state=tk.DISABLED)
        
    def generate_question(self):
        """生成练习题目"""
        dist = self.current_distribution
        
        if dist == 'bernoulli':
            p = round(random.uniform(0.1, 0.9), 2)
            question_type = random.choice(['probability', 'expectation', 'variance'])
            
            if question_type == 'probability':
                k = random.choice([0, 1])
                answer = p if k == 1 else (1 - p)
                question = f"如果0-1分布的成功概率 p = {p}，求 P(X = {k})"
            elif question_type == 'expectation':
                answer = p
                question = f"如果0-1分布的成功概率 p = {p}，求数学期望 E(X)"
            else:  # variance
                answer = p * (1 - p)
                question = f"如果0-1分布的成功概率 p = {p}，求方差 Var(X)"
                
        elif dist == 'binomial':
            n = random.randint(5, 20)
            p = round(random.uniform(0.2, 0.8), 2)
            question_type = random.choice(['probability', 'expectation', 'variance', 'specific'])
            
            if question_type == 'probability':
                k = random.randint(0, min(5, n))
                answer = math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
                question = f"如果二项分布 B(n={n}, p={p})，求 P(X = {k})"
            elif question_type == 'expectation':
                answer = n * p
                question = f"如果二项分布 B(n={n}, p={p})，求数学期望 E(X)"
            elif question_type == 'variance':
                answer = n * p * (1 - p)
                question = f"如果二项分布 B(n={n}, p={p})，求方差 Var(X)"
            else:  # specific
                k = random.randint(0, min(3, n))
                answer = math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
                question = f"进行{n}次独立试验，每次成功概率为{p}，恰好成功{k}次的概率是多少？"
                
        else:  # poisson
            lam = round(random.uniform(1, 10), 1)
            question_type = random.choice(['probability', 'expectation', 'variance'])
            
            if question_type == 'probability':
                k = random.randint(0, min(10, int(lam * 2)))
                answer = (lam ** k) * math.exp(-lam) / math.factorial(k)
                question = f"如果泊松分布 P(λ={lam})，求 P(X = {k})"
            elif question_type == 'expectation':
                answer = lam
                question = f"如果泊松分布 P(λ={lam})，求数学期望 E(X)"
            else:  # variance
                answer = lam
                question = f"如果泊松分布 P(λ={lam})，求方差 Var(X)"
        
        self.current_question = {
            'question': question,
            'answer': answer,
            'type': question_type,
            'distribution': dist
        }
        
        # 更新题目标签 - 确保题目显示
        if hasattr(self, 'question_text'):
            try:
                self.question_text.config(state=tk.NORMAL)
                self.question_text.delete(1.0, tk.END)
                self.question_text.insert(1.0, question)
                self.question_text.config(state=tk.DISABLED, fg='#2C3E50')
                self.question_text.see(1.0)  # 滚动到顶部
                self.question_text.update_idletasks()
            except Exception as e:
                print(f"更新题目时出错: {e}")
        elif hasattr(self, 'question_label'):
            # 兼容旧的Label方式
            try:
                self.question_label.config(text=question, fg='#2C3E50', font=('Arial', 11))
                self.question_label.update_idletasks()
            except Exception as e:
                print(f"更新题目时出错: {e}")
        if hasattr(self, 'answer_entry'):
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus_set()  # 设置焦点到输入框
        if hasattr(self, 'feedback_label'):
            self.feedback_label.config(text="")
            self.show_hint = False
        
        # 强制刷新界面，确保题目显示
        self.root.update_idletasks()
        
    def check_answer(self):
        """检查答案"""
        if not self.current_question:
            messagebox.showwarning("提示", "请先生成题目！")
            return
            
        try:
            user_answer = float(self.answer_entry.get())
            correct_answer = self.current_question['answer']
            
            # 允许0.01的误差
            if abs(user_answer - correct_answer) < 0.01:
                self.score += 1
                self.correct_streak += 1
                if self.correct_streak > self.max_streak:
                    self.max_streak = self.correct_streak
                
                # 挑战模式特殊处理
                if self.game_mode == 'challenge':
                    self.challenge_score += 1
                    self.challenge_current_q += 1
                else:
                    self.total_questions += 1
                
                # 记录答题历史
                self.answer_history.append({
                    'correct': True,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'distribution': self.current_distribution,
                    'time': datetime.now()
                })
                    
                self.feedback_label.config(text=f"✓ 正确！答案是 {correct_answer:.4f}", 
                                         fg='#2ECC71', font=('Arial', 11, 'bold'))
                
                # 挑战模式下自动生成下一题
                if self.game_mode == 'challenge':
                    self.root.after(1000, self.generate_question)  # 1秒后自动下一题
                else:
                    # 检查成就
                    self.check_achievements()
                
            else:
                self.correct_streak = 0
                if self.game_mode == 'challenge':
                    self.challenge_current_q += 1
                else:
                    self.total_questions += 1
                
                # 记录答题历史
                self.answer_history.append({
                    'correct': False,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'distribution': self.current_distribution,
                    'time': datetime.now()
                })
                    
                self.feedback_label.config(text=f"✗ 错误！正确答案是 {correct_answer:.4f}", 
                                         fg='#E74C3C', font=('Arial', 11, 'bold'))
                
                # 挑战模式下自动生成下一题
                if self.game_mode == 'challenge':
                    self.root.after(1000, self.generate_question)  # 1秒后自动下一题
                
            self.update_score_display()
            
            # 更新等级和经验
            self.update_level()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
            
    def show_hint_answer(self):
        """显示提示"""
        if not self.current_question:
            messagebox.showwarning("提示", "请先生成题目！")
            return
            
        dist = self.current_question['distribution']
        q_type = self.current_question['type']
        
        if dist == 'bernoulli':
            hint = "0-1分布：E(X)=p, Var(X)=p(1-p)"
        elif dist == 'binomial':
            hint = "二项分布：E(X)=np, Var(X)=np(1-p), P(X=k)=C(n,k)·p^k·(1-p)^(n-k)"
        else:
            hint = "泊松分布：E(X)=λ, Var(X)=λ, P(X=k)=λ^k·e^(-λ)/k!"
            
        self.feedback_label.config(text=f"💡 提示：{hint}", fg='#F39C12')
        self.show_hint = True
        
    def start_challenge(self):
        """开始挑战模式"""
        self.challenge_time_left = 60
        self.challenge_questions = []
        self.challenge_current_q = 0
        self.challenge_score = 0
        self.generate_question()
        self.update_challenge_timer()
        messagebox.showinfo("挑战模式", "你有一分钟时间答题！尽可能多地答对题目！\n时间到后会自动结束。")
        
    def update_challenge_timer(self):
        """更新挑战模式计时器"""
        if self.game_mode == 'challenge' and self.challenge_time_left > 0:
            self.challenge_timer_label.config(text=f"⏰ 剩余时间: {self.challenge_time_left}秒")
            self.challenge_time_left -= 1
            self.challenge_timer = self.root.after(1000, self.update_challenge_timer)
        elif self.game_mode == 'challenge' and self.challenge_time_left == 0:
            self.end_challenge()
            
    def end_challenge(self):
        """结束挑战模式"""
        if self.challenge_timer:
            self.root.after_cancel(self.challenge_timer)
            self.challenge_timer = None
            
        accuracy = (self.challenge_score / self.challenge_current_q * 100) if self.challenge_current_q > 0 else 0
        messagebox.showinfo("挑战结束", 
                          f"挑战模式结束！\n\n"
                          f"答对题目: {self.challenge_score}/{self.challenge_current_q}\n"
                          f"正确率: {accuracy:.1f}%\n\n"
                          f"太棒了！继续努力！")
        self.challenge_timer_label.config(text="")
        self.game_mode = 'practice'
        self.mode_var.set('practice')
        
    def run_simulation(self):
        """运行模拟实验"""
        count = 100  # 每次模拟100次
        
        if self.current_distribution == 'bernoulli':
            for _ in range(count):
                result = 1 if random.random() < self.p_bernoulli else 0
                self.simulation_results.append(result)
        elif self.current_distribution == 'binomial':
            for _ in range(count):
                result = sum(1 for _ in range(self.n_binomial) if random.random() < self.p_binomial)
                self.simulation_results.append(result)
        else:  # poisson
            for _ in range(count):
                result = np.random.poisson(self.lambda_poisson)
                self.simulation_results.append(result)
        
        self.simulation_count += count
        self.draw_simulation()
        
        # 检查成就
        if self.simulation_count >= 100 and not self.achievements['simulation_100']:
            self.achievements['simulation_100'] = True
            messagebox.showinfo("成就解锁", "🏆 完成100次模拟！")
            self.update_achievements()
            
    def reset_simulation(self):
        """重置模拟"""
        self.simulation_results = []
        self.simulation_count = 0
        self.draw_simulation()
        
    def save_figure(self):
        """保存图表"""
        filename = f"probability_distribution_{self.current_distribution}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.fig.savefig(filename, dpi=300, bbox_inches='tight')
        messagebox.showinfo("保存成功", f"图表已保存为：{filename}")
        
    def update_score_display(self):
        """更新得分显示"""
        if self.game_mode == 'challenge':
            accuracy = (self.challenge_score / self.challenge_current_q * 100) if self.challenge_current_q > 0 else 0
            score_text = f"挑战得分: {self.challenge_score}/{self.challenge_current_q} | 正确率: {accuracy:.1f}%"
        else:
            accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
            score_text = f"得分: {self.score}/{self.total_questions} | 正确率: {accuracy:.1f}%"
            
        self.score_label.config(
            text=f"{score_text} | 连击: {self.correct_streak} (最高: {self.max_streak}) | 等级: {self.level} | 经验: {self.exp}"
        )
        
    def update_level(self):
        """更新等级"""
        # 根据经验值计算等级（每答对1题获得10经验，连续答对额外奖励）
        old_level = self.level
        new_exp = self.score * 10 + self.correct_streak * 5
        self.exp = new_exp
        self.level = min(50, 1 + new_exp // 100)  # 最高50级
        
        if self.level > old_level:
            messagebox.showinfo("等级提升", f"🎉 恭喜！你升级到 {self.level} 级！\n继续努力！")
        
    def check_achievements(self):
        """检查成就"""
        if not self.achievements['first_correct']:
            self.achievements['first_correct'] = True
            messagebox.showinfo("成就解锁", "🎉 首次答对！")
            
        if self.correct_streak >= 5 and not self.achievements['streak_5']:
            self.achievements['streak_5'] = True
            messagebox.showinfo("成就解锁", "🔥 连续答对5题！")
            
        if self.correct_streak >= 10 and not self.achievements['streak_10']:
            self.achievements['streak_10'] = True
            messagebox.showinfo("成就解锁", "💪 连续答对10题！")
            
        if self.total_questions >= 10 and self.score == self.total_questions and not self.achievements['perfect_score']:
            self.achievements['perfect_score'] = True
            messagebox.showinfo("成就解锁", "⭐ 完美得分！")
            
        self.update_achievements()
        
    def update_achievements(self):
        """更新成就显示"""
        self.achievement_text.config(state=tk.NORMAL)
        self.achievement_text.delete(1.0, tk.END)
        
        achievement_list = []
        if self.achievements['first_correct']:
            achievement_list.append("✅ 首次答对")
        if self.achievements['streak_5']:
            achievement_list.append("🔥 连续答对5题")
        if self.achievements['streak_10']:
            achievement_list.append("💪 连续答对10题")
        if self.achievements['simulation_100']:
            achievement_list.append("🎲 完成100次模拟")
        if self.achievements['perfect_score']:
            achievement_list.append("⭐ 完美得分")
            
        if achievement_list:
            self.achievement_text.insert(1.0, "\n".join(achievement_list))
        else:
            self.achievement_text.insert(1.0, "还没有解锁成就，继续努力！")
            
        self.achievement_text.config(state=tk.DISABLED)
        
    def show_statistics(self):
        """显示统计信息窗口"""
        if len(self.answer_history) == 0:
            messagebox.showinfo("统计", "还没有答题记录，先去练习吧！")
            return
            
        # 创建统计窗口
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 答题统计")
        stats_window.geometry("800x600")
        stats_window.configure(bg='white')
        
        # 创建图表
        fig = Figure(figsize=(8, 6), facecolor='white')
        canvas = FigureCanvasTkAgg(fig, stats_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 计算统计数据
        total = len(self.answer_history)
        correct = sum(1 for h in self.answer_history if h['correct'])
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # 按分布统计
        dist_stats = {}
        for h in self.answer_history:
            dist = h['distribution']
            if dist not in dist_stats:
                dist_stats[dist] = {'total': 0, 'correct': 0}
            dist_stats[dist]['total'] += 1
            if h['correct']:
                dist_stats[dist]['correct'] += 1
        
        # 绘制图表
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)
        
        # 1. 总体准确率饼图
        colors_pie = ['#2ECC71', '#E74C3C']
        ax1.pie([correct, total - correct], labels=['正确', '错误'], 
               autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax1.set_title(f'总体准确率: {accuracy:.1f}%', fontsize=12, fontweight='bold')
        
        # 2. 按分布类型的准确率
        if dist_stats:
            dist_names = {'bernoulli': '0-1分布', 'binomial': '二项分布', 'poisson': '泊松分布'}
            dists = list(dist_stats.keys())
            accuracies = [dist_stats[d]['correct'] / dist_stats[d]['total'] * 100 
                         for d in dists]
            dist_labels = [dist_names.get(d, d) for d in dists]
            
            bars = ax2.bar(dist_labels, accuracies, color=['#E74C3C', '#3498DB', '#9B59B6'][:len(dists)])
            ax2.set_ylabel('准确率 (%)', fontsize=10)
            ax2.set_title('各分布类型准确率', fontsize=12, fontweight='bold')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # 在柱状图上显示数值
            for i, (bar, acc) in enumerate(zip(bars, accuracies)):
                ax2.text(bar.get_x() + bar.get_width()/2, acc + 2, 
                        f'{acc:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 3. 最近10题的答题情况
        recent = self.answer_history[-10:] if len(self.answer_history) >= 10 else self.answer_history
        x_pos = np.arange(len(recent))
        results = [1 if h['correct'] else 0 for h in recent]
        colors_bar = ['#2ECC71' if r == 1 else '#E74C3C' for r in results]
        
        ax3.bar(x_pos, results, color=colors_bar, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('题目序号', fontsize=10)
        ax3.set_ylabel('结果 (1=正确, 0=错误)', fontsize=10)
        ax3.set_title('最近10题答题情况', fontsize=12, fontweight='bold')
        ax3.set_ylim(-0.1, 1.1)
        ax3.set_yticks([0, 1])
        ax3.set_yticklabels(['错误', '正确'])
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 文本统计信息
        ax4.axis('off')
        stats_text = f"""
📈 答题统计报告

总答题数: {total}
答对题数: {correct}
答错题数: {total - correct}
总体准确率: {accuracy:.1f}%

各分布答题情况:
"""
        for dist, stats_info in dist_stats.items():
            dist_name = {'bernoulli': '0-1分布', 'binomial': '二项分布', 'poisson': '泊松分布'}.get(dist, dist)
            dist_acc = stats_info['correct'] / stats_info['total'] * 100
            stats_text += f"  {dist_name}: {stats_info['correct']}/{stats_info['total']} ({dist_acc:.1f}%)\n"
        
        stats_text += f"\n当前等级: {self.level}\n"
        stats_text += f"最高连击: {self.max_streak}\n"
        stats_text += f"经验值: {self.exp}"
        
        ax4.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                 family='monospace', transform=ax4.transAxes)
        
        fig.tight_layout()
        canvas.draw()
        
    def show_help(self):
        """显示帮助信息"""
        help_text = """
📚 概率分布学习游戏 - 使用帮助

【四种模式】
1. 学习模式：调整参数，观察分布变化，学习理论知识
2. 练习模式：自动生成题目，练习计算概率、期望、方差
3. 挑战模式：60秒限时答题，尽可能多地答对题目
4. 模拟模式：运行模拟实验，对比理论分布与实际结果

【三种分布】
• 0-1分布（伯努利分布）：最简单的二值分布
• 二项分布：n次独立试验中成功次数的分布
• 泊松分布：描述稀有事件发生次数的分布

【快捷键】
• Enter: 提交答案
• Ctrl+S: 保存当前图表
• F1: 显示帮助
• F2: 查看统计

【操作提示】
• 使用滑块调整分布参数，图表会实时更新
• 点击"运行模拟"进行实验，观察实际结果
• 在练习模式下，输入答案后按Enter提交
• 答对题目可以获得经验值，升级时会有提示
• 连续答对可以获得连击奖励

【成就系统】
完成特定任务可以解锁成就，包括：
• 首次答对
• 连续答对5题/10题
• 完成100次模拟
• 完美得分等

【技巧】
• 理解理论公式：期望、方差、概率计算公式
• 多做模拟：通过模拟实验加深理解
• 观察分布形状：不同参数下的分布特点
• 记住常见结论：如泊松分布的期望=方差=λ

祝学习愉快！🎉
"""
        messagebox.showinfo("帮助", help_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = ProbabilityDistributionGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

