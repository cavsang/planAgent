
import requests
from api.getproblems import getUsers
from schema.answer_schema import answerState


def send_answer(state:answerState) -> dict:
    """채점이 완료되면 텔레그램으로 결과를 보낸다."""
    pid = state.problem_id
    student_id = state.student_id
    result = state.result

    if(student_id and pid and result =="정상처리되었습니다."):
        student = getUsers(student_id)
            
        url = f"https://api.telegram.org/bot{student["telegram_bot_token"]}/sendMessage"
        payload = {
            "chat_id": student["telegram_chat_id"],
            "text": f"{student["student_name"]} 의 채점결과",
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": " [채점결과] 확인하기", "url": f"http://127.0.0.1:8000/answer/{pid}"}]
                ]
            },
        }
        response = requests.post(url, json=payload, timeout=10)
        #print(response)
        response.raise_for_status()  # 4xx/5xx 응답이면 예외 발생

        return {
            "result": response.json()
        }
    else:
        return {
            result: f"텔레그램 답변 전송중 오류 발생. [pid : {pid}, student_id:{student_id}, result={result}]"
        }
