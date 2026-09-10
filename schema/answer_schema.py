from pydantic import BaseModel, Field

##############답변 plan #######################
class answerState(BaseModel):
    """답변이 완료됬을경우 실행하는 state, 주 목적은 답변분석/채점/약점분석 등에 쓰인다."""
    problem_id:str            = Field(description="문제 테이블(problem)의 키값.")
    student_id: str|None        = Field(description="FK -> student.student_id", default=None)
    curriculum_id: str | None   = Field(description="FK -> curriculum.curriculum_id", default=None)

    problem: str | None         = Field(description="LLM이 생성한 문제", default=None)    
    correct_answer: str | None  = Field(default=None,description="LLM이 생성한 정답")
    answer: str| None  = Field(default=None,description="학생이 대답한 정답")
    status:str | None = Field(default=None,description="상태값 변화, 순서대로 WATTING, SUBMITTED, GRADED 그리고 에러발생시 ERROR 상태 변경이 된다.")
    problem_key_concepts: str | None = Field(default=None,description="LLM이 생성한 문제의 핵심 개념 키워드 (문제의 풀때 필요한 핵심 개념을 최대 10개 이하 정도 쉼표로 구분하여 작성)")

    is_correct: bool | None = Field(default=None, description="정답 여부 (채점 전에는 None)")
    feedback: str | None = Field(default=None, description="llm의 문제와 정답에 대한 feedback ")
    weakness_keyword: str | None = Field(default=None,description="약점 목록")

    result: str | None = Field(default=None, description="최종 결과값.")
