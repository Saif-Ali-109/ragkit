"""Root pytest configuration for ragkit tests.

Registers custom markers so pytest emits no PytestUnknownMarkWarning.

Optionally loads a ``.env`` from the ragkit repo root (gitignored) when
present, so the live-PostgreSQL integration tests can run on dev machines
that provide credentials — mirroring how an embedding host loads its env
before importing ragkit (see ``ragkit/config.py``).  Without a ``.env`` the
same tests hermetic-skip as designed (field-sequential fallback: the
defaults in ``ragkit/config.py`` are empty-credential safe).
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_REPO_ROOT / ".env")


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: test requires a live PostgreSQL/pgvector instance (skips when unreachable)",
    )