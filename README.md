# OpenClaw Enterprise AI Assistant

An enterprise-grade AI chatbot that answers company policy questions, creates support tickets, sends notifications, and handles general conversation. Built with FastAPI, LangGraph, and OpenAI.

![OpenClaw chat interface](assets/chat-screenshot.png)

*OpenClaw answering questions about safety policies and harassment policy from the company knowledge base.*

## Features

- **Intent-based routing** — Classifies queries as CHAT, KNOWLEDGE (policy/docs), or TOOL (tickets, notifications, reports) and routes to the right handler.
- **RAG over company policy** — Retrieves answers from your policy handbook (e.g. leave, safety, conduct, remote work) using a vector store (Chroma).
- **Tool use** — Create support tickets, send notifications, and generate reports via the OpenClaw agent.
- **Conversation memory** — Session-based history so the assistant keeps context within a conversation.
- **Streaming responses** — LLM responses are streamed for a natural feel.

## Project structure

```
├── app/                 # FastAPI app and API routes
├── agents/              # LangGraph agent (tools)
├── config/              # Settings and model config
├── frontend/             # Chat UI (HTML, CSS, JS)
├── llm/                 # OpenAI client and prompts
├── memory/              # Session memory
├── rag/                 # Retriever and vector store (Chroma)
├── tools/               # Automation tools (tickets, notifications, reports)
├── workflows/           # LangGraph flow (intent → chat / RAG / agent)
└── build_vector_store.py  # Script to index company policy into the vector DB
```

## Setup

### 1. Clone and install

```bash
git clone https://github.com/AshleyMathias/OpenClaw---Bot.git
cd OpenClaw---Bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
```

### 3. Index company policy (optional, for RAG)

From the project root:

```bash
python build_vector_store.py
```

Policy source: `rag/knoweldge/company_policy.txt`. Edit that file to change what the assistant can answer from.

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`  
Docs: `http://127.0.0.1:8000/docs`

### 5. Use the chat UI

Open `frontend/index.html` in a browser (or serve it from the same origin). The UI calls:

- `POST /chat?message=...&session_id=...` for sending messages.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Health / welcome |
| GET    | `/health`| Health check |
| POST   | `/chat`  | Send a message; query params: `message`, `session_id`. Returns `{"response": "..."}`. |

## Tech stack

- **Backend:** FastAPI, LangGraph, LangChain, OpenAI
- **RAG:** Chroma (`langchain-chroma`), OpenAI embeddings
- **Frontend:** Vanilla JS, CSS (Inter font, responsive layout)

## License

MIT
