import asyncio
import os

from dotenv import load_dotenv
from supabase import AsyncClient, acreate_client, create_client, Client
from graph.answer_builder import answer_executable

#from graph.grading_graph import grading_graph

load_dotenv()


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

async def process_answer(answer_id: str):

    print(f"[WORKER] 채점 시작: {answer_id}")

    try:
        # 이미 다른 Worker가 처리 중인지 확인하는 등의
        # 방어 로직을 여기에 넣을 수 있음

        result = await answer_executable.ainvoke({
            "problem_id": answer_id
        })

        print(f"[WORKER] 채점 완료: {answer_id}")

        # 필요하면 여기서 결과 DB 저장
        #
        # supabase.table("student_answers").update({
        #     "status": "GRADED",
        #     "score": result["score"]
        # }).eq("id", answer_id).execute()

    except Exception as e:

        print(f"[WORKER] 채점 실패: {answer_id}")
        print(e)

        # 실패 상태 저장
        #
        # supabase.table("student_answers").update({
        #     "status": "ERROR"
        # }).eq("id", answer_id).execute()


def on_answer_updated(payload):
    #print(f"[DEBUG] RAW PAYLOAD: {payload}")
    data = payload["data"]
    new_data = data["record"]
    old_data = data.get("old_record", {})

    old_status = old_data.get("status")
    new_status = new_data.get("status")

    print(
        f"[WORKER] DB 변경: "
        f"{old_status} -> {new_status}"
    )

    # WAITING → SUBMITTED 같은 경우만 처리
    if old_status != "SUBMITTED" and new_status == "SUBMITTED":

        answer_id = new_data["problem_id"]

        print(f"[WORKER] 제출 감지: {answer_id}")

        # 비동기로 LangGraph 실행
        asyncio.create_task(
            process_answer(answer_id)
        )


def on_subscribe(status, err):
    print(f"[WORKER] Realtime 상태: {status}")
    if err:
        print(f"[WORKER] Realtime 오류: {err}")

async def main():

    
    supabase: AsyncClient = await acreate_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    print("[WORKER] Grading Worker 시작")
    channel = supabase.channel(
        "grading-worker"
    )

    channel.on_postgres_changes(
        event="UPDATE",
        schema="public",
        table="problem",
        callback=on_answer_updated
    )

    await channel.subscribe(on_subscribe)
    print("[WORKER] Supabase Realtime 연결 완료")
    print("[WORKER] DB 변경을 기다리는 중...")
    # 프로그램이 종료되지 않도록 대기
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[WORKER] 종료")