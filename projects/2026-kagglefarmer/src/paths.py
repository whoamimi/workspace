from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / ".output"

print("ROOT DIRECTORY:", ROOT_DIR, "OUTPUT DIRECTORY:", DATA_DIR)
