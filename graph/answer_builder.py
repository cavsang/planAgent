from langgraph.graph import END, START, StateGraph


from answer.node.check_answer import check_answer
from answer.node.problem_answer import problem_answer
from schema.answer_schema import answerState

answer_builder = StateGraph(answerState)

answer_builder.add_node("problem_answer", problem_answer)
answer_builder.add_node("check_answer"  , check_answer)

answer_builder.add_edge(START, "problem_answer")
answer_builder.add_edge("problem_answer", "check_answer")
answer_builder.add_edge("check_answer", END)


answer_executable = answer_builder.compile()
result = answer_executable.invoke({
        "problem_id": "c82aecdf-5f3f-4d6c-9a76-59552c7e299f"
})
print(result)