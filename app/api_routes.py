from fastapi import APIRouter, Body
from requests import session
from workflows.langgraph_flow import app_graph
from fastapi import UploadFile, File
from rag.vector_store import add_documents
from memory.memory_manager import get_message, add_message
import threading

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

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()

    result = add_documents(file.filename, contents)

    return {"message": result}


@router.post("/speak")
def speak_response(text: str = Body(..., embed=True)):
    """
    Speak a text response aloud on the server using pyttsx3.
    Runs in a background thread so the API returns immediately.
    """
    def _speak_in_background(text_to_speak: str):
        try:
            import pyttsx3
            from voice.config import VOICE_RATE, VOICE_VOLUME, VOICE_NAME
            engine = pyttsx3.init()
            engine.setProperty("rate", VOICE_RATE)
            engine.setProperty("volume", VOICE_VOLUME)
            for v in engine.getProperty("voices"):
                if VOICE_NAME.lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.say(text_to_speak)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[Speak] Error: {e}")

    thread = threading.Thread(target=_speak_in_background, args=(text,), daemon=True)
    thread.start()
    return {"status": "speaking"}