import asyncio
from datetime import datetime, timedelta

from graph.builder import executable_builder


WEEKDAYS = {0, 1, 2, 3, 4}  # 월~금

RUN_HOUR = 14
RUN_MINUTE = 0


SUBJECTS = [
    {"subject": "영어", "difficulty": "보통"},
    {"subject": "수학", "difficulty": "어려움"},
    {"subject": "국어", "difficulty": "어려움"},
    {"subject": "과학", "difficulty": "보통"},
    {"subject": "사회", "difficulty": "어려움"},
]


def get_next_run_time() -> datetime:

    now = datetime.now()

    today_run = now.replace(
        hour=RUN_HOUR,
        minute=RUN_MINUTE,
        second=0,
        microsecond=0
    )

    # 오늘이 평일이고 아직 14시 전이면 오늘 실행
    if now.weekday() in WEEKDAYS and now < today_run:
        return today_run

    # 다음 평일 찾기
    next_day = now + timedelta(days=1)

    while next_day.weekday() not in WEEKDAYS:
        next_day += timedelta(days=1)

    return next_day.replace(
        hour=RUN_HOUR,
        minute=RUN_MINUTE,
        second=0,
        microsecond=0
    )


async def generate_problem(subject: str, difficulty: str = "보통"):

    print(f"[DAILY] {subject} 문제 생성 시작")

    try:

        result = await asyncio.to_thread(
            executable_builder.invoke,
            {
                "user_input": "이하랑",
                "subject_input": subject,
                "difficulty": difficulty
            }
        )

        print(f"[DAILY] {subject} 문제 생성 완료")

        return result

    except Exception as e:

        print(f"[DAILY] {subject} 문제 생성 실패")
        print(e)

        return None


async def run_daily_problems():

    print("=" * 50)
    print("[DAILY] 오늘의 문제 생성 시작")
    print("=" * 50)

    for subject in SUBJECTS:

        await generate_problem(subject["subject"], subject["difficulty"])

    print("=" * 50)
    print("[DAILY] 오늘의 모든 과목 문제 생성 완료")
    print("=" * 50)


async def main():

    print("[DAILY] Daily Problem Worker 시작")

    while True:

        next_run = get_next_run_time()
        now = datetime.now()

        wait_seconds = (next_run - now).total_seconds()

        print(
            f"[DAILY] 다음 실행: "
            f"{next_run.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await asyncio.sleep(wait_seconds)

        await run_daily_problems()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("[DAILY] 종료")