# 🤖 WhatsApp AI Agent

> A local AI-powered WhatsApp agent that automatically receives incoming WhatsApp messages, processes them using an AI agent, and replies through WhatsApp using MCP tools.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-orange)](https://www.langchain.com/langgraph)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-black)](https://modelcontextprotocol.io/)
[![Go](https://img.shields.io/badge/Go-1.24+-00ADD8?logo=go&logoColor=white)](https://go.dev/)

---

## 📌 Overview

**WhatsApp AI Agent** is a local, event-driven AI automation project that connects WhatsApp with an AI agent through the **Model Context Protocol (MCP)**.

Instead of continuously polling WhatsApp for new messages, the system receives incoming WhatsApp events and sends them to a Python-based AI workflow. The AI can then decide which MCP tool to use and send the appropriate response back to the exact WhatsApp conversation.

### High-level architecture

```text
                         ┌─────────────────────┐
                         │      WhatsApp       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   WhatsApp Bridge   │
                         │       (Go)          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    WhatsApp MCP     │
                         │       Server        │
                         └──────────┬──────────┘
                                    │ MCP / stdio
                                    ▼
                         ┌─────────────────────┐
                         │     MCP Client      │
                         │      (Python)       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   LangGraph Agent   │
                         │      Workflow       │
                         └──────────┬──────────┘
                                    │
                              AI / Tool Call
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    MCP WhatsApp     │
                         │       Tools         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  WhatsApp Reply     │
                         └─────────────────────┘
```

---

# ✨ Features

- 🤖 **AI-powered WhatsApp conversations**
- ⚡ **Event-driven message processing**
- 🔌 **Model Context Protocol (MCP) integration**
- 🧠 **LangGraph-based agent workflow**
- 🛠️ **Dynamic MCP tool discovery**
- 💬 Replies to the **exact incoming chat**
- 👤 Supports direct chats and group conversations
- 🚫 Ignores messages sent by the agent itself
- 🚫 Ignores WhatsApp broadcast/status events
- 🌐 FastAPI API for receiving WhatsApp events
- ⚙️ Redis Queue (RQ) for background AI processing
- 🐍 Python-based AI agent
- 🦫 Go-based WhatsApp bridge
- 🔒 Designed to keep WhatsApp processing local
- 🪟 Windows launcher for starting the complete system

---

# 🏗️ Project Architecture

The project is divided into several components.

## 1. WhatsApp Bridge

The Go bridge is responsible for maintaining the WhatsApp connection and communicating with WhatsApp.

```text
whatsapp-mcp/
└── whatsapp-bridge/
    └── main.go
```

The bridge handles the WhatsApp-side communication and provides the foundation used by the MCP layer.

---

## 2. WhatsApp MCP Server

The MCP server exposes WhatsApp functionality as tools that can be called by the Python agent.

```text
whatsapp-mcp/
└── whatsapp-mcp-server/
    └── ...
```

Examples of available functionality include:

- Search contacts
- Send messages
- List messages
- List chats
- Get chat information
- Get direct chats
- Get contact chats
- Get last interaction
- Retrieve message context
- Work with supported WhatsApp media

The AI agent does not directly implement WhatsApp communication. Instead, it interacts with WhatsApp through MCP tools.

---

## 3. Python MCP Client

The Python MCP client connects the AI application to the MCP server.

The client discovers the available tools and makes them available to the AI agent.

Conceptually:

```text
Python Agent
     │
     ▼
MCP Client
     │
     ▼
MCP Server
     │
     ▼
WhatsApp Bridge
```

---

## 4. AI Agent

The AI workflow is implemented in Python using LangGraph.

The agent can:

1. Receive the incoming message.
2. Retrieve relevant conversation context.
3. Discover available MCP tools.
4. Provide the tools to the AI model.
5. Let the AI determine whether a tool is required.
6. Execute the selected MCP tool.
7. Generate/send the response.

Simplified workflow:

```text
Incoming Message
       │
       ▼
Retrieve Conversation
       │
       ▼
AI Agent
       │
       ├───────────────┐
       │               │
       ▼               ▼
   No Tool          Tool Required
       │               │
       │               ▼
       │          Execute MCP Tool
       │               │
       └───────┬───────┘
               ▼
          Final Response
               │
               ▼
        WhatsApp Reply
```

---

# 🌐 FastAPI

FastAPI provides the HTTP endpoint used by the WhatsApp event-processing layer.

The main endpoint is:

```text
POST /whatsapp/incoming
```

Example payload:

```json
{
    "sender_name": "Sudhanshu",
    "message_id": "message-id",
    "chat_jid": "123456789@s.whatsapp.net",
    "sender": "123456789@s.whatsapp.net",
    "content": "Hello!",
    "timestamp": 1750000000,
    "is_from_me": false
}
```

The important identifier is `chat_jid`.

The agent uses the incoming `chat_jid` so that the response is sent back to the **same WhatsApp conversation**.

---

# 🚦 Message Filtering

The system intentionally ignores certain events.

### Messages sent by the agent

If:

```text
is_from_me = true
```

the message is ignored.

This prevents the AI from responding to its own messages and creating an infinite response loop.

### WhatsApp status/broadcast events

Events such as:

```text
status@broadcast
```

are ignored because they are not normal user conversations.

Conceptually:

```python
if is_from_me:
    ignore()

if chat_jid == "status@broadcast":
    ignore()

process_message()
```

---

# ⚙️ Background Processing

The project uses **RQ (Redis Queue)** for background processing.

The architecture is:

```text
WhatsApp Event
      │
      ▼
   FastAPI
      │
      ▼
    Queue
      │
      ▼
   RQ Worker
      │
      ▼
  AI Workflow
      │
      ▼
 MCP Tool / Reply
```

This keeps the HTTP event handler separate from potentially slower AI processing.

The worker uses:

```bash
rq worker --worker-class rq.worker.SimpleWorker default
```

---

# 📂 Project Structure

The project is organized approximately as follows:

```text
whatsapp-ai-agent/
│
├── main.pyw
│
├── whatsapp_agent/
│   ├── __init__.py
│   ├── agent_api.py
│   ├── agent_workflow.py
│   ├── ai_agent.py
│   ├── prompt.py
│   ├── state.py
│   └── ...
│
├── MCP_CLIENT/
│   ├── __init__.py
│   ├── mcp_client.py
│   └── ...
│
├── whatsapp-mcp/
│   └── ...
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

> The `whatsapp-mcp` directory is maintained as a Git submodule.

---

# 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | AI application and backend |
| **FastAPI** | HTTP API / event endpoint |
| **LangGraph** | AI agent workflow |
| **MCP** | AI ↔ WhatsApp tool communication |
| **Go** | WhatsApp bridge |
| **RQ** | Background job processing |
| **Redis** | Job queue backend |
| **WhatsApp MCP** | WhatsApp integration |
| **Git** | Version control |

---

# 💻 Requirements

Before running the project, install:

- Windows 10/11
- Python 3.12+
- Go
- Redis
- Git
- GCC/MSYS2 for the Go SQLite dependency
- A WhatsApp account/device for the WhatsApp bridge
- API credentials for the AI model used by your configuration

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone --recurse-submodules https://github.com/Sudhanshu-kumar0110/whatsapp-ai-agent.git
```

Enter the project:

```bash
cd whatsapp-ai-agent
```

If you already cloned the repository without submodules:

```bash
git submodule update --init --recursive
```

---

# 🐍 2. Create a Python Virtual Environment

Create the environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🦫 3. Configure Go / CGO

The WhatsApp bridge uses SQLite through `go-sqlite3`, which requires CGO.

On Windows, make sure GCC is installed and available.

For example, with MSYS2 UCRT64:

```text
C:\msys64\ucrt64\bin
```

Then verify:

```bash
go version
gcc --version
```

Enable CGO:

```powershell
$env:CGO_ENABLED="1"
```

---

# 🔐 4. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key
```

Add any other API credentials required by your selected AI provider.

### Important

Never commit `.env` to GitHub.

Your `.gitignore` should include:

```gitignore
.env
.venv/
__pycache__/
*.pyc
*.db
*.sqlite
messages.db
whatsapp.db
```

---

# ▶️ Running the Project

The project contains multiple services.

## Terminal 1 — WhatsApp Bridge

```bash
cd whatsapp-mcp/whatsapp-bridge
go run main.go
```

The bridge establishes the WhatsApp connection.

If this is the first run, follow the WhatsApp authentication/QR-code process provided by the bridge.

---

## Terminal 2 — MCP Server

Start the MCP server from its directory according to the included MCP server configuration.

For the current setup:

```bash
cd whatsapp-mcp/whatsapp-mcp-server
uv run main.py
```

---

## Terminal 3 — RQ Worker

Start Redis first, then run:

```bash
rq worker --worker-class rq.worker.SimpleWorker default
```

The worker should remain running and listen for queued jobs.

---

## Terminal 4 — FastAPI

From the project root:

```bash
uvicorn whatsapp_agent.agent_api:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 🪟 Automatic Windows Launcher

The project also contains:

```text
main.pyw
```

The launcher is intended to start the required project components automatically in separate Windows consoles.

The overall startup process is:

```text
main.pyw
   │
   ├──► WhatsApp Go Bridge
   │
   ├──► FastAPI / Python Agent
   │
   └──► RQ Worker
```

This allows the project to be started without manually opening and configuring every terminal.

---

# 💬 How a Message Is Processed

Suppose someone sends:

```text
Hello, how are you?
```

The system processes it approximately like this:

```text
WhatsApp
   │
   ▼
WhatsApp Bridge
   │
   ▼
MCP Layer
   │
   ▼
Incoming Event
   │
   ▼
FastAPI
   │
   ▼
RQ Queue
   │
   ▼
RQ Worker
   │
   ▼
Conversation Retrieval
   │
   ▼
LangGraph AI Agent
   │
   ├──► Think / decide
   │
   ├──► Select MCP tool if required
   │
   └──► Generate response
   │
   ▼
MCP send_message
   │
   ▼
Same chat_jid
   │
   ▼
WhatsApp
```

---

# 🔧 MCP Tool Calling

One of the main goals of the project is to allow the AI agent to work with WhatsApp through MCP tools.

The Python application discovers the tools exposed by the MCP server and converts them into a format usable by the AI model.

For example:

```text
AI Agent
   │
   │ decides it needs a WhatsApp operation
   ▼
MCP Tool
   │
   ▼
send_message
   │
   ▼
WhatsApp
```

This makes the AI layer independent from the low-level WhatsApp implementation.

---

# 🧠 Agent Design

The project follows an agentic architecture instead of hard-coding every possible conversation path.

The AI can determine whether it needs to:

- Respond directly
- Retrieve conversation information
- Search WhatsApp data
- Retrieve messages
- Use another available MCP capability
- Send a WhatsApp message through the MCP layer

The available tools are supplied to the model dynamically.

This makes it possible to expand the agent by adding additional MCP tools without rebuilding the complete AI workflow.

---

# 🔒 Security & Privacy

This project is designed around local processing of the WhatsApp integration.

However, **local execution does not mean that every piece of data necessarily remains on the computer**.

For example, if an external AI API is configured, the relevant prompt/message data sent to that API is subject to that provider's policies.

### Recommended security practices

- Never commit `.env`
- Never commit WhatsApp databases
- Never expose FastAPI publicly unless authentication and appropriate security controls are configured
- Keep Redis inaccessible from untrusted networks
- Keep the WhatsApp session/database files private
- Use environment variables for API keys
- Do not share WhatsApp authentication/session files
- Keep dependencies updated

---

# 🧪 Development

Run FastAPI during development with:

```bash
uvicorn whatsapp_agent.agent_api:app --reload
```

You can test the incoming endpoint using a JSON request:

```json
{
    "sender_name": "Test User",
    "message_id": "test-001",
    "chat_jid": "123456789@s.whatsapp.net",
    "sender": "123456789@s.whatsapp.net",
    "content": "Hello AI",
    "timestamp": 1750000000,
    "is_from_me": false
}
```

---

# 🐛 Troubleshooting

## `No module named rq.__main__`

Do not start RQ using:

```bash
python -m rq
```

Use:

```bash
rq worker --worker-class rq.worker.SimpleWorker default
```

---

## Go SQLite / CGO errors

Verify:

```bash
gcc --version
```

and:

```powershell
$env:CGO_ENABLED="1"
```

Make sure the MSYS2 UCRT64 GCC directory is available in `PATH`.

---

## MCP tool argument errors

MCP tools with JSON schemas should receive structured arguments.

For example:

```python
await tool.ainvoke({
    "jid": "123456789@s.whatsapp.net"
})
```

rather than passing a raw string.

---

## Agent responds to itself

Check that incoming events with:

```text
is_from_me = true
```

are ignored.

This is important to prevent an automated reply loop.

---

## Bot processes status events

Make sure:

```text
status@broadcast
```

is filtered before the AI workflow is triggered.

---

# 🎯 Project Goals

The project is built to explore the combination of:

```text
WhatsApp
   +
MCP
   +
LLM
   +
LangGraph
   +
FastAPI
   +
RQ
   =
Agentic WhatsApp Automation
```

The primary objective is to create an AI agent that can interact with WhatsApp through a structured tool interface rather than tightly coupling the AI logic to the WhatsApp implementation.

---

# 👨‍💻 Author

**Sudhanshu Kumar**

BCA Student | AI & Agentic AI Developer

### Interests

- Generative AI
- Agentic AI
- AI Agents
- Python
- FastAPI
- LangGraph
- MCP
- Backend Development
- Software Engineering

---

## ⭐ Contributing

Contributions, suggestions, and improvements are welcome.

If you find a bug or have an idea for improving the project, feel free to open an issue or submit a pull request.

---

## ⚠️ Disclaimer

This project is intended for educational, development, and personal automation purposes.

Users are responsible for complying with WhatsApp's terms, applicable laws, and the policies of any third-party AI/API services they use.