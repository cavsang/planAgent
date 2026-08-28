from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
#app.include_router(problems.router)
templates = Jinja2Templates(directory="templates")

# 임시 저장소 (실서비스는 DB 사용 권장)
problems = {}
answers = {}

# @app.post("/create_problem")
# def create_problem(question_text: str):
#     pid = str(uuid.uuid4())[:8]
#     problems[pid] = question_text
#     return {"url": f"https://yourdomain.com/problem/{pid}"}

@app.get("/problem/{pid}", response_class=HTMLResponse)
def show_problem(request: Request, pid: str):
    #question = problems.get(pid, "문제를 찾을 수 없습니다.")

        return templates.TemplateResponse(
        request=request,
        name="problem.html",
        context={
            "pid": pid,
            "title": "마을 축제 수학 문제",
            "problems": [
                {"id": "1", "text": "문제1"},
                {"id": "2", "text": "문제2"},
            ],
        },
    )

# @app.post("/problem/{pid}/submit")
# async def submit_answer(pid: str, answer: str = Form(...)):
#     answers[pid] = answer
#     # 여기서 채점 에이전트 호출 or DB 저장 가능
#     return {"status": "received", "pid": pid}