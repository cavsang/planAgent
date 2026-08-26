
from schema.schema import ProblemGenerationState


def router(state: ProblemGenerationState):
    print("router : ", state)
    if state.retry_cnt > 3:
        return "END"

    if state.check_problemState.is_confirm:
        return "NEXT"
    else:
        return "makeProblems"