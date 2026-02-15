"""ai package for catalog-automation-engine context.

This mirrors the top-level `ai` package so tests running with the
`catalog-automation-engine` working directory can import `ai.llm_summary`.
"""

from .llm_summary import generate_ai_summary

__all__ = ["generate_ai_summary"]
