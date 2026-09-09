# Cred Domain Support Agent

## Task 1 dataset design

The generator uses seed `20260909` and creates exactly 50 records. Categories are balanced at 10 each; status weights are Submitted 10, Under Review 12, Approved 12, Rejected 8, and Disbursed 8. Loan amounts are generated between INR 25,000 and INR 25,00,000, days since creation between 0 and 30, and 10 records are flagged for fraud review (20%).

## Task 4 calibration

The SentenceTransformer model is `all-MiniLM-L6-v2`. Five in-scope queries produced top-1 cosine similarities of 0.7473, 0.7327, 0.6560, 0.7177, and 0.6763. Two deliberately out-of-scope queries produced 0.0479 and 0.0766, so the tested fallback threshold is 0.3663, the midpoint between the lowest in-scope and highest out-of-scope scores.

Queries below 0.3663 return an explicit “I don't know based on the available policy documents” fallback.

## Task 5 evaluation

`evaluate_rag.py` evaluates the same five in-scope queries for both chunking strategies at the document level. Retrieved chunks are deduplicated by parent document before calculating Precision@3 and Recall@3.

Both strategies achieved mean Precision@3 = 0.333 and mean Recall@3 = 1.000 on the five-query comparison. Because the strategies tied, the sentence-based strategy is the recommended deployment choice for its simpler, more interpretable chunk boundaries.

## Task 6 escalation score

`check_loan_application_status(record_id)` returns the application status, loan amount, and an escalation score. The formula is `0.6 × fraud_flag + 0.4 × (days_since_created / 30)`, with escalation recommended at scores of 0.65 or higher.

## Task 7 agent graph

The LangGraph agent has four nodes: `classify`, `rag`, `status`, and `format`. A conditional edge routes loan record IDs such as `LA-0001` to the status tool and routes policy questions to the RAG tool.

## Task 8 persisted memory

`ConversationMemory` stores ordered user and assistant messages in a JSON file, reloads them for a later turn, and supports an explicit reset that starts a fresh conversation with an empty history.

## Task 9 structured output

`response_schema.py` declares and validates the required `route`, `answer`, and `details` fields. The graph validates every response in its final formatting node before returning it.

## Task 10 guardrails

Input text is checked for instruction-override phrases and fixed-format PAN, Aadhaar, and account values are masked before model use. RAG output is refused when its top similarity is below the calibrated 0.3663 threshold.

## Task 11 FastAPI

`api.py` exposes `POST /ask` for agent requests and `POST /add-document` for adding a Markdown knowledge-base document. Both endpoints use Pydantic request and response models.

## Task 12 structured logging

The API middleware appends one JSON-Lines entry per request with a trace ID, status code, and elapsed milliseconds. Request text is passed through the PII masker before it is written to `requests.jsonl`.

## Task 13 RAG-triad evaluation

`evaluate_triad.py` evaluates 15 queries under deterministic `MOCK_LLM` scoring: one query covers each required knowledge-base topic and three are deliberately out of scope. It reports context relevance, groundedness, answer relevance, every per-query score, and metric averages.

## Task 14 MCP

`mcp_server.py` exposes `lookup_loan_application` through FastMCP HTTP transport at `http://127.0.0.1:8001/mcp`. `mcp_client.py` is a separate client process that calls that endpoint.

## Task 15 SQLite checkpointing

`checkpoint_demo.py` uses `SqliteSaver` with thread ID `task15-demo-thread`. It pauses before `node_c`, then resumes the same thread and completes from the checkpoint containing `node_a` and `node_b`.

## Task 16 resilience

`resilience.py` uses four retry attempts with exponential backoff (0.01-second initial interval, 0.05-second cap, zero jitter for deterministic tests), a 0.05-second per-node timeout, and a 0.2-second global timeout. Its demos show transient recovery plus clean node and global timeout failures.
