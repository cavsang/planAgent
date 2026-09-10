
from api.getproblems import setAnswer
from schema.answer_schema import answerState


def insert_answer(state:answerState) -> dict:
    """채점의 결과를 problem 데이터와 Weakness테이블에 업데이트 한다."""
    result = setAnswer(p_id=state.problem_id, is_correct=state.is_correct, feedback=state.feedback,weaknesses=state.weakness_keyword )

    print(result)
    return {
        "result" : result
    }
