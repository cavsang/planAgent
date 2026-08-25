import json

from langgraph.graph import END, START, StateGraph
from node.LoadCurriculumNode import curriculum_node
from node.LoadHistoryNode import loadhistory_node
from node.SelectConceptNode import selectconcept_node
from node.WeaknessNode import weakness_node
from node.confirmProblemNode import confirmProblemNode
from node.makeProblemsNode import makeproblems_node
from schema.schema import ProblemGenerationState
from node.LoadStudentNode import loadStudent_node



builder = StateGraph(ProblemGenerationState)

builder.add_node('student', loadStudent_node)
builder.add_node('curriculum', curriculum_node)
builder.add_node('history', loadhistory_node)
builder.add_node('weakness', weakness_node)
builder.add_node('select_concept', selectconcept_node)  
builder.add_node('make_problems', makeproblems_node)  # 문제 생성기(LLM)에게 문제를 생성하도록 요청
builder.add_node('confirm_problems', confirmProblemNode)

builder.add_edge(START, 'student')
builder.add_edge('student', 'curriculum')
builder.add_edge('curriculum', 'history')
builder.add_edge('history', 'weakness')
builder.add_edge('weakness', 'select_concept')
builder.add_edge('select_concept', 'make_problems')
builder.add_edge('make_problems', 'confirm_problems')
builder.add_edge('confirm_problems', END)



executable_builder = builder.compile()
result= executable_builder.invoke({"user_input": "이하랑", "code": "4수01-14", "difficulty": "매우 어려움"})
#print(json.dumps(result, indent=2, ensure_ascii=False))

