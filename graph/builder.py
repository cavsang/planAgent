from langgraph.graph import END, START, StateGraph
from schema.schema import ProblemGenerationState
from node.LoadStudentNode import loadStudent_node



builder = StateGraph(ProblemGenerationState)

builder.add_node('student', loadStudent_node)

builder.add_edge(START, 'student')
builder.add_edge('student', END)

executable_builder = builder.compile()
result= executable_builder.invoke({"user_input": "이하랑"})
print(result)

