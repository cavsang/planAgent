from schema.schema import CurriculumState, ProblemState, WeaknessState


def format_curriculum_list(curriculum_list: list[CurriculumState]) -> str:
    if not curriculum_list:
        return "없음"
    
    blocks = []
    for c in curriculum_list:
        block = (
            f"- code: {c.code}\n"
            f"  domain: {c.domain}\n"
            f"  unit: {c.unit}\n"
            f"  content: {c.content or '없음'}\n"
            f"  explanation: {c.explanation or '없음'}\n"
            f"  allowed_terms: {c.allowed_terms or '없음'}"
        )
        blocks.append(block)
    
    return "\n\n".join(blocks)


def format_weaknesses(weaknesses: list[WeaknessState] | None) -> str:
    if not weaknesses:
        return "없음"
    
    blocks = []
    for w in weaknesses:
        blocks.append(f"- weakness_keyword: {w.weakness_keyword} (curriculum_id: {w.curriculum_id})")
    
    return "\n".join(blocks)


def format_history_problems(history: list[ProblemState] | None) -> str:
    if not history:
        return "없음"
    
    blocks = []
    for p in history:
        correct_str = (
            "정답" if p.is_correct is True
            else "오답" if p.is_correct is False
            else "채점 전"
        )
        blocks.append(f"- 문제: {p.problem[:50]}... / 결과: {correct_str}")
    
    return "\n".join(blocks)