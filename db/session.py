"""
DB 엔진 및 세션 관리.

alembic은 스키마(테이블 구조)를 관리하는 용도이고,
실제 애플리케이션 코드(LangGraph 노드 등)에서 데이터를 읽고 쓸 때는
이 모듈의 SessionLocal / get_db 를 사용한다.
"""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

# pool_pre_ping=True: 오래 유휴 상태였던 커넥션이 죽어있으면 자동으로 재연결.
# Supabase pooler 특성상 유휴 커넥션이 끊기는 경우가 있어 실전에서 꼭 필요.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_db():
    """
    with get_db() as db:
        db.add(obj)
        db.commit()
    형태로 사용. 블록을 벗어나면 세션이 자동으로 닫힌다.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
