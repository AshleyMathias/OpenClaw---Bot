from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage

from tools.automation_tools import tools_list
from config.settings import MODEL_NAME, TEMPERATURE

SYSTEM_PROMPT = "You are OpenClaw, an enterprise automation assistant. Use tools when necessary."

llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)
agent = create_react_agent(llm, tools_list)


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