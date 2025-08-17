import os
import shutil
from pathlib import Path


def restore_backups():
    """Search the repository tree for .bak files and restore them in-place.

    This handles backups created next to target files (e.g., core/module.py.bak)
    so that restore_backups correctly replaces the original file with the
    backed-up content.
    """
    repo_root = Path(__file__).resolve().parents[2]
    restored = []

    for dirpath, dirnames, filenames in os.walk(repo_root):
        for fname in filenames:
            if fname.endswith('.bak'):
                bak_path = os.path.join(dirpath, fname)
                original_name = fname[:-4]
                original_path = os.path.join(dirpath, original_name)

                try:
                    shutil.copy2(bak_path, original_path)
                    rel = os.path.relpath(original_path, repo_root)
                    restored.append(rel)
                except Exception:
                    # ignore individual restore failures
                    continue

    if restored:
        print(f"✅ Restored: {', '.join(restored)}")
    else:
        print("No .bak files found.")


if __name__ == "__main__":
    restore_backups()
