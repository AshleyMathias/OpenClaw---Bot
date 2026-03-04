from fastapi import APIRouter
from requests import session
from workflows.langgraph_flow import app_graph
from memory.memory_manager import get_message, add_message

router = APIRouter()

@router.post("/chat")
def chat(message: str, session_id: str):
    
    history = get_message(session_id)

    result = app_graph.invoke({
        "user_input": message,
        "history": history
    })

    response = result["response"]

    add_message(session_id, "user", message)
    add_message(session_id, "assistant", response)

    return {"response": response}
