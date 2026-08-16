
from sqlalchemy import select

from db.models import Problem
from db.session import get_db
from schema.schema import ProblemGenerationState


def loadhistory_node(state:ProblemGenerationState) -> dict:
    """학습 이력을 조회한다"""
    student_id = state.student.student_id
    #print("==========================================")
    with get_db() as db:
        stmt = (
            select(Problem)
            .where(Problem.student_id == student_id)
            .order_by(Problem.problem_id)
        )
        #print(stmt)
        results = db.execute(stmt).all()
        if results:
            history_problems = []
            for problem in results:
                history_problems.append({
                    "problem_id": str(problem.problem_id),
                    "student_id": str(problem.student_id),
                    "curriculum_id": str(problem.curriculum_id),
                    "problem": problem.problem,
                    "answer": problem.answer,
                    "is_correct": problem.is_correct,
                    "feedback": problem.feedback,
                    "llm_model": problem.llm_model
                })
            return {
                "history_problems": history_problems
            }
        else:
            return {
                "history_problems": []
            }