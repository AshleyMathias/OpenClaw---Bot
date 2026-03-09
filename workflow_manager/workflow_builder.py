from langgraph.graph import StateGraph
from workflow_manager.node_registry import NODE_REGISTRY


def build_workflow(plan):

    workflow = StateGraph(dict)

    steps = plan["workflow"]

    previous = None

    for step in steps:

        node_name = step["node"]

        node_function = NODE_REGISTRY.get(node_name)

        if not node_function:
            raise ValueError(f"Unknown node: {node_name}")

        workflow.add_node(node_name, node_function)

        if previous:
            workflow.add_edge(previous, node_name)

        previous = node_name

    workflow.set_entry_point(steps[0]["node"])
    workflow.set_finish_point(steps[-1]["node"])

    return workflow.compile()