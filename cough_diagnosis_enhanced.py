"""
贝叶斯咳嗽诊断游戏 - 增强版
功能：
1. 更多疾病和症状
2. 实时概率变化图表
3. 详细的贝叶斯计算过程
4. 疾病知识库
5. 多轮游戏统计
6. 难度等级
7. AI建议系统
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from typing import Dict, List, Tuple
import json
from datetime import datetime


class BayesianDiagnosisEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("贝叶斯咳嗽诊断游戏 - 增强版")
        self.root.geometry("1400x900")
        self.root.configure(bg='#ECF0F1')
        
        # 疾病定义及先验概率（扩展）
        self.diseases = {
            '普通感冒': {
                'prior': 0.30,
                'color': '#FF6B6B',
                'description': '由鼻病毒引起的上呼吸道感染，症状较轻',
                'treatment': '多休息、多喝水、对症治疗',
                'duration': '3-7天'
            },
            '流感': {
                'prior': 0.12,
                'color': '#4ECDC4',
                'description': '由流感病毒引起，症状比普通感冒更严重',
                'treatment': '抗病毒药物、休息、退烧',
                'duration': '7-14天'
            },
            '支气管炎': {
                'prior': 0.12,
                'color': '#45B7D1',
                'description': '支气管黏膜的炎症，常伴有咳嗽和痰',
                'treatment': '止咳药、祛痰药、抗生素（如细菌性）',
                'duration': '1-3周'
            },
            '肺炎': {
                'prior': 0.08,
                'color': '#FFA07A',
                'description': '肺部感染，可能危及生命，需要及时治疗',
                'treatment': '抗生素、住院治疗（严重时）',
                'duration': '2-4周'
            },
            '过敏性咳嗽': {
                'prior': 0.15,
                'color': '#98D8C8',
                'description': '由过敏原引起的慢性咳嗽',
                'treatment': '抗组胺药、避免过敏原',
                'duration': '持续性（需控制）'
            },
            '哮喘': {
                'prior': 0.10,
                'color': '#F7B731',
                'description': '慢性气道炎症，导致呼吸困难和喘息',
                'treatment': '吸入性支气管扩张剂、激素',
                'duration': '慢性疾病（需长期管理）'
            },
            '新冠肺炎': {
                'prior': 0.06,
                'color': '#E74C3C',
                'description': 'COVID-19病毒感染，症状多样',
                'treatment': '隔离、对症治疗、抗病毒药物',
                'duration': '1-3周'
            },
            '肺结核': {
                'prior': 0.03,
                'color': '#9B59B6',
                'description': '结核分枝杆菌感染，需要长期治疗',
                'treatment': '抗结核药物（6-9个月）',
                'duration': '6-12个月治疗周期'
            },
            '胃食管反流': {
                'prior': 0.04,
                'color': '#1ABC9C',
                'description': '胃酸反流刺激喉咙导致慢性咳嗽',
                'treatment': '抑酸药、改变生活方式',
                'duration': '慢性（需管理）'
            }
        }
        
        # 扩展的症状条件概率 P(症状|疾病)
        self.symptom_probabilities = {
            '发烧': {
                '普通感冒': 0.30, '流感': 0.90, '支气管炎': 0.50,
                '肺炎': 0.85, '过敏性咳嗽': 0.05, '哮喘': 0.10,
                '新冠肺炎': 0.75, '肺结核': 0.60, '胃食管反流': 0.05
            },
            '流鼻涕': {
                '普通感冒': 0.80, '流感': 0.40, '支气管炎': 0.20,
                '肺炎': 0.15, '过敏性咳嗽': 0.60, '哮喘': 0.15,
                '新冠肺炎': 0.35, '肺结核': 0.10, '胃食管反流': 0.10
            },
            '喉咙痛': {
                '普通感冒': 0.70, '流感': 0.65, '支气管炎': 0.30,
                '肺炎': 0.25, '过敏性咳嗽': 0.20, '哮喘': 0.15,
                '新冠肺炎': 0.50, '肺结核': 0.15, '胃食管反流': 0.40
            },
            '呼吸困难': {
                '普通感冒': 0.10, '流感': 0.30, '支气管炎': 0.60,
                '肺炎': 0.70, '过敏性咳嗽': 0.40, '哮喘': 0.80,
                '新冠肺炎': 0.65, '肺结核': 0.55, '胃食管反流': 0.15
            },
            '胸痛': {
                '普通感冒': 0.05, '流感': 0.20, '支气管炎': 0.40,
                '肺炎': 0.60, '过敏性咳嗽': 0.10, '哮喘': 0.30,
                '新冠肺炎': 0.45, '肺结核': 0.50, '胃食管反流': 0.35
            },
            '咳痰': {
                '普通感冒': 0.40, '流感': 0.50, '支气管炎': 0.80,
                '肺炎': 0.85, '过敏性咳嗽': 0.20, '哮喘': 0.30,
                '新冠肺炎': 0.55, '肺结核': 0.75, '胃食管反流': 0.15
            },
            '夜间咳嗽加重': {
                '普通感冒': 0.30, '流感': 0.40, '支气管炎': 0.50,
                '肺炎': 0.45, '过敏性咳嗽': 0.70, '哮喘': 0.85,
                '新冠肺炎': 0.40, '肺结核': 0.65, '胃食管反流': 0.80
            },
            '持续超过2周': {
                '普通感冒': 0.10, '流感': 0.15, '支气管炎': 0.60,
                '肺炎': 0.40, '过敏性咳嗽': 0.80, '哮喘': 0.75,
                '新冠肺炎': 0.30, '肺结核': 0.90, '胃食管反流': 0.85
            },
            '乏力': {
                '普通感冒': 0.50, '流感': 0.85, '支气管炎': 0.60,
                '肺炎': 0.80, '过敏性咳嗽': 0.30, '哮喘': 0.40,
                '新冠肺炎': 0.75, '肺结核': 0.85, '胃食管反流': 0.25
            },
            '肌肉酸痛': {
                '普通感冒': 0.40, '流感': 0.80, '支气管炎': 0.35,
                '肺炎': 0.45, '过敏性咳嗽': 0.10, '哮喘': 0.15,
                '新冠肺炎': 0.65, '肺结核': 0.40, '胃食管反流': 0.10
            },
            '喘息': {
                '普通感冒': 0.15, '流感': 0.25, '支气管炎': 0.50,
                '肺炎': 0.40, '过敏性咳嗽': 0.35, '哮喘': 0.90,
                '新冠肺炎': 0.30, '肺结核': 0.25, '胃食管反流': 0.10
            },
            '咳血': {
                '普通感冒': 0.02, '流感': 0.05, '支气管炎': 0.15,
                '肺炎': 0.20, '过敏性咳嗽': 0.03, '哮喘': 0.05,
                '新冠肺炎': 0.10, '肺结核': 0.50, '胃食管反流': 0.02
            },
            '盗汗': {
                '普通感冒': 0.20, '流感': 0.40, '支气管炎': 0.25,
                '肺炎': 0.35, '过敏性咳嗽': 0.10, '哮喘': 0.15,
                '新冠肺炎': 0.30, '肺结核': 0.80, '胃食管反流': 0.10
            },
            '体重下降': {
                '普通感冒': 0.05, '流感': 0.15, '支气管炎': 0.10,
                '肺炎': 0.25, '过敏性咳嗽': 0.08, '哮喘': 0.12,
                '新冠肺炎': 0.20, '肺结核': 0.70, '胃食管反流': 0.15
            },
            '味觉/嗅觉丧失': {
                '普通感冒': 0.30, '流感': 0.20, '支气管炎': 0.10,
                '肺炎': 0.15, '过敏性咳嗽': 0.15, '哮喘': 0.10,
                '新冠肺炎': 0.70, '肺结核': 0.10, '胃食管反流': 0.05
            },
            '烧心感': {
                '普通感冒': 0.05, '流感': 0.10, '支气管炎': 0.10,
                '肺炎': 0.08, '过敏性咳嗽': 0.15, '哮喘': 0.20,
                '新冠肺炎': 0.10, '肺结核': 0.10, '胃食管反流': 0.85
            }
        }
        
        # 游戏状态
        self.current_probabilities = {}
        self.asked_symptoms = []
        self.symptom_responses = {}
        self.probability_history = []  # 记录概率变化历史
        self.game_statistics = {
            'total_games': 0,
            'correct_diagnoses': 0,
            'avg_questions': 0,
            'game_history': []
        }
        
        # 难度级别
        self.difficulty = tk.StringVar(value='中等')
        self.difficulty_settings = {
            '简单': {'max_symptoms': 16, 'show_hints': True},
            '中等': {'max_symptoms': 10, 'show_hints': True},
            '困难': {'max_symptoms': 6, 'show_hints': False}
        }
        
        self.reset_probabilities()
        self.create_notebook_interface()
        
    def reset_probabilities(self):
        """重置概率为先验概率"""
        self.current_probabilities = {
            disease: info['prior'] 
            for disease, info in self.diseases.items()
        }
        self.probability_history = [self.current_probabilities.copy()]
        
    def create_notebook_interface(self):
        """创建标签页界面"""
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#2C3E50', height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🏥 贝叶斯咳嗽诊断系统 - 增强版 🏥",
            font=('Arial', 24, 'bold'),
            bg='#2C3E50',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标签页1: 诊断界面
        self.diagnosis_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.diagnosis_tab, text='📋 诊断界面')
        self.create_diagnosis_tab()
        
        # 标签页2: 概率分析
        self.analysis_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.analysis_tab, text='📊 概率分析')
        self.create_analysis_tab()
        
        # 标签页3: 疾病知识库
        self.knowledge_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.knowledge_tab, text='📚 疾病知识库')
        self.create_knowledge_tab()
        
        # 标签页4: 贝叶斯原理
        self.theory_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.theory_tab, text='🔬 贝叶斯原理')
        self.create_theory_tab()
        
        # 标签页5: 游戏统计
        self.stats_tab = tk.Frame(self.notebook, bg='#ECF0F1')
        self.notebook.add(self.stats_tab, text='📈 游戏统计')
        self.create_stats_tab()
        
    def create_diagnosis_tab(self):
        """创建诊断标签页"""
        # 顶部控制栏
        control_frame = tk.Frame(self.diagnosis_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 难度选择
        tk.Label(
            control_frame,
            text="难度：",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        for level in ['简单', '中等', '困难']:
            tk.Radiobutton(
                control_frame,
                text=level,
                variable=self.difficulty,
                value=level,
                font=('Arial', 11),
                bg='white',
                command=self.on_difficulty_change
            ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            control_frame,
            text="  |  已询问：",
            font=('Arial', 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        self.question_count_label = tk.Label(
            control_frame,
            text="0",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#E74C3C'
        )
        self.question_count_label.pack(side=tk.LEFT)
        
        # 主内容区
        main_frame = tk.Frame(self.diagnosis_tab, bg='#ECF0F1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：概率显示
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        prob_title = tk.Label(
            left_frame,
            text="🎯 当前疾病概率分布",
            font=('Arial', 16, 'bold'),
            bg='white',
            pady=10
        )
        prob_title.pack()
        
        # 概率显示画布
        canvas_frame = tk.Frame(left_frame, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.prob_canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            highlightthickness=0,
            height=500
        )
        self.prob_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：症状询问
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        symptom_title = tk.Label(
            right_frame,
            text="🔍 症状询问",
            font=('Arial', 16, 'bold'),
            bg='white',
            pady=10
        )
        symptom_title.pack()
        
        # AI建议区域
        self.ai_hint_frame = tk.Frame(right_frame, bg='#FFF9E6', relief=tk.RIDGE, borderwidth=2)
        self.ai_hint_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            self.ai_hint_frame,
            text="💡 AI建议",
            font=('Arial', 12, 'bold'),
            bg='#FFF9E6',
            fg='#F39C12'
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        self.ai_hint_label = tk.Label(
            self.ai_hint_frame,
            text="开始询问症状以获得AI建议...",
            font=('Arial', 10),
            bg='#FFF9E6',
            wraplength=350,
            justify=tk.LEFT
        )
        self.ai_hint_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # 症状选择
        symptom_select_frame = tk.Frame(right_frame, bg='white', pady=10)
        symptom_select_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(
            symptom_select_frame,
            text="选择要询问的症状：",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(anchor=tk.W, pady=5)
        
        self.symptom_var = tk.StringVar()
        self.symptom_combo = ttk.Combobox(
            symptom_select_frame,
            textvariable=self.symptom_var,
            values=list(self.symptom_probabilities.keys()),
            state='readonly',
            font=('Arial', 11),
            width=30
        )
        self.symptom_combo.pack(pady=5, fill=tk.X)
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
        
        # 症状响应按钮
        response_frame = tk.Frame(right_frame, bg='white')
        response_frame.pack(pady=15)
        
        tk.Label(
            response_frame,
            text="患者是否有此症状？",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        button_frame = tk.Frame(response_frame, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="✓ 是",
            font=('Arial', 14, 'bold'),
            bg='#27AE60',
            fg='white',
            width=12,
            height=2,
            command=lambda: self.record_symptom(True)
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="✗ 否",
            font=('Arial', 14, 'bold'),
            bg='#E74C3C',
            fg='white',
            width=12,
            height=2,
            command=lambda: self.record_symptom(False)
        ).pack(side=tk.LEFT, padx=10)
        
        # 询问历史
        history_label = tk.Label(
            right_frame,
            text="📝 询问历史",
            font=('Arial', 13, 'bold'),
            bg='white',
            pady=5
        )
        history_label.pack()
        
        history_frame = tk.Frame(right_frame, bg='white')
        history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            history_frame,
            font=('Arial', 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            bg='#F8F9FA',
            height=10
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_text.yview)
        
        # 底部按钮栏
        bottom_frame = tk.Frame(self.diagnosis_tab, bg='#ECF0F1')
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            bottom_frame,
            text="🔄 重置游戏",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='white',
            command=self.reset_game,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="🤖 AI推荐症状",
            font=('Arial', 12, 'bold'),
            bg='#9B59B6',
            fg='white',
            command=self.show_ai_recommendation,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="🏆 给出诊断",
            font=('Arial', 12, 'bold'),
            bg='#F39C12',
            fg='white',
            command=self.make_diagnosis,
            width=15,
            height=2
        ).pack(side=tk.RIGHT, padx=5)
        
    def create_analysis_tab(self):
        """创建概率分析标签页"""
        # 说明区域
        info_frame = tk.Frame(self.analysis_tab, bg='#D5DBDB', relief=tk.RAISED, borderwidth=2)
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            info_frame,
            text="📊 贝叶斯概率分析",
            font=('Arial', 16, 'bold'),
            bg='#D5DBDB'
        ).pack(pady=10)
        
        tk.Label(
            info_frame,
            text="此页面展示每次症状询问后的贝叶斯更新计算过程和概率变化趋势",
            font=('Arial', 11),
            bg='#D5DBDB'
        ).pack(pady=5)
        
        # 分割为左右两部分
        content_frame = tk.Frame(self.analysis_tab, bg='#ECF0F1')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧：计算过程
        left_panel = tk.Frame(content_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="🔢 详细计算过程",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.calculation_text = scrolledtext.ScrolledText(
            left_panel,
            font=('Courier', 10),
            wrap=tk.WORD,
            bg='#F8F9FA',
            state=tk.DISABLED
        )
        self.calculation_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 右侧：概率趋势图
        right_panel = tk.Frame(content_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_panel,
            text="📈 概率变化趋势",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.trend_canvas = tk.Canvas(
            right_panel,
            bg='white',
            highlightthickness=0
        )
        self.trend_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
    def create_knowledge_tab(self):
        """创建疾病知识库标签页"""
        # 标题
        title_label = tk.Label(
            self.knowledge_tab,
            text="📚 疾病知识库",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        )
        title_label.pack()
        
        # 疾病选择
        select_frame = tk.Frame(self.knowledge_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        select_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(
            select_frame,
            text="选择疾病查看详细信息：",
            font=('Arial', 13, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=15, pady=15)
        
        self.disease_var = tk.StringVar()
        disease_combo = ttk.Combobox(
            select_frame,
            textvariable=self.disease_var,
            values=list(self.diseases.keys()),
            state='readonly',
            font=('Arial', 12),
            width=25
        )
        disease_combo.pack(side=tk.LEFT, padx=10, pady=15)
        disease_combo.bind('<<ComboboxSelected>>', self.show_disease_info)
        if self.diseases:
            disease_combo.current(0)
        
        # 疾病信息显示区域
        self.disease_info_frame = tk.Frame(self.knowledge_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        self.disease_info_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        self.show_disease_info(None)
        
    def create_theory_tab(self):
        """创建贝叶斯原理标签页"""
        # 标题
        title_label = tk.Label(
            self.theory_tab,
            text="🔬 贝叶斯定理原理",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        )
        title_label.pack()
        
        # 创建滚动文本框
        text_frame = tk.Frame(self.theory_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        theory_text = scrolledtext.ScrolledText(
            text_frame,
            font=('Arial', 11),
            wrap=tk.WORD,
            bg='white',
            padx=20,
            pady=20
        )
        theory_text.pack(fill=tk.BOTH, expand=True)
        
        # 贝叶斯原理内容
        content = """
