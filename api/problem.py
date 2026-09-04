from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.templating import Jinja2Templates
from api.getproblems import getProblems


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
#app.include_router(problems.router)
templates = Jinja2Templates(directory="templates")

# 임시 저장소 (실서비스는 DB 사용 권장)
# problems = {}
# answers = {}

# @app.post("/create_problem")
# def create_problem(question_text: str):
#     pid = str(uuid.uuid4())[:8]
#     problems[pid] = question_text
#     return {"url": f"https://yourdomain.com/problem/{pid}"}

@app.get("/problem/{pid}", response_class=HTMLResponse)
def show_problem(request: Request, pid: str):

    problems = getProblems(pid)

    if not problems:
        raise ValueError(f"Problem {pid} not found")
    
    #question = problems.get(pid, "문제를 찾을 수 없습니다.")

    return templates.TemplateResponse(
    request=request,
    name="problem.html",
    context={
        "pid": pid,
        "title": "문제풀러고고싱",
        "problems": [
            {"id": pid, "text": problems.problem, "hint":problems.problem_hint, "keyword":problems.problem_key_concepts},
        ],
    },
    )

# @app.post("/problem/{pid}/submit")
# async def submit_answer(pid: str, answer: str = Form(...)):
#     answers[pid] = answer
#     # 여기서 채점 에이전트 호출 or DB 저장 가능
#     return {"status": "received", "pid": pid}