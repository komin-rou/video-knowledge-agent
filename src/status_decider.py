def decide_status_by_quality(quality_score: int) -> str:
    """
    根据 Reflection 评分决定最终处理状态
    """

    if quality_score >= 80:
        return "success"

    if quality_score >= 60:
        return "low_quality"

    return "needs_review"


def build_status_note(quality_score: int, quality_level: str, suggestion: str) -> str:
    """
    构造写入 memory 的说明
    """

    return (
        f"quality_score={quality_score}, "
        f"quality_level={quality_level}, "
        f"suggestion={suggestion}"
    )