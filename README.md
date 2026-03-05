<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1d24;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8f9fa;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        h1 {
            color: #1a1d24;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .tagline {
            color: #5c6370;
            font-size: 1.1em;
            margin-bottom: 30px;
            font-weight: 400;
        }
        .screenshot {
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
            margin: 30px 0;
            border: 1px solid #e4e6eb;
        }
        .caption {
            text-align: center;
            color: #5c6370;
            font-size: 0.9em;
            margin-top: -20px;
            margin-bottom: 40px;
            font-style: italic;
        }
        h2 {
            color: #1a1d24;
            font-size: 1.8em;
            margin-top: 50px;
            margin-bottom: 20px;
            font-weight: 600;
            border-bottom: 2px solid #0d6efd;
            padding-bottom: 10px;
        }
        h3 {
            color: #1a1d24;
            font-size: 1.3em;
            margin-top: 30px;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #0d6efd;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .feature-card strong {
            color: #0d6efd;
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        code {
            background: #f1f3f5;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e83e8c;
        }
        pre {
            background: #1a1d24;
            color: #e9ecef;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border: 1px solid #2d3339;
        }
        pre code {
            background: transparent;
            color: #e9ecef;
            padding: 0;
        }
        .badge {
            display: inline-block;
            background: #0d6efd;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .badge-new {
            background: #28a745;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        th {
            background: #1a1d24;
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e4e6eb;
        }
        tr:last-child td {
            border-bottom: none;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .highlight {
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 4px;
        }
        ul, ol {
            margin: 15px 0;
            padding-left: 25px;
        }
        li {
            margin: 8px 0;
        }
        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        a {
            color: #0d6efd;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #e4e6eb, transparent);
            margin: 40px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 OpenClaw Enterprise AI Assistant</h1>
        <p class="tagline">An enterprise-grade AI chatbot that answers company policy questions, creates support tickets, sends notifications, and handles general conversation. Built with FastAPI, LangGraph, and OpenAI.</p>

        <img src="assets/chat-screenshot.png" alt="OpenClaw chat interface with file upload feature" class="screenshot">
        <p class="caption">OpenClaw answering questions about safety policies and harassment policy from the company knowledge base. Now with document upload support for RAG!</p>

        <h2>✨ Features</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <strong>📤 Document Upload</strong>
                <span class="badge badge-new">NEW</span>
                Upload documents (TXT, PDF, DOCX) directly through the UI to enhance the RAG knowledge base. Documents are automatically indexed and made searchable.
            </div>
            <div class="feature-card">
                <strong>🧠 Intent-based Routing</strong>
                Classifies queries as CHAT, KNOWLEDGE (policy/docs), or TOOL (tickets, notifications, reports) and routes to the right handler.
            </div>
            <div class="feature-card">
                <strong>🔍 RAG over Company Policy</strong>
                Retrieves answers from your policy handbook (e.g. leave, safety, conduct, remote work) using a vector store (Chroma).
            </div>
            <div class="feature-card">
                <strong>🛠️ Tool Use</strong>
                Create support tickets, send notifications, and generate reports via the OpenClaw agent.
            </div>
            <div class="feature-card">
                <strong>💬 Conversation Memory</strong>
                Session-based history so the assistant keeps context within a conversation.
            </div>
            <div class="feature-card">
                <strong>⚡ Streaming Responses</strong>
                LLM responses are streamed for a natural, real-time feel.
            </div>
        </div>

        <h2>📁 Project Structure</h2>
        <pre><code>├── app/                 # FastAPI app and API routes
├── agents/              # LangGraph agent (tools)
├── config/              # Settings and model config
├── frontend/            # Chat UI (HTML, CSS, JS)
├── llm/                 # OpenAI client and prompts
├── memory/              # Session memory
├── rag/                 # Retriever and vector store (Chroma)
├── tools/               # Automation tools (tickets, notifications, reports)
├── workflows/           # LangGraph flow (intent → chat / RAG / agent)
└── build_vector_store.py  # Script to index company policy into the vector DB</code></pre>

        <h2>🚀 Setup</h2>

        <h3>1. Clone and Install</h3>
        <pre><code>git clone https://github.com/AshleyMathias/OpenClaw---Bot.git
cd OpenClaw---Bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt</code></pre>

        <h3>2. Environment Configuration</h3>
        <p>Create a <code>.env</code> file in the project root:</p>
        <pre><code>OPENAI_API_KEY=your_openai_api_key</code></pre>

        <h3>3. Index Company Policy (Optional, for RAG)</h3>
        <p>You can either:</p>
        <ul>
            <li><strong>Use the build script:</strong> Run <code>python build_vector_store.py</code> to index files from <code>rag/knoweldge/company_policy.txt</code></li>
            <li><strong>Upload via UI:</strong> Use the new document upload feature in the web interface to add documents directly!</li>
        </ul>

        <h3>4. Run the API</h3>
        <pre><code>uvicorn app.main:app --reload</code></pre>
        <p>
            <strong>API:</strong> <a href="http://127.0.0.1:8000">http://127.0.0.1:8000</a><br>
            <strong>Docs:</strong> <a href="http://127.0.0.1:8000/docs">http://127.0.0.1:8000/docs</a>
        </p>

        <h3>5. Use the Chat UI</h3>
        <p>Open <code>frontend/index.html</code> in a browser (or serve it from the same origin). The UI provides:</p>
        <ul>
            <li>Interactive chat interface with real-time responses</li>
            <li>Document upload button for adding files to the knowledge base</li>
            <li>Support for TXT, PDF, and DOCX file formats</li>
            <li>Session-based conversation history</li>
        </ul>

        <div class="divider"></div>

        <h2>🔌 API Endpoints</h2>
        <table>
            <thead>
                <tr>
                    <th>Method</th>
                    <th>Endpoint</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>GET</code></td>
                    <td><code>/</code></td>
                    <td>Health / welcome message</td>
                </tr>
                <tr>
                    <td><code>GET</code></td>
                    <td><code>/health</code></td>
                    <td>Health check endpoint</td>
                </tr>
                <tr>
                    <td><code>POST</code></td>
                    <td><code>/chat</code></td>
                    <td>Send a message. Query params: <code>message</code>, <code>session_id</code>. Returns <code>{"response": "..."}</code></td>
                </tr>
                <tr>
                    <td><code>POST</code></td>
                    <td><code>/upload</code></td>
                    <td><span class="badge badge-new">NEW</span> Upload a document file. Accepts <code>file</code> (multipart/form-data). Supports TXT, PDF, DOCX. Returns <code>{"message": "..."}</code></td>
                </tr>
            </tbody>
        </table>

        <h2>🛠️ Tech Stack</h2>
        <div class="tech-stack">
            <span class="badge">FastAPI</span>
            <span class="badge">LangGraph</span>
            <span class="badge">LangChain</span>
            <span class="badge">OpenAI</span>
            <span class="badge">Chroma</span>
            <span class="badge">Vanilla JS</span>
            <span class="badge">CSS3</span>
        </div>
        <ul>
            <li><strong>Backend:</strong> FastAPI, LangGraph, LangChain, OpenAI</li>
            <li><strong>RAG:</strong> Chroma (<code>langchain-chroma</code>), OpenAI embeddings</li>
            <li><strong>Frontend:</strong> Vanilla JS, CSS (Inter font, responsive layout)</li>
        </ul>

        <div class="divider"></div>

        <h2>📝 Usage Examples</h2>
        <h3>Chat Example</h3>
        <pre><code>POST /chat?message=What is our leave policy?&session_id=user_123</code></pre>

        <h3>Upload Document Example</h3>
        <pre><code>POST /upload
Content-Type: multipart/form-data

file: [your-document.pdf]</code></pre>

        <p class="highlight">💡 <strong>Tip:</strong> Upload company policies, documentation, or any text-based documents to instantly enhance OpenClaw's knowledge base!</p>

        <div class="divider"></div>

        <p style="text-align: center; color: #5c6370; margin-top: 40px;">
            <strong>License:</strong> MIT<br>
            Built with ❤️ for enterprise AI assistance
        </p>
    </div>
</body>
</html>
