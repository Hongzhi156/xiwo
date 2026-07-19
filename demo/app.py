"""
希沃智教π - AI智能作业批改系统 Demo
Streamlit Web界面
"""

import streamlit as st
import json
import plotly.graph_objects as go
from collections import Counter
from grader import AIGrader, MATH_KNOWLEDGE_GRAPH

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="希沃智教π - AI智能作业批改",
    page_icon="📝",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #5f6368;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 700;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.8rem;
        border-left: 4px solid #1a73e8;
    }
    .error-tag {
        background: #fce4ec;
        color: #c62828;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .success-tag {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .knowledge-tag {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.2rem;
    }
    .comment-box {
        background: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 1rem 1.2rem;
        border-radius: 0 0.8rem 0.8rem 0;
        font-size: 1rem;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 标题 ====================

st.markdown('<div class="main-header">📝 希沃智教π</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI智能作业批改系统 · 每个学生都被认真对待</div>', unsafe_allow_html=True)

# ==================== 侧边栏配置 ====================

with st.sidebar:
    st.header("⚙️ 配置")

    api_key = st.text_input("API Key", type="password", help="输入OpenAI或兼容API的Key")
    base_url = st.text_input("API Base URL（可选）", placeholder="https://api.openai.com/v1")
    model = st.selectbox("模型", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "qwen-vl-max", "glm-4v"])

    st.divider()
    st.markdown("### 📊 知识图谱")
    for chapter, sections in MATH_KNOWLEDGE_GRAPH.items():
        with st.expander(f"📘 {chapter}"):
            for section, points in sections.items():
                st.markdown(f"**{section}**：{'、'.join(points)}")

    st.divider()
    st.markdown("### ℹ️ 关于")
    st.markdown("""
    **希沃智教π** 是面向K12的AI智能作业批改系统。

    **核心能力：**
    - 🔍 多学科作业自动批改
    - 📊 知识点薄弱诊断
    - 💬 个性化评语生成
    - 📈 学情趋势追踪
    """)

# ==================== 示例数据 ====================

SAMPLE_MATH = [
    {
        "question": "解方程：x² + 3x + 2 = 0",
        "answer": "x² + 3x + 2 = 0\n(x+1)(x+2) = 0\nx+1=0 或 x+2=0\nx=-1 或 x=-2",
        "subject": "数学",
    },
    {
        "question": "解方程：x² - 5x + 6 = 0",
        "answer": "x² - 5x + 6 = 0\n(x-2)(x-3) = 0\nx=2 或 x=3",
        "subject": "数学",
    },
    {
        "question": "计算：(a+b)²",
        "answer": "(a+b)² = a² + b²",
        "subject": "数学",
    },
    {
        "question": "解方程：2x + 5 = 13",
        "answer": "2x + 5 = 13\n2x = 13 + 5\n2x = 18\nx = 9",
        "subject": "数学",
    },
    {
        "question": "已知三角形ABC中，AB=AC=5，BC=6，求三角形面积。",
        "answer": "作AD⊥BC于D\nBD=BC/2=3\nAD=√(AB²-BD²)=√(25-9)=4\nS=BC×AD/2=6×4/2=12",
        "subject": "数学",
    },
    {
        "question": "因式分解：x² - 9",
        "answer": "x² - 9 = (x+3)(x-3)",
        "subject": "数学",
    },
]

SAMPLE_CHINESE = [
    {
        "question": "请赏析李白《静夜思》中'举头望明月，低头思故乡'的表达技巧。",
        "answer": "这两句诗通过'举头'和'低头'的动作对比，表达了诗人对故乡的思念之情。用明月寄托思乡之情，是借景抒情的手法。",
        "subject": "语文",
    },
    {
        "question": "请用'虽然...但是...'造句。",
        "answer": "虽然今天下雨了，但是我还是按时到了学校。",
        "subject": "语文",
    },
]

SAMPLE_ENGLISH = [
    {
        "question": "翻译：我昨天去了图书馆。",
        "answer": "I go to the library yesterday.",
        "subject": "英语",
    },
    {
        "question": "用一般过去时写三个句子。",
        "answer": "I watched TV last night.\nShe goed to school yesterday.\nWe played basketball last weekend.",
        "subject": "英语",
    },
]

