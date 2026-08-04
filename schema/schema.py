

from datetime import date
from typing import List, Optional

from langgraph.graph import MessagesState
from numpy import number
from pydantic.v1 import BaseModel


class AgentState(BaseModel):
    """기본적으로 사용하는 전역 state"""
    user_input:str

class EnrollmentState(BaseModel):
    """학년 학기 이력 StudentState와 1:N 관계"""
    id: number
    student_id: str
    school_year: int
    grade_level: str
    semester: int
    class_name: Optional[str]
    start_date: date
    end_date: Optional[date]



class StudentState(BaseModel):
    """학생 정보"""
    id: str
    user_id: str
    name:str
    birth_date:str
    gender:str

    











    #  id: Mapped[int] = mapped_column(primary_key=True)
    # student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    # school_year: Mapped[int] = mapped_column(nullable=False)
    # grade_level: Mapped[str] = mapped_column(String(20), nullable=False)
    # semester: Mapped[int] = mapped_column(nullable=False)  # 1 or 2
    # class_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # start_date: Mapped[date] = mapped_column(Date, nullable=False)
    # end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
 