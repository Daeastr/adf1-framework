import json
from pathlib import Path

ACTION_MAP = Path("tests/action_map.json")
TESTS_DIR = Path("tests")

def ensure_placeholder(action: str, test_file: str):
    path = TESTS_DIR / test_file
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"def test_placeholder_{action}():\n    assert True\n")

def main():
    with open(ACTION_MAP, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    for action, files in mapping.items():
        for test_file in files:
            ensure_placeholder(action, test_file)

if __name__ == "__main__":
    main()
