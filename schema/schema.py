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
    created_at: datetime = Field(default_factory=utc_now, description="생성일시")
    updated_at: datetime = Field(default_factory=utc_now, description="수정일시")
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
    code:str = Field(description="진도 코드 (예: 4수01-09, 9수04-01)")
    domain:str = Field(description="진도 영역 (예: 수와 연산, 함수, 문법)")
    unit:str = Field(description="진도 단원 (예: 분수, 세 자리 수 범위의 곱셈)")
    content:str | None = Field(default=None, description="성취 기준 본문(예.양의 등분할을 통하여 분수의 필요성을 인식하고, 분수를 이해하고 읽고 쓸 수 있다.)")
    explanation:str | None = Field(default=None, description="해설(예.1보다 작은 양을 나타내는 경우를 통하여 분수의 필요성이나 그 표현의 편리함을 인식하게 할 수 있다. 양의 등분할을 통하여 분수를 도입할 때 부분과 전체를 파악하게 하고, '분모', '분자'를 사용한다.)")
    allowed_terms:str | None = Field(default=None, description="학년·영역에서 사용 가능한 수학 용어 및 기호 목록(쉼표 구분). 문제 생성 시 이 목록에 없는 상위 학년 용어(예: 약수, 배수, 기약분수 등)를 사용하지 않도록 제한하는 데 사용됨.")


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
    user_input: str = Field(description="사용자 입력 (예: '이하랑')")
    code:str = Field(description="사용자 입력에 해당하는 진도 코드 (예: 4수 (4학년 수학이라는 뜻), 9수 (9학년(중3) 수학이라는 뜻))")
    student: StudentState | None = Field(default=None, description="조회된 학생 정보")
    subject: SubjectState | None = Field(default=None, description="조회된 과목 정보")
    term: TermState | None = Field(default=None, description="조회된 학년/학기 정보")
    curriculum: list[CurriculumState] | None = Field(default_factory=list, description="조회된 진도 정보")
    weaknesses: list[WeaknessState] | None= Field(default_factory=list, description="이 학생의 기존 약점 목록 (문제 난이도/유형 결정에 활용)")

    history_problems: list[ProblemState] | None = Field(default_factory=list, description="이 학생의 기존 문제 풀이 이력 (문제 난이도/유형 결정에 활용)")
    generated_problem: Optional[ProblemState] = Field(default=None, description="LLM이 생성한 문제 결과")
    notification: Optional[NotificationState] = Field(default=None, description="발송 결과")

    error: Optional[str] = Field(default=None, description="파이프라인 중 발생한 에러 메시지")




