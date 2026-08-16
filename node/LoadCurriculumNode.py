
import json

from sqlalchemy import select

from db.models import Curriculum, Subject, Term
from db.session import get_db
from schema.schema import ProblemGenerationState


def curriculum_node(state:ProblemGenerationState) -> dict:
    """학년/학기/진도를 조회한다."""
    code = state.code

    with get_db() as db:
        stmt = (
            select(Curriculum, Subject, Term)
            .join(Subject, Curriculum.subject_id == Subject.subject_id)
            .join(Term, Curriculum.term_id == Term.term_id)
            .where(Curriculum.code == code)
            .order_by(Curriculum.code)
        )

        results = db.execute(stmt).all()

        if results:
            curriculum_list = []
            
            subjects=None
            terms=None
            
            for curriculum, subject, term in results:
                if not subjects:
                    subjects = {
                        "subject_id": str(subject.subject_id),
                        "subject_code": subject.subject_code,
                        "subject_name": subject.subject_name
                    }
                if not terms:
                    terms = {
                        "term_id": str(term.term_id),
                        "grade": term.grade,
                        "term": term.term
                    }
                
                curriculum_list.append({
                    "curriculum_id": str(curriculum.curriculum_id),
                    "subject_id": str(curriculum.subject_id),
                    "term_id": str(curriculum.term_id),
                    "code": curriculum.code,
                    "domain": curriculum.domain,
                    "unit": curriculum.unit,
                    "content": curriculum.content,
                    "explanation": curriculum.explanation,
                    "allowed_terms": curriculum.allowed_terms,
                })

            return {
                "curriculum": curriculum_list,
                "subject": subjects,
                "term": terms
            }
        else:
            return {
                "error": f"No curriculum found for code '{code}'."
            }
    