import sys
import json
import os
import shutil

def apply_patch(patch):
    target_file = patch.get("target")
    new_content = patch.get("content")

    if not target_file or not new_content:
        print("Invalid patch format.")
        return

    # Backup original
    backup_path = f"{target_file}.bak"
    shutil.copyfile(target_file, backup_path)
    print(f"Backup created: {backup_path}")

    # Apply patch
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Patch applied to: {target_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python execute.py <instruction_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        instruction = json.load(f)

    action = instruction.get("action")
    print(f"Sandboxed execution: {action}")

    if action == "apply_patch":
        apply_patch(instruction.get("patch", {}))

if __name__ == "__main__":
    main()


