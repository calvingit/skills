import json
import tempfile
import unittest
from pathlib import Path

from loopx.worker.artifacts import save


class WorkerArtifactTests(unittest.TestCase):
    def test_save_writes_raw_output_to_task_local_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = save(Path(directory), result={"outcome": "completed"}, stdout="report", stderr="debug", returncode=0)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["result"]["outcome"], "completed")
            self.assertEqual(payload["raw"]["stdout"], "report")
            self.assertEqual(path.parent.parent.name, ".loop")


if __name__ == "__main__":
    unittest.main()
