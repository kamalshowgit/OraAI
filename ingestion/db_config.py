from pathlib import Path

# Absolute project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DB_DIR = PROJECT_ROOT / "db"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "datasets.db"
