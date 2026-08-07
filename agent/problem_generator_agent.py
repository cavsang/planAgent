
from model.llm import get_llm


def problem_generator():
    """기본적으로 Vector검색을 통해 진도를 확인한뒤에,학생의 학습이력,약점등을 확인한후 문제를 생성한다."""
    llm = get_llm()
    pass