from datetime import datetime, timezone
from sqlalchemy import select
from db.models import Curriculum, Problem, Student, Subject, Term, Weakness
from db.session import get_db


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
                "status": problem.status,
                "feedback": problem.feedback,
                "is_correct": problem.is_correct,
            }

def getWeakness(student_id: str, curriculum_id:str) -> list:
    with get_db() as db:
        stmt = (
            select(Weakness)
            .where(
                Weakness.student_id == student_id,
                Weakness.curriculum_id == curriculum_id,
            )
        )
        result = db.execute(stmt).scalars().all()
        return list(result)


def getUsers(student_id:str) -> dict | None:
    with get_db() as db:
        st = db.get(Student, student_id)

        #print(problem)
        if(st is None):
            return None
        else:
            return {
                "student_id": str(st.student_id),
                "student_name": st.name,
                "telegram_chat_id":st.telegram_chat_id,
                "telegram_bot_token":st.telegram_bot_token
            }


def setProblems(p_id:str, answer:str, user:str) -> str :
    try:
        with get_db() as db:
            problem = db.get(Problem, p_id)
            problem.answer = answer
            problem.updated_by = user
            problem.updated_at = datetime.now(timezone.utc)
            problem.status="SUBMITTED"
            #db.add(problem)
            db.commit()
            return "정상처리 되었습니다."
    except Exception as e:
        return f"문제 저장 중 오류가 발생했습니다: {str(e)}"



def setAnswer(p_id:str, is_correct:str, feedback:str, weaknesses:str) -> str :
    try:
        with get_db() as db:
            problem = db.get(Problem, p_id)
            problem.is_correct = is_correct
            problem.feedback = feedback
            problem.updated_by = "answerAgent"
            problem.updated_at = datetime.now(timezone.utc)
            problem.status="GRADED"

            weak = Weakness(
                student_id          = problem.student_id,
                curriculum_id       = problem.curriculum_id,
                weakness_keyword    =  weaknesses
            )
            db.add(weak)
            db.commit()
            return "정상처리되었습니다."
    except Exception as e:
        return f"답변 저장 중 오류가 발생했습니다: {str(e)}"


def getCurriculmnInIds(curriculum_ids: list) -> list[Curriculum]:
    try:
        with get_db() as db:
            stmt = (
                select(Curriculum)
                .where(Curriculum.curriculum_id.in_(curriculum_ids))
            )
            curricula = db.execute(stmt).scalars().all()

            return [{"curriculum_id": cur.curriculum_id, "code": cur.code} for cur in curricula]
    except Exception as e:
        return f"커리큘럼 ids[] 조회중 오류가 발생했습니다: {str(e)}"


def getAllCurriculms(subjectId: str, termId: str):
    try:
        with get_db() as db:
            stmt = (
                select(Curriculum).order_by(Curriculum.code)
            )
            results = db.execute(stmt).all()

            return [{"curriculum_id": cur.curriculum_id, "code": cur.code} for cur in curricula]
    except Exception as e:
        return f"문제 저장 중 오류가 발생했습니다: {str(e)}"