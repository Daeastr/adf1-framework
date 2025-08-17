import os
import sys
import json
import shutil
from pathlib import Path

# Ensure repo root is on sys.path so `core` package can be imported reliably
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))

from core.sandbox_image.execute import run_instruction
from core.sandbox_image.restore_backup import restore_backups

INSTRUCTION_FILE = "core/instructions/demo.json"
TARGET_FILE = "core/module.py"

def setup_instruction():
    os.makedirs("core/instructions", exist_ok=True)
    os.makedirs("core", exist_ok=True)

    with open(INSTRUCTION_FILE, "w") as f:
        json.dump({
            "action": "replace",
            "target": TARGET_FILE,
            "patch": "def new_logic(): pass"
        }, f)

    with open(TARGET_FILE, "w") as f:
        f.write("def old_logic(): pass")

def cleanup():
    for path in [INSTRUCTION_FILE, TARGET_FILE, TARGET_FILE + ".bak"]:
        if os.path.exists(path):
            os.remove(path)

def test_patch_and_restore():
    setup_instruction()
    run_instruction(INSTRUCTION_FILE)

    with open(TARGET_FILE) as f:
        assert "new_logic" in f.read(), "Patch failed"

    restore_backups()

    with open(TARGET_FILE) as f:
        assert "old_logic" in f.read(), "Restore failed"

    print("✅ Patch and restore test passed.")

if __name__ == "__main__":
    test_patch_and_restore()
    cleanup()
