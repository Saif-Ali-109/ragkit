"""Shared test utilities for the ragkit agentic core (extraction S2-T2).

Canned fakes — retriever, judge, tool, generator, and canned result corpora —
used by ragkit's own test suite and by host-app suites (DocPilot imports these
from here, so there is a single copy).

Extracted verbatim from DocPilot's tests (mechanical, no behavior change);
only the ``docpilot.`` → ``ragkit.`` import prefix was swapped.

Importing this module pulls in ragkit's agent/tools modules but makes no
network / DB / LLM access; ``langgraph`` stays lazily imported by
``build_graph``.
"""

from __future__ import annotations

from ragkit.agent.graph import build_graph, trace_step_to_dict
from ragkit.agent.types import AgentLoopState, Judgment, LoopTraceStep
from ragkit.citations.engine import StandardCitationEngine
from ragkit.core.models import Chunk, RetrieverResult
from ragkit.generation.generator import Generator
from ragkit.tools import Tool, ToolRequest, ToolResult


class FakeGenerator(Generator):
    """Canned-response generator that records what it was given."""

    def __init__(self, response: str = "") -> None:
        self.response = response
        self.calls = 0
        self.last_prompt: str | None = None
        self.last_context: str | None = None
        self.last_sources: str | None = None
        self.last_question: str | None = None

    def generate(self, prompt: str) -> str:
        self.calls += 1
        self.last_prompt = prompt
        return self.response

    def generate_answer(
        self, context_text: str, sources_text: str, question: str
    ) -> str:
        from ragkit.generation.prompts import SYSTEM_PROMPT

        self.calls += 1
        self.last_context = context_text
        self.last_sources = sources_text
        self.last_question = question
        self.last_prompt = SYSTEM_PROMPT.format(
            context=context_text, sources=sources_text, question=question
        )
        return self.response


GATE_QUERY = "Combine path, query, and body parameters in one endpoint — what are the validation rules for each kind?"


# ---------------------------------------------------------------------------
# Shared fakes (also imported by tests/test_agent_pipeline.py)
# ---------------------------------------------------------------------------


class FakeRetriever:
    """Canned retriever: returns a preset result list per query string."""

    def __init__(self, results_by_query: dict[str, list[RetrieverResult]]) -> None:
        self.results_by_query = results_by_query
        self.calls: list[tuple[str, int, str | None]] = []

    def retrieve(self, query: str, top_k: int = 5, *, language: str | None = None):
        self.calls.append((query, top_k, language))
        return list(self.results_by_query.get(query, []))


class StubJudge:
    """Preset-judgment judge that pops from a queue and counts calls.

    ``tools_seen`` records every ``tools_available`` value the graph passed
    (Phase 3 — the judge must be told whether a tool is wired).
    """

    def __init__(self, judgments: list[Judgment]) -> None:
        self.judgments = list(judgments)
        self.calls = 0
        self.last_query_used: str | None = None
        self.tools_seen: list[bool] = []

    def judge(
        self,
        question: str,
        results: list[RetrieverResult],
        query_used: str,
        *,
        tools_available: bool = True,
    ) -> Judgment:
        self.calls += 1
        self.last_query_used = query_used
        self.tools_seen.append(tools_available)
        if not self.judgments:
            return Judgment(verdict="sufficient", reason="no preset remaining")
        return self.judgments.pop(0)


class StubTool(Tool):
    """Canned tool: returns a preset ToolResult per request name, records
    every request (name + params) it received."""

    name = "stub"

    def __init__(self, results_by_name: dict[str, ToolResult]) -> None:
        self.results_by_name = results_by_name
        self.calls: list[ToolRequest] = []

    def execute(self, request: ToolRequest) -> ToolResult:
        self.calls.append(request)
        return self.results_by_name.get(
            request.name,
            ToolResult(ok=False, summary="", error=f"unknown action {request.name!r}"),
        )


def github_issue_result(*, number: int = 42, title: str = "OAuth token expires") -> ToolResult:
    """Canned ok GitHub-style tool result with one per-item source_label."""
    return ToolResult(
        ok=True,
        summary=(
            f"1 matching issue(s) in acme/widget for 'oauth token expiration': "
            f"#{number} {title} (created 2026-09-01)"
        ),
        items=[
            {
                "number": number,
                "title": title,
                "state": "open",
                "html_url": f"https://github.com/acme/widget/issues/{number}",
                "created_at": "2026-09-01T10:00:00Z",
                "labels": ["auth"],
                "source_label": f"github:acme/widget#{number}",
            }
        ],
    )


def make_result(
    content: str = "FastAPI supports path, query and body parameters.",
    source_file: str = "en/docs/tutorial/params.md",
    heading: str = "Parameters",
    score: float = 0.81,
    chunk_id: str = "c1",
) -> RetrieverResult:
    return RetrieverResult(
        chunk=Chunk(
            id=chunk_id,
            content=content,
            heading_path=heading,
            source_file=source_file,
            chunk_index=0,
        ),
        score=score,
    )


RESULTS_BY_QUERY: dict[str, list[RetrieverResult]] = {
    GATE_QUERY: [
        make_result(
            content="[1] Path parameters, [2] query parameters, [3] body parameters validation.",
            source_file="en/docs/tutorial/params.md",
            heading="Parameters",
            score=0.91,
            chunk_id="c1",
        ),
        make_result(
            content="Validation rules differ per parameter kind.",
            source_file="en/docs/tutorial/validation.md",
            heading="Validation",
            score=0.72,
            chunk_id="c2",
        ),
    ],
    "reformulated validation rules": [
        make_result(
            content="Each parameter kind has its own validation rules.",
            source_file="en/docs/tutorial/validation.md",
            heading="Validation",
            score=0.88,
            chunk_id="c3",
        ),
    ],
}


def results_for(query: str) -> list[RetrieverResult]:
    """Per-query canned results (raises KeyError for unseen queries)."""
    return RESULTS_BY_QUERY[query]


def initial_state(question: str = GATE_QUERY, gate_decision: str = "agentic") -> AgentLoopState:
    """Build the same initial loop state the pipeline feeds the graph."""
    gate_step = LoopTraceStep.new("gate", question, gate_decision, detail="signals=[]; simple")
    return {
        "question": question,
        "original_question": question,
        "current_query": question,
        "results": [],
        "sources": [],
        "attempts": 0,
        "trace": [trace_step_to_dict(gate_step)],
        "tool_request": None,
        "tool_results": [],
        "tool_error": None,
        "answer": None,
        "refused": False,
        "direct": False,
        "skip_judge": False,
    }


def _trace_steps(final: dict) -> list[str]:
    return [t.get("step") for t in final["trace"]]


def _build_app(retriever, judge, generator, max_retries: int = 2, tool=None):
    return build_graph(
        retriever=retriever,
        judge=judge,
        generator=generator,
        citation_engine=StandardCitationEngine(),
        top_k=5,
        language=None,
        max_retries=max_retries,
        tool=tool,
    )


# ---------------------------------------------------------------------------
