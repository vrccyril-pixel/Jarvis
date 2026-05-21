import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from jarvis_runner import run_agent


ROOT = Path(__file__).resolve().parents[1]


class JarvisSmokeTests(unittest.TestCase):
    def test_registry_is_readable(self):
        registry_path = ROOT / "agents_registry.json"
        with registry_path.open("r", encoding="utf-8") as handle:
            registry = json.load(handle)

        self.assertIsInstance(registry, dict)

    def test_registry_entries_point_to_existing_agents(self):
        registry_path = ROOT / "agents_registry.json"
        with registry_path.open("r", encoding="utf-8") as handle:
            registry = json.load(handle)

        missing = []
        for key, value in registry.items():
            if key.startswith("_") or not isinstance(value, dict):
                continue
            agent_path = ROOT / "agents" / Path(*key.split("/"))
            if not agent_path.is_file():
                missing.append(key)

        self.assertEqual(missing, [])

    def test_web_search_placeholder_runs(self):
        with redirect_stdout(StringIO()):
            success, output = run_agent("web", "web_search.py", ["test recherche"])

        self.assertTrue(success, output)
        self.assertIn("Agent web_search non implémenté", output)

    def test_unregistered_coder_agent_is_blocked(self):
        with redirect_stdout(StringIO()):
            success, output = run_agent("system", "coder_agent.py")

        self.assertFalse(success, output)
        self.assertIn("non déclaré dans agents_registry.json", output)

    def test_jarvis_starts_and_quits(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "jarvis_main.py")],
            input=b"quit\n",
            capture_output=True,
            cwd=ROOT,
            timeout=60,
        )

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        self.assertEqual(result.returncode, 0, stdout + stderr)
        self.assertIn("Jarvis", stdout)


if __name__ == "__main__":
    unittest.main()
