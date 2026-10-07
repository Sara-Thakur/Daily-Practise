# python
from typing import TypedDict
from langgraph.graph import END,StateGraph

class State(TypedDict):
    number: int

# Initialize the graph with the state
builder = StateGraph(State)

# 2. Defining Nodes:
# Nodes are Python functions that receive the current state and return an update for the "shared whiteboard."
# python
def double(state: State)-> dict:
    new_number = state['number'] * 2
    print(f"In double: {new_number}")
    return {"number": new_number}

def finish(state: State):
    print(f"In finish: {state['number']}")
    return {"number": state['number']}

# 3. Logic and Graph Construction:
# A helper function performs decision-making to route the flow (19:16).
# python
def decision(state: State)-> str:
    return "double" if state['number'] < 100 else "finish"

# Adding nodes
builder.add_node("double", double)
builder.add_node("finish", finish)

# Setting entry point and conditional edges
builder.set_entry_point("double")
builder.add_conditional_edges("double", decision, {"double": "double", "finish": "finish"})
builder.add_edge("finish", END)

# Compile and Run
graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"number": 5})




