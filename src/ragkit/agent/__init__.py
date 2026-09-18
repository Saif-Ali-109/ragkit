"""DocPilot agent core — Phase 2 agentic retrieval (SPEC §4).

Exports the public API of the Phase 2 agent package.  No langgraph imports
at the package level — the graph wiring lives in :mod:`ragkit.agent.graph`
(AGENT G's responsibility) and is imported lazily by callers.

Typical usage (once the graph is wired)::

    from ragkit.agent import Agent, AgentResult
    from ragkit.agent.gate import HeuristicQueryClassifier
    from ragkit.agent.judge import LLMSufficiencyJudge
    from ragkit.agent.types import DEFAULT_MAX_RETRIES
"""

from ragkit.agent.interface import Agent, AgentResult
from ragkit.agent.types import (
    DEFAULT_MAX_RETRIES,
    AgentLoopState,
    GateDecision,
    Judgment,
    LoopTraceStep,
)

__all__ = [
    # Interfaces
    "Agent",
    "AgentResult",
    # Types / contract
    "GateDecision",
    "Judgment",
    "LoopTraceStep",
    "AgentLoopState",
    # Constants
    "DEFAULT_MAX_RETRIES",
]
