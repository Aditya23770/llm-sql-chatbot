import re


def extract_sql(raw: str) -> str:
    """Extract the first SELECT statement from raw LLM output."""
    match = re.search(r"SELECT.*?;", raw, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"No valid SQL query found in LLM response: {raw!r}")
    return match.group(0)
