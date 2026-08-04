

from langgraph.graph import StateGraph

from schema.schema import AgentState


builder = StateGraph(AgentState)

builder.compile()