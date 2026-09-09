"""Tests for Task 15 SQLite checkpointing."""

import tempfile
import unittest
from pathlib import Path

from checkpoint_demo import run_checkpoint_demo


class CheckpointDemoTests(unittest.TestCase):
    def test_pause_and_resume_same_thread(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paused, resumed = run_checkpoint_demo(str(Path(directory) / "checkpoints.sqlite"))
        self.assertEqual(paused["completed"], ["node_a", "node_b"])
        self.assertEqual(resumed["completed"], ["node_a", "node_b", "node_c"])


if __name__ == "__main__":
    unittest.main()