# ==================== 主界面 ====================

tab1, tab2, tab3 = st.tabs(["📝 作业批改", "📊 学情分析", "🧪 示例演示"])

# ---- Tab 1: 作业批改 ----
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        subject = st.selectbox("选择学科", ["数学", "语文", "英语"], index=0)

        st.markdown("#### 📋 输入题目和答案")

        # 支持多题
        num_questions = st.number_input("题目数量", min_value=1, max_value=10, value=1)

        questions = []
        answers = []
        for i in range(num_questions):
            st.markdown(f"**第 {i+1} 题**")
            q = st.text_area(f"题目 {i+1}", key=f"q_{i}", height=68)
            a = st.text_area(f"学生答案 {i+1}", key=f"a_{i}", height=100)
            questions.append(q)
            answers.append(a)

    with col2:
        st.markdown("#### 💡 使用提示")
        st.info("""
        **数学**：支持方程、几何、代数题
        - 会分析解题步骤
        - 定位具体出错环节

        **语文**：支持阅读理解、造句、作文
        - 逐段点评
        - 修辞手法分析

        **英语**：支持翻译、写作、语法
        - 语法错误标注
        - 地道表达建议
        """)

    if st.button("🚀 开始批改", type="primary", use_container_width=True):
        if not api_key:
            st.error("请先在左侧配置中输入API Key")
        elif not any(q.strip() for q in questions):
            st.error("请至少输入一道题目")
        else:
            grader = AIGrader(api_key=api_key, base_url=base_url or None, model=model)

            with st.spinner("AI正在认真批改中..."):
                # 过滤空题目
                valid = [(q, a) for q, a in zip(questions, answers) if q.strip()]
                valid_questions = [v[0] for v in valid]
                valid_answers = [v[1] for v in valid]

                result = grader.batch_grade(subject, valid_questions, valid_answers)

            # 保存到session
            st.session_state["last_result"] = result
            st.session_state["last_subject"] = subject

            # ---- 展示结果 ----
            st.divider()
            st.markdown("## 📊 批改结果")

            summary = result["summary"]

            # 顶部卡片
            col_score, col_acc, col_correct, col_total = st.columns(4)
            with col_score:
                st.metric("总分", f"{summary['total_score']}/{summary['max_score']}")
            with col_acc:
                st.metric("正确率", f"{summary['accuracy']:.0%}")
            with col_correct:
                st.metric("正确题数", f"{summary['correct_count']}")
            with col_total:
                st.metric("总题数", f"{summary['total_count']}")

            # 逐题详情
            st.markdown("### 📝 逐题批改详情")
            for i, r in enumerate(result["results"]):
                with st.expander(
                    f"第{i+1}题 {'✅' if r.get('is_correct') else '❌'} "
                    f"| 得分：{r.get('score', 0)}/10 "
                    f"| {r.get('error_type', '')}",
                    expanded=not r.get("is_correct"),
                ):
                    if r.get("is_correct"):
                        st.markdown(f'<span class="success-tag">✅ 回答正确</span>', unsafe_allow_html=True)
                    elif r.get("partial_credit"):
                        st.markdown(f'<span class="knowledge-tag">⭐ 过程分：{r.get("score", 0)}/10</span>', unsafe_allow_html=True)
                        if r.get("partial_credit_reason"):
                            st.markdown(f"**过程分理由：** {r['partial_credit_reason']}")
                        st.markdown(f'<span class="error-tag">❌ {r.get("error_type", "未知错误")}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="error-tag">❌ {r.get("error_type", "未知错误")}</span>', unsafe_allow_html=True)

                    if r.get("correct_steps"):
                        st.markdown(f"**✅ 已掌握的步骤：**")
                        for step in r["correct_steps"]:
                            st.markdown(f"- {step}")

                    if r.get("correct_answer"):
                        st.markdown(f"**正确答案/解题过程：**")
                        st.code(r["correct_answer"])

                    if r.get("error_step"):
                        st.markdown(f"**出错环节：** {r['error_step']}")

                    if r.get("error_analysis"):
                        st.markdown(f"**错误分析：** {r['error_analysis']}")

                    if r.get("knowledge_points"):
                        tags = " ".join(
                            f'<span class="knowledge-tag">📚 {kp}</span>'
                            for kp in r["knowledge_points"]
                        )
                        st.markdown(f"**涉及知识点：** {tags}", unsafe_allow_html=True)

                    if r.get("knowledge_path"):
                        path = " → ".join(r["knowledge_path"])
                        st.markdown(f"**知识图谱路径：** `{path}`")

                    if r.get("suggestion"):
                        st.markdown(f"**💡 建议：** {r['suggestion']}")

            # 个性化评语
            if summary.get("comment"):
                st.markdown("### 💌 个性化评语")
                st.markdown(
                    f'<div class="comment-box">✍️ {summary["comment"]}</div>',
                    unsafe_allow_html=True,
                )

            # 薄弱知识点
            if summary.get("weak_points"):
                st.markdown("### ⚠️ 薄弱知识点")
                tags = " ".join(
                    f'<span class="error-tag">🔴 {p}</span>'
                    for p in summary["weak_points"]
                )
                st.markdown(tags, unsafe_allow_html=True)


