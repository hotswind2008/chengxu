"""生成条件概率PDF课件的脚本
使用 reportlab 库创建一份完整的条件概率PDF课件
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Frame, PageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


class SlideCanvas(canvas.Canvas):
    """自定义Canvas类，用于添加页眉页脚"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            if page_num > 1:  # 不在标题页显示页码
                self.draw_page_number(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_number(self, page_num, page_count):
        """绘制页码"""
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.grey)
        text = f"{page_num} / {page_count}"
        self.drawRightString(landscape(A4)[0] - 0.5*inch, 0.4*inch, text)
        self.restoreState()


def create_title_page(story, styles):
    """创建标题页"""
    story.append(Spacer(1, 2*inch))
    
    # 主标题
    title = Paragraph("条件概率", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # 副标题
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle = Paragraph("Conditional Probability", subtitle_style)
    story.append(subtitle)
    story.append(Spacer(1, 0.2*inch))
    
    # 课程信息
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    info = Paragraph("概率论与数理统计", info_style)
    story.append(info)
    
    story.append(PageBreak())


def create_section_slide(story, styles, title, content_list):
    """创建内容页"""
    story.append(Spacer(1, 0.5*inch))
    
    # 标题
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#003366'),
        spaceAfter=20,
        spaceBefore=10
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 内容
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=14,
        leading=20,
        leftIndent=20,
        spaceAfter=8
    )
    
    for item in content_list:
        para = Paragraph(item, content_style)
        story.append(para)
    
    story.append(PageBreak())


