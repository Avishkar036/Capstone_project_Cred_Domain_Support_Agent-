"""Schema and validation for structured agent responses."""

from typing import Any


RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["route", "answer", "details"],
    "properties": {
        "route": {"enum": ["rag", "status"]},
        "answer": {"type": "string"},
        "details": {"type": "object"},
    },
}


def validate_response(response: dict[str, Any]) -> dict[str, Any]:
    """Validate and return an agent response using the declared schema."""
    if not isinstance(response, dict):
        raise TypeError("response must be an object")
    for field in RESPONSE_SCHEMA["required"]:
        if field not in response:
            raise ValueError(f"missing required field: {field}")
    if response["route"] not in RESPONSE_SCHEMA["properties"]["route"]["enum"]:
        raise ValueError("route must be 'rag' or 'status'")
    if not isinstance(response["answer"], str):
        raise TypeError("answer must be a string")
    if not isinstance(response["details"], dict):
        raise TypeError("details must be an object")
    return response
