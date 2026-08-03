from langgraph.graph import MessagesState
from pydantic import BaseModel


class AgentState(BaseModel):
    """기본적으로 사용하는 전역 state"""
    user_input:str


class StudentState(BaseModel): 
    """학생 정보를 담은 state"""
    
