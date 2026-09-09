
from api.getproblems import getProblems
from schema.answer_schema import answerState


def problem_answer(state:answerState) -> dict:
    """문제정보를 불러온다."""
    problem_id= state.problem_id
    problem = getProblems(problem_id)
    #print("problem_answer "+problem)

    if not problem:
        raise ValueError(f"Problem {problem_id} not found")

    return {
        "problem_id"        : problem['problem_id'],
        "student_id"        : problem['student_id'],
        "curriculum_id"     : problem['curriculum_id'],
        "problem"           : problem['problem'],
        "correct_answer"    : problem['correct_answer'],
        "answer"            : problem['answer'],
        "status"            : problem['status'],
        "problem_key_concepts" : problem['problem_key_concepts']
    }

