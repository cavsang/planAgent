

from langchain.messages import HumanMessage, SystemMessage

from model.llm import get_llm
from schema.schema import BaseProblemState, ConfirmProblemState, QuestionSpecState, CheckProblemState
from utils.utils import build_confirmproblem_system_prompt


def confirmProblemNode(confirmState:ConfirmProblemState) -> dict:
    """문제가 컨셉에 맞게 재대로 되었는지 검증한다."""
    base: BaseProblemState = confirmState.baseProblemState
    spec: QuestionSpecState = confirmState.questionSpecState

    system_prompt = build_confirmproblem_system_prompt()

    human_prompt = """다음은 문항 설계 명세와 실제로 생성된 문제입니다. 위 검증 기준에 따라 비교 검증해주세요.
        ## [설계 명세 - QuestionSpecState]
        - 과목: {subject}
        - 학년: {school_level}
        - 난이도등급: {difficulty_level}
        - 성취기준 요약: {standard_summary}
        - 수의 범위: {number_range}
        - 연산 단계수: {operation_steps}
        - 연산 종류: {operation_types}
        - 문장제 여부: {is_word_problem}
        - 조건 개수: {condition_count}
        - 조건 상세: {condition_details}
        - 함정 요소: {trap_elements}
        - 블룸 인지수준: {bloom_level}
        - 허용 용어: {allowed_terms}
        - 금지 용어 체크: {forbidden_terms_check}
        - 약점 반영 내용: {weakness_reflection}
        - 이력 중복회피 메모: {history_dedup_note}
        - 예상 풀이시간(초): {estimated_solving_time_sec}
        - 출제 가이드(한줄 지침): {question_writing_guide}

        ## [실제 생성된 문제 - BaseProblemState]
        - 문제: {problem}
        - 정답: {correct_answer}
        - 풀이 가이드(힌트): {problem_hint}
        - 핵심 개념 키워드: {problem_key_concepts}

        위 실제 문제가 설계 명세의 의도대로 정확히 생성되었는지 검증하세요.
        """.format(
            subject=spec.subject_str,
            school_level=spec.school_level,
            difficulty_level=spec.difficulty_level,
            standard_summary=spec.standard_summary,
            number_range=spec.number_range,
            operation_steps=spec.operation_steps,
            operation_types=", ".join(spec.operation_types),
            is_word_problem=spec.is_word_problem,
            condition_count=spec.condition_count,
            condition_details="\n  - " + "\n  - ".join(spec.condition_details) if spec.condition_details else "없음",
            trap_elements=", ".join(spec.trap_elements) if spec.trap_elements else "없음",
            bloom_level=spec.bloom_level,
            allowed_terms=", ".join(spec.allowed_terms),
            forbidden_terms_check=", ".join(spec.forbidden_terms_check) if spec.forbidden_terms_check else "없음",
            weakness_reflection=spec.weakness_reflection or "없음",
            history_dedup_note=spec.history_dedup_note,
            estimated_solving_time_sec=spec.estimated_solving_time_sec,
            question_writing_guide=spec.question_writing_guide,
            problem=base.problem,
            correct_answer=base.correct_answer,
            problem_hint=base.problem_hint,
            problem_key_concepts=base.problem_key_concepts or "없음",
        )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    #print(system_prompt)
    #print("==========================================")
    #print(human_prompt)

    llm = get_llm()
    structed_llm = llm.with_structured_output(CheckProblemState)
    result = structed_llm.invoke(messages)

    #print(result)
    if not result.is_confirm:
        return {
                "retry_cnt": spec.retry_cnt + 1,
                "check_problemState": result
        }
    else:
        return {
                "check_problemState": result,
                "generated_problem" : base.model_copy()
        }
    




    


    