"""DocPilot tools package — Phase 3 GitHub tooling (SPEC §5, PLAN §4).

The locked Phase 3 contract is a **plain** external-data tool behind the
:class:`~ragkit.tools.base.Tool` interface — no MCP protocol or SDK.  The
agent wiring imports exactly these four names::

    from ragkit.tools import GitHubTool, Tool, ToolRequest, ToolResult
"""

from ragkit.tools.base import Tool, ToolRequest, ToolResult
from ragkit.tools.github import GitHubTool

__all__ = ["GitHubTool", "Tool", "ToolRequest", "ToolResult"]