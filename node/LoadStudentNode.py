from schema.schema import ProblemGenerationState, StudentState
from db.session import get_db
from sqlalchemy import select, and_, or_, not_
from db.models import Student

def loadStudent_node(state:ProblemGenerationState) -> dict:
    """학생 정보를 조회한다."""
    name = state['user_input']

    with get_db() as db:
        student = db.query(Student).filter_by(name=name).first()
        if student:
            return {
                "student_id": str(student.student_id),
                "name": student.name,
                "email": student.email,
                "gender": student.gender,
                "grade": student.grade,
                "birth_date": student.birth_date.isoformat(),
                "created_at": student.created_at.isoformat(),
                "updated_at": student.updated_at.isoformat(),
            }
        else:
            return {
                "error": f"Student with name '{name}' not found."
            }

