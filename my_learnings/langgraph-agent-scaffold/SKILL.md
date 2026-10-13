---
name: langgraph-agent-scaffold
description: >-
  Scaffolds a new LangGraph StateGraph agent with TypedDict state, node functions,
  graph wiring, and MemorySaver. Use when creating a new AI agent, building a RAG
  system, or setting up a LangGraph state machine.
---

# LangGraph Agent Scaffold Skill

This skill generates the boilerplate for a LangGraph StateGraph agent.
It follows the pattern proven in the bank-faq-agent project.

## Architecture Overview

A LangGraph agent has 4 components:

```
state.py    → The shared whiteboard (TypedDict with keys + reducers)
nodes.py    → The worker functions (read state → do work → write state)
graph.py    → The orchestrator (wires nodes + edges + checkpointer)
retriever.py → The search engine (optional, for RAG agents)
```

## Instructions

### Step 1: Create `state.py`

Define the shared state as a TypedDict. Follow this template:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # APPEND mode (conversation history)
    # Add your custom keys below (OVERWRITE mode by default):
    # question: str
    # documents: list[Document]
    # generation: str
```

**Rules:**
- `messages` MUST use `Annotated[list, add_messages]` for multi-turn memory
- All other keys are OVERWRITE by default (no reducer needed)
- Use type hints on every key

### Step 2: Create `nodes.py`

Each node is a function that takes the full state and returns a partial update:

```python
def my_node(state: AgentState) -> dict:
    """Describe what this node does."""
    # 1. READ from state
    question = state["question"]
    
    # 2. DO the work
    result = some_function(question)
    
    # 3. WRITE to state (only the keys you want to update)
    return {"my_key": result}
```

**Rules:**
- Every node takes `state: AgentState` as its only argument
- Every node returns a `dict` with ONLY the keys it wants to update
- LangGraph handles merging — don't return the full state

### Step 3: Create `graph.py`

Wire nodes into a StateGraph:

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("node_name", node_function)
    
    # Add edges (linear flow)
    builder.add_edge(START, "first_node")
    builder.add_edge("first_node", "second_node")
    builder.add_edge("second_node", END)
    
    # Compile with memory
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
```

**For conditional routing** (non-linear flow):
```python
def route_decision(state: AgentState) -> str:
    """Returns the name of the next node."""
    if state["documents"]:
        return "generate"
    return "fallback"

builder.add_conditional_edges("grade", route_decision)
```

### Step 4: Add Interactive Chat (for testing)

```python
if __name__ == "__main__":
    graph = build_graph()
    config = {"configurable": {"thread_id": "session-1"}}
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        
        result = graph.invoke(
            {"messages": [("human", user_input)], "question": user_input},
            config=config
        )
        print(f"Agent: {result['generation']}")
```

## Examples

See the reference implementation:
- State: `examples/state_example.py`
- Nodes: `examples/nodes_example.py`  
- Graph: `examples/graph_example.py`

## Common Mistakes

| Mistake | Fix |
|---|---|
| Returning full state from node | Return only the keys you changed |
| Missing `add_messages` on messages | Must use `Annotated[list, add_messages]` |
| Forgetting `MemorySaver` | Without it, multi-turn memory doesn't work |
| Same `thread_id` for all users | Each user/session needs a unique thread_id |
| `MemorySaver` in production | Replace with `SqliteSaver` or Redis-backed checkpointer |
