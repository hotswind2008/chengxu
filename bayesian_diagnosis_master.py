"""
贝叶斯咳嗽诊断游戏 - 完整版
包含互动教学、可视化演示、练习题、游戏模式等完整功能
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import random
from typing import Dict, List, Tuple
from datetime import datetime
import json
import sys
import platform


class BayesianDiagnosisGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贝叶斯诊断游戏")
        
        # Windows 高 DPI 适配
        if sys.platform.startswith('win'):
            try:
                from ctypes import windll
                try:
                    windll.shcore.SetProcessDpiAwareness(1)
                except Exception:
                    windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        # 获取屏幕尺寸并设置合适的窗口大小（适配常见分辨率）
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # 使用屏幕的90%，且不超过1280x860（常见Windows分辨率友好）
        window_width = min(int(screen_width * 0.90), 1280)
        window_height = min(int(screen_height * 0.90), 860)
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#ECF0F1')
        
        # 设置最小窗口大小（不超过初始大小）
        min_w = min(window_width, 1200)
        min_h = min(window_height, 700)
        self.root.minsize(min_w, min_h)

        # 小屏幕自动最大化（如 1366x768/1280x800 等）
        if sys.platform.startswith('win') and (screen_width <= 1366 or screen_height <= 800):
            try:
                self.root.state('zoomed')
            except Exception:
                pass
        
        # 统一按钮样式，提升文本可见性（跨平台）
        try:
            style = ttk.Style()
            style.theme_use('clam')
            # 基础样式
            style.configure('Primary.TButton', foreground='#FFFFFF', background='#3498DB', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Primary.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#2E86C1')])
            
            style.configure('Success.TButton', foreground='#FFFFFF', background='#27AE60', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Success.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#229954')])
            
            style.configure('Info.TButton', foreground='#FFFFFF', background='#16A085', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Info.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#138D75')])
            
            style.configure('Warning.TButton', foreground='#1B1B1B', background='#F39C12', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Warning.TButton', foreground=[('active', '#1B1B1B')], background=[('active', '#D68910')])
            
            style.configure('Purple.TButton', foreground='#FFFFFF', background='#9B59B6', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Purple.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#8E44AD')])
            
            style.configure('Danger.TButton', foreground='#FFFFFF', background='#E74C3C', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Danger.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#CB4335')])
            
            style.configure('Muted.TButton', foreground='#FFFFFF', background='#95A5A6', font=('Arial', 12, 'bold'), padding=(10, 6))
            style.map('Muted.TButton', foreground=[('active', '#FFFFFF')], background=[('active', '#7F8C8D')])
        except Exception:
            pass
        
        # 游戏模式
        self.game_mode = tk.StringVar(value='教学模式')
        self.difficulty = tk.StringVar(value='简单')
        
        # 疾病数据（可以根据难度调整）
        self.all_diseases = {
            '普通感冒': {
                'prior': 0.50,
                'color': '#FF6B6B',
                'description': '最常见的呼吸道感染，症状较轻',
                'key_symptoms': ['流鼻涕', '喉咙痛']
            },
            '流感': {
                'prior': 0.30,
                'color': '#4ECDC4',
                'description': '症状更严重的病毒性感染',
                'key_symptoms': ['发烧', '肌肉酸痛']
            },
            '肺炎': {
                'prior': 0.20,
                'color': '#FFA07A',
                'description': '肺部感染，需要及时治疗',
                'key_symptoms': ['发烧', '胸痛', '呼吸困难']
            }
        }
        
        # 所有症状的条件概率
        self.all_symptom_probabilities = {
            '发烧': {
                '普通感冒': 0.30, '流感': 0.90, '肺炎': 0.85
            },
            '流鼻涕': {
                '普通感冒': 0.80, '流感': 0.40, '肺炎': 0.20
            },
            '喉咙痛': {
                '普通感冒': 0.70, '流感': 0.60, '肺炎': 0.30
            },
            '呼吸困难': {
                '普通感冒': 0.10, '流感': 0.35, '肺炎': 0.75
            },
            '胸痛': {
                '普通感冒': 0.05, '流感': 0.25, '肺炎': 0.65
            },
            '咳痰': {
                '普通感冒': 0.40, '流感': 0.50, '肺炎': 0.85
            },
            '乏力': {
                '普通感冒': 0.50, '流感': 0.85, '肺炎': 0.80
            },
            '肌肉酸痛': {
                '普通感冒': 0.40, '流感': 0.80, '肺炎': 0.45
            },
            '头痛': {
                '普通感冒': 0.35, '流感': 0.75, '肺炎': 0.40
            },
            '夜间咳嗽': {
                '普通感冒': 0.30, '流感': 0.40, '肺炎': 0.60
            }
        }
        
        # 当前使用的疾病和症状
        self.diseases = {}
        self.symptom_probabilities = {}
        self.setup_difficulty()
        
        # 游戏状态
        self.current_probabilities = {}
        self.asked_symptoms = []
        self.symptom_responses = {}
        self.calculation_history = []
        self.game_stats = {
            'total_games': 0,
            'correct_diagnoses': 0,
            'total_questions': 0,
            'game_records': []
        }
        
        # 可视化状态
        self.current_viz_step = 0
        self.animation_speed = 500  # ms
        self.viz_is_playing = False
        self.viz_after_handle = None
        
        # 练习题
        self.quiz_score = {'correct': 0, 'total': 0}
        self.current_quiz = None
        
        self.reset_probabilities()
        self.create_interface()
        
    def setup_difficulty(self):
        """根据难度设置疾病和症状"""
        difficulty = self.difficulty.get()
        
        if difficulty == '简单':
            # 3种疾病，6种症状
            self.diseases = self.all_diseases.copy()
            symptom_keys = list(self.all_symptom_probabilities.keys())[:6]
        elif difficulty == '中等':
            # 3种疾病，8种症状
            self.diseases = self.all_diseases.copy()
            symptom_keys = list(self.all_symptom_probabilities.keys())[:8]
        else:  # 困难
            # 3种疾病，所有症状
            self.diseases = self.all_diseases.copy()
            symptom_keys = list(self.all_symptom_probabilities.keys())
        
        self.symptom_probabilities = {
            symptom: {disease: self.all_symptom_probabilities[symptom][disease]
                     for disease in self.diseases.keys()}
            for symptom in symptom_keys
        }
        
    def reset_probabilities(self):
        """重置为先验概率"""
        self.current_probabilities = {
            disease: info['prior'] 
            for disease, info in self.diseases.items()
        }
        self.calculation_history = [{
            'step': 0,
            'description': '初始先验概率',
            'probabilities': self.current_probabilities.copy()
        }]
        
    def create_interface(self):
        """创建主界面"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#2C3E50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="贝叶斯诊断游戏",
            font=('Arial', 20, 'bold'),
            bg='#2C3E50',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # 模式和难度选择栏
        control_frame = tk.Frame(self.root, bg='#34495E', height=45)
        control_frame.pack(fill=tk.X)
        control_frame.pack_propagate(False)
        
        # 左侧：模式选择
        left_control = tk.Frame(control_frame, bg='#34495E')
        left_control.pack(side=tk.LEFT, padx=15)
        
        tk.Label(
            left_control,
            text="模式：",
            font=('Arial', 10, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=3)
        
        for mode in ['教学模式', '游戏模式', '挑战模式']:
            tk.Radiobutton(
                left_control,
                text=mode,
                variable=self.game_mode,
                value=mode,
                font=('Arial', 9),
                bg='#34495E',
                fg='white',
                selectcolor='#2C3E50',
                command=self.on_mode_change
            ).pack(side=tk.LEFT, padx=3)
        
        # 中间：难度选择
        mid_control = tk.Frame(control_frame, bg='#34495E')
        mid_control.pack(side=tk.LEFT, padx=15)
        
        tk.Label(
            mid_control,
            text="难度：",
            font=('Arial', 10, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=3)
        
        for level in ['简单', '中等', '困难']:
            tk.Radiobutton(
                mid_control,
                text=level,
                variable=self.difficulty,
                value=level,
                font=('Arial', 9),
                bg='#34495E',
                fg='white',
                selectcolor='#2C3E50',
                command=self.on_difficulty_change
            ).pack(side=tk.LEFT, padx=3)
        
        # 右侧：统计信息
        right_control = tk.Frame(control_frame, bg='#34495E')
        right_control.pack(side=tk.RIGHT, padx=15)
        
        self.stats_label = tk.Label(
            right_control,
            text="游戏次数: 0 | 正确率: 0%",
            font=('Arial', 10, 'bold'),
            bg='#34495E',
            fg='#F39C12'
        )
        self.stats_label.pack()
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页1: 互动诊断
        self.diagnosis_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.diagnosis_tab, text='🎯 互动诊断')
        self.create_diagnosis_tab()
        
        # 标签页2: 公式详解
        self.formula_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.formula_tab, text='📐 公式详解')
        self.create_formula_tab()
        
        # 标签页3: 动画演示
        self.animation_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.animation_tab, text='🎬 动画演示')
        self.create_animation_tab()
        
        # 标签页4: 手动计算
        self.manual_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.manual_tab, text='✍️ 手动计算')
        self.create_manual_tab()
        
        # 标签页5: 练习测验
        self.quiz_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.quiz_tab, text='📝 练习测验')
        self.create_quiz_tab()
        
        # 标签页6: 游戏统计
        self.stats_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.stats_tab, text='📊 游戏统计')
        self.create_stats_tab()
        
    def create_diagnosis_tab(self):
        """创建互动诊断标签页"""
        main_container = tk.Frame(self.diagnosis_tab, bg='#ECF0F1')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：概率显示（40%宽度）
        left_panel = tk.Frame(main_container, bg='white', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_panel,
            text="实时概率分布",
            font=('Arial', 13, 'bold'),
            bg='white',
            pady=8
        ).pack()
        
        # 概率条形图
        self.prob_bars_frame = tk.Frame(left_panel, bg='white')
        self.prob_bars_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.update_probability_bars()
        
        # 底部提示
        self.diagnosis_tip_frame = tk.Frame(left_panel, bg='#FFF9E6', relief=tk.RIDGE, borderwidth=2)
        self.diagnosis_tip_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            self.diagnosis_tip_frame,
            text="智能提示",
            font=('Arial', 10, 'bold'),
            bg='#FFF9E6',
            fg='#F39C12'
        ).pack(pady=3)
        
        self.ai_tip_label = tk.Label(
            self.diagnosis_tip_frame,
            text="开始询问症状，系统会实时更新概率并给出建议",
            font=('Arial', 9),
            bg='#FFF9E6',
            wraplength=350,
            justify=tk.LEFT
        )
        self.ai_tip_label.pack(padx=8, pady=8)
        
        # 右侧：操作区域（60%宽度）
        right_panel = tk.Frame(main_container, bg='white', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_panel,
            text="诊断过程",
            font=('Arial', 13, 'bold'),
            bg='white',
            pady=8
        ).pack()
        
        # 症状信息卡片
        self.symptom_card = tk.Frame(right_panel, bg='#E8F6F3', relief=tk.RIDGE, borderwidth=2)
        self.symptom_card.pack(fill=tk.X, padx=15, pady=8)
        
        tk.Label(
            self.symptom_card,
            text="当前症状信息",
            font=('Arial', 11, 'bold'),
            bg='#E8F6F3',
            fg='#16A085'
        ).pack(pady=5)
        
        # 症状选择
        symptom_select_frame = tk.Frame(self.symptom_card, bg='#E8F6F3')
        symptom_select_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            symptom_select_frame,
            text="选择症状：",
            font=('Arial', 10, 'bold'),
            bg='#E8F6F3'
        ).pack(side=tk.LEFT, padx=5)
        
        self.symptom_var = tk.StringVar()
        self.symptom_combo = ttk.Combobox(
            symptom_select_frame,
            textvariable=self.symptom_var,
            values=list(self.symptom_probabilities.keys()),
            state='readonly',
            font=('Arial', 10),
            width=18
        )
        self.symptom_combo.pack(side=tk.LEFT, padx=8)
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
        self.symptom_combo.bind('<<ComboboxSelected>>', self.on_symptom_selected)
        
        # 条件概率显示
        self.cond_prob_frame = tk.Frame(self.symptom_card, bg='white', relief=tk.SUNKEN, borderwidth=1)
        self.cond_prob_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.on_symptom_selected()
        
        # 患者回答按钮
        response_frame = tk.Frame(right_panel, bg='white')
        response_frame.pack(pady=10)
        
        tk.Label(
            response_frame,
            text="患者是否有此症状？",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        button_container = tk.Frame(response_frame, bg='white')
        button_container.pack()
        
        tk.Button(
            button_container,
            text="是",
            font=('Arial', 12, 'bold'),
            bg='#27AE60',
            fg='#FFFCEA',
            width=12,
            height=1,
            command=lambda: self.process_symptom(True),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_container,
            text="否",
            font=('Arial', 12, 'bold'),
            bg='#E74C3C',
            fg='#FFFCEA',
            width=12,
            height=1,
            command=lambda: self.process_symptom(False),
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=10)
        
        # 计算步骤展示
        steps_label_frame = tk.Frame(right_panel, bg='white')
        steps_label_frame.pack(fill=tk.X, padx=15)
        
        tk.Label(
            steps_label_frame,
            text="详细计算步骤",
            font=('Arial', 11, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, pady=3)
        
        self.show_steps_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            steps_label_frame,
            text="显示详细步骤",
            variable=self.show_steps_var,
            font=('Arial', 9),
            bg='white'
        ).pack(side=tk.RIGHT)
        
        self.steps_display = scrolledtext.ScrolledText(
            right_panel,
            font=('Courier', 11),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=10,
            state=tk.DISABLED
        )
        self.steps_display.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # 底部按钮栏
        bottom_buttons = tk.Frame(right_panel, bg='white')
        bottom_buttons.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(
            bottom_buttons,
            text="重新开始",
            style='Primary.TButton',
            command=self.reset_game,
            width=12
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            bottom_buttons,
            text="智能推荐",
            style='Purple.TButton',
            command=self.show_ai_recommendation,
            width=12
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            bottom_buttons,
            text="查看历史",
            style='Info.TButton',
            command=self.show_calculation_history,
            width=12
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            bottom_buttons,
            text="完成诊断",
            style='Warning.TButton',
            command=self.finalize_diagnosis,
            width=12
        ).pack(side=tk.RIGHT, padx=3)
        
    def create_formula_tab(self):
        """创建公式详解标签页"""
        # 创建可滚动区域
        canvas = tk.Canvas(self.formula_tab, bg='white')
        scrollbar = tk.Scrollbar(self.formula_tab, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 标题
        tk.Label(
            scrollable_frame,
            text="贝叶斯定理完全指南",
            font=('Arial', 18, 'bold'),
            bg='white',
            pady=15
        ).pack()
        
        # 创建各个部分
        sections = [
            {
                'title': '1️⃣ 核心公式',
                'color': '#E8F6F3',
                'title_color': '#16A085',
                'content': """
贝叶斯定理基本形式：

    P(A|B) = P(B|A) × P(A) / P(B)

在医学诊断中的应用：

    P(疾病|症状) = P(症状|疾病) × P(疾病) / P(症状)

符号说明：
├─ P(疾病|症状)：更新后的概率 - 观察到症状后患该疾病的概率
├─ P(症状|疾病)：条件概率 - 患该疾病时出现该症状的概率
├─ P(疾病)：初始概率 - 观察症状前患该疾病的概率（基于流行病学）
└─ P(症状)：症状总概率 - 出现该症状的总概率（用于计算）

关键理解：
• 贝叶斯定理将"原因→结果"的概率转换为"结果→原因"的概率
• 它告诉我们：看到证据后，如何更新我们对原因的信念
• 在诊断中：知道疾病→症状的概率，推断症状→疾病的概率
"""
            },
            {
                'title': '2️⃣ 详细推导',
                'color': '#FEF5E7',
                'title_color': '#D68910',
                'content': """
完整计算过程（以发烧为例）：

步骤1：列出初始概率
    P(普通感冒) = 0.50    P(流感) = 0.30    P(肺炎) = 0.20

步骤2：列出条件概率
    P(发烧|普通感冒) = 0.30
    P(发烧|流感) = 0.90
    P(发烧|肺炎) = 0.85

步骤3：计算中间结果（条件概率 × 初始概率）
    普通感冒：0.30 × 0.50 = 0.15
    流感：    0.90 × 0.30 = 0.27
    肺炎：    0.85 × 0.20 = 0.17

步骤4：计算总和
    P(发烧) = 0.15 + 0.27 + 0.17 = 0.59

步骤5：计算最终概率（中间结果 ÷ 总和）
    P(普通感冒|发烧) = 0.15 / 0.59 = 0.254  (25.4%)
    P(流感|发烧) = 0.27 / 0.59 = 0.458  (45.8%)
    P(肺炎|发烧) = 0.17 / 0.59 = 0.288  (28.8%)

结论：
• 发烧前，流感概率30%，肺炎20%
• 发烧后，流感概率升至45.8%，因为流感患者更容易发烧
• 普通感冒概率从50%降至25.4%，因为感冒患者较少发烧
"""
            },
            {
                'title': '3️⃣ 迭代更新',
                'color': '#FADBD8',
                'title_color': '#A93226',
                'content': """
贝叶斯诊断的强大之处在于可以不断更新：

第1次观察（症状A）：
    P₁(疾病) = P(症状A|疾病) × P₀(疾病) / Σ[P(症状A|疾病ⱼ) × P₀(疾病ⱼ)]

第2次观察（症状B）：
    P₂(疾病) = P(症状B|疾病) × P₁(疾病) / Σ[P(症状B|疾病ⱼ) × P₁(疾病ⱼ)]

关键点：
• 每次更新后的概率成为下次的初始概率
• 可以无限次迭代，每次都会更新我们的判断
• 随着证据增多，诊断越来越准确
• 不同症状的询问顺序不影响最终结果（贝叶斯定理的性质）

示例（继续上面的例子，再观察"呼吸困难"）：
使用更新后的概率作为新的初始值：
    P(普通感冒) = 0.254    P(流感) = 0.458    P(肺炎) = 0.288

已知：
    P(呼吸困难|普通感冒) = 0.10
    P(呼吸困难|流感) = 0.35
    P(呼吸困难|肺炎) = 0.75

患者有呼吸困难，再次更新：
    中间结果：
        普通感冒：0.10 × 0.254 = 0.0254
        流感：    0.35 × 0.458 = 0.1603
        肺炎：    0.75 × 0.288 = 0.2160
    
    总和 = 0.4017
    
    新的最终概率：
        P(普通感冒|发烧,呼吸困难) = 0.0254 / 0.4017 = 0.063  (6.3%)
        P(流感|发烧,呼吸困难) = 0.1603 / 0.4017 = 0.399  (39.9%)
        P(肺炎|发烧,呼吸困难) = 0.2160 / 0.4017 = 0.538  (53.8%)

观察两次后，肺炎的概率从20%→28.8%→53.8%，成为最可能的诊断！
"""
            },
            {
                'title': '4️⃣ 阴性结果的处理',
                'color': '#E8DAEF',
                'title_color': '#7D3C98',
                'content': """
患者"没有"某症状也提供信息！

公式：
    P(疾病|无症状) = P(无症状|疾病) × P(疾病) / P(无症状)
                   = [1 - P(症状|疾病)] × P(疾病) / P(无症状)

示例：患者没有发烧

先验：
    P(普通感冒) = 0.50    P(流感) = 0.30    P(肺炎) = 0.20

阴性似然度：
    P(无发烧|普通感冒) = 1 - 0.30 = 0.70
    P(无发烧|流感) = 1 - 0.90 = 0.10
    P(无发烧|肺炎) = 1 - 0.85 = 0.15

未归一化：
    普通感冒：0.70 × 0.50 = 0.35
    流感：    0.10 × 0.30 = 0.03
    肺炎：    0.15 × 0.20 = 0.03

总和 = 0.41

后验概率：
    P(普通感冒|无发烧) = 0.35 / 0.41 = 0.854  (85.4%)  ↑
    P(流感|无发烧) = 0.03 / 0.41 = 0.073  (7.3%)   ↓
    P(肺炎|无发烧) = 0.03 / 0.41 = 0.073  (7.3%)   ↓

解释：
• 流感和肺炎患者通常会发烧（概率90%和85%）
• 患者没有发烧，大大降低了流感和肺炎的可能性
• 普通感冒患者发烧较少（30%），所以无发烧反而支持感冒诊断
• 阴性结果同样重要，它排除了某些疾病的可能性
"""
            },
            {
                'title': '5️⃣ 实用技巧',
                'color': '#D6EAF8',
                'title_color': '#1F618D',
                'content': """
如何有效使用贝叶斯诊断：

1. 从先验概率开始
   ✓ 先验概率反映疾病的基础发病率
   ✓ 罕见病的先验概率低，需要更强的证据
   ✓ 考虑季节、地区、年龄等因素

2. 选择有鉴别力的症状
   ✓ 选择不同疾病中概率差异大的症状
   ✓ 例如："发烧"能很好地区分流感和普通感冒
   ✓ 避免问各疾病概率都相近的症状

3. 注意概率的数量级
   ✓ 概率>70%：可以考虑做出诊断
   ✓ 概率50-70%：继续收集证据
   ✓ 概率<30%：基本可以排除

4. 理解似然比
   ✓ 似然比 = P(症状|疾病A) / P(症状|疾病B)
   ✓ 似然比>3：该症状强烈支持疾病A
   ✓ 似然比<0.3：该症状强烈支持疾病B

5. 常见误区
   ✗ 只看条件概率，忽略先验概率
   ✗ 认为概率高的症状一定出现
   ✗ 忽略阴性结果的价值
   ✗ 过早下结论，证据不足

实战建议：
• 至少收集3-5个症状再做判断
• 优先询问关键症状（见疾病信息卡）
• 注意观察概率变化趋势
• 如果最高概率<60%，继续询问
• 对高危疾病（如肺炎）保持警惕
"""
            }
        ]
        
        for section in sections:
            frame = tk.Frame(scrollable_frame, bg=section['color'], 
                           relief=tk.RAISED, borderwidth=2)
            frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(
                frame,
                text=section['title'],
                font=('Arial', 15, 'bold'),
                bg=section['color'],
                fg=section['title_color']
            ).pack(anchor=tk.W, padx=15, pady=10)
            
            # 使用Text widget替代Label以便更好地显示多行文本
            text_widget = tk.Text(
                frame,
                font=('Courier', 12),
                bg='white',
                relief=tk.SUNKEN,
                wrap=tk.WORD,
                height=section['content'].count('\n') + 1,
                padx=15,
                pady=12,
                borderwidth=2
            )
            text_widget.insert(1.0, section['content'])
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(padx=15, pady=(0, 15), fill=tk.X)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定鼠标滚轮
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
    def create_animation_tab(self):
        """创建动画演示标签页"""
        tk.Label(
            self.animation_tab,
            text="贝叶斯更新动画演示",
            font=('Arial', 14, 'bold'),
            bg='#ECF0F1',
            pady=12
        ).pack()
        
        tk.Label(
            self.animation_tab,
            text="通过动画直观展示概率如何随证据更新而变化",
            font=('Arial', 10),
            bg='#ECF0F1'
        ).pack()
        
        # 画布
        viz_frame = tk.Frame(self.animation_tab, bg='white', 
                            relief=tk.RAISED, borderwidth=2)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        self.viz_canvas = tk.Canvas(
            viz_frame,
            bg='white',
            highlightthickness=0
        )
        self.viz_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 控制栏
        control_frame = tk.Frame(self.animation_tab, bg='#ECF0F1')
        control_frame.pack(fill=tk.X, padx=20, pady=8)
        
        tk.Button(
            control_frame,
            text="第一步",
            font=('Arial', 9, 'bold'),
            bg='#95A5A6',
            fg='#FFFCEA',
            command=self.viz_first,
            width=8,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#7F8C8D'
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            control_frame,
            text="上一步",
            font=('Arial', 9, 'bold'),
            bg='#95A5A6',
            fg='#FFFCEA',
            command=self.viz_previous,
            width=8,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#7F8C8D'
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            control_frame,
            text="下一步",
            font=('Arial', 9, 'bold'),
            bg='#3498DB',
            fg='#FFFCEA',
            command=self.viz_next,
            width=8,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#2E86C1'
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            control_frame,
            text="最后一步",
            font=('Arial', 9, 'bold'),
            bg='#95A5A6',
            fg='#FFFCEA',
            command=self.viz_last,
            width=8,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#7F8C8D'
        ).pack(side=tk.LEFT, padx=3)
        
        tk.Button(
            control_frame,
            text="自动播放",
            font=('Arial', 9, 'bold'),
            bg='#27AE60',
            fg='#FFFCEA',
            command=self.viz_auto_play,
            width=10,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#229954'
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            control_frame,
            text="停止",
            font=('Arial', 9, 'bold'),
            bg='#E74C3C',
            fg='#FFFCEA',
            command=self.viz_stop,
            width=8,
            height=1,
            activeforeground='#FFFCEA',
            activebackground='#CB4335'
        ).pack(side=tk.LEFT)
        
        self.viz_step_label = tk.Label(
            control_frame,
            text="步骤: 0 / 0",
            font=('Arial', 11, 'bold'),
            bg='#ECF0F1',
            fg='#E74C3C'
        )
        self.viz_step_label.pack(side=tk.RIGHT, padx=15)
        
    def create_manual_tab(self):
        """创建手动计算标签页"""
        tk.Label(
            self.manual_tab,
            text="手动计算练习",
            font=('Arial', 14, 'bold'),
            bg='#ECF0F1',
            pady=12
        ).pack()
        
        tk.Label(
            self.manual_tab,
            text="自己动手计算贝叶斯公式，加深理解",
            font=('Arial', 10),
            bg='#ECF0F1'
        ).pack()
        
        # 主容器（可滚动，避免按钮被遮挡）
        container_outer = tk.Frame(self.manual_tab, bg='#ECF0F1')
        container_outer.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        canvas = tk.Canvas(container_outer, bg='#ECF0F1', highlightthickness=0)
        vscroll = ttk.Scrollbar(container_outer, orient=tk.VERTICAL, command=canvas.yview)
        container = tk.Frame(canvas, bg='white', relief=tk.RAISED, borderwidth=2)
        container_id = canvas.create_window((0, 0), window=container, anchor='nw')
        canvas.configure(yscrollcommand=vscroll.set)
        
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        container.bind('<Configure>', _on_frame_configure)
        
        def _on_canvas_configure(event):
            canvas.itemconfig(container_id, width=event.width)
        canvas.bind('<Configure>', _on_canvas_configure)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 题目区域
        question_frame = tk.Frame(container, bg='#E8F6F3', 
                                 relief=tk.RIDGE, borderwidth=2)
        question_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            question_frame,
            text="📋 计算题目",
            font=('Arial', 14, 'bold'),
            bg='#E8F6F3',
            fg='#16A085'
        ).pack(pady=10)
        
        self.manual_question_text = tk.Text(
            question_frame,
            font=('Arial', 13),
            height=9,
            wrap=tk.WORD,
            bg='white',
            state=tk.DISABLED
        )
        self.manual_question_text.pack(padx=20, pady=10, fill=tk.X)
        
        btn_bar = tk.Frame(question_frame, bg='#E8F6F3')
        btn_bar.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(
            btn_bar,
            text="生成新题目",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.generate_manual_question,
            width=15
        ).pack(side=tk.LEFT)
        tk.Button(
            btn_bar,
            text="滚动到提交",
            font=('Arial', 11, 'bold'),
            bg='#16A085',
            fg='white',
            command=lambda: canvas.yview_moveto(1.0),
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        # 答题区域
        answer_container = tk.Frame(container, bg='white')
        answer_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧：输入
        left_answer = tk.Frame(answer_container, bg='#FEF5E7', 
                              relief=tk.RIDGE, borderwidth=2)
        left_answer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_answer,
            text="📝 你的答案",
            font=('Arial', 13, 'bold'),
            bg='#FEF5E7'
        ).pack(pady=10)
        
        # 输入框
        self.manual_entries = {}
        
        tk.Label(
            left_answer,
            text="步骤1：计算中间结果（条件概率 × 先验概率）",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        for disease in self.diseases.keys():
            frame = tk.Frame(left_answer, bg='#FEF5E7')
            frame.pack(fill=tk.X, padx=30, pady=5)
            
            tk.Label(
                frame,
                text=f"{disease}:",
                font=('Arial', 11),
                bg='#FEF5E7',
                width=12,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 11), width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.manual_entries[f'unnorm_{disease}'] = entry
        
        tk.Label(
            left_answer,
            text="步骤2：计算所有中间结果的总和",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        sum_frame = tk.Frame(left_answer, bg='#FEF5E7')
        sum_frame.pack(fill=tk.X, padx=30, pady=5)
        
        tk.Label(
            sum_frame,
            text="总和:",
            font=('Arial', 11),
            bg='#FEF5E7',
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.manual_sum_entry = tk.Entry(sum_frame, font=('Arial', 11), width=15)
        self.manual_sum_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            left_answer,
            text="步骤3：计算最终概率（中间结果 ÷ 总和）",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        for disease in self.diseases.keys():
            frame = tk.Frame(left_answer, bg='#FEF5E7')
            frame.pack(fill=tk.X, padx=30, pady=5)
            
            tk.Label(
                frame,
                text=f"P({disease}|症状):",
                font=('Arial', 11),
                bg='#FEF5E7',
                width=18,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 11), width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.manual_entries[f'post_{disease}'] = entry
        
        # 提交按钮（放在显眼位置）
        submit_frame = tk.Frame(left_answer, bg='#FEF5E7')
        submit_frame.pack(pady=15, fill=tk.X)
        
        tk.Button(
            submit_frame,
            text="提交答案",
            font=('Arial', 14, 'bold'),
            bg='#27AE60',
            fg='#FFFCEA',
            command=self.check_manual_answer,
            width=20,
            height=2
        ).pack()
        
        # 右侧：反馈
        right_answer = tk.Frame(answer_container, bg='white', 
                               relief=tk.RIDGE, borderwidth=2)
        right_answer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_answer,
            text="📊 反馈",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(pady=10)
        
        self.manual_feedback = scrolledtext.ScrolledText(
            right_answer,
            font=('Courier', 12),
            wrap=tk.WORD,
            bg='#F8F9FA',
            state=tk.DISABLED
        )
        self.manual_feedback.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 初始化
        self.current_manual_exercise = None
        self.generate_manual_question()
        
    def create_quiz_tab(self):
        """创建练习测验标签页"""
        tk.Label(
            self.quiz_tab,
            text="贝叶斯公式测验",
            font=('Arial', 14, 'bold'),
            bg='#ECF0F1',
            pady=12
        ).pack()
        
        # 得分栏
        score_frame = tk.Frame(self.quiz_tab, bg='#2C3E50', height=50)
        score_frame.pack(fill=tk.X, padx=20, pady=8)
        score_frame.pack_propagate(False)
        
        self.quiz_score_label = tk.Label(
            score_frame,
            text=f"得分: {self.quiz_score['correct']} / {self.quiz_score['total']}  "
                 f"(正确率: 0%)",
            font=('Arial', 13, 'bold'),
            bg='#2C3E50',
            fg='#F39C12'
        )
        self.quiz_score_label.pack(expand=True)
        
        # 题目区
        question_frame = tk.Frame(self.quiz_tab, bg='white', 
                                 relief=tk.RAISED, borderwidth=2)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            question_frame,
            text="📌 题目",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.quiz_question_text = scrolledtext.ScrolledText(
            question_frame,
            font=('Arial', 12),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=10,
            state=tk.DISABLED
        )
        self.quiz_question_text.pack(fill=tk.X, padx=30, pady=10)
        
        # 答案输入
        answer_input_frame = tk.Frame(question_frame, bg='white')
        answer_input_frame.pack(pady=15)
        
        tk.Label(
            answer_input_frame,
            text="你的答案（保留4位小数）：",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        self.quiz_answer_entry = tk.Entry(
            answer_input_frame,
            font=('Arial', 13),
            width=20
        )
        self.quiz_answer_entry.pack(side=tk.LEFT, padx=10)
        self.quiz_answer_entry.bind('<Return>', lambda e: self.check_quiz_answer())
        
        # 按钮
        btn_frame = tk.Frame(question_frame, bg='white')
        btn_frame.pack(pady=15)
        
        ttk.Button(
            btn_frame,
            text="提交",
            style='Success.TButton',
            command=self.check_quiz_answer,
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="下一题",
            style='Primary.TButton',
            command=self.next_quiz,
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame,
            text="提示",
            style='Warning.TButton',
            command=self.show_quiz_hint,
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        # 解析区
        tk.Label(
            question_frame,
            text="📖 详细解析",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.quiz_explanation = scrolledtext.ScrolledText(
            question_frame,
            font=('Courier', 12),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=12,
            state=tk.DISABLED
        )
        self.quiz_explanation.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # 初始化
        self.next_quiz()
        
    def create_stats_tab(self):
        """创建统计标签页"""
        tk.Label(
            self.stats_tab,
            text="游戏统计数据",
            font=('Arial', 14, 'bold'),
            bg='#ECF0F1',
            pady=12
        ).pack()
        
        # 总体统计
        summary_frame = tk.Frame(self.stats_tab, bg='#2C3E50', 
                                relief=tk.RAISED, borderwidth=2)
        summary_frame.pack(fill=tk.X, padx=30, pady=15)
        
        tk.Label(
            summary_frame,
            text="总体表现",
            font=('Arial', 13, 'bold'),
            bg='#2C3E50',
            fg='white',
            pady=8
        ).pack()
        
        stats_grid = tk.Frame(summary_frame, bg='#2C3E50')
        stats_grid.pack(pady=15)
        
        self.stat_labels = {}
        stats_info = [
            ('total_games', '总游戏次数', 0),
            ('correct_rate', '诊断正确率', 1),
            ('avg_questions', '平均询问次数', 2),
            ('best_score', '最佳得分', 3)
        ]
        
        for key, label_text, col in stats_info:
            frame = tk.Frame(stats_grid, bg='#34495E', relief=tk.RAISED, 
                           borderwidth=2, width=150, height=80)
            frame.grid(row=0, column=col, padx=15, pady=10)
            frame.pack_propagate(False)
            
            tk.Label(
                frame,
                text=label_text,
                font=('Arial', 11),
                bg='#34495E',
                fg='white'
            ).pack(pady=5)
            
            value_label = tk.Label(
                frame,
                text="0",
                font=('Arial', 18, 'bold'),
                bg='#34495E',
                fg='#F39C12'
            )
            value_label.pack()
            self.stat_labels[key] = value_label
        
        # 历史记录
        tk.Label(
            self.stats_tab,
            text="📜 游戏历史",
            font=('Arial', 14, 'bold'),
            bg='#ECF0F1',
            pady=10
        ).pack()
        
        history_frame = tk.Frame(self.stats_tab, bg='white', 
                                relief=tk.RAISED, borderwidth=2)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        
        # 创建表格
        columns = ('序号', '时间', '诊断结果', '询问次数', '正确性', '得分')
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                              padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20, padx=(0, 20))
        
        # 更新统计
        self.update_stats_display()
        
    # === 功能实现方法 ===
    
    def update_probability_bars(self):
        """更新概率条形图"""
        for widget in self.prob_bars_frame.winfo_children():
            widget.destroy()
        
        sorted_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for disease, prob in sorted_diseases:
            disease_frame = tk.Frame(self.prob_bars_frame, bg='white')
            disease_frame.pack(fill=tk.X, pady=8)
            
            # 疾病名
            tk.Label(
                disease_frame,
                text=disease,
                font=('Arial', 11, 'bold'),
                bg='white',
                width=10,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=8)
            
            # 概率条
            bar_container = tk.Frame(disease_frame, bg='#E0E0E0', 
                                    width=280, height=30, relief=tk.SUNKEN)
            bar_container.pack(side=tk.LEFT, padx=8)
            bar_container.pack_propagate(False)
            
            bar_width = int(280 * prob)
            color = self.diseases[disease]['color']
            
            bar = tk.Frame(bar_container, bg=color, width=bar_width, height=30)
            bar.place(x=0, y=0)
            
            # 百分比
            tk.Label(
                disease_frame,
                text=f"{prob*100:.2f}%",
                font=('Arial', 11, 'bold'),
                bg='white',
                width=7,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=8)
        
    def on_symptom_selected(self, event=None):
        """症状选择时显示条件概率"""
        symptom = self.symptom_var.get()
        if not symptom or symptom not in self.symptom_probabilities:
            return
        
        for widget in self.cond_prob_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.cond_prob_frame,
            text=f"P(症状|疾病) - 条件概率",
            font=('Arial', 11, 'bold'),
            bg='white',
            pady=5
        ).pack()
        
        for disease in self.diseases.keys():
            prob = self.symptom_probabilities[symptom][disease]
            
            frame = tk.Frame(self.cond_prob_frame, bg='white')
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(
                frame,
                text=f"P({symptom}|{disease})",
                font=('Courier', 11),
                bg='white',
                width=26,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=f"= {prob:.2f}",
                font=('Courier', 11, 'bold'),
                bg='white',
                fg=self.diseases[disease]['color'],
                width=10
            ).pack(side=tk.LEFT)
        
    def process_symptom(self, has_symptom):
        """处理症状回答"""
        symptom = self.symptom_var.get()
        
        if not symptom:
            messagebox.showwarning("提示", "请先选择一个症状！")
            return
        
        if symptom in self.asked_symptoms:
            messagebox.showwarning("提示", "这个症状已经询问过了！")
            return
        
        # 记录
        self.asked_symptoms.append(symptom)
        self.symptom_responses[symptom] = has_symptom
        
        # 保存旧概率
        old_probs = self.current_probabilities.copy()
        
        # 贝叶斯更新
        self.bayesian_update(symptom, has_symptom, old_probs)
        
        # 更新显示
        self.update_probability_bars()
        self.update_ai_tip()
        self.update_viz()
        
        # 更新可用症状
        remaining = [s for s in self.symptom_probabilities.keys() 
                    if s not in self.asked_symptoms]
        self.symptom_combo['values'] = remaining
        if remaining:
            self.symptom_var.set(remaining[0])
            self.on_symptom_selected()
        else:
            self.symptom_var.set('')
        
    def bayesian_update(self, symptom, has_symptom, old_probs):
        """贝叶斯更新并生成详细说明"""
        response = "有" if has_symptom else "无"
        
        # 生成详细步骤
        if self.show_steps_var.get():
            steps = f"\n{'='*75}\n"
            steps += f"第 {len(self.asked_symptoms)} 次更新: 患者【{response}】症状「{symptom}」\n"
            steps += f"{'='*75}\n\n"
            
            steps += "步骤1: 初始概率\n" + "-"*75 + "\n"
            for disease in self.diseases.keys():
                steps += f"  P({disease}) = {old_probs[disease]:.4f}\n"
            
            steps += f"\n步骤2: 条件概率\n" + "-"*75 + "\n"
            likelihoods = {}
            for disease in self.diseases.keys():
                cond_prob = self.symptom_probabilities[symptom][disease]
                likelihood = cond_prob if has_symptom else (1 - cond_prob)
                likelihoods[disease] = likelihood
                if has_symptom:
                    steps += f"  P({symptom}|{disease}) = {likelihood:.4f}\n"
                else:
                    steps += f"  P(无{symptom}|{disease}) = {likelihood:.4f}\n"
            
            steps += f"\n步骤3: 中间结果（条件概率 × 初始概率）\n" + "-"*75 + "\n"
            unnormalized = {}
            for disease in self.diseases.keys():
                unnorm = likelihoods[disease] * old_probs[disease]
                unnormalized[disease] = unnorm
                steps += f"  {disease}: {likelihoods[disease]:.4f} × {old_probs[disease]:.4f} = {unnorm:.6f}\n"
            
            total = sum(unnormalized.values())
            steps += f"\n步骤4: 总和（所有中间结果相加）\n" + "-"*75 + "\n"
            steps += f"  总和 = {total:.6f}\n"
            
            steps += f"\n步骤5: 最终概率（中间结果 ÷ 总和）\n" + "-"*75 + "\n"
            for disease in self.diseases.keys():
                new_prob = unnormalized[disease] / total
                self.current_probabilities[disease] = new_prob
                change = new_prob - old_probs[disease]
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                steps += f"  P({disease}|症状) = {unnormalized[disease]:.6f} / {total:.6f}\n"
                steps += f"                    = {new_prob:.4f} ({new_prob*100:.2f}%) {arrow} {abs(change)*100:.2f}%\n"
            
            steps += f"\n" + "="*75 + "\n"
            
            self.steps_display.config(state=tk.NORMAL)
            self.steps_display.delete(1.0, tk.END)
            self.steps_display.insert(1.0, steps)
            self.steps_display.config(state=tk.DISABLED)
        else:
            # 直接计算
            unnormalized = {}
            for disease in self.diseases.keys():
                cond_prob = self.symptom_probabilities[symptom][disease]
                like_value = cond_prob if has_symptom else (1 - cond_prob)
                unnormalized[disease] = like_value * old_probs[disease]
            
            total = sum(unnormalized.values())
            for disease in self.diseases.keys():
                self.current_probabilities[disease] = unnormalized[disease] / total
        
        # 保存历史
        self.calculation_history.append({
            'step': len(self.asked_symptoms),
            'symptom': symptom,
            'has_symptom': has_symptom,
            'probabilities': self.current_probabilities.copy()
        })
        
    def update_ai_tip(self):
        """更新AI提示"""
        num_asked = len(self.asked_symptoms)
        
        if num_asked == 0:
            tip = "💡 开始诊断：选择一个症状询问患者"
        elif num_asked == 1:
            tip = "💡 观察概率变化：看看贝叶斯定理如何更新概率"
        elif num_asked == 2:
            tip = "💡 继续收集证据：每次询问都会让诊断更准确"
        else:
            most_likely = max(self.current_probabilities.items(), key=lambda x: x[1])
            if most_likely[1] > 0.70:
                tip = f"💡 诊断建议：{most_likely[0]}的概率已达{most_likely[1]*100:.1f}%，可以考虑给出诊断"
            elif most_likely[1] > 0.50:
                tip = f"💡 继续询问：当前最可能是{most_likely[0]}({most_likely[1]*100:.1f}%)，但建议继续收集证据"
            else:
                tip = f"💡 概率较分散：需要更多症状来明确诊断"
        
        self.ai_tip_label.config(text=tip)
        
    def update_viz(self):
        """更新可视化"""
        self.current_viz_step = len(self.calculation_history) - 1
        self.draw_viz()
        
    def draw_viz(self):
        """绘制可视化"""
        self.viz_canvas.delete('all')
        
        if not self.calculation_history:
            self.viz_canvas.create_text(
                400, 200,
                text="还没有数据，请在‘互动诊断’里至少询问一个症状",
                font=('Arial', 12),
                fill='gray'
            )
            return
        if self.current_viz_step < 0:
            self.current_viz_step = 0
        
        w = self.viz_canvas.winfo_width()
        h = self.viz_canvas.winfo_height()
        if w <= 1: w = 800
        if h <= 1: h = 500
        
        step_data = self.calculation_history[self.current_viz_step]
        probs = step_data['probabilities']
        
        # 标题
        title = f"步骤 {step_data['step']}"
        if step_data['step'] > 0:
            symptom = step_data['symptom']
            has = "有" if step_data['has_symptom'] else "无"
            title += f": {has}{symptom}"
        else:
            title += ": 初始先验概率"
        
        self.viz_canvas.create_text(
            w//2, 30,
            text=title,
            font=('Arial', 16, 'bold')
        )
        
        # 绘制条形图
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        bar_height = 60
        spacing = 30
        start_y = 80
        max_width = w - 300
        
        for i, (disease, prob) in enumerate(sorted_probs):
            y = start_y + i * (bar_height + spacing)
            
            self.viz_canvas.create_text(
                20, y + bar_height//2,
                text=disease,
                font=('Arial', 14, 'bold'),
                anchor=tk.W
            )
            
            bar_width = max(max_width * prob, 2)
            color = self.diseases[disease]['color']
            
            self.viz_canvas.create_rectangle(
                150, y+5,
                150+bar_width, y+bar_height-5,
                fill=color,
                outline='black',
                width=2
            )
            
            self.viz_canvas.create_text(
                150+bar_width+10, y+bar_height//2,
                text=f"{prob*100:.2f}%",
                font=('Arial', 13, 'bold'),
                anchor=tk.W
            )
        
        total = len(self.calculation_history)
        self.viz_step_label.config(text=f"步骤: {self.current_viz_step} / {total-1}")
        
    def viz_first(self):
        """第一步"""
        self.current_viz_step = 0
        self.draw_viz()
        
    def viz_previous(self):
        """上一步"""
        if self.current_viz_step > 0:
            self.current_viz_step -= 1
            self.draw_viz()
        
    def viz_next(self):
        """下一步"""
        if self.current_viz_step < len(self.calculation_history) - 1:
            self.current_viz_step += 1
            self.draw_viz()
        
    def viz_last(self):
        """最后一步"""
        self.current_viz_step = len(self.calculation_history) - 1
        self.draw_viz()
        
    def viz_auto_play(self):
        """自动播放"""
        if self.viz_is_playing:
            return
        self.viz_is_playing = True
        
        def play_step(step):
            if not self.viz_is_playing:
                return
            if step < len(self.calculation_history):
                self.current_viz_step = step
                self.draw_viz()
                self.viz_after_handle = self.root.after(self.animation_speed, lambda: play_step(step + 1))
            else:
                self.viz_is_playing = False
                self.viz_after_handle = None
        
        play_step(0)

    def viz_stop(self):
        """停止自动播放"""
        self.viz_is_playing = False
        if self.viz_after_handle is not None:
            try:
                self.root.after_cancel(self.viz_after_handle)
            except Exception:
                pass
            self.viz_after_handle = None
        
    def generate_manual_question(self):
        """生成手动计算题"""
        symptom = random.choice(list(self.symptom_probabilities.keys()))
        has_symptom = random.choice([True, False])
        
        priors = {d: info['prior'] for d, info in self.diseases.items()}
        
        response = "有" if has_symptom else "没有"
        question = f"题目：\n\n"
        question += f"患者主诉咳嗽。医生询问：「您{symptom}吗？」\n"
        question += f"患者回答：「{response}。」\n\n"
        question += f"已知先验概率：\n"
        for disease, prob in priors.items():
            question += f"  P({disease}) = {prob:.2f}\n"
        question += f"\n已知条件概率：\n"
        for disease in self.diseases.keys():
            cond_prob = self.symptom_probabilities[symptom][disease]
            question += f"  P({symptom}|{disease}) = {cond_prob:.2f}\n"
        question += f"\n请计算患者{response}{symptom}后，各疾病的后验概率。"
        
        self.manual_question_text.config(state=tk.NORMAL)
        self.manual_question_text.delete(1.0, tk.END)
        self.manual_question_text.insert(1.0, question)
        self.manual_question_text.config(state=tk.DISABLED)
        
        # 计算答案
        unnormalized = {}
        for disease in self.diseases.keys():
            cond_prob = self.symptom_probabilities[symptom][disease]
            likelihood = cond_prob if has_symptom else (1 - cond_prob)
            unnormalized[disease] = likelihood * priors[disease]
        
        total = sum(unnormalized.values())
        correct_answers = {d: unnormalized[d]/total for d in self.diseases.keys()}
        
        self.current_manual_exercise = {
            'symptom': symptom,
            'has_symptom': has_symptom,
            'unnormalized': unnormalized,
            'total': total,
            'answers': correct_answers
        }
        
        # 清空输入
        for entry in self.manual_entries.values():
            entry.delete(0, tk.END)
        self.manual_sum_entry.delete(0, tk.END)
        
        self.manual_feedback.config(state=tk.NORMAL)
        self.manual_feedback.delete(1.0, tk.END)
        self.manual_feedback.insert(1.0, "完成计算后点击「提交答案」")
        self.manual_feedback.config(state=tk.DISABLED)
        
    def check_manual_answer(self):
        """检查手动计算答案"""
        if not self.current_manual_exercise:
            return
        
        try:
            feedback = "="*70 + "\n答案检查\n" + "="*70 + "\n\n"
            all_correct = True
            tol = 0.0001
            
            # 检查中间结果
            feedback += "步骤1: 中间结果（条件概率 × 先验概率）\n" + "-"*70 + "\n"
            for disease in self.diseases.keys():
                user = self.manual_entries[f'unnorm_{disease}'].get()
                correct = self.current_manual_exercise['unnormalized'][disease]
                
                if user:
                    user_val = float(user)
                    is_correct = abs(user_val - correct) < tol
                    if is_correct:
                        feedback += f"✓ {disease}: {user_val:.4f} 正确\n"
                    else:
                        feedback += f"✗ {disease}: 你的{user_val:.4f}, 正确{correct:.4f}\n"
                        all_correct = False
                else:
                    feedback += f"✗ {disease}: 未填写, 正确{correct:.4f}\n"
                    all_correct = False
            
            # 检查总和
            feedback += f"\n步骤2: 中间结果的总和\n" + "-"*70 + "\n"
            user_sum = self.manual_sum_entry.get()
            correct_sum = self.current_manual_exercise['total']
            
            if user_sum:
                user_sum_val = float(user_sum)
                if abs(user_sum_val - correct_sum) < tol:
                    feedback += f"✓ 总和: {user_sum_val:.4f} 正确\n"
                else:
                    feedback += f"✗ 总和: 你的{user_sum_val:.4f}, 正确{correct_sum:.4f}\n"
                    all_correct = False
            else:
                feedback += f"✗ 总和: 未填写, 正确{correct_sum:.4f}\n"
                all_correct = False
            
            # 检查最终概率
            feedback += f"\n步骤3: 最终概率（中间结果 ÷ 总和）\n" + "-"*70 + "\n"
            for disease in self.diseases.keys():
                user = self.manual_entries[f'post_{disease}'].get()
                correct = self.current_manual_exercise['answers'][disease]
                
                if user:
                    user_val = float(user)
                    if abs(user_val - correct) < tol:
                        feedback += f"✓ P({disease}|症状): {user_val:.4f} 正确\n"
                    else:
                        feedback += f"✗ P({disease}|症状): 你的{user_val:.4f}, 正确{correct:.4f}\n"
                        all_correct = False
                else:
                    feedback += f"✗ P({disease}|症状): 未填写, 正确{correct:.4f}\n"
                    all_correct = False
            
            feedback += "\n" + "="*70 + "\n"
            if all_correct:
                feedback += "🎉 完全正确！你已经掌握了贝叶斯计算方法！\n"
                messagebox.showinfo("正确", "答案完全正确！")
            else:
                feedback += "💪 继续努力！重新检查计算步骤。\n"
            feedback += "="*70 + "\n"
            
            self.manual_feedback.config(state=tk.NORMAL)
            self.manual_feedback.delete(1.0, tk.END)
            self.manual_feedback.insert(1.0, feedback)
            self.manual_feedback.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        
    def next_quiz(self):
        """生成下一题"""
        symptom = random.choice(list(self.symptom_probabilities.keys()))
        disease = random.choice(list(self.diseases.keys()))
        has_symptom = random.choice([True, False])
        
        response = "有" if has_symptom else "无"
        question = f"计算题：\n\n"
        question += f"已知先验概率：\n"
        for d in self.diseases.keys():
            question += f"  P({d}) = {self.diseases[d]['prior']:.2f}\n"
        question += f"\n已知条件概率：\n"
        for d in self.diseases.keys():
            question += f"  P({symptom}|{d}) = {self.symptom_probabilities[symptom][d]:.2f}\n"
        question += f"\n问题：如果患者{response}{symptom}，\n"
        question += f"请计算 P({disease}|症状) = ?\n"
        question += f"\n(保留4位小数，如: 0.1234)"
        
        self.quiz_question_text.config(state=tk.NORMAL)
        self.quiz_question_text.delete(1.0, tk.END)
        self.quiz_question_text.insert(1.0, question)
        self.quiz_question_text.config(state=tk.DISABLED)
        
        # 计算答案
        priors = {d: info['prior'] for d, info in self.diseases.items()}
        unnormalized = {}
        for d in self.diseases.keys():
            cond = self.symptom_probabilities[symptom][d]
            likelihood = cond if has_symptom else (1 - cond)
            unnormalized[d] = likelihood * priors[d]
        
        total = sum(unnormalized.values())
        answer = unnormalized[disease] / total
        
        self.current_quiz = {
            'symptom': symptom,
            'disease': disease,
            'has_symptom': has_symptom,
            'answer': answer
        }
        
        self.quiz_answer_entry.delete(0, tk.END)
        self.quiz_explanation.config(state=tk.NORMAL)
        self.quiz_explanation.delete(1.0, tk.END)
        self.quiz_explanation.config(state=tk.DISABLED)
        
    def check_quiz_answer(self):
        """检查测验答案"""
        if not self.current_quiz:
            return
        
        user_answer = self.quiz_answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("提示", "请输入答案！")
            return
        
        try:
            user_val = float(user_answer)
            correct_val = self.current_quiz['answer']
            
            self.quiz_score['total'] += 1
            is_correct = abs(user_val - correct_val) < 0.001
            
            if is_correct:
                self.quiz_score['correct'] += 1
                messagebox.showinfo("正确", f"回答正确！答案是{correct_val:.4f}")
            else:
                messagebox.showinfo("错误", f"回答错误。\n你的答案：{user_val:.4f}\n正确答案：{correct_val:.4f}")
            
            # 更新得分
            rate = self.quiz_score['correct'] / self.quiz_score['total'] * 100
            self.quiz_score_label.config(
                text=f"得分: {self.quiz_score['correct']} / {self.quiz_score['total']}  "
                     f"(正确率: {rate:.1f}%)"
            )
            
            # 显示解析
            explanation = "="*70 + "\n详细解析\n" + "="*70 + "\n\n"
            explanation += f"这是一道标准的贝叶斯后验概率计算题。\n\n"
            explanation += "详细步骤请参考「公式详解」标签页。\n"
            explanation += f"\n正确答案：{correct_val:.4f}"
            
            self.quiz_explanation.config(state=tk.NORMAL)
            self.quiz_explanation.delete(1.0, tk.END)
            self.quiz_explanation.insert(1.0, explanation)
            self.quiz_explanation.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效数字！")
        
    def show_quiz_hint(self):
        """显示提示"""
        if self.current_quiz:
            hint = "提示：\n\n"
            hint += "1. 先算每个疾病的中间结果 = 条件概率 × 初始概率\n"
            hint += "2. 把所有中间结果相加得到总和\n"
            hint += "3. 用中间结果除以总和，得到最终概率"
            messagebox.showinfo("提示", hint)
        
    def show_ai_recommendation(self):
        """显示AI推荐"""
        remaining = [s for s in self.symptom_probabilities.keys() 
                    if s not in self.asked_symptoms]
        
        if not remaining:
            messagebox.showinfo("AI推荐", "已询问所有症状")
            return
        
        # 计算信息增益（简化版）
        best_symptom = None
        max_variance = 0
        
        top_diseases = sorted(self.current_probabilities.items(), 
                             key=lambda x: x[1], reverse=True)[:2]
        
        for symptom in remaining:
            probs = [self.symptom_probabilities[symptom][d] for d, _ in top_diseases]
            variance = abs(probs[0] - probs[1])
            if variance > max_variance:
                max_variance = variance
                best_symptom = symptom
        
        if best_symptom:
            self.symptom_var.set(best_symptom)
            self.on_symptom_selected()
            
            msg = f"🤖 AI推荐询问：{best_symptom}\n\n"
            msg += "这个症状最能区分当前的疑似疾病。"
            messagebox.showinfo("AI推荐", msg)
        
    def show_calculation_history(self):
        """显示计算历史"""
        if len(self.calculation_history) <= 1:
            messagebox.showinfo("提示", "还没有进行诊断")
            return
        
        window = tk.Toplevel(self.root)
        window.title("计算历史")
        window.geometry("900x700")
        
        tk.Label(
            window,
            text="完整计算历史",
            font=('Arial', 16, 'bold'),
            pady=15
        ).pack()
        
        text = scrolledtext.ScrolledText(
            window,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        history_text = ""
        for i, step in enumerate(self.calculation_history):
            if i == 0:
                history_text += f"初始状态：先验概率\n"
            else:
                symptom = step['symptom']
                has = "有" if step['has_symptom'] else "无"
                history_text += f"\n第{i}次更新：{has}{symptom}\n"
            
            history_text += "-"*70 + "\n"
            for disease, prob in step['probabilities'].items():
                history_text += f"  {disease}: {prob:.4f} ({prob*100:.2f}%)\n"
            history_text += "\n"
        
        text.insert(1.0, history_text)
        text.config(state=tk.DISABLED)
        
        tk.Button(
            window,
            text="关闭",
            font=('Arial', 12, 'bold'),
            bg='#95A5A6',
            fg='white',
            command=window.destroy,
            width=15
        ).pack(pady=10)
        
    def finalize_diagnosis(self):
        """完成诊断"""
        if not self.asked_symptoms:
            messagebox.showinfo("提示", "请至少询问一个症状")
            return
        
        most_likely = max(self.current_probabilities.items(), key=lambda x: x[1])
        
        result = f"{'='*60}\n诊断报告\n{'='*60}\n\n"
        result += f"最可能诊断：{most_likely[0]}\n"
        result += f"置信度：{most_likely[1]*100:.2f}%\n\n"
        result += f"询问了{len(self.asked_symptoms)}个症状：\n"
        for symptom in self.asked_symptoms:
            response = "有" if self.symptom_responses[symptom] else "无"
            result += f"  • {symptom}：{response}\n"
        result += f"\n完整概率分布：\n"
        sorted_probs = sorted(self.current_probabilities.items(), 
                             key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_probs:
            result += f"  • {disease}：{prob*100:.2f}%\n"
        result += f"\n{'='*60}\n"
        
        # 记录统计
        self.game_stats['total_games'] += 1
        self.game_stats['total_questions'] += len(self.asked_symptoms)
        self.game_stats['game_records'].append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'diagnosis': most_likely[0],
            'questions': len(self.asked_symptoms),
            'confidence': most_likely[1]
        })
        
        self.update_stats_display()
        
        messagebox.showinfo("诊断结果", result)
        
        if messagebox.askyesno("继续", "开始新的诊断？"):
            self.reset_game()
        
    def update_stats_display(self):
        """更新统计显示"""
        total = self.game_stats['total_games']
        
        self.stat_labels['total_games'].config(text=str(total))
        
        if total > 0:
            avg = self.game_stats['total_questions'] / total
            self.stat_labels['avg_questions'].config(text=f"{avg:.1f}")
            
            # 更新主统计栏
            self.stats_label.config(text=f"游戏次数: {total} | 平均询问: {avg:.1f}")
            
            # 更新历史表格
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            for i, record in enumerate(reversed(self.game_stats['game_records']), 1):
                self.history_tree.insert('', 'end', values=(
                    i,
                    record['time'],
                    record['diagnosis'],
                    record['questions'],
                    '-',
                    f"{record['confidence']*100:.1f}%"
                ))
        
    def on_mode_change(self):
        """模式改变"""
        mode = self.game_mode.get()
        messagebox.showinfo("模式", f"切换到：{mode}")
        
    def on_difficulty_change(self):
        """难度改变"""
        self.setup_difficulty()
        self.reset_game()
        messagebox.showinfo("难度", f"难度设置为：{self.difficulty.get()}")
        
    def reset_game(self):
        """重置游戏"""
        self.reset_probabilities()
        self.asked_symptoms = []
        self.symptom_responses = {}
        
        self.symptom_combo['values'] = list(self.symptom_probabilities.keys())
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
            self.on_symptom_selected()
        
        self.steps_display.config(state=tk.NORMAL)
        self.steps_display.delete(1.0, tk.END)
        self.steps_display.config(state=tk.DISABLED)
        
        self.update_probability_bars()
        self.update_ai_tip()
        self.update_viz()


def main():
    root = tk.Tk()
    app = BayesianDiagnosisGame(root)
    
    root.update()
    app.draw_viz()
    
    root.mainloop()


if __name__ == '__main__':
    main()

