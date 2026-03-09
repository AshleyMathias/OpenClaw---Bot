from __future__ import annotations

import json
import re
from typing import Any

from llm.openai_client import generate_response
from workflow_manager.node_registry import NODE_REGISTRY
from workflow_manager.workflow_builder import build_workflow

MAX_STEPS = 5
MAX_NODE_REPEATS = 2
EMPTY_PLAN: dict[str, list] = {"workflow": []}


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

def plan_workflow(user_request: str) -> dict[str, Any]:
    """Use the LLM to convert a user goal into a sequential workflow plan.

    Returns a dict of the form ``{"workflow": [{"node": "..."}, ...]}``.
    Falls back to an empty plan when the LLM output cannot be parsed.
    """

    available_nodes = ", ".join(sorted(NODE_REGISTRY.keys()))

    prompt = [
        {
            "role": "system",
            "content": (
                "You are a workflow planner AI.\n\n"
                "Your job is to convert a user request into a sequence of workflow nodes.\n\n"
                f"Available nodes: {available_nodes}\n\n"
                "Rules:\n"
                "- Use ONLY the available nodes listed above.\n"
                f"- Maximum {MAX_STEPS} steps.\n"
                "- No loops — each node may appear at most twice.\n"
                "- Return ONLY valid JSON in this exact format (no markdown, no explanation):\n"
                '{"workflow": [{"node": "node_name"}, {"node": "node_name"}]}'
            ),
        },
        {
            "role": "user",
            "content": f"User request: {user_request}",
        },
    ]

    raw = "".join(generate_response(prompt))

    return _parse_plan(raw)


def _parse_plan(raw: str) -> dict[str, Any]:
    """Safely extract a workflow plan dict from raw LLM output."""

    # Strip markdown fences the model sometimes adds
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`")

    try:
        plan = json.loads(cleaned)
    except json.JSONDecodeError:
        return EMPTY_PLAN

    if not isinstance(plan, dict) or "workflow" not in plan:
        return EMPTY_PLAN
    if not isinstance(plan["workflow"], list):
        return EMPTY_PLAN

    return plan


# ---------------------------------------------------------------------------
# Safety validation
# ---------------------------------------------------------------------------

def validate_plan(plan: dict[str, Any]) -> str | None:
    """Validate a workflow plan against safety constraints.

    Returns ``None`` when the plan is valid, or an error message string
    describing the first violated constraint.
    """

    steps = plan.get("workflow", [])

    if not steps:
        return "Plan is empty — no steps to execute."

    if len(steps) > MAX_STEPS:
        return f"Plan exceeds the maximum of {MAX_STEPS} steps ({len(steps)} given)."

    node_counts: dict[str, int] = {}
    for step in steps:
        name = step.get("node", "")

        if name not in NODE_REGISTRY:
            return f"Unknown node '{name}' is not in the registry."

        node_counts[name] = node_counts.get(name, 0) + 1
        if node_counts[name] > MAX_NODE_REPEATS:
            return f"Node '{name}' is repeated more than {MAX_NODE_REPEATS} times."

    return None


# ---------------------------------------------------------------------------
# End-to-end workflow runner
# ---------------------------------------------------------------------------

def run_dynamic_workflow(user_request: str) -> str:
    """Plan, validate, build, and execute a dynamic workflow.

    1. Calls the planner LLM to produce a workflow plan.
    2. Validates the plan against safety constraints.
    3. Builds a LangGraph pipeline via ``build_workflow``.
    4. Invokes the pipeline and returns the final result.
    """

    plan = plan_workflow(user_request)

    error = validate_plan(plan)
    if error:
        return f"Workflow planning failed: {error}"

    try:
        graph = build_workflow(plan)
    except ValueError as exc:
        return f"Workflow build error: {exc}"

    result = graph.invoke({"input": user_request})

    return result.get("result", str(result))
