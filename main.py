import os
from pathlib import Path
import re
import shutil
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import create_engine, text

from agent.sql_agent import generate_sql, is_safe_sql
from agent.sql_executor import execute_sql
from ingestion.csv_excel_to_sqlite import dataframe_to_sqlite
from ingestion.db_config import DB_PATH, DATA_ROOT
from ingestion.export_utils import export_table
from ingestion.file_loader import load_file
from ingestion.schema_utils import get_table_schema, list_all_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Only cleanup /tmp on local development, not in production
    is_production = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("HEROKU_APP_NAME")
    if not is_production:
        shutil.rmtree("/tmp/ora_ai_data", ignore_errors=True)

app = FastAPI(title="ORA AI Data Platform API", lifespan=lifespan)

UPLOAD_DIR = DATA_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TABLE_NAME = "dataset"
TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DELIMITER_MAP = {
    "comma": ",",
    "tab": "\t",
    "pipe": "|",
    "semicolon": ";",
}

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials="*" not in ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def normalize_table_name(value: str | None, fallback: str = DEFAULT_TABLE_NAME) -> str:
    name = (value or fallback).strip().replace(" ", "_")

    if not TABLE_NAME_PATTERN.match(name):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid table_name. Use letters, numbers and underscores only, "
                "starting with a letter or underscore."
            ),
        )

    return name


def ensure_database_exists():
    if not DB_PATH.exists():
        raise HTTPException(status_code=400, detail="No dataset or database connected")


def resolve_table_name(requested_table: str | None = None) -> str:
    tables = list_all_tables()

    if not tables:
        raise HTTPException(status_code=400, detail="No tables available in the database")

    if requested_table:
        candidate = requested_table.strip()
        if candidate in tables:
            return candidate

        normalized_candidate = candidate.replace(" ", "_")
        if normalized_candidate in tables:
            return normalized_candidate

        raise HTTPException(status_code=404, detail=f"Table '{candidate}' not found")

    if DEFAULT_TABLE_NAME in tables:
        return DEFAULT_TABLE_NAME

    return tables[0]


def get_default_active_table(tables: list[str]) -> str | None:
    if not tables:
        return None
    return DEFAULT_TABLE_NAME if DEFAULT_TABLE_NAME in tables else tables[0]


def looks_like_sql(statement: str) -> bool:
    return bool(
        re.match(
            r"^\s*(SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|REPLACE|PRAGMA|VACUUM|EXPLAIN|BEGIN|COMMIT|ROLLBACK)\b",
            statement,
            flags=re.IGNORECASE,
        )
    )


@app.get("/health")
def health():
    tables = list_all_tables() if DB_PATH.exists() else []
    active_table = get_default_active_table(tables)

    return {
        "status": "ORA AI API is running",
        "database_exists": DB_PATH.exists(),
        "tables": tables,
        "active_table": active_table,
    }


