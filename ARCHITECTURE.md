# Cred Domain Support Agent Architecture

## System overview

```text
Support User
    |
    v
FastAPI (/ask, /add-document)
    |
    +--> Input guardrails (PII masking + injection detection)
    +--> JSON-Lines request logging (trace ID + timing)
    |
    v
LangGraph router
    |
    +--> Policy query --> RAG retrieval --> grounded answer
    |
    +--> LA-#### query --> loan lookup --> escalation score
                                      |
                                      v
                         schema validation and response
```

The system is a banking support agent for loan-policy questions and application-status questions. It combines deterministic records, authored policy documents, semantic retrieval, tool routing, safety checks, persistence, and HTTP/MCP interfaces.

## Data and retrieval pipeline

```text
knowledge_base/*.md
        |
        v
    rag_index.py
        |
        +--> fixed-size chunks (240 target, 40 overlap)
        |          --> all-MiniLM-L6-v2 --> cred_fixed_chunks
        |
        +--> sentence chunks
                   --> all-MiniLM-L6-v2 --> cred_sentence_chunks
```

Every chunk stores its parent document ID and source filename. That metadata enables document-level deduplication for Precision@3 and Recall@3 evaluation.

## Request flow

```text
1. POST /ask receives a query.
2. Middleware starts timing and creates a trace ID.
3. Input guardrails mask fixed-format PII and detect prompt injection.
4. LangGraph classifies the intent.
5. RAG or loan-status tool handles the request.
6. Groundedness and structured-output checks validate the result.
7. A masked JSON-Lines entry is written and the response is returned.
```

## LangGraph flow

```text
START -> classify
           |
           +-- rag ------+
           |             |
           +-- status ---+--> format -> END
```

Queries containing an application ID such as `LA-0001` use the status route. Other queries use the policy RAG route.

## Persistence and interoperability

```text
ConversationMemory  --> conversation_memory.json
LangGraph saver     --> checkpoints.sqlite
ChromaDB            --> chroma_db/
Request middleware  --> requests.jsonl

MCP client --> http://127.0.0.1:8001/mcp --> MCP server --> loan_tools.py
```

The runtime files are reproducible local artifacts and are ignored by Git. Source code, tests, policy documents, and documentation are version-controlled.

## Safety and reliability boundaries

```text
Input boundary       PII masking and injection rejection
Retrieval boundary   calibrated similarity threshold and fallback
Output boundary      structured schema validation
Runtime boundary     per-node and global timeouts
Failure boundary     exponential-backoff retries
Recovery boundary    SQLite checkpoint and thread resume
Integration boundary separate MCP client/server processes
```

These boundaries prevent sensitive input from reaching the model, prevent unsupported answers, and keep transient failures from becoming indefinite hangs.

## Task-to-component map

```text
Tasks 1–2   dataset.py, knowledge_base/, tests/
Tasks 3–5   rag_index.py, rag_query.py, evaluate_rag.py, evaluate_triad.py
Task 6      loan_tools.py
Task 7      agent_graph.py
Task 8      conversation_memory.py
Task 9      response_schema.py
Task 10     guardrails.py
Tasks 11–12 api.py, request_logging.py
Task 13     evaluate_triad.py
Task 14     mcp_server.py, mcp_client.py
Task 15     checkpoint_demo.py
Task 16     resilience.py
```
