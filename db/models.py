"""
Pydantic State -> SQLAlchemy ORM 모델 매핑.

대상 (DB 테이블 7개):
  StudentState      -> student
  SubjectState      -> subject
  TermState         -> term
  CurriculumState   -> curriculum
  ProblemState      -> problem
  WeaknessState     -> weakness
  NotificationState -> notification

ProblemGenerationState / AgentState는 LangGraph 실행 중에만 쓰는
런타임 조합 객체이므로 테이블로 만들지 않는다 (Pydantic State 그대로 유지).

설계 원칙:
- PK는 UUID, Python 쪽(default=uuid4)에서 생성한다.
  -> Supabase/로컬 Postgres 어느 쪽이든 확장(pgcrypto 등) 설치 여부와
     무관하게 동일하게 동작해서 이관이 쉬움.
- enum성 컬럼(gender, term, channel, status)은 native PostgreSQL ENUM
  타입 대신 VARCHAR + CHECK 제약(native_enum=False)으로 만든다.
  -> DB에 CREATE TYPE으로 별도 타입이 생기지 않으므로,
     Alembic으로 Supabase <-> 로컬 Postgres 간 스키마를 옮길 때 더 단순함.
- FK는 curriculum/problem/weakness/notification에서만 사용 (설계 그대로).
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin


class Student(Base, TimestampMixin):
    __tablename__ = "student"
    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <= 12", name="ck_student_grade_range"),
    )

    student_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(
        Enum("M", "F", name="gender_enum", native_enum=False, validate_strings=True), nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    problems: Mapped[list["Problem"]] = relationship(back_populates="student")
    weaknesses: Mapped[list["Weakness"]] = relationship(back_populates="student")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="student")

    @property
    def school_level(self) -> str:
        if self.grade <= 6:
            return "초등학교"
        if self.grade <= 9:
            return "중학교"
        return "고등학교"


class Subject(Base, TimestampMixin):
    __tablename__ = "subject"

    subject_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    subject_name: Mapped[str] = mapped_column(String(100), nullable=False)

    curricula: Mapped[list["Curriculum"]] = relationship(back_populates="subject")


class Term(Base, TimestampMixin):
    __tablename__ = "term"
    __table_args__ = (
        CheckConstraint("grade >= 1 AND grade <= 12", name="ck_term_grade_range"),
        UniqueConstraint("grade", "term", name="uq_term_grade_term"),
    )

    term_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    term: Mapped[str] = mapped_column(
        Enum(
            "1학기", "2학기", "여름방학", "겨울방학",
            name="term_enum", native_enum=False, validate_strings=True,
        ),
        nullable=False,
    )

    curricula: Mapped[list["Curriculum"]] = relationship(back_populates="term")


class Curriculum(Base, TimestampMixin):
    __tablename__ = "curriculum"
    __table_args__ = (
        UniqueConstraint("subject_id", "term_id", "step", name="uq_curriculum_subject_term_step"),
    )

    curriculum_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subject.subject_id", ondelete="RESTRICT"), nullable=False
    )
    term_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("term.term_id", ondelete="RESTRICT"), nullable=False
    )
    step: Mapped[str] = mapped_column(String(200), nullable=False)
    step_desc: Mapped[str] = mapped_column(Text, nullable=False)

    subject: Mapped["Subject"] = relationship(back_populates="curricula")
    term: Mapped["Term"] = relationship(back_populates="curricula")
    problems: Mapped[list["Problem"]] = relationship(back_populates="curriculum")
    weaknesses: Mapped[list["Weakness"]] = relationship(back_populates="curriculum")


class Problem(Base, TimestampMixin):
    __tablename__ = "problem"

    problem_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False
    )
    curriculum_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("curriculum.curriculum_id", ondelete="RESTRICT"), nullable=False
    )
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text, default=None, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(default=None, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, default=None, nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), default=None, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="problems")
    curriculum: Mapped["Curriculum"] = relationship(back_populates="problems")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="problem")


class Weakness(Base, TimestampMixin):
    __tablename__ = "weakness"

    weakness_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False
    )
    curriculum_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("curriculum.curriculum_id", ondelete="SET NULL"), default=None, nullable=True
    )
    weakness_keyword: Mapped[str] = mapped_column(String(200), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="weaknesses")
    curriculum: Mapped[Optional["Curriculum"]] = relationship(back_populates="weaknesses")


class Notification(Base, TimestampMixin):
    __tablename__ = "notification"

    notification_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False
    )
    problem_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("problem.problem_id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(
        Enum("email", "sms", "push", name="channel_enum", native_enum=False, validate_strings=True),
        nullable=False,
        default="email",
        server_default="email",
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "sent", "failed", "opened", name="notification_status_enum", native_enum=False, validate_strings=True),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True, comment="발송 완료 시각"
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None, nullable=True)

    student: Mapped["Student"] = relationship(back_populates="notifications")
    problem: Mapped["Problem"] = relationship(back_populates="notifications")
