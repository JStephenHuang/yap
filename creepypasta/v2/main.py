from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict

# Define the state
class State(TypedDict):
    message: str
    steps: list[str]

# Define simple nodes
def start_node(state: State):
    return {"message": "Hello", "steps": ["start"]}

def middle_node(state: State):
    return {"message": state["message"] + " -> Middle", "steps": state["steps"] + ["middle"]}

def end_node(state: State):
    return {"message": state["message"] + " -> End", "steps": state["steps"] + ["end"]}

# Create the workflow
workflow = StateGraph(State)
workflow.add_node(start_node)
workflow.add_node(middle_node)
workflow.add_node(end_node)

workflow.add_edge(START, "start_node")
workflow.add_edge("start_node", "middle_node")
workflow.add_edge("middle_node", "end_node")
workflow.add_edge("end_node", END)

# Set up checkpointing
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)

# Run the graph

config = {"configurable": {"thread_id": "workflow_123"}}

graph.invoke({"message": "", "steps": []}, config=config)

history = list(graph.get_state_history(config))

# History is ordered from most recent to oldest
for i, checkpoint in enumerate(history):
    print(f"Step {i}: {checkpoint.values}")
    print(f"Next: {checkpoint.next}")
    print("---")