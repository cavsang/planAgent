

from api.getproblems import getCurriculmnInIds
from db.models import Curriculum
from schema.schema import ProblemGenerationState


def makecurrcode(state:ProblemGenerationState) ->dict:
    "히스토리와 커리큘럼을 가지고 문제를 생성할 코드를 만든다."


    ##TODO: 
    # 1.student의 grade로 Term을 검색
    # 2.subject로 subject의 subject id를 검색

    history:list = state.history_problems

    if history:
        history_curri_ids = [h['curriculum_id'] for h in history]

    if history_curri_ids:
        list_curr = getCurriculmnInIds(history_curri_ids)
        if(list_curr):
            list_curr.sort(lambda x: x['code'])


    