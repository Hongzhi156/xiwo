"""
希沃智教π - AI智能批改引擎
核心模块：OCR识别 + 多学科批改 + 知识点诊断 + 个性化评语
"""

import json
import re
from typing import Optional
from openai import OpenAI


# ==================== 知识图谱 ====================

MATH_KNOWLEDGE_GRAPH = {
    "代数": {
        "整式": ["单项式", "多项式", "整式乘法", "因式分解"],
        "分式": ["分式性质", "分式运算", "分式方程"],
        "方程": ["一元一次方程", "二元一次方程组", "一元二次方程", "不等式"],
        "函数": ["一次函数", "二次函数", "反比例函数", "函数图像"],
    },
    "几何": {
        "三角形": ["三角形性质", "全等三角形", "相似三角形", "勾股定理"],
        "四边形": ["平行四边形", "矩形", "菱形", "正方形"],
        "圆": ["圆的性质", "圆与直线", "圆与圆"],
    },
}

# 错误类型到知识点的映射
ERROR_TO_KNOWLEDGE = {
    "因式分解错误": ("代数", "整式", "因式分解"),
    "移项符号错误": ("代数", "方程", "一元一次方程"),
    "去括号错误": ("代数", "整式", "整式乘法"),
    "合并同类项错误": ("代数", "整式", "单项式"),
    "公式套用错误": ("代数", "方程", "一元二次方程"),
    "计算错误": ("代数", "方程", "一元一次方程"),
    "单位换算错误": ("代数", "方程", "一元一次方程"),
    "三角形判定错误": ("几何", "三角形", "全等三角形"),
    "角度计算错误": ("几何", "三角形", "三角形性质"),
    "辅助线思路错误": ("几何", "三角形", "相似三角形"),
}


def get_knowledge_path(error_type: str) -> Optional[tuple]:
    """根据错误类型返回知识图谱路径"""
    return ERROR_TO_KNOWLEDGE.get(error_type)


# ==================== Prompt模板 ====================

MATH_GRADING_PROMPT = """你是一位经验丰富的初中数学老师，请批改以下数学作业。

【重要评分规则 - 过程分】
- 完全正确：10分
- 思路正确但计算失误：7-8分（给过程分）
- 步骤部分正确、部分错误：4-6分（按正确步骤比例给分）
- 思路完全错误但有尝试：1-3分
- 空白或完全无关：0分

【题目】
{question}

【学生答案】
{answer}

请严格按以下JSON格式返回批改结果（不要返回其他内容）：
{{
    "score": 0-10的分数（支持过程分，如7、8等）,
    "is_correct": true/false,
    "partial_credit": true/false,
    "partial_credit_reason": "给过程分的理由（如'因式分解思路正确，但最后一步符号写错'，无过程分则为null）",
    "correct_answer": "正确答案或解题过程",
    "error_type": "错误类型，如：因式分解错误/移项符号错误/计算错误/公式套用错误/无错误",
    "error_step": "具体哪一步出错（如正确则为null）",
    "correct_steps": ["学生答对的步骤列表"],
    "error_analysis": "错误原因分析（2-3句话）",
    "knowledge_points": ["涉及的知识点列表"],
    "suggestion": "给学生的具体改进建议（1-2句话，语气鼓励）"
}}"""

CHINESE_GRADING_PROMPT = """你是一位经验丰富的语文老师，请批改以下语文作业。

【题目】
{question}

【学生答案】
{answer}

请严格按以下JSON格式返回批改结果（不要返回其他内容）：
{{
    "score": 0-10的分数,
    "is_correct": true/false,
    "error_type": "错误类型，如：错别字/语病/理解偏差/表达不清/内容不完整/无错误",
    "error_analysis": "具体问题分析",
    "knowledge_points": ["涉及的知识点，如：修辞手法/阅读理解/写作技巧等"],
    "suggestion": "给学生的具体改进建议"
}}"""

