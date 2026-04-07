import os
import shutil
from pathlib import Path

# Use a fixed temp directory for data
TEMP_DIR = Path("/tmp/ora_ai_data")

# Clean up on import if exists
if TEMP_DIR.exists():
    shutil.rmtree(TEMP_DIR)

TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Optional runtime data root for cloud deployments (Railway volume mount path).
# Falls back to temp dir for local development.
DATA_ROOT = Path(os.getenv("ORA_DATA_ROOT", str(TEMP_DIR))).expanduser().resolve()

DB_DIR = DATA_ROOT / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "datasets.db"
