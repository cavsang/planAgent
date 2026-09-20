import uuid

from db.models import Problem
from db.session import get_db
from model.llm import get_Generation, get_llm
from schema.schema import ProblemGenerationState


def getllmName(llm) -> str:
    """llm 객체에서 모델 이름을 추출한다."""
    if hasattr(llm, 'model'):
        return llm.model
    elif hasattr(llm, 'name'):
        return llm.name
    else:
        return "Unknown Model"


def insertDBNode(state: ProblemGenerationState) -> dict:
    """문제를 DB에 저장한다."""

    llm = get_Generation(state.subject_input)
    
    new_problem = Problem(
        student_id=state.student.student_id,
        curriculum_id=state.curriculum[0].curriculum_id,
        problem=state.generated_problem.problem,
        llm_model=getllmName(llm),
        problem_hint=state.generated_problem.problem_hint,
        problem_key_concepts=state.generated_problem.problem_key_concepts,
        correct_answer=state.generated_problem.correct_answer,
        updated_by='planAgent',
        created_by='planAgent'
    )

    p_id = None
    with get_db() as db:
        db.add(new_problem)
        db.flush()
        p_id = new_problem.problem_id
        db.commit()
    
    return {
        "p_id":  p_id
    }
