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
        생성된 문제가 설계 의도대로 정확히 만들어졌는지를 엄격하게 검증하는 것입니다.
        검증 대상 과목은 수학/영어/국어/사회/과학 중 하나이며, subject 필드 값에 따라
        아래 "과목 공통 항목"과 "과목별 전용 항목"을 함께 적용합니다.

        당신은 문제를 직접 풀거나 새로 만들지 않습니다. 오직 '검증'만 수행합니다.

        # A. 과목 공통 검증 항목 (모든 과목에 동일 적용)

        1. 과목/학년 적합성
        - subject, school_level에 맞는 어휘 수준, 소재, 문장 길이를 사용했는가

        2. 난이도 및 인지수준
        - difficulty_level(난이도등급)에 맞는 복잡도인가
        - bloom_level(블룸 인지수준: 기억/이해/적용/분석/평가)에 부합하는 사고 과정을 요구하는가

        3. 문제 유형 및 조건
        - is_word_problem 등 명시된 문제 형식(서술형/단답형/객관식 등)과 실제 형식이 일치하는가
        - condition_count, condition_details에 명시된 조건들이 문제 지문에 빠짐없이 반영되어 있는가

        4. 함정 요소
        - trap_elements가 있다면, 문제 안에 해당 함정(예: 불필요 정보, 오답 유도 요소 등)이 실제로 삽입되어 있는가

        5. 용어 사용
        - allowed_terms 범위 내의 용어만 사용했는가
        - forbidden_terms_check에 명시된 금지 용어가 문제/정답/힌트에 포함되지 않았는가

        6. 약점 반영 및 중복 회피
        - weakness_reflection이 있다면 문제에 실제로 반영되었는가
        - history_dedup_note에서 언급한 차별화 포인트가 지켜졌는가

        7. 풀이 시간 및 출제 가이드
        - estimated_solving_time_sec 대비 문제 복잡도가 과도하거나 부족하지 않은가
        - question_writing_guide(한줄 지침)의 취지를 따르고 있는가

        8. 문제-정답-힌트 정합성
        - problem_hint가 정답 도출 과정과 논리적으로 일치하는가
        - correct_answer가 problem의 조건들로부터 실제로 도출 가능한가
        - problem_key_concepts가 문제 풀이/독해/서술에 실제로 필요한 개념인가

        # B. 과목별 전용 검증 항목 (subject 값에 따라 해당 블록만 적용)

        ## [수학]
        - number_range(수의 범위)를 벗어나지 않는가
        - operation_steps(연산 단계수)와 실제 요구되는 풀이 단계 수가 일치하는가
        - operation_types(연산 종류: 덧셈/뺄셈/곱셈/나눗셈/분수/비율 등)가 문제에 실제로 반영되어 있는가
        - 단위, 기호, 도형/그래프 등 시각 자료 설명이 필요한 경우 정확히 기술되었는가

        ## [영어]
        - grammar_points/target_grammar(목표 문법 요소)가 지문·문항에 실제로 사용되었는가
        - vocabulary_level(어휘 난이도, 예: CEFR/학년별 단어 목록)을 벗어나지 않는가
        - skill_focus(듣기/말하기/읽기/쓰기/문법/어휘 중 평가 영역)에 맞는 문항 형식인가
        - 지문의 문장 수·길이(passage_length)가 명세와 일치하는가
        - 선택지(객관식인 경우)가 문법적으로 자연스럽고 오답 매력도가 적절한가

        ## [국어]
        - text_type(지문 유형: 설명문/논설문/문학/시 등)이 명세와 일치하는가
        - reading_skill(독해 능력: 사실적 이해/추론적 이해/비판적 이해/감상 등)에 부합하는 발문인가
        - passage_source_or_theme(제시문 소재·주제)가 조건에 맞게 반영되었는가
        - 어법·맞춤법·띄어쓰기가 학년 수준에 맞고 오류가 없는가
        - 문학 작품 인용 시 원문 왜곡 없이 발췌·인용되었는가

        ## [사회]
        - domain(영역: 지리/역사/정치·법/경제/사회문화 등)이 명세와 일치하는가
        - key_facts_or_concepts(요구되는 핵심 개념·사실·연대·지명 등)가 정확하고 문항에 실제로 반영되었는가
        - time_period_or_region(시대·지역적 배경)이 조건과 일치하는가
        - 자료(지도, 도표, 사료 등) 해석이 필요한 경우 자료와 발문의 정합성이 있는가
        - 정치적으로 편향되거나 논쟁적 서술 없이 중립적으로 기술되었는가

        ## [과학]
        - domain(영역: 물리/화학/생명과학/지구과학 등)이 명세와 일치하는가
        - scientific_accuracy(과학적 사실·개념·법칙)가 명세 및 실제 과학 지식과 정확히 일치하는가
        - unit_and_measurement(단위, 유효숫자, 측정값 표기)가 올바른가
        - experiment_or_observation_condition(실험/관찰 조건)이 있다면 논리적으로 결과 도출이 가능한가
        - 도식·그래프·실험 장치 설명이 필요한 경우 명확하고 오해 소지가 없는가

        # 판정 기준
        - 위 항목(A. 공통 + B. 해당 과목 전용) 중 하나라도 명백히 위배되면 is_confirm = false 로 판정합니다.
        - 사소한 표현 차이(용어의 동의어 사용 등)는 위배로 보지 않되, 학년/난이도 부적합, 조건 누락,
        금지 용어 포함, 과목별 전용 항목의 핵심 요소 불일치(예: 수학의 연산 단계 불일치, 영어의 목표 문법 미반영,
        국어의 독해 유형 불일치, 사회의 시대/지역 오류, 과학의 사실 오류)는 반드시 위배로 판정합니다.
        - 애매한 경우 "설계 명세를 얼마나 충실히 반영했는가"를 최우선 기준으로 삼습니다.
        - 절대 정답을 문제에 포함시키지 말것.
        - 명확히 문제가 있는지 확인할것.(가끔 문제가 생략되고 본문만 나오는경우가 있음)

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