═══════════════════════════════════════════════════════════════════

                    贝叶斯定理在医学诊断中的应用

═══════════════════════════════════════════════════════════════════

一、贝叶斯定理基本公式

P(疾病|症状) = P(症状|疾病) × P(疾病) / P(症状)

各部分解释：
├─ P(疾病|症状)：后验概率 - 观察到症状后患该疾病的概率
├─ P(症状|疾病)：似然度 - 患该疾病时出现该症状的概率
├─ P(疾病)：先验概率 - 在观察症状前患该疾病的概率
└─ P(症状)：边缘概率 - 出现该症状的总概率（归一化常数）

═══════════════════════════════════════════════════════════════════

二、迭代更新过程

在诊断过程中，我们不断根据新的症状信息更新疾病概率：

第1步：从先验概率开始
    P₀(疾病) = 初始概率（基于流行病学数据）

第2步：询问第1个症状，得到响应
    P₁(疾病) = P(症状₁|疾病) × P₀(疾病) / P(症状₁)

第3步：询问第2个症状，用P₁作为新的先验
    P₂(疾病) = P(症状₂|疾病) × P₁(疾病) / P(症状₂)

第n步：继续迭代
    Pₙ(疾病) = P(症状ₙ|疾病) × Pₙ₋₁(疾病) / P(症状ₙ)

