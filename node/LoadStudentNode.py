from schema.schema import ProblemGenerationState, StudentState

from model.llm import get_llm

def loadStudent_node(state:ProblemGenerationState) -> dict:
    """학생 정보를 조회한다."""
    name = state['user_input']

    

    #TODO : DB검색

    return {
        "id": "",
        "user_id": "",
        "name":"",
        "birth_date":"",
        "gender":"" 
    }
    

