"""
贝叶斯咳嗽诊断游戏 - 教学版
专注于帮助学习者理解和掌握贝叶斯公式
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from typing import Dict, List, Tuple
from datetime import datetime


class BayesianEducationalGame:
    def __init__(self, root):
        self.root = root
        self.root.title("贝叶斯诊断游戏 - 教学版")
        self.root.geometry("1500x950")
        self.root.configure(bg='#ECF0F1')
        
        # 教学模式设置
        self.teaching_mode = tk.StringVar(value='学习模式')
        self.show_step_by_step = tk.BooleanVar(value=True)
        self.auto_calculate = tk.BooleanVar(value=False)
        
        # 疾病数据（简化为3个疾病便于教学）
        self.diseases = {
            '普通感冒': {
                'prior': 0.50,
                'color': '#FF6B6B',
                'description': '最常见的呼吸道感染',
            },
            '流感': {
                'prior': 0.30,
                'color': '#4ECDC4',
                'description': '症状更严重的病毒性感染',
            },
            '肺炎': {
                'prior': 0.20,
                'color': '#FFA07A',
                'description': '肺部感染，需要及时治疗',
            }
        }
        
        # 症状条件概率（简化数据用于教学）
        self.symptom_probabilities = {
            '发烧': {
                '普通感冒': 0.30,
                '流感': 0.90,
                '肺炎': 0.85
            },
            '流鼻涕': {
                '普通感冒': 0.80,
                '流感': 0.40,
                '肺炎': 0.20
            },
            '喉咙痛': {
                '普通感冒': 0.70,
                '流感': 0.60,
                '肺炎': 0.30
            },
            '呼吸困难': {
                '普通感冒': 0.10,
                '流感': 0.35,
                '肺炎': 0.75
            },
            '胸痛': {
                '普通感冒': 0.05,
                '流感': 0.25,
                '肺炎': 0.65
            },
            '咳痰': {
                '普通感冒': 0.40,
                '流感': 0.50,
                '肺炎': 0.85
            }
        }
        
        # 游戏状态
        self.current_probabilities = {}
        self.asked_symptoms = []
        self.symptom_responses = {}
        self.calculation_steps = []
        self.quiz_score = {'correct': 0, 'total': 0}
        
        self.reset_probabilities()
        self.create_interface()
        
    def reset_probabilities(self):
        """重置为先验概率"""
        self.current_probabilities = {
            disease: info['prior'] 
            for disease, info in self.diseases.items()
        }
        self.calculation_steps = [{
            'step': 0,
            'description': '初始先验概率',
            'probabilities': self.current_probabilities.copy()
        }]
        
    def create_interface(self):
        """创建界面"""
        # 顶部标题
        title_frame = tk.Frame(self.root, bg='#2C3E50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎓 贝叶斯诊断游戏 - 教学版 🎓",
            font=('Arial', 26, 'bold'),
            bg='#2C3E50',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # 模式选择栏
        mode_frame = tk.Frame(self.root, bg='#34495E', height=50)
        mode_frame.pack(fill=tk.X)
        mode_frame.pack_propagate(False)
        
        tk.Label(
            mode_frame,
            text="教学模式：",
            font=('Arial', 12, 'bold'),
            bg='#34495E',
            fg='white'
        ).pack(side=tk.LEFT, padx=20)
        
        modes = ['学习模式', '练习模式', '测验模式']
        for mode in modes:
            tk.Radiobutton(
                mode_frame,
                text=mode,
                variable=self.teaching_mode,
                value=mode,
                font=('Arial', 11),
                bg='#34495E',
                fg='white',
                selectcolor='#2C3E50',
                command=self.on_mode_change
            ).pack(side=tk.LEFT, padx=10)
        
        tk.Checkbutton(
            mode_frame,
            text="显示详细步骤",
            variable=self.show_step_by_step,
            font=('Arial', 11),
            bg='#34495E',
            fg='white',
            selectcolor='#2C3E50'
        ).pack(side=tk.LEFT, padx=20)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页1: 交互式教学
        self.interactive_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.interactive_tab, text='🎯 互动诊断')
        self.create_interactive_tab()
        
        # 标签页2: 公式详解
        self.formula_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.formula_tab, text='📐 公式详解')
        self.create_formula_tab()
        
        # 标签页3: 手动计算
        self.manual_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.manual_tab, text='✍️ 手动计算')
        self.create_manual_calculation_tab()
        
        # 标签页4: 可视化演示
        self.visualization_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.visualization_tab, text='📊 可视化')
        self.create_visualization_tab()
        
        # 标签页5: 练习题
        self.exercise_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.exercise_tab, text='📝 练习题')
        self.create_exercise_tab()
        
    def create_interactive_tab(self):
        """创建交互式诊断标签页"""
        # 左侧：概率显示
        left_frame = tk.Frame(self.interactive_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        tk.Label(
            left_frame,
            text="🎯 当前概率分布",
            font=('Arial', 16, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        # 概率显示区域
        self.prob_display_frame = tk.Frame(left_frame, bg='white')
        self.prob_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.create_probability_bars()
        
        # 右侧：操作区域
        right_frame = tk.Frame(self.interactive_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        tk.Label(
            right_frame,
            text="🔍 诊断过程",
            font=('Arial', 16, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        # 教学提示区
        tip_frame = tk.Frame(right_frame, bg='#FFF9E6', relief=tk.RIDGE, borderwidth=2)
        tip_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            tip_frame,
            text="💡 学习提示",
            font=('Arial', 13, 'bold'),
            bg='#FFF9E6',
            fg='#F39C12'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        self.teaching_tip_label = tk.Label(
            tip_frame,
            text="贝叶斯定理通过不断更新先验概率来进行推理。\n选择一个症状开始诊断！",
            font=('Arial', 11),
            bg='#FFF9E6',
            wraplength=450,
            justify=tk.LEFT
        )
        self.teaching_tip_label.pack(padx=10, pady=10)
        
        # 症状选择
        symptom_frame = tk.Frame(right_frame, bg='white')
        symptom_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(
            symptom_frame,
            text="选择症状：",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, pady=5)
        
        self.symptom_var = tk.StringVar()
        self.symptom_combo = ttk.Combobox(
            symptom_frame,
            textvariable=self.symptom_var,
            values=list(self.symptom_probabilities.keys()),
            state='readonly',
            font=('Arial', 12),
            width=35
        )
        self.symptom_combo.pack(pady=5, fill=tk.X)
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
        self.symptom_combo.bind('<<ComboboxSelected>>', self.on_symptom_selected)
        
        # 显示该症状的条件概率
        self.symptom_info_frame = tk.Frame(right_frame, bg='#E8F8F5', relief=tk.RIDGE, borderwidth=2)
        self.symptom_info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 症状响应按钮
        response_frame = tk.Frame(right_frame, bg='white')
        response_frame.pack(pady=15)
        
        tk.Label(
            response_frame,
            text="患者回答：",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        button_frame = tk.Frame(response_frame, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="✓ 有此症状",
            font=('Arial', 14, 'bold'),
            bg='#27AE60',
            fg='white',
            width=15,
            height=2,
            command=lambda: self.process_response(True)
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="✗ 无此症状",
            font=('Arial', 14, 'bold'),
            bg='#E74C3C',
            fg='white',
            width=15,
            height=2,
            command=lambda: self.process_response(False)
        ).pack(side=tk.LEFT, padx=10)
        
        # 计算步骤显示
        tk.Label(
            right_frame,
            text="📝 贝叶斯更新步骤",
            font=('Arial', 13, 'bold'),
            bg='white',
            pady=5
        ).pack()
        
        self.steps_text = scrolledtext.ScrolledText(
            right_frame,
            font=('Courier', 10),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=12,
            state=tk.DISABLED
        )
        self.steps_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 底部按钮
        bottom_frame = tk.Frame(right_frame, bg='white')
        bottom_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(
            bottom_frame,
            text="🔄 重新开始",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.reset_game,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="📖 查看所有步骤",
            font=('Arial', 11, 'bold'),
            bg='#9B59B6',
            fg='white',
            command=self.show_all_steps,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="🎓 完成诊断",
            font=('Arial', 11, 'bold'),
            bg='#F39C12',
            fg='white',
            command=self.finalize_diagnosis,
            width=12
        ).pack(side=tk.RIGHT, padx=5)
        
    def create_formula_tab(self):
        """创建公式详解标签页"""
        # 创建滚动文本
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
            text="📐 贝叶斯定理完全解析",
            font=('Arial', 20, 'bold'),
            bg='white',
            pady=20
        ).pack()
        
        # 第1部分：基本公式
        section1 = tk.Frame(scrollable_frame, bg='#E8F6F3', relief=tk.RAISED, borderwidth=2)
        section1.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            section1,
            text="1️⃣ 贝叶斯定理基本形式",
            font=('Arial', 16, 'bold'),
            bg='#E8F6F3',
            fg='#16A085'
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        formula1 = """
P(A|B) = P(B|A) × P(A) / P(B)

