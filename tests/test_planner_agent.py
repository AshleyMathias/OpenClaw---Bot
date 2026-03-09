"""
Comprehensive tests for the Planner Agent module.

Covers every code path in:
  - _parse_plan        (JSON parsing / fallback)
  - validate_plan      (safety constraints)
  - plan_workflow      (LLM → plan dict)
  - build_workflow     (plan → compiled LangGraph)
  - run_dynamic_workflow  (end-to-end orchestration)
  - NODE_REGISTRY sanity checks
"""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from workflow_manager.planner_agent import (
    _parse_plan,
    validate_plan,
    plan_workflow,
    run_dynamic_workflow,
    EMPTY_PLAN,
    MAX_STEPS,
    MAX_NODE_REPEATS,
)
from workflow_manager.workflow_builder import build_workflow
from workflow_manager.node_registry import NODE_REGISTRY


# ---------------------------------------------------------------------------
# Helpers — fake node functions for mocked registries
# ---------------------------------------------------------------------------

def _fake_node(state):
    return {"result": "ok"}


def _make_mock_registry(*names: str) -> dict:
    fns = {}
    for name in names:
        def fn(state, _name=name):
            return {"result": f"{_name} executed"}
        fn.__name__ = name
        fns[name] = fn
    return fns


MOCK_NODES = _make_mock_registry(
    "node_a", "node_b", "node_c", "node_d", "node_e", "node_f",
)


# ===================================================================
# 1. _parse_plan  —  pure JSON parsing, no mocking required
# ===================================================================

class TestParsePlan:

    def test_valid_json(self):
        raw = '{"workflow": [{"node": "a"}]}'
        assert _parse_plan(raw) == {"workflow": [{"node": "a"}]}

    def test_multi_step_json(self):
        raw = json.dumps({"workflow": [{"node": "a"}, {"node": "b"}]})
        result = _parse_plan(raw)
        assert len(result["workflow"]) == 2

    def test_json_in_json_fences(self):
        raw = '```json\n{"workflow": [{"node": "x"}]}\n```'
        assert _parse_plan(raw) == {"workflow": [{"node": "x"}]}

    def test_json_in_plain_fences(self):
        raw = '```\n{"workflow": [{"node": "x"}]}\n```'
        assert _parse_plan(raw) == {"workflow": [{"node": "x"}]}

    def test_invalid_json_returns_empty(self):
        assert _parse_plan("this is not json at all") == EMPTY_PLAN

    def test_empty_string_returns_empty(self):
        assert _parse_plan("") == EMPTY_PLAN

    def test_missing_workflow_key(self):
        raw = '{"steps": [{"node": "a"}]}'
        assert _parse_plan(raw) == EMPTY_PLAN

    def test_workflow_not_a_list(self):
        raw = '{"workflow": "not-a-list"}'
        assert _parse_plan(raw) == EMPTY_PLAN

    def test_extra_keys_preserved(self):
        raw = '{"workflow": [{"node": "a"}], "meta": "info"}'
        result = _parse_plan(raw)
        assert result["workflow"] == [{"node": "a"}]
        assert result["meta"] == "info"

    def test_trailing_backtick_stripped(self):
        raw = '`{"workflow": [{"node": "a"}]}`'
        assert _parse_plan(raw) == {"workflow": [{"node": "a"}]}


# ===================================================================
# 2. validate_plan  —  safety constraint checks
# ===================================================================

class TestValidatePlan:

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_valid_single_step(self):
        plan = {"workflow": [{"node": "node_a"}]}
        assert validate_plan(plan) is None

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_valid_max_steps_boundary(self):
        """Exactly MAX_STEPS (5) steps should pass."""
        plan = {"workflow": [{"node": f"node_{c}"} for c in "abcde"]}
        assert len(plan["workflow"]) == MAX_STEPS
        assert validate_plan(plan) is None

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_empty_workflow_list(self):
        plan = {"workflow": []}
        err = validate_plan(plan)
        assert err is not None
        assert "empty" in err.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_missing_workflow_key(self):
        plan = {"steps": [{"node": "node_a"}]}
        err = validate_plan(plan)
        assert err is not None
        assert "empty" in err.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_too_many_steps(self):
        plan = {"workflow": [{"node": "node_a"}] * 6}
        err = validate_plan(plan)
        assert err is not None
        assert "exceeds" in err.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_unknown_node(self):
        plan = {"workflow": [{"node": "nonexistent_node"}]}
        err = validate_plan(plan)
        assert err is not None
        assert "unknown" in err.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_two_repeats_allowed(self):
        """A node repeated exactly MAX_NODE_REPEATS times should pass."""
        plan = {"workflow": [{"node": "node_a"}, {"node": "node_a"}]}
        assert validate_plan(plan) is None

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_three_repeats_rejected(self):
        plan = {"workflow": [{"node": "node_a"}] * 3}
        err = validate_plan(plan)
        assert err is not None
        assert "repeated" in err.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_mixed_valid_and_invalid(self):
        plan = {"workflow": [{"node": "node_a"}, {"node": "bogus"}]}
        err = validate_plan(plan)
        assert err is not None
        assert "bogus" in err

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    def test_node_key_missing_in_step(self):
        """Step dict without a 'node' key → name is empty string → unknown."""
        plan = {"workflow": [{"action": "node_a"}]}
        err = validate_plan(plan)
        assert err is not None
        assert "unknown" in err.lower()


