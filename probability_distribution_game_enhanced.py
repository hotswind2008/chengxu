"""
概率分布学习游戏 - 增强版
帮助学生通过游戏化方式掌握0-1分布、二项分布、泊松分布
包含交互式学习、挑战模式、可视化对比等功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import random
from fractions import Fraction
import threading
import time

# 设置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False


class ProbabilityDistributionGame:
    """概率分布学习游戏类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("概率分布学习游戏 - 0-1分布、二项分布、泊松分布")
        self.root.geometry("1400x900")
        self.root.configure(bg='#F0F8FF')
        
        # 游戏状态
        self.distribution_type = 'bernoulli'  # 'bernoulli', 'binomial', 'poisson'
        self.game_mode = 'learn'  # 'learn' 学习模式, 'challenge' 挑战模式
        
        # 得分系统
        self.score = 0
        self.total_questions = 0
        self.correct_streak = 0
        self.max_streak = 0
        
        # 分布参数
        self.p_bernoulli = 0.5
        self.n_binomial = 10
        self.p_binomial = 0.5
        self.lambda_poisson = 3.0
        
        # 模拟数据
        self.simulation_results = []
        self.simulation_count = 0
        
        # 挑战模式问题
        self.current_question = None
        self.question_answer = None
        self.question_type = None
        
        # 创建界面
        self.create_widgets()
        self.create_figures()
        self.update_display()
        self.generate_challenge_question()
        
    def create_widgets(self):
        """创建GUI控件"""
        # 顶部控制面板
        control_frame = tk.Frame(self.root, bg='#E6F3FF', height=100)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 分布类型选择
        dist_label = tk.Label(control_frame, text="选择分布:", font=('Arial', 12, 'bold'), bg='#E6F3FF')
        dist_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.dist_var = tk.StringVar(value='bernoulli')
        tk.Radiobutton(control_frame, text="0-1分布", variable=self.dist_var, 
                      value='bernoulli', command=self.on_distribution_change,
                      font=('Arial', 11), bg='#E6F3FF').grid(row=0, column=1, padx=5)
        tk.Radiobutton(control_frame, text="二项分布", variable=self.dist_var, 
                      value='binomial', command=self.on_distribution_change,
                      font=('Arial', 11), bg='#E6F3FF').grid(row=0, column=2, padx=5)
        tk.Radiobutton(control_frame, text="泊松分布", variable=self.dist_var, 
                      value='poisson', command=self.on_distribution_change,
                      font=('Arial', 11), bg='#E6F3FF').grid(row=0, column=3, padx=5)
        
        # 模式选择
        mode_label = tk.Label(control_frame, text="游戏模式:", font=('Arial', 12, 'bold'), bg='#E6F3FF')
        mode_label.grid(row=0, column=4, padx=10)
        
        self.mode_var = tk.StringVar(value='learn')
        tk.Radiobutton(control_frame, text="学习模式", variable=self.mode_var, 
                      value='learn', command=self.on_mode_change,
                      font=('Arial', 11), bg='#E6F3FF').grid(row=0, column=5, padx=5)
        tk.Radiobutton(control_frame, text="挑战模式", variable=self.mode_var, 
                      value='challenge', command=self.on_mode_change,
                      font=('Arial', 11), bg='#E6F3FF').grid(row=0, column=6, padx=5)
        
        # 参数控制框架
        param_frame = tk.Frame(control_frame, bg='#E6F3FF')
        param_frame.grid(row=1, column=0, columnspan=7, pady=5)
        
        # 0-1分布参数
        self.bernoulli_frame = tk.Frame(param_frame, bg='#E6F3FF')
        self.bernoulli_frame.grid(row=0, column=0, padx=10)
        tk.Label(self.bernoulli_frame, text="概率 p:", font=('Arial', 10), bg='#E6F3FF').pack(side=tk.LEFT)
        self.p_bernoulli_var = tk.DoubleVar(value=0.5)
        self.p_bernoulli_scale = tk.Scale(self.bernoulli_frame, from_=0.01, to=0.99, 
                                         resolution=0.01, orient=tk.HORIZONTAL,
                                         variable=self.p_bernoulli_var, length=200,
                                         command=self.on_parameter_change)
        self.p_bernoulli_scale.pack(side=tk.LEFT, padx=5)
        self.p_bernoulli_label = tk.Label(self.bernoulli_frame, text="0.50", 
                                         font=('Arial', 10, 'bold'), bg='#E6F3FF', width=5)
        self.p_bernoulli_label.pack(side=tk.LEFT)
        
        # 二项分布参数
        self.binomial_frame = tk.Frame(param_frame, bg='#E6F3FF')
        tk.Label(self.binomial_frame, text="试验次数 n:", font=('Arial', 10), bg='#E6F3FF').pack(side=tk.LEFT)
        self.n_binomial_var = tk.IntVar(value=10)
        self.n_binomial_scale = tk.Scale(self.binomial_frame, from_=1, to=50, 
                                        orient=tk.HORIZONTAL,
                                        variable=self.n_binomial_var, length=150,
                                        command=self.on_parameter_change)
        self.n_binomial_scale.pack(side=tk.LEFT, padx=5)
        self.n_binomial_label = tk.Label(self.binomial_frame, text="10", 
                                        font=('Arial', 10, 'bold'), bg='#E6F3FF', width=5)
        self.n_binomial_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.binomial_frame, text="成功概率 p:", font=('Arial', 10), bg='#E6F3FF').pack(side=tk.LEFT)
        self.p_binomial_var = tk.DoubleVar(value=0.5)
        self.p_binomial_scale = tk.Scale(self.binomial_frame, from_=0.01, to=0.99, 
                                       resolution=0.01, orient=tk.HORIZONTAL,
                                       variable=self.p_binomial_var, length=200,
                                       command=self.on_parameter_change)
        self.p_binomial_scale.pack(side=tk.LEFT, padx=5)
        self.p_binomial_label = tk.Label(self.binomial_frame, text="0.50", 
                                        font=('Arial', 10, 'bold'), bg='#E6F3FF', width=5)
        self.p_binomial_label.pack(side=tk.LEFT)
        
        # 泊松分布参数
        self.poisson_frame = tk.Frame(param_frame, bg='#E6F3FF')
        tk.Label(self.poisson_frame, text="参数 λ:", font=('Arial', 10), bg='#E6F3FF').pack(side=tk.LEFT)
        self.lambda_poisson_var = tk.DoubleVar(value=3.0)
        self.lambda_poisson_scale = tk.Scale(self.poisson_frame, from_=0.1, to=10.0, 
                                           resolution=0.1, orient=tk.HORIZONTAL,
                                           variable=self.lambda_poisson_var, length=200,
                                           command=self.on_parameter_change)
        self.lambda_poisson_scale.pack(side=tk.LEFT, padx=5)
        self.lambda_poisson_label = tk.Label(self.poisson_frame, text="3.00", 
                                            font=('Arial', 10, 'bold'), bg='#E6F3FF', width=5)
        self.lambda_poisson_label.pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = tk.Frame(control_frame, bg='#E6F3FF')
        button_frame.grid(row=2, column=0, columnspan=7, pady=5)
        
        tk.Button(button_frame, text="模拟1次", command=self.simulate_once,
                 bg='#FFB6C1', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="模拟100次", command=self.simulate_batch,
                 bg='#90EE90', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="模拟1000次", command=lambda: self.simulate_batch(1000),
                 bg='#87CEEB', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="重置模拟", command=self.reset_simulation,
                 bg='#D3D3D3', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="新问题", command=self.generate_challenge_question,
                 bg='#FFD700', font=('Arial', 10, 'bold'), width=12).pack(side=tk.LEFT, padx=5)
        
        # 更新参数面板显示
        self.update_parameter_panel()
        
    def create_figures(self):
        """创建matplotlib图形"""
        # 主图形框架
        main_frame = tk.Frame(self.root, bg='#F0F8FF')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧：分布图
        left_frame = tk.Frame(main_frame, bg='#F0F8FF')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.fig_dist = Figure(figsize=(7, 5), facecolor='white')
        self.ax_dist = self.fig_dist.add_subplot(111)
        self.canvas_dist = FigureCanvasTkAgg(self.fig_dist, left_frame)
        self.canvas_dist.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 右侧：信息面板
        right_frame = tk.Frame(main_frame, bg='#F0F8FF', width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_frame.pack_propagate(False)
        
        # 模拟结果图
        self.fig_sim = Figure(figsize=(4, 3), facecolor='white')
        self.ax_sim = self.fig_sim.add_subplot(111)
        self.canvas_sim = FigureCanvasTkAgg(self.fig_sim, right_frame)
        self.canvas_sim.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 信息文本区域
        info_frame = tk.Frame(right_frame, bg='#FFFACD', relief=tk.RAISED, borderwidth=2)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.info_text = tk.Text(info_frame, font=('Arial', 10), wrap=tk.WORD, 
                                bg='#FFFACD', padx=10, pady=10)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 挑战模式问题面板
        challenge_frame = tk.Frame(right_frame, bg='#FFE4E1', relief=tk.RAISED, borderwidth=2)
        challenge_frame.pack(fill=tk.BOTH, pady=5)
        
        tk.Label(challenge_frame, text="挑战问题", font=('Arial', 12, 'bold'), 
                bg='#FFE4E1').pack(pady=5)
        
        self.question_label = tk.Label(challenge_frame, text="", font=('Arial', 10),
                                      bg='#FFE4E1', wraplength=350, justify=tk.LEFT)
        self.question_label.pack(padx=10, pady=5)
        
        answer_frame = tk.Frame(challenge_frame, bg='#FFE4E1')
        answer_frame.pack(pady=5)
        
        tk.Label(answer_frame, text="答案:", font=('Arial', 10, 'bold'), bg='#FFE4E1').pack(side=tk.LEFT, padx=5)
        self.answer_entry = tk.Entry(answer_frame, font=('Arial', 11), width=15)
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        self.answer_entry.bind('<Return>', lambda e: self.check_answer())
        
        tk.Button(answer_frame, text="提交", command=self.check_answer,
                 bg='#32CD32', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        tk.Button(answer_frame, text="提示", command=self.show_hint,
                 bg='#FFA500', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # 得分面板
        score_frame = tk.Frame(right_frame, bg='#E0E0E0', relief=tk.RAISED, borderwidth=2)
        score_frame.pack(fill=tk.X, pady=5)
        
        self.score_label = tk.Label(score_frame, text="得分: 0/0 | 正确率: 0% | 连击: 0", 
                                    font=('Arial', 11, 'bold'), bg='#E0E0E0')
        self.score_label.pack(pady=10)
        
    def on_distribution_change(self):
        """分布类型改变时的回调"""
        self.distribution_type = self.dist_var.get()
        self.reset_simulation()
        self.update_parameter_panel()
        self.update_display()
        self.generate_challenge_question()
        
    def on_mode_change(self):
        """游戏模式改变时的回调"""
        self.game_mode = self.mode_var.get()
        self.update_display()
        
    def on_parameter_change(self, *args):
        """参数改变时的回调"""
        self.p_bernoulli = self.p_bernoulli_var.get()
        self.n_binomial = self.n_binomial_var.get()
        self.p_binomial = self.p_binomial_var.get()
        self.lambda_poisson = self.lambda_poisson_var.get()
        
        # 更新标签显示
        self.p_bernoulli_label.config(text=f"{self.p_bernoulli:.2f}")
        self.n_binomial_label.config(text=f"{self.n_binomial}")
        self.p_binomial_label.config(text=f"{self.p_binomial:.2f}")
        self.lambda_poisson_label.config(text=f"{self.lambda_poisson:.2f}")
        
        self.update_display()
        
    def update_parameter_panel(self):
        """更新参数面板显示"""
        # 隐藏所有参数面板
        self.bernoulli_frame.grid_remove()
        self.binomial_frame.grid_remove()
        self.poisson_frame.grid_remove()
        
        # 显示对应的参数面板
        if self.distribution_type == 'bernoulli':
            self.bernoulli_frame.grid(row=0, column=0, padx=10)
        elif self.distribution_type == 'binomial':
            self.binomial_frame.grid(row=0, column=0, padx=10)
        elif self.distribution_type == 'poisson':
            self.poisson_frame.grid(row=0, column=0, padx=10)
            
    def calculate_probability(self, k):
        """计算概率值"""
        if self.distribution_type == 'bernoulli':
            if k == 0:
                return 1 - self.p_bernoulli
            elif k == 1:
                return self.p_bernoulli
            else:
                return 0
                
        elif self.distribution_type == 'binomial':
            if k < 0 or k > self.n_binomial:
                return 0
            # 手动计算组合数 C(n,k) = n! / (k! * (n-k)!)
            # 使用累积计算避免大数问题
            if k > self.n_binomial - k:
                k = self.n_binomial - k  # 利用对称性
            
            comb = 1.0
            for i in range(k):
                comb *= (self.n_binomial - i) / (i + 1)
            
            return comb * (self.p_binomial ** k) * ((1 - self.p_binomial) ** (self.n_binomial - k))
            
        elif self.distribution_type == 'poisson':
            if k < 0:
                return 0
            return (self.lambda_poisson ** k) * np.exp(-self.lambda_poisson) / np.math.factorial(k)
            
        return 0
        
    def calculate_mean(self):
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
        
    def simulate_once(self):
        """单次模拟"""
        if self.distribution_type == 'bernoulli':
            result = 1 if random.random() < self.p_bernoulli else 0
        elif self.distribution_type == 'binomial':
            result = sum(1 for _ in range(self.n_binomial) if random.random() < self.p_binomial)
        elif self.distribution_type == 'poisson':
            result = np.random.poisson(self.lambda_poisson)
        
        self.simulation_results.append(result)
        self.simulation_count += 1
        self.update_display()
        
    def simulate_batch(self, n=100):
        """批量模拟"""
        def run_simulation():
            for _ in range(n):
                if self.distribution_type == 'bernoulli':
                    result = 1 if random.random() < self.p_bernoulli else 0
                elif self.distribution_type == 'binomial':
                    result = sum(1 for _ in range(self.n_binomial) if random.random() < self.p_binomial)
                elif self.distribution_type == 'poisson':
                    result = np.random.poisson(self.lambda_poisson)
                self.simulation_results.append(result)
            
            self.simulation_count += len(self.simulation_results)
            self.root.after(0, self.update_display)
        
        # 在后台线程运行，避免界面卡顿
        thread = threading.Thread(target=run_simulation)
        thread.daemon = True
        thread.start()
        
    def reset_simulation(self):
        """重置模拟结果"""
        self.simulation_results = []
        self.simulation_count = 0
        self.update_display()
        
    def generate_challenge_question(self):
        """生成挑战问题"""
        if self.distribution_type == 'bernoulli':
            k = random.choice([0, 1])
            self.question_answer = self.calculate_probability(k)
            self.question_type = 'probability'
            self.current_question = (
                f"【0-1分布问题】\n\n"
                f"假设成功的概率为 p = {self.p_bernoulli:.2f}，\n"
                f"请问 X = {k} 的概率是多少？\n"
                f"（输入0到1之间的小数，保留4位小数）"
            )
            
        elif self.distribution_type == 'binomial':
            question_types = ['probability', 'mean', 'variance']
            qtype = random.choice(question_types)
            
            if qtype == 'probability':
                k = random.randint(0, min(self.n_binomial, 10))
                self.question_answer = self.calculate_probability(k)
                self.current_question = (
                    f"【二项分布问题】\n\n"
                    f"进行 n = {self.n_binomial} 次独立试验，\n"
                    f"每次成功的概率为 p = {self.p_binomial:.2f}，\n"
                    f"请问恰好成功 {k} 次的概率是多少？\n"
                    f"（输入0到1之间的小数，保留4位小数）"
                )
            elif qtype == 'mean':
                self.question_answer = self.calculate_mean()
                self.current_question = (
                    f"【二项分布问题】\n\n"
                    f"进行 n = {self.n_binomial} 次独立试验，\n"
                    f"每次成功的概率为 p = {self.p_binomial:.2f}，\n"
                    f"请问期望值（均值）是多少？\n"
                    f"（输入数值，保留2位小数）"
                )
            elif qtype == 'variance':
                self.question_answer = self.calculate_variance()
                self.current_question = (
                    f"【二项分布问题】\n\n"
                    f"进行 n = {self.n_binomial} 次独立试验，\n"
                    f"每次成功的概率为 p = {self.p_binomial:.2f}，\n"
                    f"请问方差是多少？\n"
                    f"（输入数值，保留2位小数）"
                )
            self.question_type = qtype
            
        elif self.distribution_type == 'poisson':
            question_types = ['probability', 'mean', 'variance']
            qtype = random.choice(question_types)
            
            if qtype == 'probability':
                k = random.randint(0, min(int(self.lambda_poisson * 3), 15))
                self.question_answer = self.calculate_probability(k)
                self.current_question = (
                    f"【泊松分布问题】\n\n"
                    f"参数 λ = {self.lambda_poisson:.2f}，\n"
                    f"请问 X = {k} 的概率是多少？\n"
                    f"（输入0到1之间的小数，保留4位小数）"
                )
            elif qtype == 'mean':
                self.question_answer = self.calculate_mean()
                self.current_question = (
                    f"【泊松分布问题】\n\n"
                    f"参数 λ = {self.lambda_poisson:.2f}，\n"
                    f"请问期望值（均值）是多少？\n"
                    f"（输入数值，保留2位小数）"
                )
            elif qtype == 'variance':
                self.question_answer = self.calculate_variance()
                self.current_question = (
                    f"【泊松分布问题】\n\n"
                    f"参数 λ = {self.lambda_poisson:.2f}，\n"
                    f"请问方差是多少？\n"
                    f"（输入数值，保留2位小数）"
                )
            self.question_type = qtype
        
        self.question_label.config(text=self.current_question)
        self.answer_entry.delete(0, tk.END)
        
    def check_answer(self):
        """检查答案"""
        try:
            user_answer = float(self.answer_entry.get())
            tolerance = 0.01 if self.question_type == 'probability' else 0.1
            
            if abs(user_answer - self.question_answer) < tolerance:
                self.score += 1
                self.correct_streak += 1
                if self.correct_streak > self.max_streak:
                    self.max_streak = self.correct_streak
                self.total_questions += 1
                messagebox.showinfo("正确！", f"答案正确！\n正确答案：{self.question_answer:.4f}")
                self.generate_challenge_question()
            else:
                self.correct_streak = 0
                self.total_questions += 1
                messagebox.showerror("错误", f"答案错误！\n正确答案：{self.question_answer:.4f}\n你的答案：{user_answer:.4f}")
                self.generate_challenge_question()
                
            self.update_score_display()
            
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")
            
    def show_hint(self):
        """显示提示"""
        if self.distribution_type == 'bernoulli':
            hint = (
                "提示：\n"
                "0-1分布只有两个可能值：0和1\n"
                f"P(X=0) = 1 - p = {1-self.p_bernoulli:.2f}\n"
                f"P(X=1) = p = {self.p_bernoulli:.2f}"
            )
        elif self.distribution_type == 'binomial':
            if self.question_type == 'probability':
                hint = (
                    "提示：\n"
                    "二项分布概率公式：\n"
                    "P(X=k) = C(n,k) × p^k × (1-p)^(n-k)\n"
                    f"其中 n={self.n_binomial}, p={self.p_binomial:.2f}"
                )
            elif self.question_type == 'mean':
                hint = f"提示：\n二项分布的期望值 E(X) = n × p = {self.n_binomial} × {self.p_binomial:.2f}"
            else:
                hint = f"提示：\n二项分布的方差 Var(X) = n × p × (1-p) = {self.n_binomial} × {self.p_binomial:.2f} × {1-self.p_binomial:.2f}"
        else:  # poisson
            if self.question_type == 'probability':
                hint = (
                    "提示：\n"
                    "泊松分布概率公式：\n"
                    "P(X=k) = (λ^k × e^(-λ)) / k!\n"
                    f"其中 λ={self.lambda_poisson:.2f}"
                )
            elif self.question_type == 'mean':
                hint = f"提示：\n泊松分布的期望值 E(X) = λ = {self.lambda_poisson:.2f}"
            else:
                hint = f"提示：\n泊松分布的方差 Var(X) = λ = {self.lambda_poisson:.2f}"
                
        messagebox.showinfo("提示", hint)
        
    def update_score_display(self):
        """更新得分显示"""
        accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        self.score_label.config(
            text=f"得分: {self.score}/{self.total_questions} | "
                 f"正确率: {accuracy:.1f}% | "
                 f"连击: {self.correct_streak} (最高: {self.max_streak})"
        )
        
    def update_display(self):
        """更新所有显示"""
        self.draw_distribution()
        self.draw_simulation()
        self.update_info_text()
        self.update_score_display()
        
    def draw_distribution(self):
        """绘制理论概率分布"""
        self.ax_dist.clear()
        
        if self.distribution_type == 'bernoulli':
            x = [0, 1]
            y = [self.calculate_probability(0), self.calculate_probability(1)]
            colors = ['#FF6B6B', '#4ECDC4']
            bars = self.ax_dist.bar(x, y, width=0.5, color=colors, edgecolor='black', linewidth=2, alpha=0.7)
            self.ax_dist.set_xlim(-0.5, 1.5)
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xticks([0, 1])
            self.ax_dist.set_xlabel('随机变量 X', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'0-1分布（伯努利分布）p = {self.p_bernoulli:.2f}', 
                                  fontsize=14, fontweight='bold')
            
            for i, (xi, yi) in enumerate(zip(x, y)):
                self.ax_dist.text(xi, yi + max(y) * 0.05, f'{yi:.3f}', 
                                ha='center', va='bottom', fontsize=11, fontweight='bold')
                
        elif self.distribution_type == 'binomial':
            x = list(range(self.n_binomial + 1))
            y = [self.calculate_probability(k) for k in x]
            bars = self.ax_dist.bar(x, y, width=0.6, color='#87CEEB', 
                                  edgecolor='navy', linewidth=1.5, alpha=0.7)
            self.ax_dist.set_xlim(-0.5, self.n_binomial + 0.5)
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xlabel('成功次数 k', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X=k)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'二项分布 (n={self.n_binomial}, p={self.p_binomial:.2f})', 
                                  fontsize=14, fontweight='bold')
            
            # 标记最可能值
            max_idx = np.argmax(y)
            self.ax_dist.axvline(max_idx, color='red', linestyle='--', linewidth=2, 
                                alpha=0.5, label=f'最可能值: {max_idx}')
            self.ax_dist.legend()
            
        elif self.distribution_type == 'poisson':
            max_k = max(20, int(self.lambda_poisson * 4))
            x = list(range(max_k + 1))
            y = [self.calculate_probability(k) for k in x]
            bars = self.ax_dist.bar(x, y, width=0.6, color='#90EE90', 
                                  edgecolor='darkgreen', linewidth=1.5, alpha=0.7)
            self.ax_dist.set_xlim(-0.5, min(max_k + 0.5, 30))
            self.ax_dist.set_ylim(0, max(y) * 1.2)
            self.ax_dist.set_xlabel('事件发生次数 k', fontsize=12, fontweight='bold')
            self.ax_dist.set_ylabel('概率 P(X=k)', fontsize=12, fontweight='bold')
            self.ax_dist.set_title(f'泊松分布 (λ={self.lambda_poisson:.2f})', 
                                  fontsize=14, fontweight='bold')
            
            # 标记λ值附近
            lambda_int = int(self.lambda_poisson)
            if lambda_int < len(y):
                self.ax_dist.axvline(lambda_int, color='red', linestyle='--', linewidth=2, 
                                    alpha=0.5, label=f'λ={self.lambda_poisson:.2f}附近')
                self.ax_dist.legend()
        
        self.ax_dist.grid(True, alpha=0.3, linestyle='--')
        self.canvas_dist.draw()
        
    def draw_simulation(self):
        """绘制模拟结果"""
        self.ax_sim.clear()
        
        if len(self.simulation_results) == 0:
            self.ax_sim.text(0.5, 0.5, '点击"模拟"按钮开始模拟', 
                           ha='center', va='center', fontsize=12,
                           transform=self.ax_sim.transAxes)
            self.ax_sim.set_title('模拟结果', fontsize=12, fontweight='bold')
            self.canvas_sim.draw()
            return
        
        # 统计频率
        if self.distribution_type == 'bernoulli':
            unique, counts = np.unique(self.simulation_results, return_counts=True)
            count_dict = dict(zip(unique, counts))
            x = [0, 1]
            y = [count_dict.get(0, 0), count_dict.get(1, 0)]
            colors = ['#FF6B6B', '#4ECDC4']
            self.ax_sim.bar(x, y, width=0.5, color=colors, edgecolor='black', linewidth=2, alpha=0.7)
            self.ax_sim.set_xlim(-0.5, 1.5)
            self.ax_sim.set_xticks([0, 1])
            
        else:
            unique, counts = np.unique(self.simulation_results, return_counts=True)
            x = list(unique)
            y = list(counts)
            color = '#87CEEB' if self.distribution_type == 'binomial' else '#90EE90'
            edge_color = 'navy' if self.distribution_type == 'binomial' else 'darkgreen'
            self.ax_sim.bar(x, y, width=0.6, color=color, edgecolor=edge_color, 
                          linewidth=1.5, alpha=0.7)
            self.ax_sim.set_xlim(-0.5, max(x) + 0.5)
        
        # 计算实际频率
        total = len(self.simulation_results)
        freq_text = "实际频率:\n"
        for xi, yi in zip(x, y):
            freq = yi / total
            freq_text += f"X={xi}: {freq:.3f} ({yi}/{total})\n"
        
        self.ax_sim.set_xlabel('观测值', fontsize=10, fontweight='bold')
        self.ax_sim.set_ylabel('出现次数', fontsize=10, fontweight='bold')
        self.ax_sim.set_title(f'模拟结果 (共{self.simulation_count}次)', fontsize=12, fontweight='bold')
        self.ax_sim.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加频率文本
        self.ax_sim.text(0.98, 0.98, freq_text.strip(), transform=self.ax_sim.transAxes,
                        fontsize=9, verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
        
        self.canvas_sim.draw()
        
    def update_info_text(self):
        """更新信息文本"""
        self.info_text.delete(1.0, tk.END)
        
        if self.distribution_type == 'bernoulli':
            info = (
                "【0-1分布（伯努利分布）】\n\n"
                "📌 定义：\n"
                "只有两种可能结果的单次试验：\n"
                "  • 成功 (X=1)，概率为 p\n"
                "  • 失败 (X=0)，概率为 1-p\n\n"
                f"📊 当前参数：\n"
                f"  p = {self.p_bernoulli:.2f}\n\n"
                f"📈 统计量：\n"
                f"  期望值 E(X) = {self.calculate_mean():.3f}\n"
                f"  方差 Var(X) = {self.calculate_variance():.3f}\n\n"
                "💡 应用：\n"
                "  • 抛硬币（正面/反面）\n"
                "  • 是否下雨\n"
                "  • 产品质量合格/不合格\n\n"
                "📚 公式：\n"
                "  P(X=0) = 1-p\n"
                "  P(X=1) = p"
            )
            
        elif self.distribution_type == 'binomial':
            info = (
                "【二项分布】\n\n"
                "📌 定义：\n"
                "进行 n 次独立的伯努利试验，\n"
                "每次成功的概率为 p，\n"
                "X 表示成功的总次数。\n\n"
                f"📊 当前参数：\n"
                f"  n = {self.n_binomial} (试验次数)\n"
                f"  p = {self.p_binomial:.2f} (成功概率)\n\n"
                f"📈 统计量：\n"
                f"  期望值 E(X) = {self.calculate_mean():.3f}\n"
                f"  方差 Var(X) = {self.calculate_variance():.3f}\n\n"
                "💡 应用：\n"
                "  • 抛硬币 n 次，正面出现次数\n"
                "  • 产品质量检测中合格品数量\n"
                "  • 投篮 n 次，命中次数\n\n"
                "📚 公式：\n"
                "  P(X=k) = C(n,k) × p^k × (1-p)^(n-k)\n"
                "  E(X) = n × p\n"
                "  Var(X) = n × p × (1-p)"
            )
            
        elif self.distribution_type == 'poisson':
            info = (
                "【泊松分布】\n\n"
                "📌 定义：\n"
                "描述单位时间内随机事件发生的次数，\n"
                "事件发生是独立的且概率很小。\n\n"
                f"📊 当前参数：\n"
                f"  λ = {self.lambda_poisson:.2f} (平均发生次数)\n\n"
                f"📈 统计量：\n"
                f"  期望值 E(X) = {self.calculate_mean():.3f}\n"
                f"  方差 Var(X) = {self.calculate_variance():.3f}\n\n"
                "💡 应用：\n"
                "  • 每小时接到的电话数\n"
                "  • 网站每分钟的访问量\n"
                "  • 单位时间内的事故数\n\n"
                "📚 公式：\n"
                "  P(X=k) = (λ^k × e^(-λ)) / k!\n"
                "  E(X) = λ\n"
                "  Var(X) = λ"
            )
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)


def main():
    """主函数"""
    print("=" * 60)
    print("概率分布学习游戏 - 增强版")
    print("=" * 60)
    print("\n游戏说明：")
    print("1. 选择分布类型：0-1分布、二项分布、泊松分布")
    print("2. 调整参数滑块，观察概率分布的变化")
    print("3. 进行模拟实验，观察实际结果与理论分布的对比")
    print("4. 在挑战模式下回答问题，检验学习成果")
    print("\n功能特点：")
    print("  • 学习模式：自由探索，理解概念")
    print("  • 挑战模式：回答问题，获得分数")
    print("  • 可视化对比：理论分布 vs 实际模拟")
    print("=" * 60 + "\n")
    
    try:
        root = tk.Tk()
        app = ProbabilityDistributionGame(root)
        root.mainloop()
    except Exception as e:
        print(f"\n✗ 运行程序时出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

