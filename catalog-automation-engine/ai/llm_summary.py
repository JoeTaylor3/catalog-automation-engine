import os
from typing import Dict

import openai

# read API key once at import time; mirrors top-level ai.llm_summary
api_key = os.getenv("OPENAI_API_KEY")


def generate_ai_summary(metrics: Dict, sql_insights: Dict, validation_summary: Dict) -> str:
    """Builds a prompt from provided statistics and sends it to an OpenAI LLM.

    Returns an executive-level paragraph suitable for leadership.
    """

    total_records = metrics.get("total_records", "unknown")
    invalid_pct = metrics.get("invalid_pct", "unknown")
    top_issues = validation_summary.get("top_issue_types", "none reported")
    duplicate_sku = sql_insights.get("duplicate_sku_count", 0)
    high_price = sql_insights.get("high_price_anomalies", 0)
    low_inv = sql_insights.get("low_inventory_warnings", 0)

    prompt = (
        "You are an executive-level business analyst. "
        "Based on the following dataset metadata, prepare a concise, "
        "professional paragraph suitable for senior leadership:\n\n"
        f"- Total records: {total_records}\n"
        f"- Invalid record percentage: {invalid_pct}%\n"
        f"- Top issue types: {top_issues}\n"
        f"- Duplicate SKU count: {duplicate_sku}\n"
        f"- High price anomalies: {high_price}\n"
        f"- Low inventory warnings: {low_inv}\n\n"
        "Your summary should address overall data integrity, primary risk "
        "drivers, operational impact, and suggested remediation focus areas. "
        "Keep the tone appropriate for a senior leadership audience."
    )

    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment")

    openai.api_key = key

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=250,
    )

    if isinstance(resp, dict):
        choices = resp.get("choices", [])
    else:
        choices = getattr(resp, "choices", [])

    if not choices:
        raise RuntimeError("No completion choices returned from OpenAI")

    first = choices[0]
    if isinstance(first, dict):
        content = first["message"]["content"]
    else:
        content = first.message["content"]

    return content.strip()
