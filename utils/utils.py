from schema.schema import CurriculumState, ProblemState, WeaknessState


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


def format_history_problems(history: list[ProblemState] | None) -> str:
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
        """
    return system_prompt