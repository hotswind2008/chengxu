"""生成条件概率课件的脚本
使用 python-pptx 库创建一份完整的条件概率PowerPoint课件
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor


def create_title_slide(prs, title_text, subtitle_text):
    """创建标题页"""
    slide_layout = prs.slide_layouts[0]  # 标题页布局
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = title_text
    subtitle.text = subtitle_text
    
    # 设置字体格式
    title.text_frame.paragraphs[0].font.size = Pt(54)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    
    subtitle.text_frame.paragraphs[0].font.size = Pt(28)
    
    return slide


def create_content_slide(prs, title_text, content_items):
    """创建内容页"""
    slide_layout = prs.slide_layouts[1]  # 标题和内容布局
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = title_text
    title.text_frame.paragraphs[0].font.size = Pt(40)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    
    # 添加内容文本框
    left = Inches(0.8)
    top = Inches(2)
    width = Inches(8.5)
    height = Inches(5)
    
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    
    for i, content in enumerate(content_items):
        if i > 0:
            p = tf.add_paragraph()
        else:
            p = tf.paragraphs[0]
        
        p.text = content
        p.font.size = Pt(20)
        p.space_before = Pt(12)
        p.space_after = Pt(12)
        
        # 如果是公式或定义，使用特殊格式
        if '=' in content or '∪' in content or '∩' in content:
            p.font.bold = True
            p.font.color.rgb = RGBColor(204, 0, 0)
    
    return slide


def create_formula_slide(prs, title_text, formula_text, explanation_items):
    """创建公式页"""
    slide_layout = prs.slide_layouts[5]  # 空白布局
    slide = prs.slides.add_slide(slide_layout)
    
    # 标题
    left = Inches(0.5)
    top = Inches(0.5)
    width = Inches(9)
    height = Inches(1)
    title_box = slide.shapes.add_textbox(left, top, width, height)
    title_frame = title_box.text_frame
    title_frame.text = title_text
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 公式框
    left = Inches(1.5)
    top = Inches(2)
    width = Inches(7)
    height = Inches(1.5)
    formula_box = slide.shapes.add_textbox(left, top, width, height)
    formula_frame = formula_box.text_frame
    formula_frame.text = formula_text
    formula_frame.paragraphs[0].font.size = Pt(32)
    formula_frame.paragraphs[0].font.bold = True
    formula_frame.paragraphs[0].font.color.rgb = RGBColor(204, 0, 0)
    formula_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 添加边框
    formula_box.line.color.rgb = RGBColor(0, 51, 102)
    formula_box.line.width = Pt(2)
    formula_box.fill.solid()
    formula_box.fill.fore_color.rgb = RGBColor(240, 248, 255)
    
    # 说明文本
    left = Inches(1)
    top = Inches(4)
    width = Inches(8)
    height = Inches(2.5)
    explain_box = slide.shapes.add_textbox(left, top, width, height)
    explain_frame = explain_box.text_frame
    explain_frame.word_wrap = True
    
    for i, item in enumerate(explanation_items):
        if i > 0:
            p = explain_frame.add_paragraph()
        else:
            p = explain_frame.paragraphs[0]
        
        p.text = item
        p.font.size = Pt(18)
        p.space_before = Pt(8)
        p.space_after = Pt(8)
    
    return slide


def create_example_slide(prs, title_text, problem_text, solution_items):
    """创建例题页"""
    slide_layout = prs.slide_layouts[5]  # 空白布局
    slide = prs.slides.add_slide(slide_layout)
    
    # 标题
    left = Inches(0.5)
    top = Inches(0.5)
    width = Inches(9)
    height = Inches(0.8)
    title_box = slide.shapes.add_textbox(left, top, width, height)
    title_frame = title_box.text_frame
    title_frame.text = title_text
    title_frame.paragraphs[0].font.size = Pt(36)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 102, 51)
    
    # 题目框
    left = Inches(0.8)
    top = Inches(1.5)
    width = Inches(8.4)
    height = Inches(1.2)
    problem_box = slide.shapes.add_textbox(left, top, width, height)
    problem_frame = problem_box.text_frame
    problem_frame.word_wrap = True
    problem_frame.text = problem_text
    problem_frame.paragraphs[0].font.size = Pt(20)
    problem_frame.paragraphs[0].font.bold = True
    
    problem_box.fill.solid()
    problem_box.fill.fore_color.rgb = RGBColor(255, 250, 205)
    problem_box.line.color.rgb = RGBColor(0, 102, 51)
    problem_box.line.width = Pt(1.5)
    
    # 解答
    left = Inches(0.8)
    top = Inches(3)
    width = Inches(8.4)
    height = Inches(3.5)
    solution_box = slide.shapes.add_textbox(left, top, width, height)
    solution_frame = solution_box.text_frame
    solution_frame.word_wrap = True
    
    for i, step in enumerate(solution_items):
        if i > 0:
            p = solution_frame.add_paragraph()
        else:
            p = solution_frame.paragraphs[0]
        
        p.text = step
        p.font.size = Pt(18)
        p.space_before = Pt(6)
        p.space_after = Pt(6)
        
        if '解：' in step or '答案：' in step:
            p.font.bold = True
            p.font.color.rgb = RGBColor(0, 102, 51)
    
    return slide


def main():
    """生成条件概率课件"""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # 第1页：标题页
    create_title_slide(
        prs,
        "条件概率",
        "Conditional Probability\n概率论与数理统计"
    )
    
    # 第2页：引入 - 什么是条件概率
    create_content_slide(
        prs,
        "引入：什么是条件概率？",
        [
            "• 生活中的问题：",
            "  - 已知某人检测呈阳性，他真正患病的概率是多少？",
            "  - 已知今天下雨，明天继续下雨的概率是多少？",
            "  - 已知抽到红球，下一次抽到红球的概率是多少？",
            "",
            "• 这些都是在「已知某一事件发生」的条件下，",
            "  求另一事件发生的概率问题",
            "",
            "• 这就是条件概率的核心思想"
        ]
    )
    
    # 第3页：条件概率的定义
    create_formula_slide(
        prs,
        "条件概率的定义",
        "P(A|B) = P(A∩B) / P(B)",
        [
            "• P(A|B) 读作：在事件B发生的条件下，事件A发生的概率",
            "",
            "• 其中：",
            "  - P(A∩B) 表示事件A和B同时发生的概率",
            "  - P(B) > 0 表示事件B发生的概率（前提条件）",
            "",
            "• 直观理解：将样本空间缩小到B，然后在B中求A发生的概率"
        ]
    )
    
    # 第4页：条件概率的性质
    create_content_slide(
        prs,
        "条件概率的性质",
        [
            "对于固定的事件B (P(B) > 0)，P(·|B)满足概率的所有性质：",
            "",
            "1. 非负性：P(A|B) ≥ 0",
            "",
            "2. 规范性：P(Ω|B) = 1",
            "",
            "3. 可加性：若A₁, A₂, ..., Aₙ互不相容，则",
            "   P(A₁∪A₂∪...∪Aₙ|B) = P(A₁|B) + P(A₂|B) + ... + P(Aₙ|B)",
            "",
            "• 条件概率本质上也是概率，只是样本空间变小了"
        ]
    )
    
    # 第5页：乘法公式
    create_formula_slide(
        prs,
        "乘法公式（Multiplication Rule）",
        "P(A∩B) = P(B) · P(A|B) = P(A) · P(B|A)",
        [
            "由条件概率的定义直接得出",
            "",
            "• 推广形式（链式法则）：",
            "  P(A₁∩A₂∩...∩Aₙ) = P(A₁)·P(A₂|A₁)·P(A₃|A₁∩A₂)·...·P(Aₙ|A₁∩...∩Aₙ₋₁)",
            "",
            "• 应用：计算多个事件同时发生的概率"
        ]
    )
    
    # 第6页：例题1 - 抽球问题
    create_example_slide(
        prs,
        "例题1：不放回抽球问题",
        "问题：袋中有5个红球和3个白球，不放回地依次抽取2个球。\n求第一次抽到红球的条件下，第二次也抽到红球的概率。",
        [
            "解：",
            "设 A = {第一次抽到红球}，B = {第二次抽到红球}",
            "",
            "P(A) = 5/8",
            "",
            "在第一次抽到红球后，袋中剩余：4个红球，3个白球（共7个）",
            "",
            "P(B|A) = 4/7",
            "",
            "答案：第二次也抽到红球的概率为 4/7"
        ]
    )
    
    # 第7页：全概率公式
    create_formula_slide(
        prs,
        "全概率公式（Law of Total Probability）",
        "P(A) = Σ P(Bᵢ) · P(A|Bᵢ)",
        [
            "设 B₁, B₂, ..., Bₙ 是样本空间的一个划分（互不相容且并集为全集）",
            "",
            "则对任意事件A：",
            "  P(A) = P(B₁)·P(A|B₁) + P(B₂)·P(A|B₂) + ... + P(Bₙ)·P(A|Bₙ)",
            "",
            "• 意义：通过「分解」来计算复杂事件的概率",
            "• 应用：将复杂问题分解为若干简单情况的组合"
        ]
    )
    
    # 第8页：例题2 - 全概率公式应用
    create_example_slide(
        prs,
        "例题2：产品质量检验",
        "问题：三个工厂A、B、C生产同一产品，产量占比为30%、45%、25%，\n次品率分别为2%、3%、4%。随机抽取一件产品，求它是次品的概率。",
        [
            "解：",
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
            "答案：抽到次品的概率约为 2.95%"
        ]
    )
    
    # 第9页：贝叶斯公式
    create_formula_slide(
        prs,
        "贝叶斯公式（Bayes' Theorem）",
        "P(Bᵢ|A) = P(Bᵢ)·P(A|Bᵢ) / Σ P(Bⱼ)·P(A|Bⱼ)",
        [
            "在全概率公式的基础上，可以推导出贝叶斯公式：",
            "",
            "  P(Bᵢ|A) = P(Bᵢ∩A) / P(A) = P(Bᵢ)·P(A|Bᵢ) / P(A)",
            "",
            "• P(Bᵢ) 称为先验概率（prior probability）",
            "• P(Bᵢ|A) 称为后验概率（posterior probability）",
            "",
            "• 意义：已知结果A发生，反推原因Bᵢ的概率",
            "• 应用：医学诊断、机器学习、风险评估等"
        ]
    )
    
    # 第10页：例题3 - 贝叶斯公式应用
    create_example_slide(
        prs,
        "例题3：医学诊断问题",
        "问题：某疾病的患病率为1%。检测该病的准确率为：患病者检测阳性\n概率95%，健康者检测阳性概率5%。若某人检测呈阳性，求其真正\n患病的概率。",
        [
            "解：",
            "设 D={患病}，T={检测阳性}",
            "已知：P(D)=0.01, P(D̄)=0.99, P(T|D)=0.95, P(T|D̄)=0.05",
            "",
            "由贝叶斯公式：",
            "P(D|T) = P(D)·P(T|D) / [P(D)·P(T|D) + P(D̄)·P(T|D̄)]",
            "       = (0.01×0.95) / (0.01×0.95 + 0.99×0.05)",
            "       = 0.0095 / (0.0095 + 0.0495)",
            "       = 0.0095 / 0.059 ≈ 0.161",
            "",
            "答案：检测呈阳性的人真正患病的概率约为 16.1%",
            "（尽管检测准确率很高，但由于患病率很低，阳性结果的可信度并不高）"
        ]
    )
    
    # 第11页：独立性
    create_content_slide(
        prs,
        "事件的独立性",
        [
            "• 定义：若 P(A∩B) = P(A)·P(B)，则称事件A与B相互独立",
            "",
            "• 等价条件（当P(B)>0时）：",
            "  - P(A|B) = P(A)",
            "  - 即：B的发生不影响A的概率",
            "",
            "• 独立性的直观理解：",
            "  - 两个事件互不影响",
            "  - 一个事件的发生不改变另一个事件的概率",
            "",
            "• 例子：",
            "  - 独立：连续两次抛硬币的结果",
            "  - 不独立：不放回抽球"
        ]
    )
    
    # 第12页：条件概率与独立性的关系
    create_content_slide(
        prs,
        "条件概率 vs 独立性",
        [
            "• 条件概率适用于「相关」的事件",
            "  - 一个事件的发生会影响另一个事件的概率",
            "  - P(A|B) ≠ P(A)",
            "",
            "• 独立性是特殊情况",
            "  - 若A、B独立，则 P(A|B) = P(A)",
            "  - 此时条件概率退化为无条件概率",
            "",
            "• 实际问题中：",
            "  - 大多数事件是相关的（需要用条件概率）",
            "  - 少数事件是独立的（可以简化计算）",
            "",
            "• 判断独立性的关键：分析事件之间的因果关系"
        ]
    )
    
    # 第13页：综合例题
    create_example_slide(
        prs,
        "综合例题：三门问题（Monty Hall Problem）",
        "问题：游戏节目中有3扇门，其中1扇门后是汽车，2扇门后是山羊。\n你选择一扇门后，主持人打开另一扇有山羊的门。此时你是否应该\n换门？",
        [
            "解：",
            "策略1：坚持原选择",
            "  - 初始选中汽车的概率：P(坚持赢) = 1/3",
            "",
            "策略2：换门",
            "  - 初始选错的概率为2/3，此时换门必赢",
            "  - P(换门赢) = 2/3",
            "",
            "条件概率分析：",
            "设A={初始选中汽车}，H={主持人打开的门}",
            "P(A|H) = P(A)·P(H|A) / P(H) = (1/3)·1 / 1 = 1/3",
            "P(Ā|H) = 1 - 1/3 = 2/3",
            "",
            "答案：应该换门，换门的获胜概率是坚持的两倍！"
        ]
    )
    
    # 第14页：重要公式总结
    create_content_slide(
        prs,
        "重要公式总结",
        [
            "1. 条件概率定义：",
            "   P(A|B) = P(A∩B) / P(B)  (P(B) > 0)",
            "",
            "2. 乘法公式：",
            "   P(A∩B) = P(A)·P(B|A) = P(B)·P(A|B)",
            "",
            "3. 全概率公式：",
            "   P(A) = Σ P(Bᵢ)·P(A|Bᵢ)  （B₁,...,Bₙ为样本空间的划分）",
            "",
            "4. 贝叶斯公式：",
            "   P(Bᵢ|A) = P(Bᵢ)·P(A|Bᵢ) / Σ P(Bⱼ)·P(A|Bⱼ)",
            "",
            "5. 独立性：",
            "   P(A∩B) = P(A)·P(B) ⟺ P(A|B) = P(A)"
        ]
    )
    
    # 第15页：应用领域
    create_content_slide(
        prs,
        "条件概率的应用领域",
        [
            "• 医学诊断",
            "  - 根据症状推断疾病概率",
            "  - 根据检测结果判断患病可能性",
            "",
            "• 机器学习与人工智能",
            "  - 朴素贝叶斯分类器",
            "  - 贝叶斯网络、隐马尔可夫模型",
            "",
            "• 金融风险评估",
            "  - 信用评分、违约概率预测",
            "",
            "• 信息检索与推荐系统",
            "  - 垃圾邮件过滤、个性化推荐",
            "",
            "• 质量控制与可靠性工程"
        ]
    )
    
    # 第16页：总结
    create_content_slide(
        prs,
        "课程总结",
        [
            "• 条件概率是概率论的核心概念之一",
            "",
            "• 关键思想：在「已知条件」下重新计算概率",
            "",
            "• 核心公式：",
            "  - 条件概率、乘法公式、全概率公式、贝叶斯公式",
            "",
            "• 应用广泛：",
            "  - 从日常生活到高科技领域都有重要应用",
            "",
            "• 学习方法：",
            "  - 理解概念的直观意义",
            "  - 熟练掌握公式推导",
            "  - 多做习题，培养建模能力"
        ]
    )
    
    # 第17页：结束页
    create_title_slide(
        prs,
        "谢谢！",
        "Questions & Discussion\n\n条件概率课程结束"
    )
    
    # 保存课件
    output_file = "conditional_probability.pptx"
    prs.save(output_file)
    print(f"✓ 课件已生成：{output_file}")
    print(f"  - 共 {len(prs.slides)} 页幻灯片")
    print(f"  - 包含定义、公式、例题和应用")
    print("\n课件内容包括：")
    print("  1. 条件概率的定义和性质")
    print("  2. 乘法公式")
    print("  3. 全概率公式")
    print("  4. 贝叶斯公式")
    print("  5. 事件独立性")
    print("  6. 丰富的例题（抽球、产品检验、医学诊断、三门问题）")
    print("  7. 应用领域介绍")


if __name__ == "__main__":
    main()





