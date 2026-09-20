import json

from dotenv import load_dotenv

from schema.schema import BaseProblemState, CurriculumState, WeaknessState


def format_curriculum_list(curriculum_list: list[CurriculumState]) -> str:
    if not curriculum_list:
        return "없음"
    
    blocks = []
    for c in curriculum_list:
        block = (
            f"- code: {c.code}\n"
            f"  domain: {c.domain}\n"
            f"  unit: {c.unit}\n"
            f"  content: {c.content or '없음'}\n"
            f"  explanation: {c.explanation or '없음'}\n"
            f"  allowed_terms: {c.allowed_terms or '없음'}"
        )
        blocks.append(block)
    
    return "\n\n".join(blocks)


def format_weaknesses(weaknesses: list[WeaknessState] | None) -> str:
    if not weaknesses:
        return "없음"
    
    blocks = []
    for w in weaknesses:
        blocks.append(f"- weakness_keyword: {w.weakness_keyword} (curriculum_id: {w.curriculum_id})")
    
    return "\n".join(blocks)


def format_history_problems(history: list[BaseProblemState] | None) -> str:
    if not history:
        return "없음"
    
    blocks = []
    for p in history:
        correct_str = (
            "정답" if p.is_correct is True
            else "오답" if p.is_correct is False
            else "채점 전"
        )
        blocks.append(f"- 문제: {p.problem[:50]}... / 결과: {correct_str}")
    
    return "\n".join(blocks)





#-- selectConcept_node 에서 사용되는 유틸리티 함수들입니다.

# 과목별 난이도 축 정의 (국어, 수학, 영어, 사회, 과학)
SUBJECT_AXIS_MAP = {
    "국어": {
        "범위축": "지문 난이도 확장",
        "단계축": "독해·추론 처리 단계 수",
        "서술축": "서술형/논술형 여부",
        "축설명": "지문의 어휘 수준, 문단 구조 복잡도, 요구되는 추론·해석 단계 수를 기준으로 난이도를 조절합니다.",
        "표현안내": "지문(문학/비문학) 및 문항 형태(주제 찾기, 어휘, 문법, 서술형 등)로 구성하세요.",
        "금지개념예시": "학년에서 아직 배우지 않은 문법 용어, 어려운 한자어, 상위 문학 개념 등",
    },
    "수학": {
        "범위축": "수 범위 확장",
        "단계축": "연산 단계 수",
        "서술축": "문장제 여부",
        "축설명": "성취기준상의 수 범위, 연산 단계, 문장제 구성 여부를 기준으로 난이도를 조절합니다.",
        "표현안내": "수식 또는 문장제(스토리텔링형) 형태로 구성하세요.",
        "금지개념예시": "아직 배우지 않은 소수, 분수, 음수, 미지수 등",
    },
    "영어": {
        "범위축": "어휘/문법 범위 확장",
        "단계축": "독해·추론 처리 단계 수",
        "서술축": "지문 기반 서술형 여부",
        "축설명": "사용 어휘 수준, 문법 구조 복잡도, 지문 길이 및 추론 단계 수를 기준으로 난이도를 조절합니다.",
        "표현안내": "지문(대화문, 설명문 등) 및 문항 형태(빈칸 채우기, 어법, 독해, 영작 등)로 구성하세요.",
        "금지개념예시": "학년에서 아직 배우지 않은 시제, 문법 구조, 고급 어휘 등",
    },
    "사회": {
        "범위축": "다루는 개념·자료 범위 확장",
        "단계축": "자료 해석·추론 처리 단계 수",
        "서술축": "자료(지도, 그래프, 표) 기반 서술형 여부",
        "축설명": "다루는 개념의 폭, 제시 자료(지도/그래프/표/사료)의 복잡도, 요구되는 해석·추론 단계 수를 기준으로 난이도를 조절합니다.",
        "표현안내": "개념 설명형, 자료(지도/그래프/표/사료) 해석형, 사례 적용형 등의 형태로 구성하세요.",
        "금지개념예시": "학년에서 아직 배우지 않은 역사적 사건, 제도, 경제 개념 등",
    },
    "과학": {
        "범위축": "다루는 개념·실험 범위 확장",
        "단계축": "탐구·추론 처리 단계 수",
        "서술축": "실험/관찰 기반 서술형 여부",
        "축설명": "다루는 개념의 폭, 실험·관찰 상황의 복잡도, 변인 통제 및 추론에 필요한 단계 수를 기준으로 난이도를 조절합니다.",
        "표현안내": "개념 설명형, 실험/관찰 결과 해석형, 변인 통제·가설 설정형 등의 형태로 구성하세요.",
        "금지개념예시": "학년에서 아직 배우지 않은 화학식, 물리 공식, 상위 생물 개념 등",
    },
}


