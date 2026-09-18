"""Host-application wiring hooks for the agentic core (Stage 2, S2-T2).

The default-component machinery (DB-backed retriever construction consulting
the app's rerank/hybrid levers, Phase-1 ``ask()`` wrapper with observability
logging) stays in the extraction host (DocPilot) because it reads app-owned
config keys.  The host registers its builders once via
:func:`set_host_wiring`; the agentic core calls them when the caller did not
inject components, and runs the framework core directly for injected components.

Ragkit's own hermetic test suite needs no host wiring: the fast path runs
the framework's ``_run_direct_core`` natively when components are injected.
"""

from __future__ import annotations

from typing import Any, Callable

_direct_ask_hook: Callable[..., Any] | None = None
_default_retriever_builder: Callable[[], Any] | None = None


def set_host_wiring(
    *,
    direct_ask: Callable[..., Any] | None = None,
    default_retriever: Callable[[], Any] | None = None,
) -> None:
    """Register host-application wiring for the agentic core.

    Called once by the extraction host at import time (see
    ``docpilot/__init__.py``).  Calling again replaces the current hooks.
    """
    global _direct_ask_hook, _default_retriever_builder
    if direct_ask is not None:
        _direct_ask_hook = direct_ask
    if default_retriever is not None:
        _default_retriever_builder = default_retriever


def get_direct_ask_hook() -> Callable[..., Any] | None:
    """Return the registered direct-ask hook (``None`` when unregistered)."""
    return _direct_ask_hook


def get_default_retriever_builder() -> Callable[[], Any] | None:
    """Return the registered default-retriever builder (``None`` when unregistered)."""
    return _default_retriever_builder
