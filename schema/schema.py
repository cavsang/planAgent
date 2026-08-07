from datetime import date, datetime, timezone
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# 0. 공통 필드 (DB 테이블에 섞어 쓰는 mixin)
# ---------------------------------------------------------------------------

class CommonState(BaseModel):
    """공통 감사(audit) 필드. 모든 DB 저장용 모델이 상속한다."""
    created_at: datetime = Field(default_factory=utc_now(), description="생성일시")
    updated_at: datetime = Field(default_factory=utc_now(), description="수정일시")
    deleted_at: Optional[datetime] = Field(default=None, description="삭제일시 (soft delete)")
    created_by: Optional[str] = Field(default=None, description="생성자 (system/teacher/admin 등)")
    updated_by: Optional[str] = Field(default=None, description="수정자")


# ---------------------------------------------------------------------------
# 1. DB 저장용 모델 (Supabase 테이블과 1:1로 매칭되는 것들)
#    -> 서로 상속하지 않고, id(FK)로만 참조한다.
# ---------------------------------------------------------------------------

class StudentState(CommonState):
    """학생 정보 테이블 (student)"""
    student_id: UUID = Field(default_factory=uuid4, description="학생 PK")
    name: str = Field(description="이름")
    birth_date: date = Field(description="생년월일")
    gender: Literal["M", "F"] = Field(description="성별")
    grade: int = Field(ge=1, le=12, description="학년 (1~12, 초/중/고 구분은 계산해서 사용)")
    email: str = Field(description="학생 또는 보호자 수신 이메일")

    @property
    def school_level(self) -> Literal["초등학교", "중학교", "고등학교"]:
        if self.grade <= 6:
            return "초등학교"
        if self.grade <= 9:
            return "중학교"
        return "고등학교"


class SubjectState(CommonState):
    """과목 마스터 테이블 (subject)"""
    subject_id: UUID = Field(default_factory=uuid4, description="과목 PK")
    subject_code: str = Field(description="과목 코드 (예: MATH, ENG)")
    subject_name: str = Field(description="과목명 (예: 수학, 영어)")


class TermState(CommonState):
    """학년/학기 마스터 테이블 (term)"""
    term_id: UUID = Field(default_factory=uuid4, description="학년/학기 PK")
    grade: int = Field(ge=1, le=12, description="학년")
    term: Literal["1학기", "2학기", "여름방학", "겨울방학"] = Field(description="학기 구분")


class CurriculumState(CommonState):
    """학기 x 과목 x 진도 테이블 (curriculum)
    subject_id, term_id는 FK 참조만 한다. (subject_name, grade 등 실값은 중복 저장 X)
    """
    curriculum_id: UUID = Field(default_factory=uuid4, description="진도 PK")
    subject_id: UUID = Field(description="FK -> subject.subject_id")
    term_id: UUID = Field(description="FK -> term.term_id")
    step: str = Field(description="진도 단원/차시")
    step_desc: str = Field(description="진도 설명 및 학습 목표")


class ProblemState(CommonState):
    """생성된 문제 및 채점 결과 테이블 (problem)
    학생/과목/진도 정보는 FK로만 연결한다.
    """
    problem_id: UUID = Field(default_factory=uuid4, description="문제 PK")
    student_id: UUID = Field(description="FK -> student.student_id")
    curriculum_id: UUID = Field(description="FK -> curriculum.curriculum_id")
    problem: str = Field(description="LLM이 생성한 문제")
    answer: Optional[str] = Field(default=None, description="학생이 제출한 답변")
    is_correct: Optional[bool] = Field(default=None, description="정답 여부 (채점 전에는 None)")
    feedback: Optional[str] = Field(default=None, description="LLM 피드백")
    llm_model: Optional[str] = Field(default=None, description="문제 생성에 사용한 모델명")


class WeaknessState(CommonState):
    """학생 약점 테이블 (weakness)"""
    weakness_id: UUID = Field(default_factory=uuid4, description="약점 PK")
    student_id: UUID = Field(description="FK -> student.student_id")
    curriculum_id: Optional[UUID] = Field(default=None, description="FK -> curriculum.curriculum_id (관련 진도)")
    weakness_keyword: str = Field(description="약점 키워드")


class NotificationState(CommonState):
    """문제 발송 이력 테이블 (notification)"""
    notification_id: UUID = Field(default_factory=uuid4, description="발송 PK")
    student_id: UUID = Field(description="FK -> student.student_id")
    problem_id: UUID = Field(description="FK -> problem.problem_id")
    channel: Literal["email", "sms", "push"] = Field(default="email", description="발송 채널")
    status: Literal["pending", "sent", "failed", "opened"] = Field(default="pending", description="발송 상태")
    sent_at: Optional[datetime] = Field(default=None, description="발송 완료 시각")
    error_message: Optional[str] = Field(default=None, description="실패 사유")


# ---------------------------------------------------------------------------
# 2. LangGraph 워크플로우 실행용 State
#    -> DB 테이블이 아니다. 실행 중 필요한 객체를 필드로 조합해서 들고 있는다.
# ---------------------------------------------------------------------------

class ProblemGenerationState(BaseModel):
    """문제 생성 파이프라인 실행 중 흐르는 state.
    student / curriculum 등은 DB에서 조회해온 결과를 그대로 담는다.
    """
    student: StudentState
    curriculum: CurriculumState
    weaknesses: list[WeaknessState] = Field(default_factory=list, description="이 학생의 기존 약점 목록 (문제 난이도/유형 결정에 활용)")

    generated_problem: Optional[ProblemState] = Field(default=None, description="LLM이 생성한 문제 결과")
    notification: Optional[NotificationState] = Field(default=None, description="발송 결과")

    error: Optional[str] = Field(default=None, description="파이프라인 중 발생한 에러 메시지")



class AgentState(BaseModel):
    """기본적으로 사용하는 전역 state"""
    user_input:str = Field(description="사용자 입력")
    student: Optional[StudentState] = Field(description="학생 정보")


