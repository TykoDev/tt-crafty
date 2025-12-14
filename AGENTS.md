# AGENTS.md: AI Bot Architecture & Development Standards (v2025.12)

## 1. Executive Summary & Foundational Mandate
This document defines the technical standards for building production-grade AI Agents. All development must adhere to the **Event-Driven LangGraph (EDLG)** architecture to ensure scalability, reliability, and security.

### Core Technology Stack (Strict Version Pinning)
| Component | Technology | Version Requirement (Dec 2025) | Justification |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | `3.12+` | Asyncio native performance & typing enhancements. |
| **Orchestration** | LangGraph | `1.0+` | Mandatory for stateful, multi-agent control flows & cyclic graphs. |
| **API Interface** | FastAPI | `~0.124.x` | High-concurrency async I/O & automatic OpenAPI generation. |
| **Validation** | Pydantic | `V2+` | Strict runtime data validation & schema enforcement. |
| **Package Mgr** | uv | Latest Stable | High-speed dependency resolution & locking. |

---

## 2. Architectural Patterns

### 2.1 Event-Driven Architecture (EDA)
Bots must be designed as loosely coupled services. Do not couple the Bot logic directly to the transport layer (e.g., HTTP request/response cycle).
*   **Pattern:** Ingress (FastAPI/Webhooks) -> Message Bus (Kafka/Redpanda) -> Agent Worker (LangGraph).
*   **Benefit:** Allows elastic scaling of AI inference workers independent of web traffic peaks.

### 2.2 Asynchronous I/O Mandate
All I/O-bound operations (LLM calls, DB queries, API requests) must be `async`. Blocking synchronous code is strictly prohibited in the main execution loop.
*   **Correct:** `await client.chat.completions.create(...)`
*   **Incorrect:** `client.chat.completions.create(...)`

### 2.3 State Management (Finite State Machine)
Agents must use a Component-Based Finite State Machine (FSM) model.
*   **State Schema:** Define all state variables using Pydantic models.
*   **Hygiene:** Explicitly clear large data structures (e.g., RAG context) from the shared graph state upon exiting a node to prevent context window bloat.

---

## 3. Implementation Guidelines & Code Examples

### 3.1 Project Setup with `uv`
Use `uv` for reproducible environment management.
```bash
# Initialize project
mkdir my-bot && cd my-bot
uv init .

# Add core dependencies
uv add fastapi uvicorn langgraph pydantic langchain-openai

# Lock environment for CI/CD
uv pip freeze > requirements.txt
```

### 3.2 State Definition (Pydantic + LangGraph)
Define the agent's state explicitly. This enforces type safety across graph nodes.

```python
from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator

# 1. Define the internal state
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    context_data: str
    current_step: str

# 2. Define Structured Output Models (Pydantic V2)
class IntentAnalysis(BaseModel):
    intent: str = Field(..., description="The user's primary intent")
    confidence: float
    requires_human_handoff: bool
```

### 3.3 The Agent Node (LangGraph 1.0 Pattern)
Nodes must allow for **Human-in-the-Loop (HITL)** interaction and handle errors gracefully.

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

async def reasoning_node(state: AgentState):
    """Core reasoning node utilizing Chain of Thought."""
    messages = state["messages"]
    
    # SECURITY: System prompt must constrain model behavior
    system_prompt = SystemMessage(
        content="You are a helpful assistant. You must refuse to execute SQL."
    )
    
    # Async LLM call
    try:
        response = await llm.ainvoke([system_prompt] + messages)
        return {"messages": [response]}
    except Exception as e:
        # TIER 2 Error Handling: Return graceful fallback
        return {"messages": ["I encountered a temporary issue. Please try again."]}

# Define Graph
workflow = StateGraph(AgentState)
workflow.add_node("reasoning", reasoning_node)
workflow.set_entry_point("reasoning")
workflow.add_edge("reasoning", END)

# Compile with checkpointing for persistence
app = workflow.compile()
```

### 3.4 Secure Tool Execution (OWASP LLM06 Mitigation)
Tools must verify permissions and use "Least Privilege". Never pass raw API keys to the model.

```python
async def sensitive_tool(user_id: str):
    # SECURITY: Authentication Check
    if not verify_user_access(user_id, "execute_tool"):
        raise PermissionError("User not authorized")
        
    # Execute logic...
    return "Action Completed"
```

---

## 4. Security & Compliance (OWASP LLM 2025)

| Risk | Mitigation Strategy |
| :--- | :--- |
| **LLM01: Prompt Injection** | Use "Model Armor" pattern. Separate system prompts from user input. Validate outputs against strict schemas. |
| **LLM02: Sensitive Info** | Implement PII redaction (e.g., Presidio) on input/output streams. Do not log raw prompts containing PII. |
| **LLM06: Excessive Agency** | Tools must handle authentication invisibly to the agent. Use tokens, not keys, within the execution context. |

---

## 5. Testing & LLMOps

### 5.1 Evaluation Framework
*   **RAGAS:** Mandatory for evaluating RAG pipelines (Faithfulness, Answer Relevance).
*   **LangSmith:** Required for tracing execution steps and debugging complex agent loops.

### 5.2 CI/CD Pipeline
*   **Build Once:** Promote the same Docker artifact from Dev -> Staging -> Prod.
*   **Regression Testing:** CI pipelines must run a subset of "Golden Prompts" using `pytest` and `DeepEval` to ensure prompt changes do not degrade performance.
