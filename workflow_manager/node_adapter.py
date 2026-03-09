def tool_to_tool(tool):

    tool_name = tool.name

    def node(state):


        # get tool is required
        tool_input = state.get("input", {})

        try:
            result = tool.invoke(tool_input)
        except Exception as e:
            result = f"Error: {str(e)}"

        return{
            "result": result,
        }

    node.__name__ = f"{tool_name}_node"

    return node