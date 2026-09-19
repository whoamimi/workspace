# delete
from pathlib import Path
import subprocess

lm_dir = BASELINE_MODEL_PATH

# Ensure script is executable (may be no-op in read-only dirs)
subprocess.run(["chmod", "+x", "setup_lm.sh"], cwd=str(lm_dir), check=False)

# Run the script with lm_dir as working directory
result = subprocess.run(
    ["bash", "setup_lm.sh"],
    cwd=str(lm_dir),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

print("Return code:", result.returncode)
print("STDOUT:\n", result.stdout)
print("STDERR:\n", result.stderr)
