# Task 10 manual transcript

PII masking:

```text
PAN [PAN-MASKED], Aadhaar [AADHAAR-MASKED], account [ACCOUNT-MASKED]
```

Prompt-injection test:

```text
guardrails.PromptInjectionError: Prompt injection detected
```

Groundedness test:

```text
guardrails.UngroundedResponseError: Retrieved context does not support this question
```

All three deliberate guardrail cases fired successfully.
