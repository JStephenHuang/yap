"""
Shared type definitions for the graph.
"""

from typing import Literal
from typing_extensions import TypedDict


class TriageResult(TypedDict):
    """Structured output for triage evaluation."""
    decision: Literal["approved", "rejected"]
    reason: str
