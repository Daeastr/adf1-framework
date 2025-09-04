import subprocess
import tempfile
import json

def run_in_sandbox(instruction: dict) -> dict:
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(instruction, f)
        f.flush()
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{f.name}:/app/instruction.json",
            "sandbox-runner-image",  # Replace with your image name
            "python", "/app/execute.py", "/app/instruction.json"
        ]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            return {"status": "sandboxed", "output": output}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "output": e.output}
