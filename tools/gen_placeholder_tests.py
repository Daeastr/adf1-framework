import json
import os

ACTION_MAP_PATH = "tests/action_map.json"
PLACEHOLDER_DIR = "tests/actions"

def load_action_map():
    with open(ACTION_MAP_PATH, "r") as f:
        return json.load(f)

def ensure_placeholder(action_name):
    test_path = os.path.join(PLACEHOLDER_DIR, f"test_{action_name}.py")
    if not os.path.exists(test_path):
        with open(test_path, "w") as f:
            f.write(f"# Placeholder test for '{action_name}'\n")
            f.write("def test_placeholder():\n")
            f.write("    assert True  # TODO: replace with real test\n")
        print(f"Created: {test_path}")
    else:
        print(f"Exists: {test_path}")

def main():
    os.makedirs(PLACEHOLDER_DIR, exist_ok=True)
    action_map = load_action_map()
    for action in action_map:
        ensure_placeholder(action)

if __name__ == "__main__":
    main()
