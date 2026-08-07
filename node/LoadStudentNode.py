from schema.schema import StudentState

from model.llm import get_llm
from schema.schema import AgentState

def loadStudent_node(state:AgentState) -> dict:
    """학생 정보를 조회한다."""
    input = state['user_input']

    #TODO : DB검색

    return {
        "id": "",
        "user_id": "",
        "name":"",
        "birth_date":"",
        "gender":"" 
    }
    

