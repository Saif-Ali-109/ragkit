"""Framework configuration for ragkit.

ragkit owns the environment keys its modules read: the PostgreSQL connection
settings, the embedding / generation models, the retrieval / reranking knobs,
the agentic-loop keys (``AGENT_*``) and the GitHub-tool keys (``GITHUB_*``).
Values are read from ``os.environ`` at import time.

Import is deliberately hard-fail-free: a missing value falls back to a safe
default (empty strings for credentials) so ``import ragkit`` works in any
host application, with or without a populated environment.  Applications
that *require* credentials keep their own fail-fast checks (DocPilot does so
in ``docpilot.config``) and load their ``.env`` file **before** importing a
ragkit module, so the values are already visible here.
"""

from __future__ import annotations

import os

# --- Database ---
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "docpilot")
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

# --- Embeddings ---
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# --- Generation (Groq) ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_MAX_RETRIES: int = int(os.getenv("GROQ_MAX_RETRIES", "3"))

# --- Retrieval ---
RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))

# --- Reranking ---
RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
"""Cross-encoder model for ``BCEReranker`` (downloaded lazily, CPU)."""

RERANK_CANDIDATES: int = int(os.getenv("RERANK_CANDIDATES", "20"))
"""Width of the candidate window fetched before reranking down to top_k."""

# --- Retrieval language ---
RETRIEVAL_LANGUAGE: str = os.getenv("RETRIEVAL_LANGUAGE", "en")
"""Default retrieval language filter; the literal ``"any"`` disables filtering."""

# --- Agentic loop (Stage 2) ---
AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "2"))
"""Maximum judge/reformulate iterations before the agent refuses."""

AGENT_LOOP_TOP_K: int = int(os.getenv("AGENT_LOOP_TOP_K", "5"))
"""Retrieval count used inside the agentic loop when the caller does not override it."""

AGENT_JUDGE_SKIP_MIN_SCORE: float = float(os.getenv("AGENT_JUDGE_SKIP_MIN_SCORE", "0.0"))
"""Fast-path judge skip: when > 0, the retrieve node marks ``skip_judge`` when the top score clears it."""

AGENT_JUDGE_MODEL: str = os.getenv("AGENT_JUDGE_MODEL", "")
"""Optional separate Groq model for the sufficiency judge; empty → ``GROQ_MODEL``."""

AGENT_JUDGE_SCORE_FLOOR: float = float(os.getenv("AGENT_JUDGE_SCORE_FLOOR", "0.0"))
"""Score-floor backstop for the LLM judge; 0.0 disables it."""

AGENT_GATE_LONG_THRESHOLD: int = int(os.getenv("AGENT_GATE_LONG_THRESHOLD", "18"))
"""Word count above which the heuristic query classifier fires ``long_question``."""

# --- GitHub tool (Stage 2) ---
GITHUB_PAT: str = os.getenv("GITHUB_PAT", "")
"""GitHub Personal Access Token — optional.  An empty PAT disables the tool
(never logs this value)."""

GITHUB_API_BASE: str = os.getenv("GITHUB_API_BASE", "https://api.github.com")
"""GitHub REST API base URL — defaults to the public ``api.github.com``."""

GITHUB_OWNER: str = os.getenv("GITHUB_OWNER", "")
"""Default repository owner for the GitHub tool (e.g. ``fastapi``)."""

GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
"""Default repository name for the GitHub tool (e.g. ``fastapi``)."""