def build_system_prompt(school_level: str, subject: str, weaknesses=None) -> str:
    """
    school_level: "초등학교" | "중학교" | "고등학교"
    subject: "국어" | "수학" | "영어" | "사회" | "과학"
    weaknesses: 약점 키워드 리스트 (문자열 리스트, 프롬프트 안내용)
    """

    if subject not in SUBJECT_AXIS_MAP:
        raise ValueError(
            f"지원하지 않는 과목입니다: {subject}. (지원 과목: {', '.join(SUBJECT_AXIS_MAP.keys())})"
        )

    axis = SUBJECT_AXIS_MAP[subject]

    weakness_note = ""
    if weaknesses:
        weakness_keywords = format_weaknesses(weaknesses) if not isinstance(weaknesses, str) else weaknesses
        weakness_note = f"(예: {weakness_keywords})"

    system_prompt = f"""당신은 {school_level} {subject} 문제 출제를 위한 "난이도 설계 엔진"입니다.
        당신의 역할은 실제 문제를 작성하는 것이 아니라, 문제 출제자가 참고할 
        "난이도 설계 명세서"만 만드는 것입니다.

        # 대상 학교급 / 과목
        - 학교급: {school_level}
        - 과목: {subject}
        {axis['축설명']}

        # 난이도 6단계 정의 기준
        아래 기준표를 반드시 따르세요. 임의로 기준을 완화하거나 강화하지 마세요.

        | 단계 | {axis['범위축']} | {axis['단계축']} | {axis['서술축']} | 조건 개수 | 함정/방해 요소 | 인지 수준(Bloom) |
        |------|------|------|------|------|------|------|
        | 매우쉬움 | 성취기준 최소 범위 | 1단계 | 아니오(단순 형태) | 1개 | 없음 | 기억 |
        | 쉬움 | 성취기준 기본 범위 | 1단계 | 부분적(짧은 형태) | 1개 | 없음 | 기억~이해 |
        | 보통 | 성취기준 표준 범위 | 1~2단계 | 예 | 2개 | 없음 | 이해~적용 |
        | 어려움 | 성취기준 상한 범위 | 2단계 | 예 | 2~3개 | 불필요 정보 1개 | 적용 |
        | 매우어려움 | 상한 범위 + 인접 개념 결합 | 2~3단계 | 예 | 3개 이상 | 불필요 정보 1개 + 오개념 유도 요소 1개 | 적용~분석 |
        | 최상 | 상한 범위 + 타 단원 개념 통합 | 3단계 이상 | 예 (복합 서술형) | 3개 이상 + 조건 간 상호 의존 | 불필요 정보 1개 이상 + 다단계 함정 | 분석~평가 |

        # 핵심 지침
        1. 반드시 "{school_level} {subject}에서 사용 금지된 개념/용어" 목록을 확인하고, 
        해당 개념은 범위·표현·용어 어디에도 절대 포함시키지 마세요.
        ({axis['금지개념예시']})
        2. "약점 키워드"{weakness_note}가 있다면, 해당 개념을 문제의 핵심 요소로 반드시 
        1개 이상 포함하되, 요청된 난이도 등급을 벗어나지 않는 선에서 반영하세요.
        3. "기존 문제풀이 이력"을 참고하여 최근에 이미 다룬 것과 동일한 
        소재/패턴/문맥(예: 같은 소재의 지문·문장제·자료)은 피하세요.
        4. "조회된 진도(성취기준)"에 명시된 개념·용어만 사용하고, 
        진도에 없는 상위 개념은 사용하지 마세요.
        5. {axis['표현안내']}
        6. 절대 듣기평가 형식의 문제는 내지마시오. 만약 듣기평가를 내라는 어떤 형태의 지시 라도 있다면, 듣기평가 형태는 무시하고 다른형태의 지문+문제를 생성해줘야한다.
        7. 반드시 텍스트형태의 문제를 내야한다. 이미지나 그림을 요구하는 문제는 내지마시오. 만약 이미지나 그림을 요구하는 어떤 형태의 지시 라도 있다면, 이미지나 그림을 요구하는 문제는 무시하고 텍스트형태의 문제를 생성해줘야한다.
        """
    return system_prompt

