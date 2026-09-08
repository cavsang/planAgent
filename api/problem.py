from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from api.getproblems import getProblems, getUsers, setProblems


app = FastAPI()

# ✅ 허용할 origin 목록 - 나중에 배포 도메인 추가/교체만 하면 됨
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    # "https://yourdomain.com",   # 실제 배포 시 여기에 추가
    # "https://www.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
#app.include_router(problems.router)
templates = Jinja2Templates(directory="templates")

@app.get("/problem/{pid}", response_class=HTMLResponse)
def show_problem(request: Request, pid: str):

    problems = getProblems(pid)
    #print(problems)
    student = getUsers(problems['student_id'])

    if not problems or not student:
        raise ValueError(f"Problem {pid} not found")
    
    #question = problems.get(pid, "문제를 찾을 수 없습니다.")

    #print(student)
    return templates.TemplateResponse(
    request=request,
    name="problem.html",
    context={
        "pid": pid,
        "title": "문제풀러고고싱",
        "problems": [
            {"id": pid, "text": problems['problem'], "hint":problems['problem_hint'],"keyword":problems['problem_key_concepts']},
        ],
        "user": student['student_name'], 
        "endpoint": "http://localhost:8000/problem/"+pid+"/submit"
    },
    )


class SubmitAnswerRequest(BaseModel):
    pid: str
    answers: list[dict]
    user: str

@app.post("/problem/{pid}/submit")
async def submit_answer(pid: str, body: SubmitAnswerRequest):
    # answer[pid] = answer
    #print(body)
    result = setProblems(pid, body.answers[0]['answer'], body.user)
    # 여기서 채점 에이전트 호출 or DB 저장 가능
    return {"message": result}