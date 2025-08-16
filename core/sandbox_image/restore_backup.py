import os
import shutil

INSTRUCTION_DIR = "core/instructions"

def restore_backups():
    restored = []
    for file in os.listdir(INSTRUCTION_DIR):
        if file.endswith(".bak"):
            original = file[:-4]  # Strip .bak
            bak_path = os.path.join(INSTRUCTION_DIR, file)
            original_path = os.path.join(INSTRUCTION_DIR, original)

            shutil.copy2(bak_path, original_path)
            restored.append(original)

    if restored:
        print(f"✅ Restored: {', '.join(restored)}")
    else:
        print("No .bak files found.")

if __name__ == "__main__":
    restore_backups()
