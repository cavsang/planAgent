
import os
import requests
from dotenv import load_dotenv

from schema.schema import ProblemGenerationState

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

def sendProblems(state: ProblemGenerationState) -> dict:
    "문제를 telegram을 통해서 링크를 보낸다."
    pid = state.p_id

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{state.student.name} 의 {state.subject.subject_name} 문제",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🚀 문제 풀러가기", "url": f"http://127.0.0.1:5000/problem/{pid}"}]
            ]
        },
    }
    response = requests.post(url, json=payload, timeout=10)
    print(response)
    response.raise_for_status()  # 4xx/5xx 응답이면 예외 발생
    return response.json()