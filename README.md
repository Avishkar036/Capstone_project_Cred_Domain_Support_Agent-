# Cred Domain Support Agent

## Task 4 calibration

The SentenceTransformer model is `all-MiniLM-L6-v2`. Five in-scope queries produced top-1 cosine similarities of 0.7473, 0.7327, 0.6560, 0.7177, and 0.6763. Two deliberately out-of-scope queries produced 0.0479 and 0.0766, so the tested fallback threshold is 0.3663, the midpoint between the lowest in-scope and highest out-of-scope scores.

Queries below 0.3663 return an explicit “I don't know based on the available policy documents” fallback.

## Task 5 evaluation

`evaluate_rag.py` evaluates the same five in-scope queries for both chunking strategies at the document level. Retrieved chunks are deduplicated by parent document before calculating Precision@3 and Recall@3.

## Task 6 escalation score

`check_loan_application_status(record_id)` returns the application status, loan amount, and an escalation score. The formula is `0.6 × fraud_flag + 0.4 × (days_since_created / 30)`, with escalation recommended at scores of 0.65 or higher.

## Task 7 agent graph

The LangGraph agent has four nodes: `classify`, `rag`, `status`, and `format`. A conditional edge routes loan record IDs such as `LA-0001` to the status tool and routes policy questions to the RAG tool.

## Task 8 persisted memory

`ConversationMemory` stores ordered user and assistant messages in a JSON file, reloads them for a later turn, and supports an explicit reset that starts a fresh conversation with an empty history.

## Task 9 structured output

`response_schema.py` declares and validates the required `route`, `answer`, and `details` fields. The graph validates every response in its final formatting node before returning it.
