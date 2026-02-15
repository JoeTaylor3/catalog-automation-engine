"""ai package initializer.

Expose core helpers for other modules/tests to import as `ai.xxx`.
"""

from .llm_summary import generate_ai_summary

__all__ = ["generate_ai_summary"]
