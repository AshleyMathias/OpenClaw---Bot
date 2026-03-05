from typing import TypedDict, List
from langgraph.graph import StateGraph
from llm.openai_client import generate_response
from agents.openclaw_agent import run_openclaw_agent
from rag.retriever import get_retriever


class OpenClawState(TypedDict):
    user_input: str
    intent:str
    response: str
    history: List[dict]


retriever = get_retriever()
def rag_node(state: OpenClawState):
    user_input = state["user_input"]
    history = state["history"]

    messages=[
        {"role": "system", "content": "You are OpenClaw enterprise asssiatnt"}
    ]

    messages.extend(history)

    messages.append({"role": "user", "content": user_input})

    docs = retriever.invoke(user_input)
    context = "\n".join([doc.page_content for doc in docs]).strip()

    if not context:
        return {
            "response": "No relevant documents were found in the knowledge base for your question. The index may need to be rebuilt. Please try rephrasing or contact support."
        }

    prompt = [
        {
            "role": "system",
            "content": "You are OpenClaw. Answer the user's question using ONLY the provided context. Do not say the context does not include information if the answer is in the context. If the context does not contain the answer, say so briefly.",
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {user_input}",
        },
    ]
    response = "".join(generate_response(prompt))
    return {"response": response}

def detect_intent(state: OpenClawState):
    user_input = state["user_input"]
    prompt = [
        {
            "role": "system",
            "content": """
            You classify user intent.

    Return ONLY one word:
    TOOL
    CHAT
    KNOWLEDGE

    Use TOOL when the user asks about company database information like:
    - employees
    - departments
    - salaries
    - counts
    - statistics

    Use KNOWLEDGE for company policies or documentation.

    Use CHAT for normal conversation.

            """,
        },
        {"role": "user", "content": user_input},
    ]
    intent = "".join(generate_response(prompt))
    return {"intent": intent.strip().upper()}


def route_intent(state: OpenClawState):
    user_input = state["user_input"]
    intent = state["intent"]
    # Route to RAG for policy/handbook/leave questions even if model misclassifies
    knowledge_keywords = ("policy", "leave", "handbook", "remote work", "attendance", "conduct", "benefits", "hr ", "company ")
    if any(kw in user_input.lower() for kw in knowledge_keywords):
        return "rag"
    if "TOOL" in intent:
        return "agent"
    if "KNOWLEDGE" in intent:
        return "rag"
    return "chat"


def chat_node(state: OpenClawState):
    user_input = state["user_input"]
    history = state.get("history") or []

    messages = [
        {"role": "system", "content": "You are OpenClaw enterprise assistant"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    response = "".join(generate_response(messages))
    return {"response": response}


def agent_node(state: OpenClawState):

    user_input = state["user_input"]

    result = run_openclaw_agent(user_input)

    return {"response": result}


#Create workflow graph
workflow = StateGraph(OpenClawState)

#Add nodes
workflow.add_node("intent_detection", detect_intent)
workflow.add_node("agent", agent_node)
workflow.add_node("chat", chat_node)
workflow.add_node("rag", rag_node)
#set Entry point
workflow.set_entry_point("intent_detection")
workflow.add_conditional_edges(
    "intent_detection",
    route_intent,
    {
        "agent": "agent",
        "chat": "chat",
        "rag": "rag"
    }
)

workflow.set_finish_point("agent")
workflow.set_finish_point("chat")
workflow.set_finish_point("rag")
#Compile workflow
app_graph = workflow.compile()