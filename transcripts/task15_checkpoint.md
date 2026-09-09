# Task 15 manual transcript

Command:

```powershell
.\\.venv\\Scripts\\python.exe -B checkpoint_demo.py
```

Result:

```text
Paused checkpoint state: {'completed': ['node_a', 'node_b']}
Resumed completed state: {'completed': ['node_a', 'node_b', 'node_c', 'node_d']}
Checkpoint reused node_a and node_b: True
```

The same thread resumed from SQLite without re-executing the completed nodes.
