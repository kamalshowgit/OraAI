import os
from pathlib import Path

# Production: Use environment variable or persistent app data directory
# Local development: Use /tmp with cleanup
IS_PRODUCTION = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HEROKU_APP_NAME")

if IS_PRODUCTION:
    # Production: Use app-relative persistent directory or environment variable
    DATA_ROOT = Path(os.getenv("ORA_DATA_ROOT", "./data")).expanduser().resolve()
else:
    # Local development: Use ephemeral /tmp directory, but avoid destructive cleanup
    # on import so reloads do not remove directories from a live worker process.
    TEMP_DIR = Path("/tmp/ora_ai_data")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    DATA_ROOT = Path(os.getenv("ORA_DATA_ROOT", str(TEMP_DIR))).expanduser().resolve()

# Ensure directories exist
DB_DIR = DATA_ROOT / "db"
EXPORT_DIR = DATA_ROOT / "exports"
UPLOAD_DIR = DATA_ROOT / "uploads"

DB_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "datasets.db"