每次更新后，归一化确保所有疾病概率和为1。

═══════════════════════════════════════════════════════════════════

三、处理阴性症状

当患者没有某个症状时：

P(疾病|无症状) = P(无症状|疾病) × P(疾病) / P(无症状)
                = (1 - P(症状|疾病)) × P(疾病) / P(无症状)

这同样提供了诊断信息！某些疾病的典型症状不出现时，
该疾病的概率会下降。

═══════════════════════════════════════════════════════════════════

四、实际应用示例

假设初始概率：
• 普通感冒：40%
• 流感：15%
• 肺炎：10%
• 其他：35%

询问"是否发烧"，患者回答"是"：

条件概率：
• P(发烧|普通感冒) = 30%
• P(发烧|流感) = 90%
• P(发烧|肺炎) = 85%

贝叶斯更新：
• 流感的概率会上升（因为发烧是流感的典型症状）
• 普通感冒的概率会下降（相对于流感）

更新后概率：
• 普通感冒：约25%  ↓
• 流感：约33%       ↑
• 肺炎：约20%       ↑
• 其他：约22%       ↓

═══════════════════════════════════════════════════════════════════

五、贝叶斯方法的优势

1. 充分利用先验知识
   基于已知的疾病流行率和临床经验

2. 动态更新
   每个新信息都会即时影响诊断