# ===================================================================
# 3. plan_workflow  —  LLM integration (mocked)
# ===================================================================

class TestPlanWorkflow:

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_llm_returns_valid_json(self, mock_llm):
        plan_json = '{"workflow": [{"node": "node_a"}]}'
        mock_llm.return_value = iter(list(plan_json))
        result = plan_workflow("do something")
        assert result == {"workflow": [{"node": "node_a"}]}

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_llm_returns_fenced_json(self, mock_llm):
        fenced = '```json\n{"workflow": [{"node": "node_b"}]}\n```'
        mock_llm.return_value = iter(list(fenced))
        result = plan_workflow("another task")
        assert result["workflow"] == [{"node": "node_b"}]

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_llm_returns_garbage(self, mock_llm):
        mock_llm.return_value = iter(list("Sorry, I can't do that."))
        result = plan_workflow("impossible request")
        assert result == EMPTY_PLAN

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_llm_returns_empty_string(self, mock_llm):
        mock_llm.return_value = iter([])
        result = plan_workflow("nothing")
        assert result == EMPTY_PLAN

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_prompt_includes_available_nodes(self, mock_llm):
        """The system prompt sent to the LLM must list the available nodes."""
        mock_llm.return_value = iter(list('{"workflow": []}'))
        plan_workflow("test")
        args = mock_llm.call_args[0][0]
        system_msg = args[0]["content"]
        for name in MOCK_NODES:
            assert name in system_msg


# ===================================================================
# 4. build_workflow  —  LangGraph compilation
# ===================================================================

class TestBuildWorkflow:

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    def test_single_step_compiles(self):
        plan = {"workflow": [{"node": "node_a"}]}
        graph = build_workflow(plan)
        assert graph is not None

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    def test_multi_step_compiles(self):
        plan = {"workflow": [{"node": "node_a"}, {"node": "node_b"}]}
        graph = build_workflow(plan)
        assert graph is not None

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    def test_unknown_node_raises(self):
        plan = {"workflow": [{"node": "does_not_exist"}]}
        with pytest.raises(ValueError, match="Unknown node"):
            build_workflow(plan)

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    def test_graph_is_invocable(self):
        """Compiled graph should be invocable and return a dict with 'result'."""
        plan = {"workflow": [{"node": "node_a"}]}
        graph = build_workflow(plan)
        output = graph.invoke({"input": "test input"})
        assert "result" in output

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    def test_multi_step_executes_last_node(self):
        plan = {"workflow": [{"node": "node_a"}, {"node": "node_b"}]}
        graph = build_workflow(plan)
        output = graph.invoke({"input": "test"})
        assert "node_b executed" in output["result"]


# ===================================================================
# 5. run_dynamic_workflow  —  end-to-end orchestration
# ===================================================================

class TestRunDynamicWorkflow:

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_happy_path(self, mock_llm):
        plan_json = '{"workflow": [{"node": "node_a"}, {"node": "node_b"}]}'
        mock_llm.return_value = iter(list(plan_json))
        result = run_dynamic_workflow("do both steps")
        assert "node_b executed" in result

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_empty_plan_returns_error(self, mock_llm):
        mock_llm.return_value = iter(list("not json"))
        result = run_dynamic_workflow("bad request")
        assert "planning failed" in result.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_too_many_steps_returns_error(self, mock_llm):
        plan = {"workflow": [{"node": "node_a"}] * 6}
        mock_llm.return_value = iter(list(json.dumps(plan)))
        result = run_dynamic_workflow("overloaded request")
        assert "exceeds" in result.lower()

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_unknown_node_returns_error(self, mock_llm):
        plan = {"workflow": [{"node": "fake_node"}]}
        mock_llm.return_value = iter(list(json.dumps(plan)))
        result = run_dynamic_workflow("bad node request")
        assert "unknown" in result.lower()

    @patch("workflow_manager.workflow_builder.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_single_step_workflow(self, mock_llm):
        plan_json = '{"workflow": [{"node": "node_c"}]}'
        mock_llm.return_value = iter(list(plan_json))
        result = run_dynamic_workflow("one step only")
        assert "node_c executed" in result

    @patch("workflow_manager.planner_agent.NODE_REGISTRY", MOCK_NODES)
    @patch("workflow_manager.planner_agent.generate_response")
    def test_repeated_node_three_times_rejected(self, mock_llm):
        plan = {"workflow": [{"node": "node_a"}] * 3}
        mock_llm.return_value = iter(list(json.dumps(plan)))
        result = run_dynamic_workflow("spam request")
        assert "repeated" in result.lower()


# ===================================================================
# 6. NODE_REGISTRY sanity  —  real registry from project tools
# ===================================================================

class TestNodeRegistrySanity:

    def test_registry_is_populated(self):
        assert len(NODE_REGISTRY) > 0, "NODE_REGISTRY should not be empty"

    def test_all_entries_are_callable(self):
        for name, fn in NODE_REGISTRY.items():
            assert callable(fn), f"{name} is not callable"

    def test_node_names_end_with_node(self):
        for name in NODE_REGISTRY:
            assert name.endswith("_node"), f"{name} doesn't follow the _node naming convention"

    def test_expected_tools_present(self):
        expected = [
            "send_notification_node",
            "generate_chart_node",
            "count_employees_node",
            "department_employee_count_node",
        ]
        for name in expected:
            assert name in NODE_REGISTRY, f"{name} missing from NODE_REGISTRY"
