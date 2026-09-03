from datetime import date, datetime, timezone
from typing import List, Literal, NotRequired, Optional
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


class BaseProblemState(CommonState):
    """문제 생성기(LLM)에게 전달할 문제 설계 명세 State"""
    problem: str = Field(description="LLM이 생성한 문제")
    correct_answer: str|None = Field(default=None,description="LLM이 생성한 정답")
    problem_hint: str = Field(description="LLM이 생성한 문제의 풀이 과정에대한 가이드")
    problem_key_concepts: Optional[str] = Field(..., description="LLM이 생성한 문제의 핵심 개념 키워드 (문제의 풀때 필요한 핵심 개념을 최대 10개 이하 정도 쉼표로 구분하여 작성)")



class WeaknessState(CommonState):
    """학생 약점 테이블 (weakness)"""
    weakness_id: UUID = Field(default_factory=uuid4, description="약점 PK")
    student_id: UUID = Field(description="FK -> student.student_id")
    curriculum_id: Optional[UUID] = Field(default=None, description="FK -> curriculum.curriculum_id (관련 진도)")
    weakness_keyword: str = Field(description="약점 키워드")


class CheckProblemState(BaseModel):
    """QuestionSpecState의 항목을 비교해 컨셉대로 baseProblemState의 문제를 생성했는지 확인한다."""
    is_confirm: Optional[bool] = Field(default=None, description="문제 생성후 confirm에서 문제가 컨셉과 적합한지 여부 ")
    confirm_feedback: str | None = Field(default=None, description="is_confirm이 False일때만 이유를 적음")


class QuestionSpecState(CommonState):
    """2단계 LLM(문제 생성기)에게 전달할 문항 설계 명세 State"""

    difficulty_level: Literal["매우쉬움", "쉬움", "보통", "어려움", "매우어려움", "최상"] = Field(..., description="난이도등급")
    standard_summary: str = Field(..., description="성취기준_요약 - 입력받은 성취기준을 한 문장으로 재정리")
    number_range: str = Field(..., description="수_범위 - 예: 0~100, 진분수(분모 10 이하) 등 구체적 범위")
    operation_steps: int = Field(..., ge=1, le=5, description="연산_단계수 - 1~5 사이의 정수")
    operation_types: List[str] = Field(default_factory=list, description="연산_종류 - 예: 덧셈, 뺄셈, 곱셈, 나눗셈, 분수화 등")
    is_word_problem: bool = Field(..., description="문장제_여부")
    condition_count: int = Field(..., ge=0, description="조건_개수")
    condition_details: List[str] = Field(default_factory=list, description="조건_상세 - 조건 설명 리스트")
    trap_elements: List[str] = Field(default_factory=list, description="함정_요소 - 예: 불필요 정보 삽입 등, 없으면 빈 배열")
    bloom_level: Literal["기억", "이해", "적용", "분석", "평가"] = Field(..., description="블룸_인지수준")
    allowed_terms: List[str] = Field(default_factory=list, description="허용_용어 - 해당 학년/진도에서 사용 가능한 수학 용어 목록")
    forbidden_terms_check: List[str] = Field(default_factory=list, description="금지_용어_확인 - 체크한 금지 용어 목록과 각각 미포함 확인(true)")
    weakness_reflection: Optional[str] = Field(default=None, description="약점_반영_내용 - 약점 키워드를 어떻게 반영했는지, 없으면 null")
    history_dedup_note: str = Field(..., description="이력_중복회피_메모 - 과거 이력과 어떻게 차별화했는지")
    estimated_solving_time_sec: int = Field(..., ge=0, description="예상_풀이시간_초")
    question_writing_guide: str = Field(..., description="출제_가이드_한줄 - 실제 문제 작성자(2단계 LLM)에게 줄 한 줄 지침")

    subject_str: Literal["국어", "수학", "영어", "사회", "과학"] = Field(..., description="과목명 (예: 국어, 수학, 영어, 사회, 과학)")
    school_level: Literal["초등학교", "중학교", "고등학교"] = Field(..., description="학년 구분 (예: 초등학교, 중학교, 고등학교)")
    
    
    



class ConfirmProblemState(CommonState):
    "QuestionSpecState과 BaseProblemState를 합쳐는 state"
    baseProblemState : BaseProblemState  = Field(description="문제 생성기에서 생성한 문제가 들어있는 객체")
    questionSpecState: QuestionSpecState = Field(description="LLM(문제 생성기)에게 전달할 문항 설계 명세 State")



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
    difficulty: Optional[str] = Field(default="보통", description="사용자가 선택한 난이도 (예: 최상,매우어려움, 어려움, 보통, 쉽게, 매우쉽게)")

    #step1
    student: StudentState | None = Field(default=None, description="조회된 학생 정보")
    #step2
    curriculum: list[CurriculumState] | None = Field(default_factory=list, description="조회된 진도 정보")
    subject: SubjectState | None = Field(default=None, description="조회된 과목 정보")
    term: TermState | None = Field(default=None, description="조회된 학년/학기 정보")
    #step3
    history_problems: list[BaseProblemState] | None = Field(default_factory=list, description="이 학생의 기존 문제 풀이 이력 (문제 난이도/유형 결정에 활용)")
    #step4
    weaknesses: list[WeaknessState] | None= Field(default_factory=list, description="이 학생의 기존 약점 목록 (문제 난이도/유형 결정에 활용)")

    #step5
    check_problemState : CheckProblemState | None = Field(default=None, description="CheckProblemState 의 객채")
    generated_problem: Optional[BaseProblemState] = Field(default=None, description="LLM이 생성한 문제 결과")

    #notification: Optional[NotificationState] = Field(default=None, description="발송 결과")
    retry_cnt: int = Field(description="문제가 적합하지않아서 실패했을시 문제를 다시 만든 시도횟수", default=0)
    error: Optional[str] = Field(default=None, description="파이프라인 중 발생한 에러 메시지")
    p_id: UUID | None = Field(description="문제가 생성된후의 problem_id 값", default=None)
    




# class ProblemState(BaseProblemState):
#     """생성된 문제 및 채점 결과 테이블 (problem)
#     학생/과목/진도 정보는 FK로만 연결한다.
#     """
#     problem_id: UUID = Field(default_factory=uuid4, description="문제 PK")
#     student_id: UUID = Field(description="FK -> student.student_id")
#     curriculum_id: UUID = Field(description="FK -> curriculum.curriculum_id")
    
    #answer: Optional[str] = Field(default=None, description="학생이 제출한 답변")
    #is_correct: Optional[bool] = Field(default=None, description="정답 여부 (채점 전에는 None)")
    #feedback: Optional[str] = Field(default=None, description="LLM 피드백")


# class NotificationState(CommonState):
#     """문제 발송 이력 테이블 (notification)"""
#     notification_id: UUID = Field(default_factory=uuid4, description="발송 PK")
#     student_id: UUID = Field(description="FK -> student.student_id")
#     problem_id: UUID = Field(description="FK -> problem.problem_id")
#     channel: Literal["email", "sms", "push"] = Field(default="email", description="발송 채널")
#     status: Literal["pending", "sent", "failed", "opened"] = Field(default="pending", description="발송 상태")
#     sent_at: Optional[datetime] = Field(default=None, description="발송 완료 시각")
#     error_message: Optional[str] = Field(default=None, description="실패 사유")