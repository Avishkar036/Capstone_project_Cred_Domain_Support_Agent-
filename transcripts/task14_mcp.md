# Task 14 manual transcript

The MCP server was started separately with `mcp_server.py`, and the client was run in a second process:

```powershell
.\\.venv\\Scripts\\python.exe -B mcp_client.py
```

The client successfully called the MCP tool for two record IDs:

```text
LA-0001: status=Under Review, loan_amount_inr=1298538, escalation_score=0.76, recommend_escalation=True
LA-0002: status=Approved, loan_amount_inr=1154898, escalation_score=0.2533, recommend_escalation=False
```

Both responses returned `is_error=False` from the MCP server.
