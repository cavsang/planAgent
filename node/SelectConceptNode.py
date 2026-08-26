
import json

from langchain.messages import HumanMessage, SystemMessage

from model.llm import get_llm
from schema.schema import ProblemGenerationState, QuestionSpecState
from utils.utils import build_system_prompt, format_curriculum_list, format_history_problems, format_weaknesses


def selectconcept_node(state: ProblemGenerationState) -> dict:
    """문제 생성을 구체화 한다."""

    #print("selectconcept_node의 들어왔을때의 값 : ", state)

    student = state.student
    curriculum = state.curriculum
    weaknesses = state.weaknesses
    history_problems = state.history_problems
    difficulty = state.difficulty
    subject = state.subject.subject_name  # "국어" | "수학" | "영어" | "사회" | "과학"
    # ※ ProblemGenerationState에 subject 필드가 아직 없다면 추가해주세요.

    system_prompt = build_system_prompt(
        school_level=student.school_level,
        subject=subject,
        weaknesses=weaknesses,
    )

    human_prompt = """
        다음 학생 정보와 조건을 참고하여 난이도 설계 명세서를 생성해주세요.

        [요청 난이도 등급]
        {difficulty}

        [학생 정보]
        - 이름: {student_name}
        - 학년: {student_grade}({student_school_level})
        - 성별: {student_gender}

        [약점 키워드]
        {weaknesses_str}

        [기존 문제풀이 이력]
        {history_problems_str}

        [조회된 진도 - 성취기준]
        {curriculum_str}
    """.format(
        student_name=student.name,
        student_grade=student.grade,
        student_gender=student.gender,
        student_school_level=student.school_level,
        weaknesses_str=format_weaknesses(weaknesses),
        history_problems_str=format_history_problems(history_problems),
        curriculum_str=format_curriculum_list(curriculum),
        difficulty=difficulty,
    )

    messages=[
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    llm = get_llm()
    structured_llm = llm.with_structured_output(QuestionSpecState)
    results = structured_llm.invoke(messages)
    #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #print(results)
    #print("SelectConceptNode 에서의 result 값 : ", results)
    return results.model_dump()

