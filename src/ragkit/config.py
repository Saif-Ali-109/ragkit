"""Framework configuration for ragkit.

ragkit owns the environment keys its core chain reads directly: the
PostgreSQL connection settings, the embedding / generation models, and the
retrieval / reranking knobs.  Values are read from ``os.environ`` at import
time.

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