3. 量化不确定性
   给出概率而非绝对判断

4. 处理不完整信息
   即使症状不完全，也能给出合理判断

5. 考虑多种可能
   同时评估所有疾病的可能性

═══════════════════════════════════════════════════════════════════

六、数学推导

边缘概率的计算：
P(症状) = Σ P(症状|疾病ᵢ) × P(疾病ᵢ)
         所有疾病i

完整的后验概率计算：
P(疾病ⱼ|症状) = P(症状|疾病ⱼ) × P(疾病ⱼ) / Σ P(症状|疾病ᵢ) × P(疾病ᵢ)
                                           所有疾病i

这确保了：
Σ P(疾病ᵢ|症状) = 1
所有疾病i

═══════════════════════════════════════════════════════════════════

七、局限性与注意事项

1. 依赖条件概率的准确性
   需要可靠的医学统计数据

2. 假设症状独立性
   实际上某些症状可能相关

3. 先验概率的选择
   不同地区、季节的疾病流行率不同

4. 需要临床判断
   算法辅助而非替代医生

═══════════════════════════════════════════════════════════════════

八、实践建议

• 从最具鉴别力的症状开始询问
• 关注概率变化大的症状
• 至少询问3-5个症状再做判断
• 结合患者的年龄、病史等背景信息
• 对高危疾病（如肺炎）保持警惕

