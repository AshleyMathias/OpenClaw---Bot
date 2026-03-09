from workflow_manager.node_adapter import tool_to_tool
from tools.database_tools import database_tools_list
from tools.automation_tools import tools_list


ALL_TOOLS = database_tools_list + tools_list


NODE_REGISTRY = {}

for tool in ALL_TOOLS:

    node = tool_to_tool(tool)

    NODE_REGISTRY[node.__name__] = node