@app.get("/debug")
def debug_info():
    """Debug endpoint for production troubleshooting"""
    try:
        return {
            "environment": "production" if os.getenv("RENDER") else "development",
            "data_root": str(DATA_ROOT),
            "db_path": str(DB_PATH),
            "upload_dir": str(UPLOAD_DIR),
            "dirs_exist": {
                "data_root": DATA_ROOT.exists(),
                "upload_dir": UPLOAD_DIR.exists(),
                "db_dir": DB_PATH.parent.exists(),
                "db_file": DB_PATH.exists(),
            },
            "upload_dir_contents": list(UPLOAD_DIR.iterdir()) if UPLOAD_DIR.exists() else [],
            "tables": list_all_tables() if DB_PATH.exists() else [],
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    delimiter: str | None = Form(None),
    table_name: str | None = Form(None),
):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".csv", ".xlsx", ".txt"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = UPLOAD_DIR / unique_name

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        parsed_delimiter = DELIMITER_MAP.get(delimiter, None)
        df = load_file(file_path, delimiter=parsed_delimiter)

        target_table = normalize_table_name(table_name)
        dataframe_to_sqlite(df, target_table)
        schema = get_table_schema(target_table)

        return {
            "message": "Dataset uploaded successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "schema": schema,
            "table_name": target_table,
            "tables": list_all_tables(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/connect/sqlite")
async def connect_sqlite_db(
    file: UploadFile = File(...),
    active_table: str | None = Form(None),
):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [".db", ".sqlite", ".sqlite3"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported DB file type. Use .db, .sqlite or .sqlite3",
            )

        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        uploaded_path = UPLOAD_DIR / unique_name

        with uploaded_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(uploaded_path, DB_PATH)
        uploaded_path.unlink(missing_ok=True)

        tables = list_all_tables()
        if not tables:
            raise HTTPException(status_code=400, detail="Connected database contains no tables")

        resolved_table = resolve_table_name(active_table)
        schema = get_table_schema(resolved_table)

        return {
            "message": "Database connected successfully",
            "database_path": str(DB_PATH),
            "tables": tables,
            "active_table": resolved_table,
            "schema": schema,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/tables")
def get_tables():
    if not DB_PATH.exists():
        return {"tables": [], "active_table": None}

    tables = list_all_tables()
    active_table = get_default_active_table(tables)
    return {"tables": tables, "active_table": active_table}


@app.get("/schema")
def get_schema(table_name: str | None = None):
    try:
        ensure_database_exists()
        resolved_table = resolve_table_name(table_name)
        schema = get_table_schema(resolved_table)
        return {"table_name": resolved_table, "schema": schema}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/schemas")
def get_all_schemas():
    try:
        ensure_database_exists()
        tables = list_all_tables()
        return {
            "tables": tables,
            "schemas": [
                {
                    "table_name": table_name,
                    "schema": get_table_schema(table_name),
                }
                for table_name in tables
            ],
            "active_table": get_default_active_table(tables),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/query")
def run_query(payload: dict):
    try:
        ensure_database_exists()

        user_query = (payload.get("query") or "").strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")

        selected_table = payload.get("table_name")
        resolved_table = resolve_table_name(selected_table) if selected_table else None
        try:
            sql = generate_sql(user_query, resolved_table)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"AI SQL generation failed: {str(exc)}") from exc
        result = execute_sql(sql)
        tables = list_all_tables()
        active_table = resolved_table or get_default_active_table(tables)

        has_result_set = bool(result["columns"] and result["rows"] is not None)
        return {
            "mode": "ai",
            "generated_sql": sql,
            "table_name": active_table,
            "columns": result["columns"] or [],
            "rows": result["rows"] or [],
            "has_result_set": has_result_set,
            "tables": tables,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/sql")
def run_sql(payload: dict):
    try:
        ensure_database_exists()

        input_text = (payload.get("sql") or payload.get("instruction") or "").strip()
        if not input_text:
            raise HTTPException(status_code=400, detail="SQL or instruction is required")

        input_type = (payload.get("input_type") or "sql").strip().lower()
        if input_type not in {"sql", "english", "auto"}:
            raise HTTPException(status_code=400, detail="input_type must be one of: sql, english, auto")

        requested_active_table = (payload.get("active_table") or "").strip()
        resolved_table = resolve_table_name(requested_active_table) if requested_active_table else None

        if input_type == "auto":
            input_type = "sql" if looks_like_sql(input_text) else "english"

        generated_sql = None
        executable_sql = input_text

        if input_type == "english":
            try:
                generated_sql = generate_sql(input_text, resolved_table)
            except RuntimeError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"AI SQL generation failed: {str(exc)}") from exc
            executable_sql = generated_sql

        if not is_safe_sql(executable_sql):
            raise HTTPException(
                status_code=400,
                detail="Unsafe SQL detected (blocked keywords: ATTACH, DETACH, PRAGMA, DROP DATABASE, VACUUM)",
            )

        result = execute_sql(executable_sql)
        tables = list_all_tables()
        active_table = resolved_table if resolved_table in tables else get_default_active_table(tables)

        has_result_set = bool(result["columns"] and result["rows"] is not None)
        return {
            "mode": "sql",
            "input_type": input_type,
            "input_text": input_text,
            "generated_sql": generated_sql,
            "executed_sql": executable_sql,
            "table_name": active_table,
            "columns": result["columns"] or [],
            "rows": result["rows"] or [],
            "has_result_set": has_result_set,
            "tables": tables,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/download")
def download_dataset(table_name: str | None = None):
    try:
        ensure_database_exists()
        resolved_table = resolve_table_name(table_name)
        path = export_table(resolved_table)

        return FileResponse(
            path=path,
            filename=path.name,
            media_type="text/csv",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/table")
def get_table(
    limit: int = Query(default=100, ge=1, le=5000),
    table_name: str | None = None,
):
    try:
        ensure_database_exists()
        resolved_table = resolve_table_name(table_name)
        engine = get_engine()

        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT * FROM {quote_identifier(resolved_table)} LIMIT :limit"),
                {"limit": limit},
            )
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]

        return {
            "table_name": resolved_table,
            "columns": columns,
            "rows": rows,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def serve_landing():
    with open("index.html", "r", encoding="utf-8") as landing_file:
        return landing_file.read()


@app.get("/app", response_class=HTMLResponse)
def serve_frontend():
    with open("frontend.html", "r", encoding="utf-8") as frontend_file:
        return frontend_file.read()
