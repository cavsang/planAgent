
from schema.schema import QuestionSpecState


def router(state: QuestionSpecState):
    print(state)
    if state.retry_cnt > 3:
        return "END"

    if state.check_problemState.is_confirm:
        return "END"
    else:
        return "makeProblems"