各部分含义：
• P(A|B)：后验概率 - 在事件B发生的条件下，事件A发生的概率
• P(B|A)：似然度 - 在事件A发生的条件下，事件B发生的概率  
• P(A)：先验概率 - 事件A本身发生的概率
• P(B)：边缘概率 - 事件B本身发生的概率（归一化常数）
"""
        tk.Label(
            section1,
            text=formula1,
            font=('Courier', 12),
            bg='white',
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=15,
            pady=10
        ).pack(padx=20, pady=10)
        
        # 第2部分：医学诊断应用
        section2 = tk.Frame(scrollable_frame, bg='#FEF5E7', relief=tk.RAISED, borderwidth=2)
        section2.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            section2,
            text="2️⃣ 应用于医学诊断",
            font=('Arial', 16, 'bold'),
            bg='#FEF5E7',
            fg='#D68910'
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        formula2 = """
P(疾病|症状) = P(症状|疾病) × P(疾病) / P(症状)

示例：计算"有发烧症状时患流感的概率"

已知信息：
• P(流感) = 0.30                    [先验概率：流感的基础发病率]
• P(发烧|流感) = 0.90               [似然度：流感患者发烧的概率]
• P(发烧) = ?                       [需要计算]

计算P(发烧)（全概率公式）：
P(发烧) = P(发烧|感冒)×P(感冒) + P(发烧|流感)×P(流感) + P(发烧|肺炎)×P(肺炎)
        = 0.30×0.50 + 0.90×0.30 + 0.85×0.20
        = 0.15 + 0.27 + 0.17
        = 0.59

代入贝叶斯公式：
P(流感|发烧) = P(发烧|流感) × P(流感) / P(发烧)
             = 0.90 × 0.30 / 0.59
             = 0.27 / 0.59
             = 0.458  (45.8%)

结论：患者有发烧症状时，患流感的概率从30%上升到45.8%
"""
        tk.Label(
            section2,
            text=formula2,
            font=('Courier', 11),
            bg='white',
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=15,
            pady=10
        ).pack(padx=20, pady=10)
        
        # 第3部分：归一化
        section3 = tk.Frame(scrollable_frame, bg='#FADBD8', relief=tk.RAISED, borderwidth=2)
        section3.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            section3,
            text="3️⃣ 归一化处理",
            font=('Arial', 16, 'bold'),
            bg='#FADBD8',
            fg='#A93226'
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        formula3 = """
当同时计算多个疾病的后验概率时，可以简化计算：

P(疾病ᵢ|症状) = P(症状|疾病ᵢ) × P(疾病ᵢ) / Σ[P(症状|疾病ⱼ) × P(疾病ⱼ)]
                                            j=所有疾病

步骤：
1. 计算每个疾病的未归一化概率：
   未归一化(疾病ᵢ) = P(症状|疾病ᵢ) × P(疾病ᵢ)

2. 计算总和：
   总和 = Σ 未归一化(疾病ⱼ)
          j

3. 归一化：
   P(疾病ᵢ|症状) = 未归一化(疾病ᵢ) / 总和

示例（有发烧症状）：
┌──────────┬────────┬────────────┬──────────────┬────────────┐
│ 疾病     │ 先验   │ P(发烧|病) │ 未归一化     │ 后验概率   │
├──────────┼────────┼────────────┼──────────────┼────────────┤
│ 普通感冒 │ 0.50   │ 0.30       │ 0.50×0.30    │ 0.15/0.59  │
│          │        │            │ = 0.15       │ = 0.254    │
├──────────┼────────┼────────────┼──────────────┼────────────┤
│ 流感     │ 0.30   │ 0.90       │ 0.30×0.90    │ 0.27/0.59  │
│          │        │            │ = 0.27       │ = 0.458    │
├──────────┼────────┼────────────┼──────────────┼────────────┤
│ 肺炎     │ 0.20   │ 0.85       │ 0.20×0.85    │ 0.17/0.59  │
│          │        │            │ = 0.17       │ = 0.288    │
├──────────┼────────┼────────────┼──────────────┼────────────┤
│ 总和     │ 1.00   │ —          │ 0.59         │ 1.000      │
└──────────┴────────┴────────────┴──────────────┴────────────┘
"""
        tk.Label(
            section3,
            text=formula3,
            font=('Courier', 10),
            bg='white',
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=15,
            pady=10
        ).pack(padx=20, pady=10)
        
        # 第4部分：迭代更新
        section4 = tk.Frame(scrollable_frame, bg='#D6EAF8', relief=tk.RAISED, borderwidth=2)
        section4.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            section4,
            text="4️⃣ 迭代更新过程",
            font=('Arial', 16, 'bold'),
            bg='#D6EAF8',
            fg='#1F618D'
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        formula4 = """
多次观察症状的贝叶斯更新：

