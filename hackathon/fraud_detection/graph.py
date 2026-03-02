"""
Workflow assembly for the fraud detection agents.
"""

from __future__ import annotations

from typing import Callable, Dict

try:  # pragma: no cover - optional dependency surface
    from langgraph.graph import END, StateGraph
except ImportError:  # noqa: F401 - fallback handled below
    StateGraph = None  # type: ignore[assignment]
    END = None  # type: ignore[assignment]

from .analyzer import analyzer_agent
from .scanner import scanner_agent
from .scanner_direct import scanner_agent_direct
from .state import FraudState

# Use direct Lenses API scanner (bypasses MCP for simpler deployment)
USE_DIRECT_API = False


class SequentialWorkflow:
    """Fallback workflow that runs agents sequentially without langgraph."""

    def __init__(self, nodes: Dict[str, Callable[[FraudState], FraudState]]):
        self._nodes = nodes

    def invoke(self, state: FraudState) -> FraudState:
        current_state = state
        for node_name in ("scanner", "analyzer"):
            current_state = self._nodes[node_name](current_state)
        return current_state


def build_fraud_detection_graph():
    """Create and compile the 2-agent fraud detection workflow."""
    # Choose scanner based on configuration
    active_scanner = scanner_agent_direct if USE_DIRECT_API else scanner_agent

    if StateGraph is None:
        print("⚠️  langgraph not available – falling back to sequential execution.")
        return SequentialWorkflow({"scanner": active_scanner, "analyzer": analyzer_agent})

    workflow = StateGraph(FraudState)
    workflow.add_node("scanner", active_scanner)
    workflow.add_node("analyzer", analyzer_agent)
    workflow.set_entry_point("scanner")
    workflow.add_edge("scanner", "analyzer")
    workflow.add_edge("analyzer", END)
    return workflow.compile()