def create_formula_slide(story, styles, title, formula, explanations):
    """创建公式页"""
    story.append(Spacer(1, 0.5*inch))
    
    # 标题
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#003366'),
        spaceAfter=20
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.4*inch))
    
    # 公式框
    formula_style = ParagraphStyle(
        'Formula',
        parent=styles['Normal'],
        fontSize=20,
        textColor=colors.HexColor('#CC0000'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=28
    )
    
    formula_table = Table(
        [[Paragraph(formula, formula_style)]],
        colWidths=[7*inch]
    )
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F8FF')),
        ('LINEWIDTH', (0, 0), (-1, -1), 2),
        ('LINECOLOR', (0, 0), (-1, -1), colors.HexColor('#003366')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(formula_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 说明
    explain_style = ParagraphStyle(
        'Explain',
        parent=styles['Normal'],
        fontSize=13,
        leading=18,
        leftIndent=30,
        spaceAfter=6
    )
    
    for exp in explanations:
        story.append(Paragraph(exp, explain_style))
    
    story.append(PageBreak())


def create_example_slide(story, styles, title, problem, solution_steps):
    """创建例题页"""
    story.append(Spacer(1, 0.4*inch))
    
    # 标题
    title_style = ParagraphStyle(
        'ExampleTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#006633'),
        spaceAfter=18
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 问题框
    problem_style = ParagraphStyle(
        'Problem',
        parent=styles['Normal'],
        fontSize=14,
        leading=20,
        fontName='Helvetica-Bold'
    )
    problem_table = Table(
        [[Paragraph(problem, problem_style)]],
        colWidths=[8*inch]
    )
    problem_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFACD')),
        ('LINEWIDTH', (0, 0), (-1, -1), 1.5),
        ('LINECOLOR', (0, 0), (-1, -1), colors.HexColor('#006633')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(problem_table)
    story.append(Spacer(1, 0.25*inch))
    
    # 解答
    solution_style = ParagraphStyle(
        'Solution',
        parent=styles['Normal'],
        fontSize=13,
        leading=18,
        leftIndent=20,
        spaceAfter=5
    )
    
    for step in solution_steps:
        if '解：' in step or '答案：' in step:
            bold_style = ParagraphStyle(
                'BoldSolution',
                parent=solution_style,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#006633')
            )
            story.append(Paragraph(step, bold_style))
        else:
            story.append(Paragraph(step, solution_style))
    
    story.append(PageBreak())


def main():
    """生成PDF课件"""
    
    # 创建PDF文档
    filename = "conditional_probability.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # 准备内容容器
    story = []
    styles = getSampleStyleSheet()
    
    # 第1页：标题页
    create_title_page(story, styles)
    
    # 第2页：引入
    create_section_slide(
        story, styles,
        "引入：什么是条件概率？",
        [
            "<b>• 生活中的问题：</b>",
            "  • 已知某人检测呈阳性，他真正患病的概率是多少？",
            "  • 已知今天下雨，明天继续下雨的概率是多少？",
            "  • 已知抽到红球，下一次抽到红球的概率是多少？",
            "",
            "<b>• 这些都是在「已知某一事件发生」的条件下，求另一事件发生的概率问题</b>",
            "",
            "<b>• 这就是条件概率的核心思想</b>"
        ]
    )
    
    # 第3页：条件概率的定义
    create_formula_slide(
        story, styles,
        "条件概率的定义",
        "P(A|B) = P(A∩B) / P(B)",
        [
            "<b>• P(A|B)</b> 读作：在事件B发生的条件下，事件A发生的概率",
            "",
            "<b>• 其中：</b>",
            "  • <i>P(A∩B)</i> 表示事件A和B同时发生的概率",
            "  • <i>P(B) &gt; 0</i> 表示事件B发生的概率（前提条件）",
            "",
            "<b>• 直观理解：</b>将样本空间缩小到B，然后在B中求A发生的概率"
        ]
    )
    
    # 第4页：条件概率的性质
    create_section_slide(
        story, styles,
        "条件概率的性质",
        [
            "<b>对于固定的事件B (P(B) &gt; 0)，P(·|B)满足概率的所有性质：</b>",
            "",
            "<b>1. 非负性：</b> P(A|B) ≥ 0",
            "",
            "<b>2. 规范性：</b> P(Ω|B) = 1",
            "",
            "<b>3. 可加性：</b> 若A₁, A₂, ..., Aₙ互不相容，则",
            "   P(A₁∪A₂∪...∪Aₙ|B) = P(A₁|B) + P(A₂|B) + ... + P(Aₙ|B)",
            "",
            "• 条件概率本质上也是概率，只是样本空间变小了"
        ]
    )
    
    # 第5页：乘法公式
    create_formula_slide(
        story, styles,
        "乘法公式（Multiplication Rule）",
        "P(A∩B) = P(B) · P(A|B) = P(A) · P(B|A)",
        [
            "由条件概率的定义直接得出",
            "",
            "<b>• 推广形式（链式法则）：</b>",
            "  P(A₁∩A₂∩...∩Aₙ) = P(A₁)·P(A₂|A₁)·P(A₃|A₁∩A₂)·...·P(Aₙ|A₁∩...∩Aₙ₋₁)",
            "",
            "<b>• 应用：</b>计算多个事件同时发生的概率"
        ]
    )
    
    # 第6页：例题1
    create_example_slide(
        story, styles,
        "例题1：不放回抽球问题",
        "<b>问题：</b>袋中有5个红球和3个白球，不放回地依次抽取2个球。求第一次抽到红球的条件下，第二次也抽到红球的概率。",
        [
            "<b>解：</b>",
            "设 A = {第一次抽到红球}，B = {第二次抽到红球}",
            "",
            "P(A) = 5/8",
            "",
            "在第一次抽到红球后，袋中剩余：4个红球，3个白球（共7个）",
            "",
            "P(B|A) = 4/7",
            "",
            "<b>答案：</b>第二次也抽到红球的概率为 <font color='red'>4/7</font>"
        ]
    )
    
    # 第7页：全概率公式
    create_formula_slide(
        story, styles,
        "全概率公式（Law of Total Probability）",
        "P(A) = Σ P(Bᵢ) · P(A|Bᵢ)",
        [
            "设 B₁, B₂, ..., Bₙ 是样本空间的一个<b>划分</b>（互不相容且并集为全集）",
            "",
            "则对任意事件A：",
            "  P(A) = P(B₁)·P(A|B₁) + P(B₂)·P(A|B₂) + ... + P(Bₙ)·P(A|Bₙ)",
            "",
            "<b>• 意义：</b>通过「分解」来计算复杂事件的概率",
            "<b>• 应用：</b>将复杂问题分解为若干简单情况的组合"
        ]
    )
    
    # 第8页：例题2
    create_example_slide(
        story, styles,
        "例题2：产品质量检验",
        "<b>问题：</b>三个工厂A、B、C生产同一产品，产量占比为30%、45%、25%，次品率分别为2%、3%、4%。随机抽取一件产品，求它是次品的概率。",
        [
            "<b>解：</b>",
            "设 D = {抽到次品}，A₁={来自工厂A}，A₂={来自工厂B}，A₃={来自工厂C}",
            "",
            "已知：P(A₁)=0.30, P(A₂)=0.45, P(A₃)=0.25",
            "      P(D|A₁)=0.02, P(D|A₂)=0.03, P(D|A₃)=0.04",
            "",
            "由全概率公式：",
            "P(D) = P(A₁)·P(D|A₁) + P(A₂)·P(D|A₂) + P(A₃)·P(D|A₃)",
            "     = 0.30×0.02 + 0.45×0.03 + 0.25×0.04",
            "     = 0.006 + 0.0135 + 0.010 = 0.0295",
            "",
            "<b>答案：</b>抽到次品的概率约为 <font color='red'>2.95%</font>"
        ]
    )
    
    # 第9页：贝叶斯公式
    create_formula_slide(
        story, styles,
        "贝叶斯公式（Bayes' Theorem）",
        "P(Bᵢ|A) = [P(Bᵢ)·P(A|Bᵢ)] / [Σ P(Bⱼ)·P(A|Bⱼ)]",
        [
            "在全概率公式的基础上，可以推导出贝叶斯公式：",
            "",
            "  P(Bᵢ|A) = P(Bᵢ∩A) / P(A) = P(Bᵢ)·P(A|Bᵢ) / P(A)",
            "",
            "<b>• P(Bᵢ)</b> 称为<i>先验概率</i>（prior probability）",
            "<b>• P(Bᵢ|A)</b> 称为<i>后验概率</i>（posterior probability）",
            "",
            "<b>• 意义：</b>已知结果A发生，反推原因Bᵢ的概率",
            "<b>• 应用：</b>医学诊断、机器学习、风险评估等"
        ]
    )
    
    # 第10页：例题3
    create_example_slide(
        story, styles,
        "例题3：医学诊断问题（贝叶斯公式经典应用）",
        "<b>问题：</b>某疾病的患病率为1%。检测该病的准确率为：患病者检测阳性概率95%，健康者检测阳性概率5%。若某人检测呈阳性，求其真正患病的概率。",
        [
            "<b>解：</b>",
            "设 D={患病}，T={检测阳性}",
            "已知：P(D)=0.01, P(D̄)=0.99, P(T|D)=0.95, P(T|D̄)=0.05",
            "",
            "由贝叶斯公式：",
            "P(D|T) = P(D)·P(T|D) / [P(D)·P(T|D) + P(D̄)·P(T|D̄)]",
            "       = (0.01×0.95) / (0.01×0.95 + 0.99×0.05)",
            "       = 0.0095 / (0.0095 + 0.0495)",
            "       = 0.0095 / 0.059 ≈ 0.161",
            "",
            "<b>答案：</b>检测呈阳性的人真正患病的概率约为 <font color='red'>16.1%</font>",
            "",
            "<i>（尽管检测准确率很高，但由于患病率很低，阳性结果的可信度并不高）</i>"
        ]
    )
    
    # 第11页：独立性
    create_section_slide(
        story, styles,
        "事件的独立性",
        [
            "<b>• 定义：</b>若 P(A∩B) = P(A)·P(B)，则称事件A与B<b>相互独立</b>",
            "",
            "<b>• 等价条件</b>（当P(B)&gt;0时）：",
            "  • P(A|B) = P(A)",
            "  • 即：B的发生不影响A的概率",
            "",
            "<b>• 独立性的直观理解：</b>",
            "  • 两个事件互不影响",
            "  • 一个事件的发生不改变另一个事件的概率",
            "",
            "<b>• 例子：</b>",
            "  • <font color='green'>独立：</font>连续两次抛硬币的结果",
            "  • <font color='red'>不独立：</font>不放回抽球"
        ]
    )
    
    # 第12页：条件概率与独立性
    create_section_slide(
        story, styles,
        "条件概率 vs 独立性",
        [
            "<b>• 条件概率</b>适用于「相关」的事件",
            "  • 一个事件的发生会影响另一个事件的概率",
            "  • P(A|B) ≠ P(A)",
            "",
            "<b>• 独立性</b>是特殊情况",
            "  • 若A、B独立，则 P(A|B) = P(A)",
            "  • 此时条件概率退化为无条件概率",
            "",
            "<b>• 实际问题中：</b>",
            "  • 大多数事件是相关的（需要用条件概率）",
            "  • 少数事件是独立的（可以简化计算）",
            "",
            "<b>• 判断独立性的关键：</b>分析事件之间的因果关系"
        ]
    )
    
    # 第13页：综合例题 - 三门问题
    create_example_slide(
        story, styles,
        "综合例题：三门问题（Monty Hall Problem）",
        "<b>问题：</b>游戏节目中有3扇门，其中1扇门后是汽车，2扇门后是山羊。你选择一扇门后，主持人打开另一扇有山羊的门。此时你是否应该换门？",
        [
            "<b>解：</b>",
            "<b>策略1：坚持原选择</b>",
            "  • 初始选中汽车的概率：P(坚持赢) = 1/3",
            "",
            "<b>策略2：换门</b>",
            "  • 初始选错的概率为2/3，此时换门必赢",
            "  • P(换门赢) = 2/3",
            "",
            "<b>条件概率分析：</b>",
            "设A={初始选中汽车}，H={主持人打开的门}",
            "P(A|H) = P(A)·P(H|A) / P(H) = (1/3)·1 / 1 = 1/3",
            "P(Ā|H) = 1 - 1/3 = 2/3",
            "",
            "<b>答案：</b><font color='red'>应该换门</font>，换门的获胜概率是坚持的<font color='red'>两倍</font>！"
        ]
    )
    
    # 第14页：重要公式总结
    create_section_slide(
        story, styles,
        "重要公式总结",
        [
            "<b>1. 条件概率定义：</b>",
            "   P(A|B) = P(A∩B) / P(B)  (P(B) &gt; 0)",
            "",
            "<b>2. 乘法公式：</b>",
            "   P(A∩B) = P(A)·P(B|A) = P(B)·P(A|B)",
            "",
            "<b>3. 全概率公式：</b>",
            "   P(A) = Σ P(Bᵢ)·P(A|Bᵢ)  （B₁,...,Bₙ为样本空间的划分）",
            "",
            "<b>4. 贝叶斯公式：</b>",
            "   P(Bᵢ|A) = P(Bᵢ)·P(A|Bᵢ) / Σ P(Bⱼ)·P(A|Bⱼ)",
            "",
            "<b>5. 独立性：</b>",
            "   P(A∩B) = P(A)·P(B) ⟺ P(A|B) = P(A)"
        ]
    )
    
    # 第15页：应用领域
    create_section_slide(
        story, styles,
        "条件概率的应用领域",
        [
            "<b>• 医学诊断</b>",
            "  • 根据症状推断疾病概率",
            "  • 根据检测结果判断患病可能性",
            "",
            "<b>• 机器学习与人工智能</b>",
            "  • 朴素贝叶斯分类器",
            "  • 贝叶斯网络、隐马尔可夫模型",
            "",
            "<b>• 金融风险评估</b>",
            "  • 信用评分、违约概率预测",
            "",
            "<b>• 信息检索与推荐系统</b>",
            "  • 垃圾邮件过滤、个性化推荐",
            "",
            "<b>• 质量控制与可靠性工程</b>"
        ]
    )
    
    # 第16页：课程总结
    create_section_slide(
        story, styles,
        "课程总结",
        [
            "<b>• 条件概率是概率论的核心概念之一</b>",
            "",
            "<b>• 关键思想：</b>在「已知条件」下重新计算概率",
            "",
            "<b>• 核心公式：</b>",
            "  • 条件概率、乘法公式、全概率公式、贝叶斯公式",
            "",
            "<b>• 应用广泛：</b>",
            "  • 从日常生活到高科技领域都有重要应用",
            "",
            "<b>• 学习方法：</b>",
            "  • 理解概念的直观意义",
            "  • 熟练掌握公式推导",
            "  • 多做习题，培养建模能力"
        ]
    )
    
    # 第17页：结束页
    story.append(Spacer(1, 2.5*inch))
    
    end_title_style = ParagraphStyle(
        'EndTitle',
        parent=styles['Title'],
        fontSize=48,
        textColor=colors.HexColor('#003366')
    )
    story.append(Paragraph("谢谢！", end_title_style))
    story.append(Spacer(1, 0.3*inch))
    
    end_subtitle_style = ParagraphStyle(
        'EndSubtitle',
        parent=styles['Normal'],
        fontSize=22,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Questions &amp; Discussion", end_subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("条件概率课程结束", end_subtitle_style))
    
    # 生成PDF
    doc.build(story, canvasmaker=SlideCanvas)
    
    print(f"✓ PDF课件已生成：{filename}")
    print(f"  - 页面尺寸：A4 横向")
    print(f"  - 共 17 页内容")
    print(f"  - 包含定义、公式、例题和应用")
    print("\nPDF课件内容包括：")
    print("  1. 条件概率的定义和性质")
    print("  2. 乘法公式")
    print("  3. 全概率公式")
    print("  4. 贝叶斯公式")
    print("  5. 事件独立性")
    print("  6. 丰富的例题（抽球、产品检验、医学诊断、三门问题）")
    print("  7. 应用领域介绍")


if __name__ == "__main__":
    main()





