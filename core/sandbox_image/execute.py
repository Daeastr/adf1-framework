import sys
import json
import os
import shutil


def apply_patch(patch):
    target_file = patch.get("target")
    new_content = patch.get("patch") or patch.get("content")

    if not target_file or new_content is None:
        print("Invalid patch format.")
        return

    # Backup original if it exists
    if os.path.exists(target_file):
        backup_path = f"{target_file}.bak"
        shutil.copyfile(target_file, backup_path)
        print(f"Backup created: {backup_path}")

    # Apply patch (replace file content)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Patch applied to: {target_file}")


def run_instruction(instruction_path: str):
    with open(instruction_path, "r", encoding="utf-8") as f:
        instruction = json.load(f)
    action = instruction.get("action")
    print(f"Sandboxed execution: {action}")
    # support both 'apply_patch' (dict patch) and 'replace' (direct target+patch)
    if action == "apply_patch":
        apply_patch(instruction.get("patch", {}))
    elif action == "replace":
        patch = {"target": instruction.get("target"), "patch": instruction.get("patch")}
        apply_patch(patch)


def main():
    if len(sys.argv) < 2:
        print("Usage: python execute.py <instruction_file>")
        sys.exit(1)

    run_instruction(sys.argv[1])


if __name__ == "__main__":
    main()


