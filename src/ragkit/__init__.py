"""ragkit — reusable RAG framework extracted from DocPilot.

Stage 1: core chain (loader / parser / chunker / embeddings / vector store /
retrieval / generation / citations). DocPilot consumes this package and
dogfoods it (DocPilot PLAN §8).
"""

__version__ = "0.1.0"