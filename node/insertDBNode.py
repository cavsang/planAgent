

from db.session import get_db
from schema.schema import ProblemGenerationState


def insertDBNode(state: ProblemGenerationState) -> dict:
    """문제를 DB에 저장한다."""

    # print(state.generated_problem)

    # with get_db() as db:
    #     pass
    
    return {}
