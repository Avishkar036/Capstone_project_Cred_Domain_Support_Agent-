"""Input and output guardrails for the Cred support agent."""

import re
from typing import Any


class PromptInjectionError(ValueError):
    """Raised when a query attempts to override agent instructions."""


class UngroundedResponseError(ValueError):
    """Raised when retrieved context is below the calibrated threshold."""


def mask_pii(text: str) -> str:
    """Mask PAN, Aadhaar, and bank-account values while preserving shape."""
    text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "[PAN-MASKED]", text, flags=re.IGNORECASE)
    text = re.sub(
        r"(\baccount(?:\s+number)?\s*[:#-]?\s*)\d{9,18}\b",
        r"\1[ACCOUNT-MASKED]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b", "[AADHAAR-MASKED]", text)
    text = re.sub(r"\b\d{9,18}\b", "[ACCOUNT-MASKED]", text)
    return text


def detect_prompt_injection(text: str) -> bool:
    """Return whether text contains common instruction-override language."""
    patterns = (r"ignore\s+(all|any|previous)\s+instructions", r"system\s+prompt", r"reveal\s+your\s+instructions")
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def guard_input(text: str) -> str:
    """Reject injection attempts and return masked text for model use/logging."""
    if detect_prompt_injection(text):
        raise PromptInjectionError("Prompt injection detected")
    return mask_pii(text)


def check_grounded_output(result: dict[str, Any], threshold: float = 0.3663) -> dict[str, Any]:
    """Refuse a RAG result whose top similarity is below the calibrated threshold."""
    if result.get("similarity", 0.0) < threshold:
        raise UngroundedResponseError("Retrieved context does not support this question")
    return result
