

import uuid

from db.models import Problem, Student
from db.session import get_db
from schema.schema import BaseProblemState, StudentState


def getProblems(p_id:str) -> dict | None:
    with get_db() as db:
        problem = db.get(Problem, p_id)

        #print(problem)
        if(problem is None):
            return None
        else:
            return {
                "problem_id": str(problem.problem_id),
                "student_id": str(problem.student_id),
                "curriculum_id": str(problem.curriculum_id),
                "problem": problem.problem,
                "problem_hint": problem.problem_hint,
                "problem_key_concepts": problem.problem_key_concepts,
                "correct_answer": problem.correct_answer,
                "answer": problem.answer,
                "status": problem.status
            }


def getUsers(student_id:str) -> dict | None:
    with get_db() as db:
        st = db.get(Student, student_id)

        #print(problem)
        if(st is None):
            return None
        else:
            return {
                "student_id": str(st.student_id),
                "student_name": st.name
            }


def setProblems(p_id:str, answer:str, user:str) -> str :
    try:
        with get_db() as db:
            problem = db.get(Problem, p_id)
            problem.answer = answer
            problem.updated_by = user
            problem.updated_at = problem.updated_at
            problem.status="SUBMITTED"
            #db.add(problem)
            db.commit()
            return "정상처리 되었습니다."
    except Exception as e:
        return f"문제 저장 중 오류가 발생했습니다: {str(e)}"
