import uuid

from db.models import Problem
from db.session import get_db
from model.llm import get_llm
from schema.schema import ProblemGenerationState


def insertDBNode(state: ProblemGenerationState) -> dict:
    """문제를 DB에 저장한다."""

    llm = get_llm()
    
    new_problem = Problem(
        student_id=state.student.student_id,
        curriculum_id=state.curriculum[0].curriculum_id,
        problem=state.generated_problem.problem,
        llm_model=llm.model_name,
        problem_hint=state.generated_problem.problem_hint,
        problem_key_concepts=state.generated_problem.problem_key_concepts
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
