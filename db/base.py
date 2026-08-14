"""
공통 Base 클래스 및 audit(감사) 컬럼 mixin.

- Supabase / 로컬 PostgreSQL 어디에 붙이든 동일하게 동작하도록
  PostgreSQL 표준 기능만 사용한다 (Supabase 전용 확장 X).
- created_at/updated_at은 server_default=func.now()로 DB 레벨에서도 보장한다.
  (ORM을 거치지 않은 raw SQL insert에도 값이 채워지도록)
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """공통 감사(audit) 필드. 모든 테이블 모델이 상속한다."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False,
        comment="생성일시",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        onupdate=utc_now,
        nullable=False,
        comment="수정일시",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True, comment="삭제일시 (soft delete)"
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        String(100), default=None, nullable=True, comment="생성자 (system/teacher/admin 등)"
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(100), default=None, nullable=True, comment="수정자"
    )
