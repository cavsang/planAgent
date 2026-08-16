

from sqlalchemy import select

from db.models import Weakness
from db.session import get_db
from schema.schema import ProblemGenerationState


def weakness_node(state:ProblemGenerationState) -> dict:
    """학습 약점을 확인한다"""
    student_id = state.student.student_id
    
    with get_db() as db:
        stmt = (
                    select(Weakness)
                    .where(Weakness.student_id == student_id, Weakness.deleted_at is None)
                    .order_by(Weakness.weakness_id)
                )
        results = db.execute(stmt).all()

        if results:
            weaknesses = []
            for weakness in results:
                weaknesses.append({
                    "weakness_id": str(weakness.weakness_id),
                    "student_id": str(weakness.student_id),
                    "curriculum_id": str(weakness.curriculum_id) if weakness.curriculum_id else None,
                    "weakness_keyword": weakness.weakness_keyword
                })
            return {
                "weaknesses": weaknesses
            }
        else:
            return {
                "weaknesses": []
            }