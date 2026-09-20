

import json

from langchain.messages import HumanMessage, SystemMessage
from model.llm import get_Generation, get_llm
from schema.schema import BaseProblemState, QuestionSpecState
from utils.utils import build_makeproblems_system_prompt


def makeproblems_node(state: QuestionSpecState) -> dict:
    """문제 생성기(LLM)에게 문제를 생성하도록 요청한다."""

    #print("makeproblems_node 들어왔을때의 값 : ", state)

    school_level = state.school_level  # 예: "초등학교" | "중학교" | "고등학교"
    subject = state.subject_str            # 예: "국어" | "수학" | "영어" | "사회" | "과학"
    # ※ QuestionSpecState의 실제 필드명이 다르다면 아래 두 줄만 맞춰주세요.

    system_prompt = build_makeproblems_system_prompt(
        school_level=school_level,
        subject=subject,
    )

    human_prompt = f"""아래는 문제 출제자가 제공한 문항 설계 명세서입니다.
        이 명세서를 기반으로 실제 문제와 정답을 생성하세요.
        confirm_feedback 이 있다면 feedback을 참고해서 생성해주세요.
        (feedback이 있다면 반영하되, feedback 이외에는 나머지는 좋다는 의미이니까, 문제를 전체적으로 새로만들지말고,feedback을 추가/수정 해서 문제를 만드는 방향으로 진행하세요.)
        {state.model_dump_json(indent=2, ensure_ascii=False)}
    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    print("==========================================start")
    print(system_prompt)
    print("==========================================")
    print(human_prompt)
    print("==========================================end")

    llm = get_Generation(subject)
    structured_llm = llm.with_structured_output(BaseProblemState)
    result = structured_llm.invoke(messages)
    #result = llm.invoke(messages)

    print(f"[문제생성결과] : {result}")
    return {
        "baseProblemState":   result.model_dump(),
        "questionSpecState": state
    }



