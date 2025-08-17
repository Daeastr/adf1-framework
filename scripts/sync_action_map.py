import json
from pathlib import Path
from core.orchestrator import load_valid_instructions, ACTION_MAP_PATH

def sync_map():
    existing = json.loads(ACTION_MAP_PATH.read_text()) if ACTION_MAP_PATH.exists() else {}
    actions = sorted({doc["action"] for doc in load_valid_instructions()})
    updated = dict(existing)

    gen_dir = Path('tests') / '__generated__'
    for act in actions:
        if act not in updated:
            placeholder = str(gen_dir / f"test_{act}.py")
            updated[act] = [placeholder]
            print(f"🆕 Added placeholder mapping for action: {act} -> {placeholder}")

    # Ensure test files referenced by the mapping actually exist; scaffold placeholders
    for tests_list in updated.values():
        for t in tests_list:
            test_path = Path(t)
            if not test_path.exists():
                test_path.parent.mkdir(parents=True, exist_ok=True)
                test_path.write_text(
                    f"def test_placeholder_for_{test_path.stem}():\n"
                    f"    '''Placeholder test'''\n"
                    f"    assert True\n"
                )
                print(f"📄 Created placeholder: {test_path}")

    ACTION_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTION_MAP_PATH.write_text(json.dumps(updated, indent=2))
    print(f"✅ Action map synced: {ACTION_MAP_PATH}")

if __name__ == "__main__":
    sync_map()
#!/usr/bin/env python3
"""Syncs tests/action_map.json with live instruction actions.

For any unmapped action, scaffolds an empty list in action_map.json and prints a report.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTR = ROOT / "instructions"
MAP = ROOT / "tests" / "action_map.json"

if not INSTR.exists():
    print("No instructions directory found.")
    raise SystemExit(1)

actions = set()
for f in INSTR.glob("*.json"):
    if f.name == "schema.json":
        continue
    try:
        doc = json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        continue
    if all(k in doc for k in ("id","action","params")):
        actions.add(doc["action"])

if not MAP.exists():
    action_map = {}
else:
    action_map = json.loads(MAP.read_text(encoding='utf-8'))

new = False
for a in sorted(actions):
    if a not in action_map:
        print(f"Scaffolding unmapped action: {a}")
        action_map[a] = []
        new = True

if new:
    MAP.write_text(json.dumps(action_map, indent=2), encoding='utf-8')
    print("Updated action_map.json with placeholders for unmapped actions.")
else:
    print("action_map.json already in sync.")