═══════════════════════════════════════════════════════════════════
"""
        
        theory_text.insert(1.0, content)
        theory_text.config(state=tk.DISABLED)
        
    def create_stats_tab(self):
        """创建游戏统计标签页"""
        # 标题
        title_label = tk.Label(
            self.stats_tab,
            text="📈 游戏统计",
            font=('Arial', 18, 'bold'),
            bg='#ECF0F1',
            pady=15
        )
        title_label.pack()
        
        # 统计信息显示区域
        stats_frame = tk.Frame(self.stats_tab, bg='white', relief=tk.RAISED, borderwidth=2)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # 总体统计
        summary_frame = tk.Frame(stats_frame, bg='#D5DBDB', relief=tk.RIDGE, borderwidth=2)
        summary_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            summary_frame,
            text="📊 总体统计",
            font=('Arial', 16, 'bold'),
            bg='#D5DBDB',
            pady=10
        ).pack()
        
        stat_grid = tk.Frame(summary_frame, bg='#D5DBDB')
        stat_grid.pack(pady=15)
        
        self.total_games_label = tk.Label(
            stat_grid,
            text="总游戏次数：0",
            font=('Arial', 14),
            bg='#D5DBDB'
        )
        self.total_games_label.grid(row=0, column=0, padx=30, pady=5)
        
        self.correct_rate_label = tk.Label(
            stat_grid,
            text="正确率：N/A",
            font=('Arial', 14),
            bg='#D5DBDB'
        )
        self.correct_rate_label.grid(row=0, column=1, padx=30, pady=5)
        
        self.avg_questions_label = tk.Label(
            stat_grid,
            text="平均询问数：N/A",
            font=('Arial', 14),
            bg='#D5DBDB'
        )
        self.avg_questions_label.grid(row=1, column=0, padx=30, pady=5)
        
        # 历史记录
        tk.Label(
            stats_frame,
            text="📝 游戏历史",
            font=('Arial', 14, 'bold'),
            bg='white',
            pady=10
        ).pack()
        
        self.history_tree = ttk.Treeview(
            stats_frame,
            columns=('时间', '诊断结果', '询问次数', '准确度'),
            show='headings',
            height=15
        )
        
        self.history_tree.heading('时间', text='时间')
        self.history_tree.heading('诊断结果', text='诊断结果')
        self.history_tree.heading('询问次数', text='询问次数')
        self.history_tree.heading('准确度', text='准确度')
        
        self.history_tree.column('时间', width=150)
        self.history_tree.column('诊断结果', width=150)
        self.history_tree.column('询问次数', width=100)
        self.history_tree.column('准确度', width=100)
        
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 20))
        
    def update_probability_display(self):
        """更新概率显示"""
        self.prob_canvas.delete('all')
        
        canvas_width = self.prob_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 500
        
        # 排序疾病
        sorted_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        bar_height = 45
        spacing = 10
        start_y = 20
        max_bar_width = canvas_width - 250
        
        for i, (disease, prob) in enumerate(sorted_diseases):
            y = start_y + i * (bar_height + spacing)
            
            # 疾病名称
            self.prob_canvas.create_text(
                15, y + bar_height // 2,
                text=disease,
                font=('Arial', 12, 'bold'),
                anchor=tk.W
            )
            
            # 概率条
            bar_width = max(max_bar_width * prob, 2)
            color = self.diseases[disease]['color']
            
            self.prob_canvas.create_rectangle(
                140, y + 5,
                140 + bar_width, y + bar_height - 5,
                fill=color,
                outline=color,
                width=2
            )
            
            # 概率数值
            prob_text = f"{prob * 100:.2f}%"
            self.prob_canvas.create_text(
                140 + bar_width + 10, y + bar_height // 2,
                text=prob_text,
                font=('Arial', 11, 'bold'),
                anchor=tk.W
            )
        
    def record_symptom(self, has_symptom):
        """记录症状并更新概率"""
        symptom = self.symptom_var.get()
        
        if not symptom:
            messagebox.showwarning("提示", "请先选择一个症状！")
            return
        
        if symptom in self.asked_symptoms:
            messagebox.showwarning("提示", "这个症状已经询问过了！")
            return
        
        # 记录症状
        self.asked_symptoms.append(symptom)
        self.symptom_responses[symptom] = has_symptom
        
        # 保存更新前的概率（用于计算展示）
        old_probs = self.current_probabilities.copy()
        
        # 贝叶斯更新
        self.bayesian_update(symptom, has_symptom)
        
        # 保存到历史
        self.probability_history.append(self.current_probabilities.copy())
        
        # 更新显示
        self.update_probability_display()
        self.update_history(symptom, has_symptom)
        self.update_calculation_display(symptom, has_symptom, old_probs)
        self.update_trend_chart()
        self.update_ai_hint()
        
        # 更新可用症状列表
        max_symptoms = self.difficulty_settings[self.difficulty.get()]['max_symptoms']
        if len(self.asked_symptoms) < max_symptoms:
            remaining_symptoms = [s for s in self.symptom_probabilities.keys() 
                                 if s not in self.asked_symptoms]
            self.symptom_combo['values'] = remaining_symptoms
            if remaining_symptoms:
                self.symptom_var.set(remaining_symptoms[0])
            else:
                self.symptom_var.set('')
        else:
            self.symptom_combo['values'] = []
            self.symptom_var.set('')
            messagebox.showinfo("提示", f"已达到难度限制的最大询问次数（{max_symptoms}次），请给出诊断！")
        
        # 更新询问计数
        self.question_count_label.config(text=str(len(self.asked_symptoms)))
        
    def bayesian_update(self, symptom, has_symptom):
        """贝叶斯更新"""
        old_probs = self.current_probabilities.copy()
        new_probs = {}
        
        for disease in self.diseases:
            prob_symptom_given_disease = self.symptom_probabilities[symptom][disease]
            
            if has_symptom:
                likelihood = prob_symptom_given_disease
            else:
                likelihood = 1 - prob_symptom_given_disease
            
            new_probs[disease] = likelihood * old_probs[disease]
        
        # 归一化
        total = sum(new_probs.values())
        if total > 0:
            self.current_probabilities = {
                disease: prob / total 
                for disease, prob in new_probs.items()
            }
    
    def update_history(self, symptom, has_symptom):
        """更新询问历史"""
        self.history_text.config(state=tk.NORMAL)
        
        response = "有 ✓" if has_symptom else "无 ✗"
        
        sorted_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top_disease = sorted_diseases[0][0]
        
        history_entry = f"\n{'='*45}\n"
        history_entry += f"第{len(self.asked_symptoms)}次询问\n"
        history_entry += f"症状：{symptom}\n"
        history_entry += f"回答：{response}\n"
        history_entry += f"当前最可能：{top_disease} "
        history_entry += f"({self.current_probabilities[top_disease]*100:.2f}%)\n"
        
        self.history_text.insert(tk.END, history_entry)
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def update_calculation_display(self, symptom, has_symptom, old_probs):
        """更新计算过程显示"""
        self.calculation_text.config(state=tk.NORMAL)
        self.calculation_text.delete(1.0, tk.END)
        
        response_text = "有" if has_symptom else "无"
        
        calc_text = f"""
{'='*60}
第 {len(self.asked_symptoms)} 次贝叶斯更新
症状：{symptom} ({response_text})
{'='*60}

