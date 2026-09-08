
from api.getproblems import getProblems
from schema.schema import answerState


def problem_answer(state:answerState) -> dict:
    """문제정보를 불러온다."""
    p_id = state.problem_id

    problem = getProblems(p_id)

    if not problem:
        raise ValueError(f"Problem {p_id} not found")

    return {
        "problem_id"        : problem['problem_id'],
        "student_id"        : problem['student_id'],
        "curriculum_id"     : problem['curriculum_id'],
        "problem"           : problem['problem'],
        "correct_answer"    : problem['correct_answer'],
        "answer"            : problem['answer'],
        "status"            : problem['status'] 
    }

