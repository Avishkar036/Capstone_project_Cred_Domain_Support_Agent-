# Cred Domain Support Agent

## Project purpose

This project develops a production-minded banking support agent for Cred’s lending operations. It answers loan-policy questions from a controlled knowledge base, looks up real application records from a deterministic dataset, remembers conversation context, protects sensitive inputs, and exposes reusable tools through HTTP and MCP interfaces. The goal is to demonstrate how a support assistant can remain grounded, testable, observable, resumable, and safe rather than acting as an unconstrained text generator.

## Why the project has 16 tasks

The project is divided into 16 tasks so each production capability can be designed, implemented, tested, and demonstrated independently before being combined. Tasks 1–5 establish the data and retrieval foundation; Tasks 6–10 add tools, orchestration, memory, structured responses, and guardrails; Tasks 11–13 add deployment, logging, and evaluation; and Tasks 14–16 add interoperability, checkpoint recovery, retries, and timeouts. This progression makes failures easier to isolate and proves the acceptance criteria incrementally.

## Repository structure

```text
Capstone_project_Cred_Domain_Support_Agent-/
├── __pycache__/                        # local Python bytecode cache (ignored)
├── .venv/                              # local virtual environment (ignored)
├── chroma_db/                          # generated persistent Chroma indexes
├── knowledge_base/                     # 12 required banking-policy documents
├── tests/                              # automated tests for every task
├── .gitignore                           # ignored environments and runtime files
├── agent_graph.py                      # four-node LangGraph routing
├── api.py                              # FastAPI /ask and /add-document endpoints
├── architecture.md                     # text-only system architecture
├── checkpoint_demo.py                  # SQLite checkpoint/resume demonstration
├── checkpoints.sqlite                  # generated checkpoint database (ignored)
├── conversation_memory.py              # JSON-backed conversation history
├── dataset.py                          # deterministic 50-record loan dataset
├── evaluate_rag.py                     # Precision@3 / Recall@3 comparison
├── evaluate_triad.py                   # 15-query MOCK_LLM RAG-triad evaluation
├── guardrails.py                       # PII, injection, and grounding checks
├── loan_tools.py                       # status lookup and escalation score
├── mcp_client.py                       # separate MCP client process
├── mcp_server.py                       # FastMCP HTTP server
├── problem_statement_banking.md        # original project brief
├── rag_index.py                        # chunk, embed, and index documents
├── rag_query.py                        # retrieve and ground answers
├── README.md                           # project guide and implementation rationale
├── ARCHITECTURE.md                     # visual system architecture and data flows
├── request_logging.py                  # masked JSON-Lines request logging
├── requests.jsonl                      # generated request log (ignored)
├── resilience.py                       # retries and timeout demonstrations
└── response_schema.py                  # structured response validation
```

## Task 1 dataset design

The generator uses seed `20260909` and creates exactly 50 records. Categories are balanced at 10 each; status weights are Submitted 10, Under Review 12, Approved 12, Rejected 8, and Disbursed 8. Loan amounts are generated between INR 25,000 and INR 25,00,000, days since creation between 0 and 30, and 10 records are flagged for fraud review (20%).

## Task 2 knowledge base

The `knowledge_base/` directory contains 12 Markdown documents, each written in 2–5 sentences. The documents cover loan eligibility by type, EMI calculation, credit-card fees, KYC requirements, fraud-dispute resolution, account closure, interest-rate slabs, prepayment penalties, minimum-balance requirements, credit-score factors, joint-account rules, and NRI-account eligibility. `tests/test_knowledge_base.py` checks that all required topics exist and that each document stays within the required sentence range.

## Task 3 chunking, embeddings, and indexing

`rag_index.py` loads the Markdown documents and creates two representations: fixed-size word chunks with a 240-character target and 40-character overlap, and sentence-based chunks split at sentence boundaries. Both sets use the local `all-MiniLM-L6-v2` SentenceTransformer model and are stored in separate persistent ChromaDB collections named `cred_fixed_chunks` and `cred_sentence_chunks`.

The two collections are kept separate so their retrieval quality can be compared fairly. Parent-document metadata is stored with every chunk, which allows later Precision@3 and Recall@3 calculations to deduplicate chunks correctly. Run `rag_index.py` once after installing the embedding and ChromaDB dependencies to build the local indexes.

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

## Implementation overview and design rationale

This project was implemented as a staged support-agent system. The deterministic dataset provides realistic loan records; the authored knowledge base supplies policy grounding; the embedding and ChromaDB layer provides semantic retrieval; LangGraph routes each incoming request to either policy retrieval or the loan-status tool; and FastAPI exposes the resulting agent as an HTTP service.

The implementation uses deterministic seeds, fixed test fixtures, local embeddings, and `MOCK_LLM`-style scoring so the project can run without paid API keys or nondeterministic external generation. Sentence-based chunks were selected as the recommended retrieval strategy because they preserve readable policy units, while the fixed-size strategy remains available for measured comparison. PII masking and prompt-injection checks run before model use, groundedness is checked before an answer is returned, and JSON-Lines logging applies the same masking before writing request text to disk.

Persistence and resilience were added because a support agent must survive interruptions and transient failures: JSON memory preserves conversation turns, SQLite checkpoints allow a LangGraph thread to resume, and retry/timeout helpers prevent temporary failures or slow calls from hanging the service. The MCP server is separate from the LangGraph process so the lookup capability can be reused through a standard tool protocol.