第1次观察（症状A）：
P₁(疾病) = P(症状A|疾病) × P₀(疾病) / Σ[P(症状A|疾病ⱼ) × P₀(疾病ⱼ)]

第2次观察（症状B）：
P₂(疾病) = P(症状B|疾病) × P₁(疾病) / Σ[P(症状B|疾病ⱼ) × P₁(疾病ⱼ)]

第n次观察（症状N）：
Pₙ(疾病) = P(症状N|疾病) × Pₙ₋₁(疾病) / Σ[P(症状N|疾病ⱼ) × Pₙ₋₁(疾病ⱼ)]

关键点：
• 每次更新后的后验概率成为下次更新的先验概率
• 随着观察到的症状增多，诊断越来越准确
• 不同症状的询问顺序不影响最终结果（数学上可证明）
"""
        tk.Label(
            section4,
            text=formula4,
            font=('Courier', 11),
            bg='white',
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=15,
            pady=10
        ).pack(padx=20, pady=10)
        
        # 第5部分：阴性结果
        section5 = tk.Frame(scrollable_frame, bg='#E8DAEF', relief=tk.RAISED, borderwidth=2)
        section5.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            section5,
            text="5️⃣ 处理阴性症状（没有某症状）",
            font=('Arial', 16, 'bold'),
            bg='#E8DAEF',
            fg='#7D3C98'
        ).pack(anchor=tk.W, padx=20, pady=10)
        
        formula5 = """
当患者没有某个症状时：

P(疾病|无症状) = P(无症状|疾病) × P(疾病) / P(无症状)
               = [1 - P(症状|疾病)] × P(疾病) / P(无症状)

示例：患者没有发烧

已知：
• P(流感) = 0.30
• P(发烧|流感) = 0.90
• 因此 P(无发烧|流感) = 1 - 0.90 = 0.10

计算：
┌──────────┬─────────────┬───────────────┬──────────────┬────────────┐
│ 疾病     │ P(疾病)     │ P(无发烧|病)  │ 未归一化     │ 后验概率   │
├──────────┼─────────────┼───────────────┼──────────────┼────────────┤
│ 普通感冒 │ 0.50        │ 1-0.30=0.70   │ 0.50×0.70    │ 0.35/0.47  │
│          │             │               │ = 0.35       │ = 0.745    │
├──────────┼─────────────┼───────────────┼──────────────┼────────────┤
│ 流感     │ 0.30        │ 1-0.90=0.10   │ 0.30×0.10    │ 0.03/0.47  │
│          │             │               │ = 0.03       │ = 0.064    │
├──────────┼─────────────┼───────────────┼──────────────┼────────────┤
│ 肺炎     │ 0.20        │ 1-0.85=0.15   │ 0.20×0.15    │ 0.09/0.47  │
│          │             │               │ = 0.09       │ = 0.191    │
├──────────┼─────────────┼───────────────┼──────────────┼────────────┤
│ 总和     │ 1.00        │ —             │ 0.47         │ 1.000      │
└──────────┴─────────────┴───────────────┴──────────────┴────────────┘

结论：患者无发烧时，流感的概率大幅下降（从30%降到6.4%），
      而普通感冒的概率上升（从50%升到74.5%）