# ---- Tab 2: 学情分析 ----
with tab2:
    st.markdown("## 📊 学情诊断报告")

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        subject = st.session_state.get("last_subject", "数学")
        summary = result["summary"]

        col1, col2 = st.columns(2)

        with col1:
            # 雷达图：知识点掌握度
            st.markdown("### 🎯 知识点掌握度")

            all_points = []
            for r in result["results"]:
                all_points.extend(r.get("knowledge_points", []))

            if all_points:
                point_counter = Counter(all_points)
                labels = list(point_counter.keys())
                values = [10 - point_counter[k] * 2 for k in labels]  # 错得越多掌握度越低
                values = [max(0, min(10, v)) for v in values]

                fig = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    fillcolor='rgba(26, 115, 232, 0.2)',
                    line=dict(color='#1a73e8', width=2),
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("所有题目回答正确，暂无薄弱知识点 🎉")

        with col2:
            # 错误类型分布饼图
            st.markdown("### 📊 错误类型分布")

            error_types = [r["error_type"] for r in result["results"] if not r.get("is_correct")]
            if error_types:
                error_counter = Counter(error_types)
                fig = go.Figure(data=go.Pie(
                    labels=list(error_counter.keys()),
                    values=list(error_counter.values()),
                    hole=0.4,
                    marker=dict(colors=['#ff6b6b', '#ffa502', '#ff6348', '#eccc68', '#7bed9f']),
                ))
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("全部正确，无错误分布 🎉")

        # 知识图谱路径可视化
        st.markdown("### 🗺️ 知识图谱追踪")

        kb_paths = [r.get("knowledge_path", []) for r in result["results"] if r.get("knowledge_path")]
        if kb_paths:
            for i, path in enumerate(kb_paths):
                chain = " → ".join(f"`{p}`" for p in path)
                st.markdown(f"**错题{i+1}的薄弱链路：** {chain}")
        else:
            st.info("暂无知识图谱追踪数据")

        # 评语
        if summary.get("comment"):
            st.markdown("### 💌 教师评语")
            st.markdown(
                f'<div class="comment-box">✍️ {summary["comment"]}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("请先在「作业批改」标签页完成一次批改，此处将自动生成学情报告。")


# ---- Tab 3: 示例演示 ----
with tab3:
    st.markdown("## 🧪 示例演示（无需API Key）")
    st.markdown("以下为预设的批改示例，展示系统的核心能力。")

    demo_subject = st.selectbox("选择示例学科", ["数学", "语文", "英语"], index=0, key="demo_subject")

    if demo_subject == "数学":
        samples = SAMPLE_MATH
    elif demo_subject == "语文":
        samples = SAMPLE_CHINESE
    else:
        samples = SAMPLE_ENGLISH

    for i, sample in enumerate(samples):
        with st.expander(f"示例 {i+1}：{sample['question'][:40]}...", expanded=(i == 0)):
            st.markdown(f"**题目：** {sample['question']}")
            st.markdown(f"**学生答案：**")
            st.code(sample["answer"])

            # 模拟批改结果（支持过程分）
            if demo_subject == "数学":
                if "a² + b²" in sample["answer"]:
                    st.markdown('<span class="knowledge-tag">⭐ 过程分：4/10</span>', unsafe_allow_html=True)
                    st.markdown('<span class="error-tag">❌ 公式套用错误</span>', unsafe_allow_html=True)
                    st.markdown("**过程分理由：** 展开了(a+b)²的思路正确，但遗漏了交叉项2ab，属于公式记忆不完整")
                    st.markdown("**✅ 已掌握的步骤：** 正确识别了需要展开完全平方表达式")
                    st.markdown("**正确答案：** (a+b)² = a² + 2ab + b²")
                    st.markdown("**错误分析：** 完全平方公式记忆不牢，遗漏了交叉项2ab")
                    st.markdown(
                        '<span class="knowledge-tag">📚 完全平方公式</span> '
                        '<span class="knowledge-tag">📚 整式乘法</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("**💡 建议：** 把完全平方公式写在笔记本第一页，每天默写一遍，做题时对照验证。")
                elif "13 + 5" in sample.get("answer", ""):
                    st.markdown('<span class="knowledge-tag">⭐ 过程分：7/10</span>', unsafe_allow_html=True)
                    st.markdown('<span class="error-tag">❌ 移项符号错误</span>', unsafe_allow_html=True)
                    st.markdown("**过程分理由：** 解方程思路正确（移项→合并→系数化1），但移项时符号错误，+5移到右边应变-5")
                    st.markdown("**✅ 已掌握的步骤：** 正确识别了需要移项求解，系数化1的方法正确")
                    st.markdown("**正确解题过程：**")
                    st.code("2x + 5 = 13\n2x = 13 - 5\n2x = 8\nx = 4")
                    st.markdown("**错误分析：** 移项时忘记变号，这是初学方程最常见的错误之一")
                    st.markdown(
                        '<span class="knowledge-tag">📚 移项法则</span> '
                        '<span class="knowledge-tag">📚 一元一次方程</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("**💡 建议：** 移项时在心里默念"过桥变号"，把+5移到等号右边就变成-5，养成检查习惯。")
                elif "goed" in sample.get("answer", ""):
                    pass  # 英语示例
                else:
                    st.markdown('<span class="success-tag">✅ 回答正确</span>', unsafe_allow_html=True)
                    st.markdown("解题过程完整，步骤清晰，继续保持！")

            elif demo_subject == "语文":
                st.markdown('<span class="success-tag">✅ 回答正确</span>', unsafe_allow_html=True)
                st.markdown("**批改意见：** 分析到位，准确指出了对比手法和借景抒情。建议补充：'低头'与'举头'形成空间对比，强化了思乡情感的层次感。")
                st.markdown(
                    '<span class="knowledge-tag">📚 借景抒情</span> '
                    '<span class="knowledge-tag">📚 对比手法</span>',
                    unsafe_allow_html=True,
                )

            elif demo_subject == "英语":
                if "goed" in sample["answer"]:
                    st.markdown('<span class="error-tag">❌ 语法错误（动词过去式）</span>', unsafe_allow_html=True)
                    st.markdown("**错误分析：** 'go'是不规则动词，过去式不是goed，而是went")
                    st.markdown("**正确表达：** She **went** to school yesterday.")
                    st.markdown(
                        '<span class="knowledge-tag">📚 不规则动词</span> '
                        '<span class="knowledge-tag">📚 一般过去时</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("**💡 建议：** 整理一份不规则动词表，重点记忆go-went-gone、do-did-done、see-saw-seen等高频词。")
                else:
                    st.markdown('<span class="success-tag">✅ 回答正确</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    > 💡 **提示：** 配置API Key后，在「作业批改」标签页可以输入任意题目进行实时批改。
    > 示例演示仅展示系统的核心交互效果。
    """)
