from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage

from tools.database_tools import database_tools_list
from tools.automation_tools import tools_list
from config.settings import MODEL_NAME, TEMPERATURE

SYSTEM_PROMPT = """You are OpenClaw, an enterprise automation assistant. 

When users ask to:
- Create a support ticket (for laptop issues, software bugs, login problems, etc.) → Use the create_support_ticket tool
- Send a notification or alert → Use the send_notification tool  
- Generate a report → Use the generate_report tool
- Query database information → Use the appropriate database tool

Always use the available tools to perform actions. Do not ask for additional information - use the tools directly with the information provided by the user."""

all_tools = database_tools_list + tools_list

llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
agent = create_react_agent(llm, all_tools)


def run_openclaw_agent(user_input: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    result = agent.invoke({"messages": messages})
    reply_messages = result.get("messages", [])
    if not reply_messages:
        return ""
    return reply_messages[-1].content