"""
        tk.Label(
            section5,
            text=formula5,
            font=('Courier', 10),
            bg='white',
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=15,
            pady=10
        ).pack(padx=20, pady=10)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_manual_calculation_tab(self):
        """创建手动计算标签页"""
        tk.Label(
            self.manual_tab,
            text="✍️ 手动计算练习",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        ).pack()
        
        instruction = tk.Label(
            self.manual_tab,
            text="在这里，你可以手动输入计算结果，系统会检查你的答案是否正确",
            font=('Arial', 12),
            bg='#ECF0F1'
        )
        instruction.pack(pady=5)
        
        # 主容器
        main_container = tk.Frame(self.manual_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 场景设置
        scenario_frame = tk.Frame(main_container, bg='#E8F6F3', relief=tk.RIDGE, borderwidth=2)
        scenario_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            scenario_frame,
            text="📋 练习场景",
            font=('Arial', 14, 'bold'),
            bg='#E8F6F3',
            fg='#16A085'
        ).pack(pady=10)
        
        self.scenario_text = tk.Text(
            scenario_frame,
            font=('Arial', 11),
            height=8,
            wrap=tk.WORD,
            bg='white',
            state=tk.DISABLED
        )
        self.scenario_text.pack(padx=20, pady=10, fill=tk.X)
        
        tk.Button(
            scenario_frame,
            text="🎲 生成新练习",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.generate_manual_exercise,
            width=15
        ).pack(pady=10)
        
        # 计算区域
        calc_frame = tk.Frame(main_container, bg='white')
        calc_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧：输入区
        left_calc = tk.Frame(calc_frame, bg='#FEF5E7', relief=tk.RIDGE, borderwidth=2)
        left_calc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_calc,
            text="📝 你的计算",
            font=('Arial', 13, 'bold'),
            bg='#FEF5E7'
        ).pack(pady=10)
        
        # 步骤1：计算未归一化概率
        tk.Label(
            left_calc,
            text="步骤1：计算未归一化概率",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        self.manual_inputs = {}
        for disease in self.diseases.keys():
            frame = tk.Frame(left_calc, bg='#FEF5E7')
            frame.pack(fill=tk.X, padx=30, pady=5)
            
            tk.Label(
                frame,
                text=f"{disease}：",
                font=('Arial', 11),
                bg='#FEF5E7',
                width=12,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 11), width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.manual_inputs[f'unnorm_{disease}'] = entry
        
        # 步骤2：计算总和
        tk.Label(
            left_calc,
            text="步骤2：计算总和（归一化常数）",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        sum_frame = tk.Frame(left_calc, bg='#FEF5E7')
        sum_frame.pack(fill=tk.X, padx=30, pady=5)
        
        tk.Label(
            sum_frame,
            text="总和：",
            font=('Arial', 11),
            bg='#FEF5E7',
            width=12,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.manual_sum_entry = tk.Entry(sum_frame, font=('Arial', 11), width=15)
        self.manual_sum_entry.pack(side=tk.LEFT, padx=5)
        
        # 步骤3：计算后验概率
        tk.Label(
            left_calc,
            text="步骤3：计算归一化后的后验概率",
            font=('Arial', 11, 'bold'),
            bg='#FEF5E7'
        ).pack(anchor=tk.W, padx=20, pady=(15, 5))
        
        for disease in self.diseases.keys():
            frame = tk.Frame(left_calc, bg='#FEF5E7')
            frame.pack(fill=tk.X, padx=30, pady=5)
            
            tk.Label(
                frame,
                text=f"P({disease}|症状)：",
                font=('Arial', 11),
                bg='#FEF5E7',
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=('Arial', 11), width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.manual_inputs[f'posterior_{disease}'] = entry
        
        # 提交按钮
        tk.Button(
            left_calc,
            text="✅ 检查答案",
            font=('Arial', 13, 'bold'),
            bg='#27AE60',
            fg='white',
            command=self.check_manual_calculation,
            width=20,
            height=2
        ).pack(pady=20)
        
        # 右侧：反馈区
        right_calc = tk.Frame(calc_frame, bg='white', relief=tk.RIDGE, borderwidth=2)
        right_calc.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_calc,
            text="📊 反馈与正确答案",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(pady=10)
        
        self.feedback_text = scrolledtext.ScrolledText(
            right_calc,
            font=('Courier', 11),
            wrap=tk.WORD,
            bg='#F8F9FA',
            state=tk.DISABLED
        )
        self.feedback_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 初始化练习
        self.current_exercise = None
        self.generate_manual_exercise()
        
    def create_visualization_tab(self):
        """创建可视化标签页"""
        tk.Label(
            self.visualization_tab,
            text="📊 贝叶斯更新可视化",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        ).pack()
        
        # 说明
        tk.Label(
            self.visualization_tab,
            text="通过动画展示概率如何随着新证据的加入而更新",
            font=('Arial', 12),
            bg='#ECF0F1'
        ).pack()
        
        # 可视化画布
        viz_frame = tk.Frame(self.visualization_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.viz_canvas = tk.Canvas(
            viz_frame,
            bg='white',
            highlightthickness=0
        )
        self.viz_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 控制按钮
        control_frame = tk.Frame(self.visualization_tab, bg='#ECF0F1')
        control_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Button(
            control_frame,
            text="◀ 上一步",
            font=('Arial', 12, 'bold'),
            bg='#95A5A6',
            fg='white',
            command=self.viz_previous_step,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="▶ 下一步",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.viz_next_step,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🔄 重置",
            font=('Arial', 12, 'bold'),
            bg='#E74C3C',
            fg='white',
            command=self.viz_reset,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        self.viz_step_label = tk.Label(
            control_frame,
            text="当前步骤：0 / 0",
            font=('Arial', 12, 'bold'),
            bg='#ECF0F1'
        )
        self.viz_step_label.pack(side=tk.RIGHT, padx=20)
        
        self.current_viz_step = 0
        
    def create_exercise_tab(self):
        """创建练习题标签页"""
        tk.Label(
            self.exercise_tab,
            text="📝 贝叶斯公式练习题",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        ).pack()
        
        # 得分显示
        score_frame = tk.Frame(self.exercise_tab, bg='#2C3E50', height=60)
        score_frame.pack(fill=tk.X, padx=30, pady=10)
        score_frame.pack_propagate(False)
        
        self.score_label = tk.Label(
            score_frame,
            text=f"得分：{self.quiz_score['correct']} / {self.quiz_score['total']}",
            font=('Arial', 16, 'bold'),
            bg='#2C3E50',
            fg='white'
        )
        self.score_label.pack(expand=True)
        
        # 题目显示区
        question_frame = tk.Frame(self.exercise_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(
            question_frame,
            text="📌 当前题目",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.question_text = scrolledtext.ScrolledText(
            question_frame,
            font=('Arial', 12),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=10,
            state=tk.DISABLED
        )
        self.question_text.pack(fill=tk.X, padx=30, pady=10)
        
        # 答案输入
        answer_frame = tk.Frame(question_frame, bg='white')
        answer_frame.pack(pady=15)
        
        tk.Label(
            answer_frame,
            text="你的答案（保留4位小数）：",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        self.answer_entry = tk.Entry(
            answer_frame,
            font=('Arial', 13),
            width=20
        )
        self.answer_entry.pack(side=tk.LEFT, padx=10)
        self.answer_entry.bind('<Return>', lambda e: self.check_quiz_answer())
        
        # 按钮
        button_frame = tk.Frame(question_frame, bg='white')
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="✅ 提交答案",
            font=('Arial', 13, 'bold'),
            bg='#27AE60',
            fg='white',
            command=self.check_quiz_answer,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="➡️ 下一题",
            font=('Arial', 13, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.next_quiz_question,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="💡 显示提示",
            font=('Arial', 13, 'bold'),
            bg='#F39C12',
            fg='white',
            command=self.show_quiz_hint,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        # 解释区域
        tk.Label(
            question_frame,
            text="📖 详细解释",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.explanation_text = scrolledtext.ScrolledText(
            question_frame,
            font=('Courier', 11),
            wrap=tk.WORD,
            bg='#F8F9FA',
            height=12,
            state=tk.DISABLED
        )
        self.explanation_text.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        # 初始化第一题
        self.current_quiz = None
        self.next_quiz_question()
        
    def create_probability_bars(self):
        """创建概率条形图"""
        for widget in self.prob_display_frame.winfo_children():
            widget.destroy()
        
        sorted_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for disease, prob in sorted_diseases:
            disease_frame = tk.Frame(self.prob_display_frame, bg='white')
            disease_frame.pack(fill=tk.X, pady=15)
            
            # 疾病名称
            name_label = tk.Label(
                disease_frame,
                text=disease,
                font=('Arial', 14, 'bold'),
                bg='white',
                width=12,
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=10)
            
            # 概率条容器
            bar_frame = tk.Frame(disease_frame, bg='#E0E0E0', width=400, height=40)
            bar_frame.pack(side=tk.LEFT, padx=10)
            bar_frame.pack_propagate(False)
            
            # 概率条
            bar_width = int(400 * prob)
            color = self.diseases[disease]['color']
            
            bar = tk.Frame(bar_frame, bg=color, width=bar_width, height=40)
            bar.place(x=0, y=0)
            
            # 概率数值
            prob_label = tk.Label(
                disease_frame,
                text=f"{prob*100:.2f}%",
                font=('Arial', 14, 'bold'),
                bg='white',
                width=10,
                anchor=tk.W
            )
            prob_label.pack(side=tk.LEFT, padx=10)
        
    def on_symptom_selected(self, event=None):
        """当选择症状时显示条件概率"""
        symptom = self.symptom_var.get()
        if not symptom:
            return
        
        # 清空之前的内容
        for widget in self.symptom_info_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.symptom_info_frame,
            text=f"📊 症状「{symptom}」的条件概率",
            font=('Arial', 12, 'bold'),
            bg='#E8F8F5',
            pady=5
        ).pack()
        
        tk.Label(
            self.symptom_info_frame,
            text="即：各疾病患者出现此症状的概率",
            font=('Arial', 10),
            bg='#E8F8F5',
            fg='#555'
        ).pack()
        
        for disease in self.diseases.keys():
            prob = self.symptom_probabilities[symptom][disease]
            
            frame = tk.Frame(self.symptom_info_frame, bg='#E8F8F5')
            frame.pack(fill=tk.X, padx=15, pady=3)
            
            tk.Label(
                frame,
                text=f"P({symptom}|{disease}) =",
                font=('Courier', 11),
                bg='#E8F8F5',
                width=25,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=f"{prob:.2f}",
                font=('Courier', 11, 'bold'),
                bg='#E8F8F5',
                fg=self.diseases[disease]['color'],
                width=8,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=f"({prob*100:.0f}%)",
                font=('Arial', 10),
                bg='#E8F8F5',
                fg='#666'
            ).pack(side=tk.LEFT, padx=5)
        
    def process_response(self, has_symptom):
        """处理患者回答"""
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
        
        # 保存更新前的概率
        old_probs = self.current_probabilities.copy()
        
        # 执行贝叶斯更新
        self.bayesian_update_with_explanation(symptom, has_symptom, old_probs)
        
        # 更新显示
        self.create_probability_bars()
        self.update_teaching_tip()
        
        # 更新可用症状
        remaining = [s for s in self.symptom_probabilities.keys() 
                    if s not in self.asked_symptoms]
        self.symptom_combo['values'] = remaining
        if remaining:
            self.symptom_var.set(remaining[0])
            self.on_symptom_selected()
        else:
            self.symptom_var.set('')
            for widget in self.symptom_info_frame.winfo_children():
                widget.destroy()
        
    def bayesian_update_with_explanation(self, symptom, has_symptom, old_probs):
        """贝叶斯更新并生成详细解释"""
        response_text = "有" if has_symptom else "无"
        
        # 生成详细步骤
        steps = f"\n{'='*70}\n"
        steps += f"第 {len(self.asked_symptoms)} 次贝叶斯更新：患者【{response_text}】症状「{symptom}」\n"
        steps += f"{'='*70}\n\n"
        
        # 步骤1：列出先验概率
        steps += "📌 步骤1：当前先验概率（更新前）\n"
        steps += "-" * 70 + "\n"
        for disease in self.diseases.keys():
            steps += f"  P({disease}) = {old_probs[disease]:.4f}  ({old_probs[disease]*100:.2f}%)\n"
        
        # 步骤2：列出条件概率（似然度）
        steps += f"\n📌 步骤2：条件概率（似然度）\n"
        steps += "-" * 70 + "\n"
        
        likelihoods = {}
        for disease in self.diseases.keys():
            cond_prob = self.symptom_probabilities[symptom][disease]
            if has_symptom:
                likelihood = cond_prob
                steps += f"  P({symptom}|{disease}) = {likelihood:.4f}\n"
            else:
                likelihood = 1 - cond_prob
                steps += f"  P(无{symptom}|{disease}) = 1 - {cond_prob:.4f} = {likelihood:.4f}\n"
            likelihoods[disease] = likelihood
        
        # 步骤3：计算未归一化概率
        steps += f"\n📌 步骤3：计算未归一化后验概率\n"
        steps += "-" * 70 + "\n"
        steps += "  公式：未归一化概率 = 似然度 × 先验概率\n\n"
        
        unnormalized = {}
        for disease in self.diseases.keys():
            unnorm = likelihoods[disease] * old_probs[disease]
            unnormalized[disease] = unnorm
            if has_symptom:
                steps += f"  {disease}:\n"
                steps += f"    = P({symptom}|{disease}) × P({disease})\n"
                steps += f"    = {likelihoods[disease]:.4f} × {old_probs[disease]:.4f}\n"
                steps += f"    = {unnorm:.6f}\n\n"
            else:
                steps += f"  {disease}:\n"
                steps += f"    = P(无{symptom}|{disease}) × P({disease})\n"
                steps += f"    = {likelihoods[disease]:.4f} × {old_probs[disease]:.4f}\n"
                steps += f"    = {unnorm:.6f}\n\n"
        
        # 步骤4：计算归一化常数
        total = sum(unnormalized.values())
        steps += f"📌 步骤4：计算归一化常数（总和）\n"
        steps += "-" * 70 + "\n"
        steps += f"  总和 = "
        steps += " + ".join([f"{unnormalized[d]:.6f}" for d in self.diseases.keys()])
        steps += f"\n       = {total:.6f}\n"
        
        # 步骤5：归一化
        steps += f"\n📌 步骤5：归一化得到后验概率\n"
        steps += "-" * 70 + "\n"
        steps += "  公式：P(疾病|症状) = 未归一化概率 / 总和\n\n"
        
        for disease in self.diseases.keys():
            new_prob = unnormalized[disease] / total
            self.current_probabilities[disease] = new_prob
            change = new_prob - old_probs[disease]
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            
            steps += f"  P({disease}|{symptom}) = {unnormalized[disease]:.6f} / {total:.6f}\n"
            steps += f"                        = {new_prob:.4f}  ({new_prob*100:.2f}%)\n"
            steps += f"                        变化：{arrow} {abs(change)*100:.2f}%\n\n"
        
        # 步骤6：总结
        steps += f"📌 总结\n"
        steps += "-" * 70 + "\n"
        most_likely = max(self.current_probabilities.items(), key=lambda x: x[1])
        steps += f"  当前最可能的诊断：{most_likely[0]} ({most_likely[1]*100:.2f}%)\n"
        steps += f"{'='*70}\n"
        
        # 显示步骤
        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(1.0, steps)
        self.steps_text.config(state=tk.DISABLED)
        
        # 保存到历史
        self.calculation_steps.append({
            'step': len(self.asked_symptoms),
            'symptom': symptom,
            'has_symptom': has_symptom,
            'old_probs': old_probs,
            'new_probs': self.current_probabilities.copy(),
            'explanation': steps
        })
        
        # 更新可视化
        self.update_visualization()
        
    def update_teaching_tip(self):
        """更新教学提示"""
        num_asked = len(self.asked_symptoms)
        
        if num_asked == 0:
            tip = "贝叶斯定理通过不断更新先验概率来进行推理。\n选择一个症状开始诊断！"
        elif num_asked == 1:
            tip = "很好！注意观察概率是如何变化的。\n有些疾病的概率上升了，有些下降了。\n这是因为不同疾病出现该症状的概率不同。"
        elif num_asked == 2:
            tip = "继续！每次新的观察都会更新我们的判断。\n更新后的后验概率会成为下次更新的先验概率。"
        elif num_asked >= 3:
            most_likely = max(self.current_probabilities.items(), key=lambda x: x[1])
            tip = f"经过{num_asked}次观察，当前最可能的诊断是：{most_likely[0]}\n"
            tip += f"置信度：{most_likely[1]*100:.2f}%\n"
            if most_likely[1] > 0.7:
                tip += "概率已经比较高了，可以考虑给出诊断。"
            else:
                tip += "还可以继续询问症状来提高准确性。"
        
        self.teaching_tip_label.config(text=tip)
        
    def generate_manual_exercise(self):
        """生成手动计算练习"""
        import random
        
        # 随机选择一个症状和回答
        symptom = random.choice(list(self.symptom_probabilities.keys()))
        has_symptom = random.choice([True, False])
        
        # 使用先验概率
        probs = {d: info['prior'] for d, info in self.diseases.items()}
        
        # 构建场景描述
        response_text = "有" if has_symptom else "没有"
        scenario = f"练习场景：\n\n"
        scenario += f"患者主诉咳嗽。医生询问：「您是否有{symptom}症状？」\n"
        scenario += f"患者回答：「{response_text}。」\n\n"
        scenario += f"已知先验概率（基于流行病学数据）：\n"
        for disease, prob in probs.items():
            scenario += f"  P({disease}) = {prob:.2f}\n"
        scenario += f"\n已知条件概率：\n"
        for disease in self.diseases.keys():
            cond_prob = self.symptom_probabilities[symptom][disease]
            scenario += f"  P({symptom}|{disease}) = {cond_prob:.2f}\n"
        scenario += f"\n请计算：在患者{response_text}{symptom}的情况下，各疾病的后验概率。"
        
        self.scenario_text.config(state=tk.NORMAL)
        self.scenario_text.delete(1.0, tk.END)
        self.scenario_text.insert(1.0, scenario)
        self.scenario_text.config(state=tk.DISABLED)
        
        # 计算正确答案
        correct_answers = {}
        unnormalized = {}
        
        for disease in self.diseases.keys():
            cond_prob = self.symptom_probabilities[symptom][disease]
            likelihood = cond_prob if has_symptom else (1 - cond_prob)
            unnorm = likelihood * probs[disease]
            unnormalized[disease] = unnorm
        
        total = sum(unnormalized.values())
        
        for disease in self.diseases.keys():
            correct_answers[disease] = unnormalized[disease] / total
        
        self.current_exercise = {
            'symptom': symptom,
            'has_symptom': has_symptom,
            'priors': probs,
            'unnormalized': unnormalized,
            'total': total,
            'correct_answers': correct_answers
        }
        
        # 清空输入
        for entry in self.manual_inputs.values():
            entry.delete(0, tk.END)
        self.manual_sum_entry.delete(0, tk.END)
        
        # 清空反馈
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.insert(1.0, "请完成计算后点击「检查答案」按钮。")
        self.feedback_text.config(state=tk.DISABLED)
        
    def check_manual_calculation(self):
        """检查手动计算答案"""
        if not self.current_exercise:
            return
        
        try:
            feedback = "=" * 70 + "\n"
            feedback += "答案检查结果\n"
            feedback += "=" * 70 + "\n\n"
            
            all_correct = True
            tolerance = 0.0001
            
            # 检查未归一化概率
            feedback += "步骤1：未归一化概率\n"
            feedback += "-" * 70 + "\n"
            for disease in self.diseases.keys():
                user_input = self.manual_inputs[f'unnorm_{disease}'].get()
                correct = self.current_exercise['unnormalized'][disease]
                
                if user_input:
                    user_value = float(user_input)
                    is_correct = abs(user_value - correct) < tolerance
                    
                    if is_correct:
                        feedback += f"✓ {disease}: {user_value:.4f} (正确！)\n"
                    else:
                        feedback += f"✗ {disease}: 你的答案 {user_value:.4f}, 正确答案 {correct:.4f}\n"
                        all_correct = False
                else:
                    feedback += f"✗ {disease}: 未填写，正确答案 {correct:.4f}\n"
                    all_correct = False
            
            # 检查总和
            feedback += f"\n步骤2：归一化常数（总和）\n"
            feedback += "-" * 70 + "\n"
            user_sum = self.manual_sum_entry.get()
            correct_sum = self.current_exercise['total']
            
            if user_sum:
                user_sum_value = float(user_sum)
                is_correct = abs(user_sum_value - correct_sum) < tolerance
                
                if is_correct:
                    feedback += f"✓ 总和: {user_sum_value:.4f} (正确！)\n"
                else:
                    feedback += f"✗ 总和: 你的答案 {user_sum_value:.4f}, 正确答案 {correct_sum:.4f}\n"
                    all_correct = False
            else:
                feedback += f"✗ 总和: 未填写，正确答案 {correct_sum:.4f}\n"
                all_correct = False
            
            # 检查后验概率
            feedback += f"\n步骤3：后验概率\n"
            feedback += "-" * 70 + "\n"
            for disease in self.diseases.keys():
                user_input = self.manual_inputs[f'posterior_{disease}'].get()
                correct = self.current_exercise['correct_answers'][disease]
                
                if user_input:
                    user_value = float(user_input)
                    is_correct = abs(user_value - correct) < tolerance
                    
                    if is_correct:
                        feedback += f"✓ P({disease}|症状): {user_value:.4f} (正确！)\n"
                    else:
                        feedback += f"✗ P({disease}|症状): 你的答案 {user_value:.4f}, 正确答案 {correct:.4f}\n"
                        all_correct = False
                else:
                    feedback += f"✗ P({disease}|症状): 未填写，正确答案 {correct:.4f}\n"
                    all_correct = False
            
            # 总结
            feedback += "\n" + "=" * 70 + "\n"
            if all_correct:
                feedback += "🎉 完全正确！你已经掌握了贝叶斯计算！\n"
            else:
                feedback += "💪 继续努力！重新检查计算步骤。\n"
            feedback += "=" * 70 + "\n"
            
            self.feedback_text.config(state=tk.NORMAL)
            self.feedback_text.delete(1.0, tk.END)
            self.feedback_text.insert(1.0, feedback)
            self.feedback_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        
    def update_visualization(self):
        """更新可视化"""
        self.current_viz_step = len(self.calculation_steps) - 1
        self.draw_visualization()
        
    def draw_visualization(self):
        """绘制可视化"""
        self.viz_canvas.delete('all')
        
        if not self.calculation_steps or self.current_viz_step < 0:
            return
        
        canvas_width = self.viz_canvas.winfo_width()
        canvas_height = self.viz_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 500
        
        step_data = self.calculation_steps[self.current_viz_step]
        probs = step_data['probabilities']
        
        # 标题
        title = f"步骤 {step_data['step']}"
        if step_data['step'] == 0:
            title += ": 初始先验概率"
        else:
            symptom = step_data.get('symptom', '')
            has_symptom = step_data.get('has_symptom', True)
            response = "有" if has_symptom else "无"
            title += f": {response}{symptom}"
        
        self.viz_canvas.create_text(
            canvas_width // 2, 30,
            text=title,
            font=('Arial', 16, 'bold')
        )
        
        # 绘制概率条
        num_diseases = len(probs)
        bar_height = 60
        spacing = 30
        start_y = 80
        max_bar_width = canvas_width - 300
        
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        for i, (disease, prob) in enumerate(sorted_probs):
            y = start_y + i * (bar_height + spacing)
            
            # 疾病名称
            self.viz_canvas.create_text(
                20, y + bar_height // 2,
                text=disease,
                font=('Arial', 14, 'bold'),
                anchor=tk.W
            )
            
            # 概率条
            bar_width = max(max_bar_width * prob, 2)
            color = self.diseases[disease]['color']
            
            self.viz_canvas.create_rectangle(
                150, y + 5,
                150 + bar_width, y + bar_height - 5,
                fill=color,
                outline='black',
                width=2
            )
            
            # 概率值
            self.viz_canvas.create_text(
                150 + bar_width + 10, y + bar_height // 2,
                text=f"{prob*100:.2f}%",
                font=('Arial', 13, 'bold'),
                anchor=tk.W
            )
        
        # 更新步骤标签
        total_steps = len(self.calculation_steps)
        self.viz_step_label.config(text=f"当前步骤：{self.current_viz_step} / {total_steps - 1}")
        
    def viz_previous_step(self):
        """可视化上一步"""
        if self.current_viz_step > 0:
            self.current_viz_step -= 1
            self.draw_visualization()
        
    def viz_next_step(self):
        """可视化下一步"""
        if self.current_viz_step < len(self.calculation_steps) - 1:
            self.current_viz_step += 1
            self.draw_visualization()
        
    def viz_reset(self):
        """重置可视化"""
        self.current_viz_step = 0
        self.draw_visualization()
        
    def next_quiz_question(self):
        """生成下一道练习题"""
        import random
        
        # 随机生成题目
        question_types = [
            'calculate_posterior',
            'calculate_likelihood',
            'calculate_unnormalized',
            'compare_probs'
        ]
        
        q_type = random.choice(question_types)
        
        symptom = random.choice(list(self.symptom_probabilities.keys()))
        disease = random.choice(list(self.diseases.keys()))
        has_symptom = random.choice([True, False])
        
        if q_type == 'calculate_posterior':
            # 计算后验概率
            response = "有" if has_symptom else "无"
            question = f"题目类型：计算后验概率\n\n"
            question += f"已知：\n"
            for d in self.diseases.keys():
                question += f"  P({d}) = {self.diseases[d]['prior']:.2f}\n"
            question += f"\n"
            for d in self.diseases.keys():
                question += f"  P({symptom}|{d}) = {self.symptom_probabilities[symptom][d]:.2f}\n"
            question += f"\n问题：\n"
            question += f"如果患者{response}{symptom}，请计算P({disease}|症状) = ?\n"
            question += f"\n（请保留4位小数，例如：0.1234）"
            
            # 计算答案
            probs = {d: info['prior'] for d, info in self.diseases.items()}
            unnormalized = {}
            for d in self.diseases.keys():
                cond_prob = self.symptom_probabilities[symptom][d]
                likelihood = cond_prob if has_symptom else (1 - cond_prob)
                unnormalized[d] = likelihood * probs[d]
            total = sum(unnormalized.values())
            answer = unnormalized[disease] / total
            
            hint = f"提示：使用贝叶斯公式\n"
            hint += f"P({disease}|症状) = P(症状|{disease}) × P({disease}) / P(症状)"
            
        elif q_type == 'calculate_likelihood':
            # 已知后验求似然
            question = f"题目类型：理解条件概率\n\n"
            question += f"在贝叶斯诊断中，P({symptom}|{disease})表示什么？\n"
            question += f"请直接输入该概率的数值。\n"
            question += f"\n（请保留2位小数，例如：0.85）"
            
            answer = self.symptom_probabilities[symptom][disease]
            hint = f"提示：这是条件概率，表示患有{disease}的患者中，出现{symptom}症状的概率。"
            
        elif q_type == 'calculate_unnormalized':
            # 计算未归一化概率
            response = "有" if has_symptom else "无"
            prior = self.diseases[disease]['prior']
            cond_prob = self.symptom_probabilities[symptom][disease]
            
            question = f"题目类型：计算未归一化概率\n\n"
            question += f"已知：\n"
            question += f"  P({disease}) = {prior:.2f}\n"
            question += f"  P({symptom}|{disease}) = {cond_prob:.2f}\n"
            question += f"\n问题：\n"
            question += f"患者{response}{symptom}，计算{disease}的未归一化后验概率。\n"
            question += f"\n（请保留6位小数，例如：0.123456）"
            
            likelihood = cond_prob if has_symptom else (1 - cond_prob)
            answer = likelihood * prior
            hint = f"提示：未归一化概率 = 似然度 × 先验概率"
            
        else:  # compare_probs
            # 概率比较
            d1, d2 = random.sample(list(self.diseases.keys()), 2)
            response = "有" if has_symptom else "无"
            
            question = f"题目类型：概率推理\n\n"
            question += f"已知先验概率：\n"
            question += f"  P({d1}) = {self.diseases[d1]['prior']:.2f}\n"
            question += f"  P({d2}) = {self.diseases[d2]['prior']:.2f}\n"
            question += f"\n已知条件概率：\n"
            question += f"  P({symptom}|{d1}) = {self.symptom_probabilities[symptom][d1]:.2f}\n"
            question += f"  P({symptom}|{d2}) = {self.symptom_probabilities[symptom][d2]:.2f}\n"
            question += f"\n问题：\n"
            question += f"患者{response}{symptom}后，哪个疾病的概率更高？\n"
            question += f"请输入概率更高的那个疾病的后验概率。\n"
            question += f"\n（请保留4位小数）"
            
            # 计算两个疾病的后验概率
            probs = {d: info['prior'] for d, info in self.diseases.items()}
            unnorm1 = (self.symptom_probabilities[symptom][d1] if has_symptom 
                      else 1-self.symptom_probabilities[symptom][d1]) * probs[d1]
            unnorm2 = (self.symptom_probabilities[symptom][d2] if has_symptom 
                      else 1-self.symptom_probabilities[symptom][d2]) * probs[d2]
            
            # 简化：只计算这两个的归一化
            total_simple = unnorm1 + unnorm2
            post1 = unnorm1 / total_simple
            post2 = unnorm2 / total_simple
            
            answer = max(post1, post2)
            hint = f"提示：分别计算两个疾病的后验概率，然后比较。"
        
        # 显示题目
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, question)
        self.question_text.config(state=tk.DISABLED)
        
        # 清空输入和解释
        self.answer_entry.delete(0, tk.END)
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        
        # 保存当前题目
        self.current_quiz = {
            'type': q_type,
            'question': question,
            'answer': answer,
            'hint': hint,
            'symptom': symptom,
            'disease': disease,
            'has_symptom': has_symptom
        }
        
    def check_quiz_answer(self):
        """检查练习题答案"""
        if not self.current_quiz:
            return
        
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("提示", "请先输入答案！")
            return
        
        try:
            user_value = float(user_answer)
            correct_value = self.current_quiz['answer']
            
            tolerance = 0.001
            is_correct = abs(user_value - correct_value) < tolerance
            
            # 更新得分
            self.quiz_score['total'] += 1
            if is_correct:
                self.quiz_score['correct'] += 1
            
            self.score_label.config(
                text=f"得分：{self.quiz_score['correct']} / {self.quiz_score['total']}"
            )
            
            # 显示详细解释
            explanation = "=" * 70 + "\n"
            if is_correct:
                explanation += "✓ 回答正确！\n"
                messagebox.showinfo("正确！", "太棒了！答案正确！")
            else:
                explanation += "✗ 回答错误\n"
                explanation += f"你的答案：{user_value:.4f}\n"
                explanation += f"正确答案：{correct_value:.4f}\n"
                messagebox.showinfo("错误", f"答案不正确。\n正确答案是：{correct_value:.4f}")
            explanation += "=" * 70 + "\n\n"
            
            # 添加详细解析
            explanation += "详细解析：\n"
            explanation += "-" * 70 + "\n"
            
            if self.current_quiz['type'] == 'calculate_posterior':
                symptom = self.current_quiz['symptom']
                disease = self.current_quiz['disease']
                has_symptom = self.current_quiz['has_symptom']
                response = "有" if has_symptom else "无"
                
                explanation += f"这是一道计算后验概率的题目。\n\n"
                explanation += f"步骤1：列出先验概率和条件概率\n"
                for d in self.diseases.keys():
                    explanation += f"  P({d}) = {self.diseases[d]['prior']:.2f}\n"
                explanation += f"\n"
                for d in self.diseases.keys():
                    cond = self.symptom_probabilities[symptom][d]
                    explanation += f"  P({symptom}|{d}) = {cond:.2f}\n"
                
                explanation += f"\n步骤2：计算各疾病的未归一化概率\n"
                probs = {d: info['prior'] for d, info in self.diseases.items()}
                unnormalized = {}
                for d in self.diseases.keys():
                    cond_prob = self.symptom_probabilities[symptom][d]
                    likelihood = cond_prob if has_symptom else (1 - cond_prob)
                    unnorm = likelihood * probs[d]
                    unnormalized[d] = unnorm
                    if has_symptom:
                        explanation += f"  {d}: {cond_prob:.2f} × {probs[d]:.2f} = {unnorm:.4f}\n"
                    else:
                        explanation += f"  {d}: {likelihood:.2f} × {probs[d]:.2f} = {unnorm:.4f}\n"
                
                total = sum(unnormalized.values())
                explanation += f"\n步骤3：计算总和\n"
                explanation += f"  总和 = {total:.4f}\n"
                
                explanation += f"\n步骤4：归一化\n"
                for d in self.diseases.keys():
                    post = unnormalized[d] / total
                    explanation += f"  P({d}|症状) = {unnormalized[d]:.4f} / {total:.4f} = {post:.4f}\n"
                
                explanation += f"\n因此，P({disease}|症状) = {correct_value:.4f}\n"
            
            self.explanation_text.config(state=tk.NORMAL)
            self.explanation_text.delete(1.0, tk.END)
            self.explanation_text.insert(1.0, explanation)
            self.explanation_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
        
    def show_quiz_hint(self):
        """显示练习题提示"""
        if self.current_quiz:
            messagebox.showinfo("提示", self.current_quiz['hint'])
        
    def on_mode_change(self):
        """模式改变处理"""
        mode = self.teaching_mode.get()
        messagebox.showinfo(
            "教学模式",
            f"当前模式：{mode}\n\n"
            f"学习模式：详细的步骤说明和公式展示\n"
            f"练习模式：自己动手计算，系统给出反馈\n"
            f"测验模式：独立完成题目，检验学习效果"
        )
        
    def show_all_steps(self):
        """显示所有计算步骤"""
        if not self.calculation_steps or len(self.calculation_steps) <= 1:
            messagebox.showinfo("提示", "还没有进行任何贝叶斯更新！")
            return
        
        # 创建新窗口
        window = tk.Toplevel(self.root)
        window.title("完整计算步骤")
        window.geometry("900x700")
        
        tk.Label(
            window,
            text="完整的贝叶斯更新过程",
            font=('Arial', 16, 'bold'),
            pady=15
        ).pack()
        
        text_widget = scrolledtext.ScrolledText(
            window,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        all_steps = ""
        for step_data in self.calculation_steps[1:]:  # 跳过初始状态
            all_steps += step_data.get('explanation', '') + "\n\n"
        
        text_widget.insert(1.0, all_steps)
        text_widget.config(state=tk.DISABLED)
        
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
            messagebox.showinfo("提示", "请至少询问一个症状后再诊断！")
            return
        
        most_likely = max(self.current_probabilities.items(), key=lambda x: x[1])
        
        result = f"{'='*60}\n"
        result += f"诊断结果\n"
        result += f"{'='*60}\n\n"
        result += f"最可能的诊断：{most_likely[0]}\n"
        result += f"置信度：{most_likely[1]*100:.2f}%\n\n"
        result += f"询问了 {len(self.asked_symptoms)} 个症状：\n"
        for symptom in self.asked_symptoms:
            response = "有" if self.symptom_responses[symptom] else "无"
            result += f"  • {symptom}：{response}\n"
        result += f"\n完整概率分布：\n"
        sorted_probs = sorted(self.current_probabilities.items(), key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_probs:
            result += f"  • {disease}：{prob*100:.2f}%\n"
        result += f"\n{'='*60}\n"
        
        messagebox.showinfo("诊断结果", result)
        
        if messagebox.askyesno("继续", "是否开始新的诊断？"):
            self.reset_game()
        
    def reset_game(self):
        """重置游戏"""
        self.reset_probabilities()
        self.asked_symptoms = []
        self.symptom_responses = []
        
        self.symptom_combo['values'] = list(self.symptom_probabilities.keys())
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
            self.on_symptom_selected()
        
        self.steps_text.config(state=tk.NORMAL)
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.config(state=tk.DISABLED)
        
        self.create_probability_bars()
        self.update_teaching_tip()
        self.update_visualization()
        

def main():
    root = tk.Tk()
    app = BayesianEducationalGame(root)
    
    root.update()
    app.draw_visualization()
    
    root.mainloop()


if __name__ == '__main__':
    main()