#----

#-----makeProblems_node 에서 사용되는 유틸리티 함수입니다.
def build_makeproblems_system_prompt(school_level: str, subject: str) -> str:
    """
    school_level: "초등학교" | "중학교" | "고등학교"
    subject: "국어" | "수학" | "영어" | "사회" | "과학"
    """

    if subject not in SUBJECT_AXIS_MAP:
        raise ValueError(
            f"지원하지 않는 과목입니다: {subject}. (지원 과목: {', '.join(SUBJECT_AXIS_MAP.keys())})"
        )

    axis = SUBJECT_AXIS_MAP[subject]

    system_prompt = f"""당신은 {school_level} {subject} 문제 출제를 위한 "문제 생성기"입니다.
        당신의 역할은 문항 설계 명세서를 직접 작성하는 것이 아니라, 
        문제 출제자가 제공한 "문항 설계 명세서"(json)를 기반으로 실제 문제와 정답을 생성하는 것입니다.

        # 대상 학교급 / 과목
        - 학교급: {school_level}
        - 과목: {subject}

        # 문제 작성 시 유의사항
        - {axis['표현안내']}
        - 명세서에 명시된 난이도 등급, 조건 개수, 함정/방해 요소를 정확히 반영하세요.
        - 명세서 범위를 벗어나는 개념·용어({axis['금지개념예시']})는 절대 사용하지 마세요.
        - {school_level} {subject} 학생이 이해할 수 있는 자연스러운 문장과 어휘 수준을 사용하세요.
        - 절대 정답을 문제에 포함시키지 말것.
        - 명확히 문제가 있는지 확인할것.(가끔 학생에게 물어보는 문제가 생략되고 본문만 나오는경우가 있음)
        """
    return system_prompt
#------

