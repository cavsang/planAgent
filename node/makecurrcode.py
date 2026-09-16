
from api.getproblems import getAllCurriculmCodes, getCurriculmnInIds, getSubjectInfo, getTermInfo
from db.models import Curriculum
from schema.schema import ProblemGenerationState


def makecurrcode(state:ProblemGenerationState) -> dict:
    "히스토리와 커리큘럼을 가지고 문제를 생성할 코드를 만든다."

    #ex)"4수01-07"
    grade = state.student.grade
    subject_input = state.subject_input
    # 1.term의 term_id를 가져옴
    term = getTermInfo(grade)

    if not term:
        raise  ValueError("Term 조회중 오류")


    # 2.subject로 subject의 subject id를 검색
    subject = getSubjectInfo(subject_input)

    if not subject:
        raise ValueError("Subject 조회중 오류")


    history:list = state.history_problems
    false_history = [h for h in history if h.is_correct == False]

    history_curri_ids = []
    if false_history:
        history_curri_ids = [h.curriculum_id for h in false_history]

        if history_curri_ids:
            hist_curr_list = getCurriculmnInIds(history_curri_ids)

        #1. 틀린부분이 있다면, 틀린 code부터.
        min_code = min(hist_curr_list)

        if min_code:
            return {
                "code": min_code
            }


    #2. 틀린부분이 없으면 전체리스트에서 - 해서 제일첫번째꺼
    all_curr_list = getAllCurriculmCodes(subject['subject_id'], term['term_id'])

    # print("subject : ", subject['subject_id'])
    # print("term : ", term['term_id'])
    # print("all_curr_list : ", all_curr_list)

    if history_curri_ids:
        hist_curr_list = getCurriculmnInIds(history_curri_ids)
        #print(list_curr)
        not_study_list = list(set(all_curr_list) - set(hist_curr_list))
        min_code = min(not_study_list)

        if min_code:
            return {
                "code": min_code
            }

    #3. 리스트를 다하면 처음부터 반복.
    min_code = min(all_curr_list)

    return {
        "code": min_code
    }
    