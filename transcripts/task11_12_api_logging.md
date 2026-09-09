# Tasks 11–12 manual transcript

The API was started with:

```powershell
.\\.venv\\Scripts\\python.exe -m uvicorn api:app
```

A supported KYC request returned HTTP 200, and the deliberate PII-only query returned the controlled HTTP 422 groundedness response.

Representative final log entries from `requests.jsonl`:

```json
{"trace_id":"1e1f4616-a194-45d9-a154-dd220af9651e","method":"POST","path":"/ask","request_text":"What documents are needed for KYC?","status_code":200,"elapsed_ms":10728.243}
{"trace_id":"9d7ddf62-3460-4775-88ad-b6c0d88851eb","method":"POST","path":"/ask","request_text":"PAN [PAN-MASKED] account [ACCOUNT-MASKED]","status_code":422,"elapsed_ms":10317.622}
```

The raw PAN and account values do not appear in the log. Each entry contains a trace ID, HTTP method, path, status code, and elapsed time.
