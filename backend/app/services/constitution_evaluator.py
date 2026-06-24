"""体质辨识引擎 — 王琦九种体质评估"""

# 九种体质定义
CONSTITUTION_TYPES = {
    "平和质": {"description": "阴阳气血调和，体态适中，面色润泽", "color": "#52c41a"},
    "气虚质": {"description": "元气不足，疲乏气短，易感冒", "color": "#faad14"},
    "阳虚质": {"description": "阳气不足，手足不温，畏寒怕冷", "color": "#1890ff"},
    "阴虚质": {"description": "阴液亏少，口燥咽干，手足心热", "color": "#f5222d"},
    "痰湿质": {"description": "痰湿凝聚，体形肥胖，腹部肥满", "color": "#722ed1"},
    "湿热质": {"description": "湿热内蕴，面垢油光，口苦口干", "color": "#eb2f96"},
    "血瘀质": {"description": "血行不畅，肤色晦暗，舌质紫暗", "color": "#13c2c2"},
    "气郁质": {"description": "气机郁滞，神情抑郁，忧虑脆弱", "color": "#fa8c16"},
    "特禀质": {"description": "先天失常，过敏体质为主", "color": "#2f54eb"},
}

# 每种体质的题目ID范围及转化分公式
# 简化版：answers 格式为 {体质类型: 原始分}
CONSTITUTION_QUESTIONS = {
    "平和质": [1, 2, 3, 4, 5],
    "气虚质": [6, 7, 8, 9, 10],
    "阳虚质": [11, 12, 13, 14, 15],
    "阴虚质": [16, 17, 18, 19, 20],
    "痰湿质": [21, 22, 23, 24, 25],
    "湿热质": [26, 27, 28, 29, 30],
    "血瘀质": [31, 32, 33, 34, 35],
    "气郁质": [36, 37, 38, 39, 40],
    "特禀质": [41, 42, 43, 44, 45],
}


def evaluate_constitution(answers: dict[str, int]) -> dict:
    """
    评估体质类型。

    参数:
        answers: {题目ID(字符串): 分值(1-5)}

    返回:
        {"primary_type": "气虚质", "scores": {...}, "secondary_types": [...]}
    """
    scores = {}

    for ctype, question_ids in CONSTITUTION_QUESTIONS.items():
        raw_scores = []
        for qid in question_ids:
            key = str(qid)
            if key in answers:
                raw_scores.append(answers[key])

        if raw_scores:
            # 转化分 = (原始分 - 题目数) / (题目数 × 4) × 100
            raw_total = sum(raw_scores)
            num_questions = len(raw_scores)
            transformed_score = (raw_total - num_questions) / (num_questions * 4) * 100
            scores[ctype] = round(transformed_score, 1)
        else:
            scores[ctype] = 0.0

    # 判定规则
    # 平和质: 转化分 ≥ 60 且其他体质 < 30
    # 偏颇体质: 转化分 ≥ 30
    pinghe_score = scores.get("平和质", 0)
    other_high = any(v >= 30 for k, v in scores.items() if k != "平和质")

    if pinghe_score >= 60 and not other_high:
        primary_type = "平和质"
    else:
        # 取非平和质中得分最高的
        non_pinghe = {k: v for k, v in scores.items() if k != "平和质"}
        primary_type = max(non_pinghe, key=non_pinghe.get)

    # 倾向体质：非主要体质中转化分 ≥ 30 的
    secondary_types = [
        k for k, v in scores.items()
        if k != primary_type and k != "平和质" and v >= 30
    ]

    return {
        "primary_type": primary_type,
        "scores": scores,
        "secondary_types": secondary_types,
    }
