---
name: gemini-native-agent-scaffold
description: Scaffolds a 100% Google Cloud Native Agent using Gemini 1.5 Flash Function Calling, Multi-Turn Chat Sessions, and Deterministic Python Tools. Zero third-party frameworks.
---

# Gemini Native Agent Scaffold Skill

This skill documents how to build a production-grade, multi-turn AI Agent using **only Google Native services** (`google-genai` / Vertex AI) without third-party frameworks like LangChain or LangGraph.

## Core Concepts

1. **Native Tool Binding**: Tools are defined using `google.genai.types.FunctionDeclaration` and wrapped in `types.Tool`.
2. **Session Persistence**: Multi-turn conversational memory is managed natively via `client.chats.create()`, indexed by `session_id`.
3. **ReAct Loop Execution**:
   - Agent inspects user query.
   - If a tool is needed, Gemini returns structured `function_calls`.
   - Your gateway executes the local Python tool.
   - The tool output is fed back via `types.Part.from_function_response()`.
   - Gemini synthesizes the final grounded answer.

## Python Implementation Pattern

```python
from google import genai
from google.genai import types

# 1. Initialize Native Client
client = genai.Client(vertexai=True, project="my-project", location="asia-south1")

# 2. Declare Deterministic Tools
calculator_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="calculate_loan_emi",
            description="Calculates exact monthly EMI and total interest for a bank loan.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "principal": types.Schema(type="NUMBER", description="Loan principal amount in INR"),
                    "annual_rate_pct": types.Schema(type="NUMBER", description="Annual interest rate percentage"),
                    "tenure_years": types.Schema(type="INTEGER", description="Loan tenure in years")
                },
                required=["principal", "annual_rate_pct", "tenure_years"]
            )
        )
    ]
)

# 3. Create Multi-Turn Chat Session
chat = client.chats.create(
    model="gemini-1.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are an enterprise underwriting copilot. Always invoke tools for calculations.",
        tools=[calculator_tool],
        temperature=0.1
    )
)

# 4. Multi-Turn Execution & Tool Feedback
response = chat.send_message("What is the EMI for 50 Lakhs at 8.5% for 15 years?")

if response.function_calls:
    call = response.function_calls[0]
    # Execute deterministic local Python math
    tool_result = calculate_loan_emi(**call.args)
    
    # Send Observation back to Gemini
    final_response = chat.send_message(
        types.Part.from_function_response(
            name=call.name,
            response={"result": tool_result}
        )
    )
    print(final_response.text)
else:
    print(response.text)
```