1. 更新前概率（先验概率）：
"""
        
        sorted_old = sorted(old_probs.items(), key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_old[:5]:
            calc_text += f"   P({disease}) = {prob:.4f} ({prob*100:.2f}%)\n"
        
        calc_text += f"\n2. 条件概率（似然度）：\n"
        for disease in list(self.diseases.keys())[:5]:
            cond_prob = self.symptom_probabilities[symptom][disease]
            if has_symptom:
                calc_text += f"   P({symptom}|{disease}) = {cond_prob:.4f}\n"
            else:
                calc_text += f"   P(无{symptom}|{disease}) = {1-cond_prob:.4f}\n"
        
        calc_text += f"\n3. 贝叶斯更新计算：\n"
        calc_text += f"   P(疾病|症状) ∝ P(症状|疾病) × P(疾病)\n\n"
        
        unnormalized = {}
        for disease in self.diseases:
            cond_prob = self.symptom_probabilities[symptom][disease]
            likelihood = cond_prob if has_symptom else (1 - cond_prob)
            unnormalized[disease] = likelihood * old_probs[disease]
        
        calc_text += "   未归一化的后验概率：\n"
        sorted_unnorm = sorted(unnormalized.items(), key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_unnorm[:5]:
            calc_text += f"   {disease}: {prob:.6f}\n"
        
        total = sum(unnormalized.values())
        calc_text += f"\n   归一化常数（总和）：{total:.6f}\n"
        
        calc_text += f"\n4. 归一化后验概率（更新后）：\n"
        sorted_new = sorted(self.current_probabilities.items(), key=lambda x: x[1], reverse=True)
        for disease, prob in sorted_new[:5]:
            old_prob = old_probs[disease]
            change = prob - old_prob
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            calc_text += f"   P({disease}|{symptom}) = {prob:.4f} ({prob*100:.2f}%) "
            calc_text += f"{arrow} {abs(change)*100:.2f}%\n"
        
        calc_text += f"\n{'='*60}\n"
        
        self.calculation_text.insert(1.0, calc_text)
        self.calculation_text.config(state=tk.DISABLED)
    
    def update_trend_chart(self):
        """更新概率趋势图"""
        self.trend_canvas.delete('all')
        
        if len(self.probability_history) < 2:
            self.trend_canvas.create_text(
                300, 200,
                text="至少询问一个症状后才会显示趋势图",
                font=('Arial', 12),
                fill='gray'
            )
            return
        
        canvas_width = self.trend_canvas.winfo_width()
        canvas_height = self.trend_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        # 设置边距
        margin_left = 80
        margin_right = 150
        margin_top = 40
        margin_bottom = 60
        
        plot_width = canvas_width - margin_left - margin_right
        plot_height = canvas_height - margin_top - margin_bottom
        
        # 绘制标题
        self.trend_canvas.create_text(
            canvas_width // 2, 20,
            text="疾病概率变化趋势图",
            font=('Arial', 14, 'bold')
        )
        
        # 绘制坐标轴
        self.trend_canvas.create_line(
            margin_left, margin_top + plot_height,
            margin_left + plot_width, margin_top + plot_height,
            width=2
        )
        self.trend_canvas.create_line(
            margin_left, margin_top,
            margin_left, margin_top + plot_height,
            width=2
        )
        
        # Y轴标签
        for i in range(11):
            y = margin_top + plot_height - (i * plot_height / 10)
            self.trend_canvas.create_line(
                margin_left - 5, y,
                margin_left, y,
                width=1
            )
            self.trend_canvas.create_text(
                margin_left - 20, y,
                text=f"{i*10}%",
                font=('Arial', 9)
            )
        
        # X轴标签
        num_steps = len(self.probability_history)
        for i in range(num_steps):
            x = margin_left + (i * plot_width / max(num_steps - 1, 1))
            self.trend_canvas.create_line(
                x, margin_top + plot_height,
                x, margin_top + plot_height + 5,
                width=1
            )
            self.trend_canvas.create_text(
                x, margin_top + plot_height + 20,
                text=str(i),
                font=('Arial', 9)
            )
        
        # 轴标签
        self.trend_canvas.create_text(
            margin_left + plot_width // 2,
            canvas_height - 20,
            text="询问次数",
            font=('Arial', 11, 'bold')
        )
        
        self.trend_canvas.create_text(
            20,
            margin_top + plot_height // 2,
            text="概率 (%)",
            font=('Arial', 11, 'bold'),
            angle=90
        )
        
        # 绘制概率曲线（只显示前5个疾病）
        top_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        legend_y = margin_top
        for disease, _ in top_diseases:
            color = self.diseases[disease]['color']
            points = []
            
            for i, hist_probs in enumerate(self.probability_history):
                prob = hist_probs[disease]
                x = margin_left + (i * plot_width / max(num_steps - 1, 1))
                y = margin_top + plot_height - (prob * plot_height)
                points.append((x, y))
            
            # 绘制线条
            for i in range(len(points) - 1):
                self.trend_canvas.create_line(
                    points[i][0], points[i][1],
                    points[i+1][0], points[i+1][1],
                    fill=color,
                    width=3
                )
            
            # 绘制点
            for x, y in points:
                self.trend_canvas.create_oval(
                    x-4, y-4, x+4, y+4,
                    fill=color,
                    outline='black'
                )
            
            # 图例
            legend_x = margin_left + plot_width + 20
            self.trend_canvas.create_line(
                legend_x, legend_y,
                legend_x + 30, legend_y,
                fill=color,
                width=3
            )
            self.trend_canvas.create_text(
                legend_x + 40, legend_y,
                text=disease,
                font=('Arial', 10),
                anchor=tk.W
            )
            legend_y += 25
    
    def update_ai_hint(self):
        """更新AI建议"""
        if not self.difficulty_settings[self.difficulty.get()]['show_hints']:
            self.ai_hint_label.config(text="困难模式：AI建议已禁用")
            return
        
        if not self.asked_symptoms:
            self.ai_hint_label.config(text="开始询问症状以获得AI建议...")
            return
        
        # 计算信息增益
        best_symptom = self.calculate_best_symptom()
        
        if best_symptom:
            hint_text = f"建议询问：【{best_symptom}】\n"
            hint_text += "这个症状最能帮助区分当前疑似的疾病。"
            self.ai_hint_label.config(text=hint_text)
        else:
            self.ai_hint_label.config(text="已询问所有可用症状。")
    
    def calculate_best_symptom(self):
        """计算最佳下一个症状（基于信息增益）"""
        remaining_symptoms = [s for s in self.symptom_probabilities.keys() 
                             if s not in self.asked_symptoms]
        
        if not remaining_symptoms:
            return None
        
        # 简化的启发式：选择在top3疾病中概率差异最大的症状
        top_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        best_symptom = None
        max_variance = 0
        
        for symptom in remaining_symptoms:
            probs = [self.symptom_probabilities[symptom][disease] 
                    for disease, _ in top_diseases]
            variance = max(probs) - min(probs)
            
            if variance > max_variance:
                max_variance = variance
                best_symptom = symptom
        
        return best_symptom
    
    def show_ai_recommendation(self):
        """显示AI推荐"""
        best_symptom = self.calculate_best_symptom()
        
        if not best_symptom:
            messagebox.showinfo("AI推荐", "没有更多可询问的症状了。")
            return
        
        # 设置推荐的症状
        self.symptom_var.set(best_symptom)
        
        # 显示详细分析
        top_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        message = f"🤖 AI推荐询问：【{best_symptom}】\n\n"
        message += "在当前最可能的疾病中，此症状的条件概率：\n\n"
        
        for disease, prob in top_diseases:
            cond_prob = self.symptom_probabilities[best_symptom][disease]
            message += f"• {disease}（{prob*100:.1f}%）\n"
            message += f"  P({best_symptom}|{disease}) = {cond_prob*100:.1f}%\n\n"
        
        message += "这个症状最能帮助区分这些疾病！"
        
        messagebox.showinfo("AI推荐分析", message)
    
    def show_disease_info(self, event):
        """显示疾病详细信息"""
        # 清空之前的内容
        for widget in self.disease_info_frame.winfo_children():
            widget.destroy()
        
        disease_name = self.disease_var.get()
        if not disease_name:
            return
        
        disease_info = self.diseases[disease_name]
        color = disease_info['color']
        
        # 标题
        title_frame = tk.Frame(self.disease_info_frame, bg=color, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text=disease_name,
            font=('Arial', 22, 'bold'),
            bg=color,
            fg='white'
        ).pack(expand=True)
        
        # 内容区域
        content_frame = tk.Frame(self.disease_info_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # 基本信息
        info_items = [
            ("📝 描述", disease_info['description']),
            ("💊 治疗方案", disease_info['treatment']),
            ("⏱️ 病程", disease_info['duration']),
            ("📊 先验概率", f"{disease_info['prior']*100:.1f}%")
        ]
        
        for label, value in info_items:
            frame = tk.Frame(content_frame, bg='white')
            frame.pack(fill=tk.X, pady=10)
            
            tk.Label(
                frame,
                text=label,
                font=('Arial', 13, 'bold'),
                bg='white',
                fg=color
            ).pack(anchor=tk.W)
            
            tk.Label(
                frame,
                text=value,
                font=('Arial', 12),
                bg='white',
                wraplength=700,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=20, pady=5)
        
        # 典型症状
        tk.Label(
            content_frame,
            text="🔍 典型症状及出现概率",
            font=('Arial', 13, 'bold'),
            bg='white',
            fg=color
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # 获取该疾病的症状概率并排序
        symptom_probs = {
            symptom: probs[disease_name]
            for symptom, probs in self.symptom_probabilities.items()
        }
        sorted_symptoms = sorted(symptom_probs.items(), key=lambda x: x[1], reverse=True)
        
        # 创建症状表格
        symptom_frame = tk.Frame(content_frame, bg='white')
        symptom_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        for i, (symptom, prob) in enumerate(sorted_symptoms):
            row_frame = tk.Frame(symptom_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(
                row_frame,
                text=symptom,
                font=('Arial', 11),
                bg='white',
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            # 进度条
            bar_width = int(300 * prob)
            canvas = tk.Canvas(row_frame, width=300, height=20, bg='white', highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=10)
            canvas.create_rectangle(0, 0, bar_width, 20, fill=color, outline='')
            
            tk.Label(
                row_frame,
                text=f"{prob*100:.1f}%",
                font=('Arial', 11, 'bold'),
                bg='white',
                width=8,
                anchor=tk.W
            ).pack(side=tk.LEFT)
    
    def make_diagnosis(self):
        """给出最终诊断"""
        if not self.asked_symptoms:
            messagebox.showinfo("提示", "请至少询问一个症状后再做出诊断！")
            return
        
        # 找出概率最高的疾病
        most_likely = max(
            self.current_probabilities.items(),
            key=lambda x: x[1]
        )
        
        disease_name = most_likely[0]
        probability = most_likely[1] * 100
        
        # 构建诊断报告
        diagnosis = f"═══════════════════════════════════════\n"
        diagnosis += f"          🏥 诊断报告 🏥\n"
        diagnosis += f"═══════════════════════════════════════\n\n"
        diagnosis += f"诊断时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        diagnosis += f"询问症状数：{len(self.asked_symptoms)}\n"
        diagnosis += f"难度级别：{self.difficulty.get()}\n\n"
        diagnosis += f"───────────────────────────────────────\n"
        diagnosis += f"最可能的诊断：\n\n"
        diagnosis += f"  【{disease_name}】\n"
        diagnosis += f"  置信度：{probability:.2f}%\n\n"
        diagnosis += f"───────────────────────────────────────\n"
        diagnosis += f"询问的症状：\n\n"
        
        for symptom in self.asked_symptoms:
            response = "✓ 有" if self.symptom_responses[symptom] else "✗ 无"
            diagnosis += f"  {response}  {symptom}\n"
        
        diagnosis += f"\n───────────────────────────────────────\n"
        diagnosis += f"完整概率分布：\n\n"
        sorted_diseases = sorted(
            self.current_probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for i, (disease, prob) in enumerate(sorted_diseases, 1):
            diagnosis += f"  {i}. {disease}: {prob*100:.2f}%\n"
        
        diagnosis += f"\n───────────────────────────────────────\n"
        disease_info = self.diseases[disease_name]
        diagnosis += f"治疗建议：\n  {disease_info['treatment']}\n"
        diagnosis += f"\n预计病程：\n  {disease_info['duration']}\n"
        diagnosis += f"═══════════════════════════════════════\n"
        
        # 记录到游戏统计
        self.game_statistics['total_games'] += 1
        self.game_statistics['game_history'].append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'diagnosis': disease_name,
            'num_questions': len(self.asked_symptoms),
            'confidence': probability
        })
        
        # 更新统计显示
        self.update_stats_display()
        
        messagebox.showinfo("诊断结果", diagnosis)
        
        # 询问是否重新开始
        if messagebox.askyesno("继续游戏", "是否开始新的诊断？"):
            self.reset_game()
    
    def update_stats_display(self):
        """更新统计显示"""
        total = self.game_statistics['total_games']
        
        self.total_games_label.config(text=f"总游戏次数：{total}")
        
        if total > 0:
            avg_questions = sum(g['num_questions'] for g in self.game_statistics['game_history']) / total
            self.avg_questions_label.config(text=f"平均询问数：{avg_questions:.1f}")
            
            # 更新历史表格
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            for game in reversed(self.game_statistics['game_history']):
                self.history_tree.insert('', 'end', values=(
                    game['time'],
                    game['diagnosis'],
                    game['num_questions'],
                    f"{game['confidence']:.1f}%"
                ))
    
    def on_difficulty_change(self):
        """难度变更处理"""
        messagebox.showinfo(
            "难度设置",
            f"难度已设置为：{self.difficulty.get()}\n\n"
            f"最大询问次数：{self.difficulty_settings[self.difficulty.get()]['max_symptoms']}\n"
            f"AI提示：{'开启' if self.difficulty_settings[self.difficulty.get()]['show_hints'] else '关闭'}"
        )
        self.update_ai_hint()
    
    def reset_game(self):
        """重置游戏"""
        self.reset_probabilities()
        self.asked_symptoms = []
        self.symptom_responses = {}
        
        # 重置界面
        self.symptom_combo['values'] = list(self.symptom_probabilities.keys())
        if self.symptom_probabilities:
            self.symptom_combo.current(0)
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state=tk.DISABLED)
        
        self.calculation_text.config(state=tk.NORMAL)
        self.calculation_text.delete(1.0, tk.END)
        self.calculation_text.config(state=tk.DISABLED)
        
        self.question_count_label.config(text="0")
        
        self.update_probability_display()
        self.update_trend_chart()
        self.update_ai_hint()


def main():
    root = tk.Tk()
    app = BayesianDiagnosisEnhanced(root)
    
    # 等待窗口完全显示后更新画布
    root.update()
    app.update_probability_display()
    app.update_trend_chart()
    
    root.mainloop()


if __name__ == '__main__':
    main()






