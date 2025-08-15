from datetime import datetime, timezone
from typing import Union, Dict, Any
import json
import re


def clean_crewai_topics(raw):
    # Cleans and parses any CrewAI response into a consistent dict with a 'root' key.
    # Ensures `cleaned["root"]` is always safe to access.

    cleaned = {"root": []}

    try:
        # If already a dict with 'root'
        if isinstance(raw, dict):
            if "root" in raw and isinstance(raw["root"], list):
                return raw
            else:
                return cleaned

        # Ensure it's a string
        if not isinstance(raw, str):
            raw = str(raw)

        # Remove code block formatting like ```json or triple quotes
        raw = raw.strip()
        raw = re.sub(r"^(```(json)?|'''|\"\"\")", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"(```|'''|\"\"\")$", "", raw, flags=re.IGNORECASE).strip()

        # Try parsing it as JSON
        parsed = json.loads(raw)

        # Ensure it has a 'root' key that is a list
        if isinstance(parsed, dict) and isinstance(parsed.get("root"), list):
            return parsed
        else:
            return cleaned

    except Exception as e:
        print(f"[!] Failed to parse input: {e}")
        return cleaned


def clean_crewai_article(raw: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    # Cleans and parses any CrewAI raw article output into a consistent dict.
    # Handles cases where output is wrapped with ```json, ```, ''' or """.
    # Always returns a dict. Returns {} on failure.

    # If already a dict, return as is
    if isinstance(raw, dict):
        return raw

    if not isinstance(raw, str):
        raw = str(raw)

    try:
        # Remove leading markdown wrappers like ```json, ``` , ''' ,
        cleaned = raw.strip()

        # Remove leading 'json' or similar tags (e.g. 'json\n{...}')
        cleaned = re.sub(r"^\s*(json)?\s*[\n\r]+", "", cleaned, flags=re.IGNORECASE)

        # Remove wrapping triple quotes or backticks
        cleaned = re.sub(
            r"^(```(json)?|'''|\"\"\")", "", cleaned, flags=re.IGNORECASE
        ).strip()
        cleaned = re.sub(r"(```|'''|\"\"\")$", "", cleaned, flags=re.IGNORECASE).strip()

        # Testing:
        print("=== CLEANED ARTICLE STRING ===")
        print(repr(cleaned))


        # Final attempt to parse
        return json.loads(cleaned)

    except Exception as e:
        print(f"[!] Failed to parse article JSON: {e}")
        return {}


def clean_usage_tokens(metrics_obj) -> dict:
    # Accepts a CrewAI UsageMetrics object (crewai.types.usage_metrics.UsageMetrics)
    # and returns a clean dict with ISO date and key usage fields.

    # Attempt to convert the Pydantic model to a dict
    try:
        metrics = metrics_obj.dict()
    except AttributeError:
        # Fallback if for some reason it's not a pydantic model
        metrics = metrics_obj.__dict__

    required = {
        "total_tokens",
        "prompt_tokens",
        "completion_tokens",
        "successful_requests",
    }
    if not required.issubset(metrics):
        missing = required - set(metrics)
        raise ValueError(f"Missing required fields in UsageMetrics: {missing}")

    # Get today's date at UTC midnight
    date_iso = (
        datetime.now(timezone.utc)
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .isoformat()
    )

    return {
        "date": date_iso,
        "total_tokens": metrics["total_tokens"],
        "prompt_tokens": metrics["prompt_tokens"],
        "completion_tokens": metrics["completion_tokens"],
        "successful_requests": metrics["successful_requests"],
    }