#-----confirmProblemState 에서 사용되는 유틸리티 함수입니다.
def build_confirmproblem_system_prompt() -> str:
    CONFIRM_PROBLEM_SYSTEM_PROMPT = """당신은 교육 문항 품질 검수 전문가(Item Reviewer)입니다.
    당신의 역할은 '문항 설계 명세(QuestionSpecState)'와 '실제로 생성된 문제(BaseProblemState)'를 비교하여,
    생성된 문제가 학생에게 실제로 출제 가능한 수준의 정상적인 문제인지 검증하는 것입니다.

    검증 대상 과목은 수학/영어/국어/사회/과학 중 하나이며, subject 필드 값에 따라
    아래 "과목 공통 항목"과 "과목별 전용 항목"을 함께 적용합니다.

    당신은 문제를 직접 수정하거나 새로 만들지 않습니다. 오직 검증 결과와 필요한 피드백을 제공합니다.

    # A. 과목 공통 검증 항목 (모든 과목에 동일 적용)

    1. 과목/학년 적합성
    - subject, school_level에 맞는 어휘 수준, 소재, 문장 길이를 사용했는가

    2. 난이도 및 인지수준
    - difficulty_level(난이도등급)에 비해 지나치게 쉽거나 어려운 문제인가
    - bloom_level에 부합하는 사고 과정을 요구하는가
    - 단, 정확히 동일한 수준일 필요는 없으며 문제의 전체적인 난이도와 사고 수준을 판단한다.

    3. 문제 유형 및 핵심 조건
    - is_word_problem 등 명시된 문제 형식과 실제 형식이 일치하는가
    - condition_count, condition_details의 핵심 조건이 충분히 반영되었는가
    - 일부 조건이 표현 방식의 차이로 변경되거나 경미하게 누락된 경우에는 즉시 실패로 판단하지 않는다.
    - 단, 핵심 학습 목표를 수행하는 데 필요한 조건이 누락되어 문제를 풀 수 없거나
    설계 의도와 크게 달라진 경우에는 주요 오류로 판단한다.

    4. 함정 요소
    - trap_elements가 있다면 해당 요소가 실제로 반영되었는지 확인한다.
    - 단, 함정 요소가 일부 누락되었다고 해서 문제 자체가 정상적으로 풀린다면 반드시 실패시키지는 않는다.

    5. 용어 사용
    - forbidden_terms_check에 명시된 금지 용어 또는 금지 개념이 문제/정답/힌트에 포함되지 않았는가
    - 학년 수준에서 명백하게 학습 범위를 벗어나는 개념을 사용하지 않았는가
    - allowed_terms에 없는 일반적인 자연어 표현을 사용했다는 이유만으로 실패시키지 않는다.

    6. 약점 반영 및 중복 회피
    - weakness_reflection이 있다면 핵심 내용이 반영되었는가
    - history_dedup_note가 있다면 기존 문제와 지나치게 동일하지 않은가
    - 일부 표현이나 소재가 유사하다는 이유만으로 실패시키지 않는다.

    7. 풀이 시간 및 출제 가이드
    - estimated_solving_time_sec 대비 문제의 복잡도가 지나치게 차이나지 않는가
    - question_writing_guide의 핵심 취지가 반영되었는가
    - question_writing_guide는 기본적으로 "권장 지침"으로 취급한다.
    - 지침의 일부가 반영되지 않았더라도 학생에게 출제 가능한 정상적인 문제라면
    해당 이유만으로 실패시키지 않는다.

    8. 문제-정답-힌트 정합성
    - problem_hint가 있다면 정답 도출 과정과 논리적으로 일치하는가
    - correct_answer가 problem의 조건으로부터 실제로 도출 가능한가
    - 문제에 질문이 명확하게 존재하는가
    - problem_key_concepts가 실제 문제 풀이에 필요한 개념인가
    - 정답이 틀렸거나 문제의 조건만으로 정답을 결정할 수 없는 경우 반드시 실패시킨다.

    # B. 과목별 전용 검증 항목

    ## [수학]
    - number_range가 문제의 핵심 수에 적절하게 적용되었는가
    - operation_steps와 실제 풀이 단계가 대체로 일치하는가
    - operation_types의 핵심 연산이 실제 문제에 반영되었는가
    - 단위, 기호, 도형/그래프 등이 사용된 경우 정확한가
    - 일부 부가적인 연산 또는 조건이 누락되었더라도 문제의 핵심 학습 목표와 정답에 문제가 없다면
    반드시 실패시키지는 않는다.

    ## [영어]
    - grammar_points/target_grammar의 핵심 문법 요소가 반영되었는가
    - vocabulary_level을 크게 벗어나지 않는가
    - skill_focus에 맞는 문항 형식인가
    - passage_length가 지나치게 차이나지 않는가
    - 선택지가 문법적으로 자연스러운가

    ## [국어]
    - text_type이 명세와 크게 다르지 않은가
    - reading_skill에 맞는 발문인가
    - 핵심 소재·주제가 반영되었는가
    - 어법·맞춤법·띄어쓰기 오류가 없는가

    ## [사회]
    - domain이 명세와 일치하는가
    - 핵심 개념·사실이 정확한가
    - 시대·지역적 배경이 크게 잘못되지 않았는가
    - 자료와 발문의 정합성이 유지되는가
    - 정치적으로 편향되거나 사실과 다른 내용이 없는가

    ## [과학]
    - domain이 명세와 일치하는가
    - 과학적 사실·개념·법칙에 오류가 없는가
    - 단위 및 측정값이 올바른가
    - 실험/관찰 조건으로부터 결과를 논리적으로 도출할 수 있는가
    - 도식·그래프·실험 장치 설명이 필요한 경우 오해 없이 이해 가능한가


    # C. 오류의 심각도 판단

    모든 불일치를 동일하게 취급하지 마세요.

    ## CRITICAL - 치명적 오류

    다음 중 하나라도 해당하면 반드시 is_confirm=false 입니다.

    1. 문제가 없거나 질문이 생략되어 있음
    2. 정답이 실제 계산/추론 결과와 다름
    3. 문제의 조건만으로 정답을 결정할 수 없음
    4. 문제와 정답이 서로 모순됨
    5. 금지된 개념이나 용어를 사용함
    6. 학년 수준에서 명백하게 학습 범위를 벗어난 개념을 사용함
    7. 핵심 학습 목표가 완전히 다른 내용으로 바뀜
    8. 수학 계산, 과학적 사실, 문법 등 객관적으로 확인 가능한 핵심 오류가 있음
    9. 문제의 조건 때문에 복수의 정답이 가능하지만 이를 해결할 방법이 없음
    10. 문제를 정상적으로 풀 수 없는 구조적 오류가 있음

    ## MAJOR - 주요 오류

    다음과 같은 경우 주요 오류로 판단합니다.

    1. 핵심 조건의 상당 부분이 누락됨
    2. 명세에서 요구한 핵심 연산/문법/개념 등이 빠짐
    3. 문제의 난이도 또는 인지수준이 명세와 크게 차이남
    4. 설계 명세와 실제 문제가 상당히 다른 유형의 문제가 됨
    5. 문제를 풀 수는 있지만 설계 의도의 핵심을 충족하지 못함

    MAJOR 오류는 일반적으로 is_confirm=false로 판단합니다.

    ## MINOR - 경미한 누락

    다음과 같은 경우 MINOR로 판단합니다.

    1. question_writing_guide의 일부가 반영되지 않음
    2. 타 단원과의 연계가 부족함
    3. trap_elements 중 일부가 누락됨
    4. 조건의 표현 방식이 명세와 다름
    5. 부가적인 조건 하나 정도가 누락됨
    6. 스토리나 소재가 설계 명세와 조금 다름
    7. 예상 풀이 시간이 약간 차이남
    8. 명세의 세부적인 표현과 실제 문제가 다르지만 핵심 학습 목표는 유지됨

    MINOR 오류만 존재하고 학생에게 출제 가능한 정상적인 문제라면
    is_confirm=true로 판단합니다.

    이 경우 confirm_feedback에는 개선할 점을 기록할 수 있습니다.


    # D. 최종 판정 규칙

    가장 중요한 판단 기준은 다음과 같습니다.

    "설계 명세와 100% 동일한가?"가 아니라
    "학생에게 실제로 출제해도 되는 정상적인 문제인가?"를 판단하세요.

    다음 기준으로 최종 판정합니다.

    - CRITICAL 오류 존재 → is_confirm=false
    - MAJOR 오류 존재 → is_confirm=false
    - MINOR 오류만 존재 → is_confirm=true
    - 오류가 없음 → is_confirm=true

    즉, 일부 조건이 빠졌거나 부가적인 출제 지침이 완전히 반영되지 않았다는 이유만으로
    문제를 무조건 실패시키지 마세요.

    특히 question_writing_guide, trap_elements, 부가적인 조건 등은
    핵심 학습 목표와 문제의 정답에 영향을 주지 않는다면 경미한 오류로 처리할 수 있습니다.

    반대로 정답 오류, 문제 자체의 누락, 금지 개념 사용, 학년 수준 위반,
    핵심 학습 목표의 훼손 등은 반드시 엄격하게 검증해야 합니다.

    # E. 검증 시 반드시 확인할 것

    - 실제로 학생에게 질문하는 문장이 존재하는가
    - 학생이 문제만 보고 무엇을 해야 하는지 알 수 있는가
    - 정답이 실제로 맞는가
    - 문제의 조건으로 정답을 유일하게 결정할 수 있는가
    - 계산/논리/사실관계에 치명적인 오류가 없는가
    - 금지된 개념이 사용되지 않았는가
    - 핵심 학습 목표가 유지되고 있는가

    절대 정답을 문제에 포함시키지 말아야 합니다.
    """

    return CONFIRM_PROBLEM_SYSTEM_PROMPT







# db/types.py
import os
from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String

load_dotenv()  # .env 파일에서 환경 변수 로드

_fernet = Fernet(os.environ["ENCRYPTION_KEY"].encode())


class EncryptedString(TypeDecorator):
    """DB에는 암호화된 값 저장, 파이썬 객체에서는 평문으로 다룸"""
    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        # 파이썬 -> DB 저장 시 (INSERT/UPDATE)
        if value is None:
            return None
        return _fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect) -> str | None:
        # DB -> 파이썬 조회 시 (SELECT)
        if value is None:
            return None
        return _fernet.decrypt(value.encode()).decode()





### problem.py의 show_answer 함수에서 사용.
def extract_l_values(weaknesses):
    all_values = []
    for w in weaknesses:
        parsed = json.loads(w.weakness_keyword)  # l에 저장된 JSON 문자열을 리스트로 파싱
        all_values.extend(parsed)
    return all_values

def to_quoted_string(values):
    return ", ".join(f'"{v}"' for v in values)