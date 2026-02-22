from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uuid
import shutil

# -----------------------------
# Your existing modules
# -----------------------------
from ingestion.file_loader import load_file
from ingestion.csv_excel_to_sqlite import dataframe_to_sqlite
from ingestion.schema_utils import get_table_schema
from ingestion.db_config import DB_PATH
from ingestion.export_utils import export_table

from agent.sql_agent import generate_sql
from agent.sql_executor import execute_sql





app = FastAPI(title="Data Automation API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

TABLE_NAME = "dataset"


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# 1️⃣ HEALTH CHECK
# ==========================================================
# @app.get("/")
# def health():
#     return {"status": "API is running"}

@app.get("/health")
def health():
    return {"status": "API is running"}


# ==========================================================
# 2️⃣ UPLOAD DATASET
# ==========================================================
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    delimiter: str = Form(None)
):
    try:
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in [".csv", ".xlsx", ".txt"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Save file
        unique_name = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = UPLOAD_DIR / unique_name

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Normalize delimiter
        delimiter_map = {
            "comma": ",",
            "tab": "\t",
            "pipe": "|",
            "semicolon": ";"
        }

        parsed_delimiter = delimiter_map.get(delimiter, None)

        # Load DataFrame
        df = load_file(file_path, delimiter=parsed_delimiter)

        # Store in SQLite
        dataframe_to_sqlite(df, TABLE_NAME)

        schema = get_table_schema(TABLE_NAME)

        return {
            "message": "Dataset uploaded successfully",
            "rows": len(df),
            "columns": list(df.columns),
            "schema": schema
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 3️⃣ GENERATE + EXECUTE SQL
# ==========================================================
# @app.post("/query")
# def run_query(payload: dict):
#     try:
#         if not DB_PATH.exists():
#             raise HTTPException(status_code=400, detail="No dataset uploaded")

#         user_query = payload.get("query")

#         if not user_query:
#             raise HTTPException(status_code=400, detail="Query is required")

#         sql = generate_sql(user_query, TABLE_NAME)

#         result = execute_sql(sql)

#         return {
#             "generated_sql": sql,
#             "result": {
#                 "columns": result["columns"],
#                 "rows": result["rows"]
#             }
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def run_query(payload: dict):
    try:
        if not DB_PATH.exists():
            raise HTTPException(status_code=400, detail="No dataset uploaded")

        user_query = payload.get("query")

        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")

        sql = generate_sql(user_query, TABLE_NAME)

        result = execute_sql(sql)

        return {
            "generated_sql": sql,
            "columns": result["columns"],
            "rows": result["rows"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# 4️⃣ DOWNLOAD UPDATED DATASET
# ==========================================================
@app.get("/download")
def download_dataset():
    try:
        if not DB_PATH.exists():
            raise HTTPException(status_code=400, detail="No dataset available")

        path = export_table(TABLE_NAME)

        return FileResponse(
            path=path,
            filename=path.name,
            media_type="text/csv"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 5️⃣ GET TABLE DATA (NO LLM)
# ==========================================================
@app.get("/table")
def get_table(limit: int = 100):
    try:
        if not DB_PATH.exists():
            raise HTTPException(status_code=400, detail="No dataset uploaded")

        from sqlalchemy import create_engine, text
        engine = create_engine(f"sqlite:///{DB_PATH}")

        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {TABLE_NAME} LIMIT {limit}"))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]

        return {
            "columns": columns,
            "rows": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()