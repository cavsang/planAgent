"""
db/models.py 에 정의된 모델을 실제로 어떻게 쓰는지 보여주는 예제.

실행:
    python examples/basic_usage.py

주의: 이 스크립트는 실행할 때마다 실제로 Supabase에 데이터를 씁니다.
    한 번 실행해보고 나서, Supabase Table Editor에서 확인 후
    필요하면 지워도 됩니다 (연습용 데이터이므로).
"""

from datetime import date

from db.models import Curriculum, Student, Subject, Term
from db.session import get_db


def create_example_data():
    with get_db() as db:
        # 1. 과목 생성 (없으면 새로 만들고, 있으면 기존 것 사용)
        subject = db.query(Subject).filter_by(subject_code="MATH").first()
        if subject is None:
            subject = Subject(subject_code="MATH", subject_name="수학")
            db.add(subject)
            db.flush()  # subject.subject_id 를 바로 쓰기 위해 flush (commit 전 DB에 반영)

        # 2. 학기 생성
        # term = db.query(Term).filter_by(grade=4, term="1학기").first()
        # if term is None:
        #     term = Term(grade=4, term="1학기")
        #     db.add(term)
        #     db.flush()

        # 3. 진도(커리큘럼) 생성 - subject/term은 FK로만 연결
        # curriculum = Curriculum(
        #     subject_id=subject.subject_id,
        #     term_id=term.term_id,
        #     step="1단원 - 유리수와 순환소수",
        #     step_desc="유리수를 소수로 표현하고 순환소수를 이해한다",
        # )
        # db.add(curriculum)

        # 4. 학생 생성
        student = Student(
            name="이하랑",
            birth_date=date(2016, 11, 1),
            gender="M",
            grade=4,
            email="",
        )
        db.add(student)

        db.commit()  # 여기서 실제로 DB에 반영됨
        print(f"생성됨: subject={subject.subject_name}, student={student.name}")
        return student.student_id


def query_example(student_id):
    with get_db() as db:
        student = db.get(Student, student_id)
        print(f"조회: {student.name} ({student.school_level}, {student.grade}학년)")

        # 학년(grade)으로 커리큘럼 조회 예시 (JOIN)
        curricula = (
            db.query(Curriculum)
            .join(Term, Curriculum.term_id == Term.term_id)
            .filter(Term.grade == student.grade)
            .all()
        )
        for c in curricula:
            print(f"  - {c.step}: {c.step_desc}")


if __name__ == "__main__":
    new_student_id = create_example_data()
    query_example(new_student_id)
