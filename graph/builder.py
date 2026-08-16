import json

from langgraph.graph import END, START, StateGraph
from node.LoadCurriculumNode import curriculum_node
from node.LoadHistoryNode import loadhistory_node
from node.SelectConceptNode import selectconcept_node
from node.WeaknessNode import weakness_node
from schema.schema import ProblemGenerationState
from node.LoadStudentNode import loadStudent_node



builder = StateGraph(ProblemGenerationState)

builder.add_node('student', loadStudent_node)
builder.add_node('curriculum', curriculum_node)
builder.add_node('history', loadhistory_node)
builder.add_node('weakness', weakness_node)
builder.add_node('select_concept', selectconcept_node)  # select_concept 노드는 아직 구현되지 않았으므로 None으로 설정

builder.add_edge(START, 'student')
builder.add_edge('student', 'curriculum')
builder.add_edge('curriculum', 'history')
builder.add_edge('history', 'weakness')
builder.add_edge('weakness', 'select_concept')
builder.add_edge('select_concept', END)

executable_builder = builder.compile()
result= executable_builder.invoke({"user_input": "이하랑", "code": "4수01-14"})
#print(json.dumps(result, indent=2, ensure_ascii=False))

