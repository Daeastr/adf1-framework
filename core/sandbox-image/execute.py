import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python execute.py <instruction_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        instruction = json.load(f)

    print(f"Sandboxed execution: {instruction['action']}")

if __name__ == "__main__":
    main()

