import os
import sys
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

load_dotenv()  # 프로젝트 루트의 .env 파일을 읽어 DATABASE_URL 등을 환경변수로 로드

# 프로젝트 루트(=alembic.ini가 있는 위치)를 import 경로에 추가
# -> planAgent/db/models.py 를 "db.models" 로 import하기 위함
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.base import Base  # noqa: E402
from db import models  # noqa: E402,F401  (Base.metadata에 테이블을 등록하기 위한 import)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# DATABASE_URL 환경변수가 있으면 alembic.ini의 값보다 우선 사용한다.
# -> 지금은 Supabase 커넥션 문자열, 나중엔 로컬 Postgres 커넥션 문자열만 바꿔주면 됨.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate가 우리 모델(7개 테이블)을 인식하도록 연결
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
