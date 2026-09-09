# Task 16 manual transcript

Command:

```powershell
.\\.venv\\Scripts\\python.exe -B resilience.py
```

Result:

```text
Retry demo: ('recovered', 3)
Node timeout: clean timeout
Global timeout: clean timeout
```

The transient operation recovered on its third attempt, and both timeout protections fired cleanly.
