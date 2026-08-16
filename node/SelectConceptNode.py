
from langchain.messages import HumanMessage, SystemMessage

from model.llm import get_llm
from schema.schema import ProblemGenerationState
from utils.utils import format_curriculum_list, format_history_problems, format_weaknesses


def selectconcept_node(state: ProblemGenerationState) -> dict:
    """종합적으로 문제를 생성한다."""

    system_prompt = """당신은 초/중/고 학생 맞춤형 문제를 출제하는 전문 교육 콘텐츠 생성 AI입니다.

        [역할]
        주어진 학생 정보, 교육과정(curriculum) 정보, 학생의 약점, 기존 풀이 이력을 바탕으로
        학생의 학년 수준에 정확히 맞는 문제를 1개 생성합니다.

        [출제 우선순위 규칙]
        1. weaknesses(학생의 기존 약점)가 존재하면, 해당 약점 키워드와 관련된 curriculum 항목을 최우선으로 선택하여 그 영역을 보완할 수 있는 문제를 출제한다.
        2. weaknesses가 없고 history_problems(기존 풀이 이력)가 존재하면, 이력을 참고하여 이미 다룬 code/domain은 피하고 아직 다루지 않았거나 오답률이 높았던 영역 위주로 출제한다.
        3. weaknesses와 history_problems가 모두 없다면, curriculum 목록을 code 오름차순으로 정렬했을 때 가장 앞선 code의 진도부터 출제한다.

        [출제 시 반드시 지켜야 할 제약]
        - 문제는 반드시 curriculum의 content(성취기준)와 explanation(해설)에서 다루는 개념 범위 안에서만 출제한다.
        - allowed_terms에 명시된 용어/기호만 사용한다. allowed_terms에 없는 상위 학년 용어(예: 약수, 배수, 기약분수 등)는 절대 사용하지 않는다.
        - 학생의 grade(학년) 수준에 맞는 문장 길이와 어휘 난이도로 작성한다. (예: 초등 저학년은 짧고 쉬운 문장, 중고등은 정형화된 서술 가능)
        - 문제는 반드시 curriculum의 unit(단원)과 domain(영역)에서 벗어나지 않아야 한다.
        - 계산 문제의 경우 정답이 명확히 하나로 정해지도록 출제한다. (모호한 조건 금지)

        [출력 형식]
        다음 JSON 형식으로만 응답한다. 그 외 설명, 마크다운, 코드블록 등은 포함하지 않는다.
        {{
        "problem": "생성된 문제 전문",
        "curriculum_code": "이 문제가 근거로 한 curriculum의 code",
        "selection_reason": "약점/이력/순차 진도 중 어떤 기준으로 이 진도를 선택했는지에 대한 한 줄 설명"
        }}
        """

    student = state.student
    curriculum = state.curriculum
    weaknesses = state.weaknesses
    history_problems = state.history_problems

    human_prompt = """아래는 문제를 생성할 학생 정보와 관련 데이터입니다. 이를 참고하여 [출제 우선순위 규칙]에 따라 문제를 1개 생성해주세요.

        [학생 정보]
        - 이름: {student_name}
        - 학년: {student_grade}학년 ({student_school_level})
        - 성별: {student_gender}

        [학생의 기존 약점 목록]
        {weaknesses_str}

        [학생의 기존 문제 풀이 이력]
        {history_problems_str}

        [조회된 진도(curriculum) 목록 - 학년에 해당하는 전체 후보]
        {curriculum_str}

        [난이도]
        최상,상,중,하 중 최상 으로 문제를 출제해야한다.

        위 정보를 바탕으로, [출제 우선순위 규칙] 1→2→3 순서로 판단하여 가장 적절한 curriculum 항목 1개를 선택하고, 그에 맞는 문제를 System Prompt의 [출력 형식]에 맞춰 생성해주세요.
    """.format(
        student_name=state.student.name,
        student_grade=state.student.grade,
        student_school_level=state.student.school_level,
        student_gender=state.student.gender,
        weaknesses_str=format_weaknesses(state.weaknesses),
        history_problems_str=format_history_problems(state.history_problems),
        curriculum_str=format_curriculum_list(state.curriculum),
    )

    messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    #print(system_prompt)
    #print("==========================================")
    #print(human_prompt)
    
    llm = get_llm()
    results = llm.invoke(messages)
    print(results)
    return {}