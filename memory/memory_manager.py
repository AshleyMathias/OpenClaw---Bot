session_memory = {}

def get_session_memory(session_id: str):

    if session_id not in session_memory:
        session_memory[session_id] = []
    return session_memory[session_id]

def add_message(session_id: str, role: str, content: str):
    history = get_session_memory(session_id)
    history.append({"role": role, "content": content})


def get_message(session_id:str):
    return session_memory.get(session_id, [])