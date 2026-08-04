
from schema.schema import StudentState


def curriculum_node(state:StudentState) -> dict:
    """학년/학기/진도를 조회한다."""
    input = state['user_input']

    #TODO : DB검색

    return{}