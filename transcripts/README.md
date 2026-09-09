# Demonstration transcript checklist

Capture the terminal output for each command below and save it beside this file.
These transcripts provide the evidence requested by the project brief.

| Evidence | Suggested filename | Command or action |
|---|---|---|
| Task 4 calibration and fallback | `task4_grounded_generation.txt` | `python -B rag_query.py` |
| Task 5 retrieval comparison | `task5_retrieval_evaluation.txt` | `python -B evaluate_rag.py` |
| Task 8 memory | `memory_demo.md` | Already recorded |
| Task 10 guardrails | `task10_guardrails.txt` | Run the three guardrail commands |
| Tasks 11–12 API/logging | `task11_12_api_logging.txt` | Start Uvicorn, call `/ask`, inspect `requests.jsonl` |
| Task 13 triad | `task13_triad.txt` | `python -B evaluate_triad.py` |
| Task 14 MCP | `task14_mcp.txt` | Start server, run `python -B mcp_client.py` |
| Task 15 checkpoint | `task15_checkpoint.txt` | `python -B checkpoint_demo.py` |
| Task 16 resilience | `task16_resilience.txt` | `python -B resilience.py` |

Runtime files such as `requests.jsonl` and `checkpoints.sqlite` remain ignored and should not be committed as source artifacts.
