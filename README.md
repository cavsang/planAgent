# planAgent에 DB 스키마 통합하기

이 zip은 **독립 프로젝트가 아니라, planAgent 루트에 그대로 덮어써서 병합**하는 용도입니다.

## 압축 풀고 나면 이렇게 병합됩니다
```
planAgent/                    ← 기존 프로젝트 루트
├── requirements.txt           (기존 그대로 — ADD_TO_requirements.txt 내용만 추가)
├── ADD_TO_requirements.txt    (신규 — 참고 후 삭제해도 됨)
├── alembic.ini                (신규)
├── alembic/                   (신규)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── .env.example                (신규 — 복사해서 .env 로)
├── schema/
│   └── schema.py                (기존 Pydantic State, 건드리지 않음)
└── db/                          (신규 — schema/ 와 형제 폴더)
    ├── __init__.py
    ├── base.py                    (Base + audit 공통 컬럼 mixin)
    └── models.py                  (SQLAlchemy 7개 테이블 모델)
```

## 적용 방법
1. 이 zip을 압축 풀어서 나온 `alembic.ini`, `alembic/`, `db/`, `.env.example` 을 planAgent 루트에 그대로 복사
2. `ADD_TO_requirements.txt` 내용을 기존 `requirements.txt`에 추가하고 `pip install -r requirements.txt`
3. `.env.example` → `.env` 복사 후 `DATABASE_URL`에 Supabase Direct connection 문자열 입력
4. **반드시 planAgent 루트에서** (schema/ 와 db/ 가 보이는 위치) 아래 실행
   ```bash
   alembic revision --autogenerate -m "initial schema"
   ```
5. `alembic/versions/`에 생긴 파일 열어서 7개 테이블(`student, subject, term, curriculum, problem, weakness, notification`)이 `create_table`로 들어있는지 확인
6. 문제없으면 적용
   ```bash
   alembic upgrade head
   ```

## schema/schema.py 와 db/models.py, 왜 따로 두나요
- `schema/schema.py`의 Pydantic 모델들은 **LangGraph 파이프라인 실행 중 메모리에서 흐르는 state** 용도입니다.
- `db/models.py`의 SQLAlchemy 모델들은 **실제 DB 테이블**입니다.
- 둘은 필드가 겹치지만 역할이 다르므로 합치지 않고 분리 유지합니다. 나중에 "DB에서 조회한 결과를 Pydantic State로 변환" 하는 매핑 함수가 필요해지면, `schema/` 또는 `db/` 어느 한쪽에 conversion 함수를 추가하는 방식을 권장합니다 (다음 단계에서 다룰 수 있음).

## 로컬 PostgreSQL로 이관할 때
`.env`의 `DATABASE_URL`만 로컬 주소로 바꾸고 `alembic upgrade head` 다시 실행하면 됩니다. 코드는 동일합니다.
