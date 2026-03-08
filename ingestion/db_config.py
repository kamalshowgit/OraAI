import os
from pathlib import Path

# Absolute project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Optional runtime data root for cloud deployments (Railway volume mount path).
# Falls back to project root for local development.
DATA_ROOT = Path(os.getenv("ORA_DATA_ROOT", str(PROJECT_ROOT))).expanduser().resolve()

DB_DIR = DATA_ROOT / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "datasets.db"