ENGLISH_GRADING_PROMPT = """你是一位经验丰富的英语老师，请批改以下英语作业。

【题目】
{question}

【学生答案】
{answer}

请严格按以下JSON格式返回批改结果（不要返回其他内容）：
{{
    "score": 0-10的分数,
    "is_correct": true/false,
    "error_type": "错误类型，如：语法错误/拼写错误/时态错误/词汇误用/中式英语/无错误",
    "error_analysis": "具体问题分析",
    "correction": "正确的表达方式",
    "knowledge_points": ["涉及的语法点或词汇点"],
    "suggestion": "给学生的具体改进建议"
}}"""

COMMENT_PROMPT = """你是一位温暖而专业的班主任，需要为学生写一段个性化评语。

【学生信息】
学科：{subject}
本次得分：{score}/10
错误类型分布：{error_types}
薄弱知识点：{weak_points}
近期表现趋势：{trend}

请写一段50-80字的个性化评语，要求：
1. 先肯定学生的努力或进步
2. 指出最需要改进的1个具体问题
3. 给出可操作的学习建议
4. 语气鼓励，像班主任面对面谈话

直接返回评语文本，不要JSON格式。"""


# ==================== 批改引擎 ====================

class AIGrader:
    """AI智能批改引擎"""

    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = OpenAI(**client_kwargs)
        self.model = model

    def _call_llm(self, prompt: str) -> str:
        """调用LLM"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content

    def grade(self, subject: str, question: str, answer: str) -> dict:
        """
        批改单道题目
        返回：{score, is_correct, error_type, error_analysis, knowledge_points, suggestion, ...}
        """
        prompt_map = {
            "数学": MATH_GRADING_PROMPT,
            "语文": CHINESE_GRADING_PROMPT,
            "英语": ENGLISH_GRADING_PROMPT,
        }

        prompt = prompt_map.get(subject, MATH_GRADING_PROMPT)
        prompt = prompt.format(question=question, answer=answer)

        raw = self._call_llm(prompt)

        # 尝试解析JSON
        try:
            # 提取JSON部分（处理LLM可能返回多余文字的情况）
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "score": 0,
                "is_correct": False,
                "error_type": "解析失败",
                "error_analysis": raw,
                "knowledge_points": [],
                "suggestion": "请重新提交",
            }

        # 补充知识图谱路径
        error_type = result.get("error_type", "")
        kb_path = get_knowledge_path(error_type)
        if kb_path:
            result["knowledge_path"] = list(kb_path)

        return result

    def generate_comment(
        self, subject: str, score: int, error_types: list,
        weak_points: list, trend: str = "稳定"
    ) -> str:
        """生成个性化评语"""
        prompt = COMMENT_PROMPT.format(
            subject=subject,
            score=score,
            error_types="、".join(error_types) if error_types else "无明显错误",
            weak_points="、".join(weak_points) if weak_points else "掌握良好",
            trend=trend,
        )
        return self._call_llm(prompt)

    def batch_grade(self, subject: str, questions: list, answers: list) -> dict:
        """
        批量批改
        questions: 题目列表
        answers: 学生答案列表
        返回：{results: [...], summary: {...}}
        """
        results = []
        for q, a in zip(questions, answers):
            result = self.grade(subject, q, a)
            results.append(result)

        # 汇总分析
        total_score = sum(r.get("score", 0) for r in results)
        max_score = len(results) * 10
        error_types = [r["error_type"] for r in results if not r.get("is_correct")]
        weak_points = []
        for r in results:
            weak_points.extend(r.get("knowledge_points", []))

        # 统计知识点出现频次
        from collections import Counter
        weak_counter = Counter(weak_points)
        top_weak = [p for p, _ in weak_counter.most_common(5)]

        summary = {
            "total_score": total_score,
            "max_score": max_score,
            "accuracy": total_score / max_score if max_score > 0 else 0,
            "error_types": list(set(error_types)),
            "weak_points": top_weak,
            "correct_count": sum(1 for r in results if r.get("is_correct")),
            "total_count": len(results),
        }

        # 生成评语
        comment = self.generate_comment(
            subject=subject,
            score=int(summary["accuracy"] * 10),
            error_types=summary["error_types"],
            weak_points=summary["weak_points"],
        )
        summary["comment"] = comment

        return {"results": results, "summary": summary}
