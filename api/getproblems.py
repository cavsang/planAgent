

import uuid

from db.models import Problem
from db.session import get_db
from schema.schema import BaseProblemState


def getProblems(p_id:str) -> BaseProblemState | None:
    with get_db() as db:
        problem = db.get(Problem, p_id)

        #print(problem)

        return BaseProblemState(
            problem = problem.problem,
            problem_hint=problem.problem_hint,
            problem_key_concepts=problem.problem_key_concepts
        )
