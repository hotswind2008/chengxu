"""生成条件概率PDF课件的脚本（改进版）
使用 reportlab 库创建一份完整的条件概率PDF课件
支持中文字体和专业数学公式排版
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os


def register_chinese_fonts():
    """注册中文字体"""
    try:
        # 尝试注册系统中文字体
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))  # 华文宋体
        pdfmetrics.registerFont(UnicodeCIDFont('STHeiti-Light'))  # 华文黑体
        return 'STSong-Light', 'STHeiti-Light'
    except:
        try:
            # 备选方案：使用其他CID字体
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            return 'HeiseiMin-W3', 'HeiseiKakuGo-W5'
        except:
            # 最后备选：返回默认字体
            print("警告：未找到中文字体，将使用默认字体")
            return 'Helvetica', 'Helvetica-Bold'


# 注册中文字体
FONT_SONG, FONT_HEI = register_chinese_fonts()


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
    
    # 主标题 - 使用中文字体
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName=FONT_HEI if FONT_HEI != 'Helvetica-Bold' else 'Helvetica-Bold',
        fontSize=54,
        textColor=colors.HexColor('#003366'),
        alignment=TA_CENTER,
        leading=60
    )
    title = Paragraph("条件概率", title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # 副标题
    subtitle_style = ParagraphStyle(
        'Subtitle',
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
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
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
        fontName=FONT_HEI if FONT_HEI != 'Helvetica-Bold' else 'Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#003366'),
        spaceAfter=20,
        spaceBefore=10,
        leading=32
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 内容
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
        fontSize=15,
        leading=24,
        leftIndent=20,
        spaceAfter=8
    )
    
    for item in content_list:
        para = Paragraph(item, content_style)
        story.append(para)
    
    story.append(PageBreak())


def create_formula_slide(story, styles, title, formula, explanations):
    """创建公式页 - 使用更专业的数学排版"""
    story.append(Spacer(1, 0.5*inch))
    
    # 标题
    title_style = ParagraphStyle(
        'SlideTitle',
        parent=styles['Heading1'],
        fontName=FONT_HEI if FONT_HEI != 'Helvetica-Bold' else 'Helvetica-Bold',
        fontSize=28,
        textColor=colors.HexColor('#003366'),
        spaceAfter=20,
        leading=32
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.4*inch))
    
    # 公式框 - 使用教科书风格
    formula_style = ParagraphStyle(
        'Formula',
        parent=styles['Normal'],
        fontSize=24,
        textColor=colors.HexColor('#000000'),
        alignment=TA_CENTER,
        fontName='Times-Bold',  # 使用Times字体使公式更专业
        leading=32
    )
    
    formula_table = Table(
        [[Paragraph(formula, formula_style)]],
        colWidths=[7.5*inch]
    )
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFEF0')),
        ('BOX', (0, 0), (-1, -1), 2.5, colors.HexColor('#8B4513')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(formula_table)
    story.append(Spacer(1, 0.35*inch))
    
    # 说明
    explain_style = ParagraphStyle(
        'Explain',
        parent=styles['Normal'],
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
        fontSize=14,
        leading=22,
        leftIndent=30,
        spaceAfter=8
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
        fontName=FONT_HEI if FONT_HEI != 'Helvetica-Bold' else 'Helvetica-Bold',
        fontSize=26,
        textColor=colors.HexColor('#006633'),
        spaceAfter=18,
        leading=30
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 问题框
    problem_style = ParagraphStyle(
        'Problem',
        parent=styles['Normal'],
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
        fontSize=14,
        leading=22
    )
    problem_table = Table(
        [[Paragraph(problem, problem_style)]],
        colWidths=[8.2*inch]
    )
    problem_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFEF5')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8B7355')),
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
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
        fontSize=13,
        leading=20,
        leftIndent=25,
        spaceAfter=6
    )
    
    for step in solution_steps:
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
            "<b>● 生活中的问题：</b>",
            "",
            "　　• 已知某人检测呈阳性，他真正患病的概率是多少？",
            "",
            "　　• 已知今天下雨，明天继续下雨的概率是多少？",
            "",
            "　　• 已知抽到红球，下一次抽到红球的概率是多少？",
            "",
            "<b>● 这些都是在「已知某一事件发生」的条件下，求另一事件发生的概率问题</b>",
            "",
            "<b>● 这就是条件概率的核心思想</b>"
        ]
    )
    
    # 第3页：条件概率的定义
    create_formula_slide(
        story, styles,
        "条件概率的定义",
        '<font size="26"><i>P</i>(<i>A</i>|<i>B</i>) = <i>P</i>(<i>A</i>∩<i>B</i>) / <i>P</i>(<i>B</i>)</font>',
        [
            "<b>【定义】</b>设 <i>A</i>、<i>B</i> 是两个事件，且 <i>P</i>(<i>B</i>) &gt; 0，称",
            "",
            '　　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>|<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>∩<font face="Times-Italic" size="15">B</font>) / <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>)',
            "",
            "为在事件 <i>B</i> 发生的条件下，事件 <i>A</i> 发生的<b>条件概率</b>。",
            "",
            "<b>【直观理解】</b>将样本空间缩小到 <i>B</i>，然后在 <i>B</i> 中求 <i>A</i> 发生的概率。",
            "",
            "<b>【读作】</b><i>P</i>(<i>A</i>|<i>B</i>) 读作：\"<i>A</i> 在 <i>B</i> 条件下的概率\"或\"<i>B</i> 发生时 <i>A</i> 的概率\"。"
        ]
    )
    
    # 第4页：条件概率的性质
    create_section_slide(
        story, styles,
        "条件概率的性质",
        [
            "<b>【定理】</b>对于固定的事件 <i>B</i> (<i>P</i>(<i>B</i>) &gt; 0)，<i>P</i>(·|<i>B</i>) 满足概率的所有性质：",
            "",
            '<b>（1）非负性：</b><font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font>) ≥ 0',
            "",
            '<b>（2）规范性：</b><font face="Times-Italic" size="14">P</font>(Ω|<font face="Times-Italic" size="14">B</font>) = 1',
            "",
            '<b>（3）可列可加性：</b>若 <font face="Times-Italic" size="14">A</font>₁, <font face="Times-Italic" size="14">A</font>₂, ..., <font face="Times-Italic" size="14">A</font><sub>n</sub> 两两互不相容，则',
            "",
            '　　<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>₁∪<font face="Times-Italic" size="14">A</font>₂∪...∪<font face="Times-Italic" size="14">A</font><sub>n</sub>|<font face="Times-Italic" size="14">B</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>₁|<font face="Times-Italic" size="14">B</font>) + <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>₂|<font face="Times-Italic" size="14">B</font>) + ... + <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font><sub>n</sub>|<font face="Times-Italic" size="14">B</font>)',
            "",
            "<b>【注】</b>条件概率本质上也是概率，只是样本空间由 Ω 变为 <i>B</i>。"
        ]
    )
    
    # 第5页：乘法公式
    create_formula_slide(
        story, styles,
        "乘法公式（Multiplication Rule）",
        '<font size="24"><i>P</i>(<i>A</i>∩<i>B</i>) = <i>P</i>(<i>A</i>) · <i>P</i>(<i>B</i>|<i>A</i>) = <i>P</i>(<i>B</i>) · <i>P</i>(<i>A</i>|<i>B</i>)</font>',
        [
            "<b>【定理】</b>设 <i>P</i>(<i>A</i>) &gt; 0，<i>P</i>(<i>B</i>) &gt; 0，则",
            "",
            '　　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>∩<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>) · <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>|<font face="Times-Italic" size="15">A</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>) · <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>|<font face="Times-Italic" size="15">B</font>)',
            "",
            "<b>【推广】</b>（链式法则）对于 <i>n</i> 个事件：",
            "",
            '　　<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>₁∩<font face="Times-Italic" size="13">A</font>₂∩...∩<font face="Times-Italic" size="13">A</font><sub>n</sub>) = <font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>₁)·<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>₂|<font face="Times-Italic" size="13">A</font>₁)·<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>₃|<font face="Times-Italic" size="13">A</font>₁∩<font face="Times-Italic" size="13">A</font>₂)·...·<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font><sub>n</sub>|<font face="Times-Italic" size="13">A</font>₁∩...∩<font face="Times-Italic" size="13">A</font><sub>n-1</sub>)',
            "",
            "<b>【应用】</b>计算多个事件同时发生的概率。"
        ]
    )
    
    # 第6页：例题1
    create_example_slide(
        story, styles,
        "例题1：不放回抽球问题",
        "<b>【题目】</b>袋中有5个红球和3个白球，不放回地依次抽取2个球。求第一次抽到红球的条件下，第二次也抽到红球的概率。",
        [
            "<b>【解】</b>",
            "",
            "设 <i>A</i> = {第一次抽到红球}，<i>B</i> = {第二次抽到红球}",
            "",
            '初始时袋中共有 8 个球，其中红球 5 个，故　<font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>) = 5/8',
            "",
            "在第一次抽到红球后，袋中剩余：<b>4个红球，3个白球</b>（共7个球）",
            "",
            '因此　<font face="Times-Italic">P</font>(<font face="Times-Italic">B</font>|<font face="Times-Italic">A</font>) = <sup>4</sup>/<sub>7</sub>',
            "",
            '<b>【答】</b>第二次也抽到红球的概率为　<font color="#CC0000" size="15"><b>4/7</b></font>'
        ]
    )
    
    # 第7页：全概率公式
    create_formula_slide(
        story, styles,
        "全概率公式（Law of Total Probability）",
        '<font size="22"><i>P</i>(<i>A</i>) = Σ<sub>i=1</sub><sup>n</sup> <i>P</i>(<i>B</i><sub>i</sub>) · <i>P</i>(<i>A</i>|<i>B</i><sub>i</sub>)</font>',
        [
            '<b>【定理】</b>设 <font face="Times-Italic">B</font>₁, <font face="Times-Italic">B</font>₂, ..., <font face="Times-Italic">B</font><sub>n</sub> 是样本空间 Ω 的一个<b>划分</b>，即',
            "",
            '　　（1）<font face="Times-Italic">B</font><sub>i</sub>∩<font face="Times-Italic">B</font><sub>j</sub> = ∅（<font face="Times-Italic">i</font> ≠ <font face="Times-Italic">j</font>）',
            '　　（2）<font face="Times-Italic">B</font>₁∪<font face="Times-Italic">B</font>₂∪...∪<font face="Times-Italic">B</font><sub>n</sub> = Ω',
            '　　（3）<font face="Times-Italic">P</font>(<font face="Times-Italic">B</font><sub>i</sub>) &gt; 0（<font face="Times-Italic">i</font> = 1, 2, ..., <font face="Times-Italic">n</font>）',
            "",
            '则对任意事件 <font face="Times-Italic">A</font>：',
            "",
            '　　<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font>₁)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font>₁) + <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font>₂)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font>₂) + ... + <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font><sub>n</sub>)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font><sub>n</sub>)',
            "",
            "<b>【意义】</b>通过对样本空间的「分解」来计算复杂事件的概率。"
        ]
    )
    
    # 第8页：例题2
    create_example_slide(
        story, styles,
        "例题2：产品质量检验问题",
        "<b>【题目】</b>三个工厂 A、B、C 生产同一产品，产量占比分别为 30%、45%、25%，次品率分别为 2%、3%、4%。从所有产品中随机抽取一件，求它是次品的概率。",
        [
            "<b>【解】</b>",
            "",
            "设 <i>D</i> = {抽到次品}",
            "　 <i>A</i>₁ = {产品来自工厂A}，<i>A</i>₂ = {产品来自工厂B}，<i>A</i>₃ = {产品来自工厂C}",
            "",
            "由题意知：",
            "　　<i>P</i>(<i>A</i>₁) = 0.30，　<i>P</i>(<i>A</i>₂) = 0.45，　<i>P</i>(<i>A</i>₃) = 0.25",
            "　　<i>P</i>(<i>D</i>|<i>A</i>₁) = 0.02，　<i>P</i>(<i>D</i>|<i>A</i>₂) = 0.03，　<i>P</i>(<i>D</i>|<i>A</i>₃) = 0.04",
            "",
            "显然 <i>A</i>₁, <i>A</i>₂, <i>A</i>₃ 构成样本空间的一个划分，由<b>全概率公式</b>：",
            "",
            "　　<i>P</i>(<i>D</i>) = <i>P</i>(<i>A</i>₁)·<i>P</i>(<i>D</i>|<i>A</i>₁) + <i>P</i>(<i>A</i>₂)·<i>P</i>(<i>D</i>|<i>A</i>₂) + <i>P</i>(<i>A</i>₃)·<i>P</i>(<i>D</i>|<i>A</i>₃)",
            "　　　　= 0.30×0.02 + 0.45×0.03 + 0.25×0.04",
            "　　　　= 0.006 + 0.0135 + 0.010",
            "　　　　= 0.0295",
            "",
            '<b>【答】</b>抽到次品的概率为　<font color="#CC0000" size="15"><b>0.0295 = 2.95%</b></font>'
        ]
    )
    
    # 第9页：贝叶斯公式
    create_formula_slide(
        story, styles,
        "贝叶斯公式（Bayes' Theorem）",
        '<font size="18"><i>P</i>(<i>B</i><sub>i</sub>|<i>A</i>) = <i>P</i>(<i>B</i><sub>i</sub>)·<i>P</i>(<i>A</i>|<i>B</i><sub>i</sub>) / [Σ<sub>j=1</sub><sup>n</sup> <i>P</i>(<i>B</i><sub>j</sub>)·<i>P</i>(<i>A</i>|<i>B</i><sub>j</sub>)]</font>',
        [
            '<b>【定理】</b>设 <font face="Times-Italic">B</font>₁, <font face="Times-Italic">B</font>₂, ..., <font face="Times-Italic">B</font><sub>n</sub> 是样本空间的一个划分，<font face="Times-Italic">A</font> 为任一事件，<font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>) &gt; 0，则',
            "",
            '　　<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font><sub>i</sub>|<font face="Times-Italic" size="14">A</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font><sub>i</sub>∩<font face="Times-Italic" size="14">A</font>) / <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font><sub>i</sub>)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font><sub>i</sub>) / <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>)',
            "",
            "<b>【术语】</b>",
            '　　• <font face="Times-Italic">P</font>(<font face="Times-Italic">B</font><sub>i</sub>) 称为<b>先验概率</b>（prior probability）',
            '　　• <font face="Times-Italic">P</font>(<font face="Times-Italic">B</font><sub>i</sub>|<font face="Times-Italic">A</font>) 称为<b>后验概率</b>（posterior probability）',
            "",
            "<b>【意义】</b>已知结果 <i>A</i> 发生，反推原因 <i>B</i><sub>i</sub> 的概率。",
            "",
            "<b>【应用】</b>医学诊断、机器学习、风险评估、统计推断等。"
        ]
    )
    
    # 第10页：例题3
    create_example_slide(
        story, styles,
        "例题3：医学诊断问题（贝叶斯公式经典应用）",
        "<b>【题目】</b>某疾病的患病率为 1%。检测该病的准确率为：患病者检测呈阳性的概率为 95%，健康者检测呈阳性的概率为 5%（假阳性）。若某人检测呈阳性，求其真正患病的概率。",
        [
            "<b>【解】</b>",
            "",
            "设 <i>D</i> = {患病}，<i>T</i> = {检测阳性}",
            "",
            "由题意知：",
            "　　<i>P</i>(<i>D</i>) = 0.01，　<i>P</i>(<i>D̄</i>) = 0.99",
            "　　<i>P</i>(<i>T</i>|<i>D</i>) = 0.95，　<i>P</i>(<i>T</i>|<i>D̄</i>) = 0.05",
            "",
            "求 <i>P</i>(<i>D</i>|<i>T</i>)，由<b>贝叶斯公式</b>：",
            "",
            "　　<i>P</i>(<i>D</i>|<i>T</i>) = <i>P</i>(<i>D</i>)·<i>P</i>(<i>T</i>|<i>D</i>) / [<i>P</i>(<i>D</i>)·<i>P</i>(<i>T</i>|<i>D</i>) + <i>P</i>(<i>D̄</i>)·<i>P</i>(<i>T</i>|<i>D̄</i>)]",
            "",
            "　　　　　 = (0.01 × 0.95) / (0.01 × 0.95 + 0.99 × 0.05)",
            "",
            "　　　　　 = 0.0095 / (0.0095 + 0.0495)",
            "",
            "　　　　　 = 0.0095 / 0.059 ≈ 0.161",
            "",
            '<b>【答】</b>检测呈阳性的人真正患病的概率约为　<font color="#CC0000" size="15"><b>16.1%</b></font>',
            "",
            "<i>【注】尽管检测准确率很高（95%），但由于患病率很低（1%），阳性结果的可信度并不高。这是贝叶斯公式的经典应用，揭示了先验概率的重要性。</i>"
        ]
    )
    
    # 第11页：独立性
    create_section_slide(
        story, styles,
        "事件的独立性",
        [
            '<b>【定义】</b>设 <font face="Times-Italic" size="14">A</font>、<font face="Times-Italic" size="14">B</font> 是两个事件，若',
            "",
            '　　<font face="Times-Italic" size="16">P</font>(<font face="Times-Italic" size="16">A</font>∩<font face="Times-Italic" size="16">B</font>) = <font face="Times-Italic" size="16">P</font>(<font face="Times-Italic" size="16">A</font>)·<font face="Times-Italic" size="16">P</font>(<font face="Times-Italic" size="16">B</font>)',
            "",
            "则称事件 <i>A</i> 与 <i>B</i> <b>相互独立</b>（independent）。",
            "",
            '<b>【等价条件】</b>若 <font face="Times-Italic">P</font>(<font face="Times-Italic">B</font>) &gt; 0，则 <font face="Times-Italic">A</font>、<font face="Times-Italic">B</font> 相互独立 ⟺ <font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>|<font face="Times-Italic">B</font>) = <font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>)',
            "",
            "<b>【直观理解】</b>两个事件互不影响，一个事件的发生不改变另一个事件的概率。",
            "",
            "<b>【例子】</b>",
            "　　• <font color='#006600'><b>独立：</b></font>连续两次抛硬币的结果",
            "　　• <font color='#CC0000'><b>不独立：</b></font>不放回抽球的结果"
        ]
    )
    
    # 第12页：条件概率与独立性
    create_section_slide(
        story, styles,
        "条件概率与独立性的关系",
        [
            "<b>● 条件概率</b>适用于「相关」的事件",
            "　　• 一个事件的发生会影响另一个事件的概率",
            '　　• <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font>) ≠ <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>)',
            "",
            "<b>● 独立性</b>是特殊情况",
            '　　• 若 <font face="Times-Italic">A</font>、<font face="Times-Italic">B</font> 独立，则 <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>)',
            "　　• 此时条件概率退化为无条件概率",
            '　　• <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>∩<font face="Times-Italic" size="14">B</font>) = <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font>)',
            "",
            "<b>● 实际问题中</b>",
            "　　• 大多数事件是<b>相关的</b>（需要用条件概率分析）",
            "　　• 少数事件是<b>独立的</b>（可以简化计算）",
            "",
            "<b>● 判断独立性的关键</b>",
            "　　分析事件之间是否存在因果关系或相互影响"
        ]
    )
    
    # 第13页：综合例题 - 三门问题
    create_example_slide(
        story, styles,
        "综合例题：三门问题（Monty Hall Problem）",
        "<b>【题目】</b>游戏节目中有3扇门，其中1扇门后是汽车，2扇门后是山羊。你选择一扇门后，主持人（他知道门后是什么）打开剩余两扇门中的一扇，展示一只山羊。此时你是否应该换门？",
        [
            "<b>【解】</b>",
            "",
            "<b>策略1：坚持原选择</b>",
            '　　初始选中汽车的概率：<font face="Times-Italic">P</font>(坚持赢) = 1/3',
            "",
            "<b>策略2：换门</b>",
            "　　初始选错的概率为 2/3，此时主持人打开的必是有山羊的门，",
            "　　剩下的门后必是汽车，因此换门必赢：",
            '　　<font face="Times-Italic">P</font>(换门赢) = 2/3',
            "",
            "<b>用条件概率严格分析：</b>",
            "　　设 <i>A</i> = {初始选中汽车}，<i>H</i> = {主持人打开某扇有山羊的门}",
            '　　<font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>) = 1/3，　<font face="Times-Italic">P</font>(<font face="Times-Italic">H</font>|<font face="Times-Italic">A</font>) = 1（若选中汽车，主持人必然打开有山羊的门）',
            '　　<font face="Times-Italic">P</font>(<font face="Times-Italic">Ā</font>) = 2/3，　<font face="Times-Italic">P</font>(<font face="Times-Italic">H</font>|<font face="Times-Italic">Ā</font>) = 1（若选错，主持人也必然打开有山羊的门）',
            '　　由贝叶斯公式：<font face="Times-Italic">P</font>(<font face="Times-Italic">A</font>|<font face="Times-Italic">H</font>) = 1/3，　<font face="Times-Italic">P</font>(<font face="Times-Italic">Ā</font>|<font face="Times-Italic">H</font>) = 2/3',
            "",
            '<b>【答】</b><font color="#CC0000" size="15"><b>应该换门！</b></font>换门的获胜概率是坚持的<b>两倍</b>。'
        ]
    )
    
    # 第14页：重要公式总结
    create_section_slide(
        story, styles,
        "重要公式总结",
        [
            '<b>1. 条件概率定义：</b>　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>|<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>∩<font face="Times-Italic" size="15">B</font>) / <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>)　　(<font face="Times-Italic">P</font>(<font face="Times-Italic">B</font>) &gt; 0)',
            "",
            '<b>2. 乘法公式：</b>　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>∩<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>)·<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>|<font face="Times-Italic" size="15">A</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>)·<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>|<font face="Times-Italic" size="15">B</font>)',
            "",
            '<b>3. 全概率公式：</b>　<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>) = Σ <font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">B</font><sub>i</sub>)·<font face="Times-Italic" size="14">P</font>(<font face="Times-Italic" size="14">A</font>|<font face="Times-Italic" size="14">B</font><sub>i</sub>)',
            '　　　　　　　　　（<font face="Times-Italic">B</font>₁, <font face="Times-Italic">B</font>₂, ..., <font face="Times-Italic">B</font><sub>n</sub> 为样本空间的划分）',
            "",
            '<b>4. 贝叶斯公式：</b>　<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">B</font><sub>i</sub>|<font face="Times-Italic" size="13">A</font>) = <font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">B</font><sub>i</sub>)·<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>|<font face="Times-Italic" size="13">B</font><sub>i</sub>) / [Σ <font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">B</font><sub>j</sub>)·<font face="Times-Italic" size="13">P</font>(<font face="Times-Italic" size="13">A</font>|<font face="Times-Italic" size="13">B</font><sub>j</sub>)]',
            "",
            '<b>5. 独立性：</b>　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>∩<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>)·<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">B</font>)　⟺　<font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>|<font face="Times-Italic" size="15">B</font>) = <font face="Times-Italic" size="15">P</font>(<font face="Times-Italic" size="15">A</font>)'
        ]
    )
    
    # 第15页：应用领域
    create_section_slide(
        story, styles,
        "条件概率的应用领域",
        [
            "<b>● 医学诊断</b>",
            "　　• 根据症状推断疾病概率",
            "　　• 根据检测结果判断患病可能性",
            "",
            "<b>● 机器学习与人工智能</b>",
            "　　• 朴素贝叶斯分类器（Naive Bayes Classifier）",
            "　　• 贝叶斯网络（Bayesian Network）",
            "　　• 隐马尔可夫模型（Hidden Markov Model）",
            "",
            "<b>● 金融风险评估</b>",
            "　　• 信用评分、违约概率预测",
            "　　• 金融衍生品定价",
            "",
            "<b>● 信息检索与推荐系统</b>",
            "　　• 垃圾邮件过滤",
            "　　• 个性化推荐算法",
            "",
            "<b>● 质量控制与可靠性工程</b>",
            "　　• 产品缺陷检测",
            "　　• 系统可靠性分析"
        ]
    )
    
    # 第16页：课程总结
    create_section_slide(
        story, styles,
        "课程总结",
        [
            "<b>● 条件概率是概率论的核心概念之一</b>",
            "",
            "<b>● 关键思想</b>",
            "　　在「已知某一事件发生」的条件下重新计算概率",
            "",
            "<b>● 核心公式</b>",
            "　　• 条件概率定义",
            "　　• 乘法公式（链式法则）",
            "　　• 全概率公式（正向推理）",
            "　　• 贝叶斯公式（逆向推理）",
            "",
            "<b>● 应用广泛</b>",
            "　　从日常生活到高科技领域都有重要应用",
            "",
            "<b>● 学习建议</b>",
            "　　• 理解概念的直观意义和几何意义",
            "　　• 熟练掌握公式推导和运算",
            "　　• 多做习题，培养概率建模能力",
            "　　• 关注实际应用，理论联系实际"
        ]
    )
    
    # 第17页：结束页
    story.append(Spacer(1, 2.5*inch))
    
    end_title_style = ParagraphStyle(
        'EndTitle',
        parent=styles['Title'],
        fontName=FONT_HEI if FONT_HEI != 'Helvetica-Bold' else 'Helvetica-Bold',
        fontSize=48,
        textColor=colors.HexColor('#003366'),
        leading=56
    )
    story.append(Paragraph("谢谢！", end_title_style))
    story.append(Spacer(1, 0.3*inch))
    
    end_subtitle_style = ParagraphStyle(
        'EndSubtitle',
        parent=styles['Normal'],
        fontName=FONT_SONG if FONT_SONG != 'Helvetica' else 'Helvetica',
        fontSize=22,
        textColor=colors.grey,
        alignment=TA_CENTER,
        leading=28
    )
    story.append(Paragraph("Questions &amp; Discussion", end_subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("条件概率课程结束", end_subtitle_style))
    
    # 生成PDF
    doc.build(story, canvasmaker=SlideCanvas)
    
    print(f"✓ PDF课件已生成：{filename}")
    print(f"  - 页面尺寸：A4 横向")
    print(f"  - 共 17 页内容")
    print(f"  - 支持中文显示")
    print(f"  - 数学公式采用教科书风格排版")
    print("\n课件特色：")
    print("  • 使用斜体表示数学变量（P、A、B等）")
    print("  • 公式框采用教科书风格设计")
    print("  • 中文字体清晰显示")
    print("  • 专业的数学排版")


if __name__ == "__main__":
    main()
