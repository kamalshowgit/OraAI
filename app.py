# import streamlit as st
# from pathlib import Path
# import uuid

# # ------------------------
# # Ingestion imports
# # ------------------------
# from ingestion.file_loader import load_file
# from ingestion.csv_excel_to_sqlite import dataframe_to_sqlite
# from ingestion.schema_utils import (
#     get_table_schema,
#     list_all_tables
# )
# from ingestion.db_config import DB_PATH

# # ------------------------
# # SQL Agent imports
# # ------------------------
# from agent.sql_agent import generate_sql
# from agent.sql_executor import execute_sql


# # ------------------------
# # Streamlit Config
# # ------------------------
# st.set_page_config(
#     page_title="Data Automation – SQL Agent",
#     layout="centered"
# )

# st.title("📊 Data Automation Platform")
# st.caption("SQLite + Groq SQL Agent")

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# # ==========================================================
# # SECTION 1: DATABASE STATUS
# # ==========================================================
# st.subheader("🗄️ Database Status")

# st.info(f"SQLite DB Path: {DB_PATH}")
# st.info(f"Database Exists: {DB_PATH.exists()}")

# existing_tables = list_all_tables()
# st.write("### 📚 Available Tables")
# st.table(existing_tables if existing_tables else ["No datasets loaded yet"])

# st.divider()

# # ==========================================================
# # SECTION 2: FILE UPLOAD & INGESTION (SINGLE DB)
# # ==========================================================
# st.subheader("⬆️ Upload Dataset (CSV / Excel)")

# uploaded_file = st.file_uploader(
#     "Upload a CSV or Excel file",
#     type=["csv", "xlsx"]
# )

# if uploaded_file:
#     dataset_id = uuid.uuid4().hex[:8]
#     file_path = UPLOAD_DIR / f"{dataset_id}_{uploaded_file.name}"

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     df = load_file(file_path)

#     st.write("### 🔍 Data Preview")
#     st.dataframe(df.head())

#     table_name = "dataset"  # single-table mode (as decided)

#     if st.button("Store Dataset in SQLite"):
#         info = dataframe_to_sqlite(df, table_name)
#         schema = get_table_schema(table_name)

#         st.success("✅ Dataset stored successfully")

#         st.write("### 📐 SQL Schema")
#         st.table(schema)

# st.divider()

# # ==========================================================
# # SECTION 3: GROQ SQL AGENT
# # ==========================================================
# st.subheader("🧠 SQL Agent (Groq)")

# if not DB_PATH.exists():
#     st.warning("No database found. Please upload a dataset first.")
# else:
#     user_query = st.text_area(
#         "Ask a question about your data",
#         placeholder="Example: Show average monthly charges by churn"
#     )

#     if st.button("Run SQL Agent"):
#         try:
#             sql_query = generate_sql(
#                 user_query=user_query,
#                 table_name="dataset"
#             )

#             st.write("### 🧾 Generated SQL")
#             st.code(sql_query, language="sql")

#             result = execute_sql(sql_query)

#             if result["rows"]:
#                 st.write("### 📊 Query Result")
#                 st.dataframe(
#                     result["rows"],
#                     use_container_width=True
#                 )
#             else:
#                 st.info("Query executed successfully, but returned no rows.")

#         except Exception as e:
#             st.error(f"❌ Error: {str(e)}")







# import streamlit as st
# from pathlib import Path
# import uuid

# # ------------------------
# # Ingestion imports
# # ------------------------
# from ingestion.file_loader import load_file
# from ingestion.csv_excel_to_sqlite import dataframe_to_sqlite
# from ingestion.schema_utils import (
#     get_table_schema,
#     list_all_tables
# )
# from ingestion.db_config import DB_PATH

# # ------------------------
# # SQL Agent imports
# # ------------------------
# from agent.sql_agent import generate_sql
# from agent.sql_executor import execute_sql

# # ------------------------
# # Export
# # ------------------------
# from ingestion.export_utils import export_table


# # ------------------------
# # Streamlit Config
# # ------------------------
# st.set_page_config(
#     page_title="Data Automation – SQL Agent",
#     layout="centered"
# )

# st.title("📊 Data Automation Platform")
# st.caption("CSV / Excel → SQLite → LLM-powered SQL → Updated Dataset")

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# # ==========================================================
# # SECTION 1: DATABASE STATUS
# # ==========================================================
# st.subheader("🗄️ Database Status")

# st.info(f"SQLite DB Path: {DB_PATH}")
# st.info(f"Database Exists: {DB_PATH.exists()}")

# existing_tables = list_all_tables()
# st.write("### 📚 Available Tables")
# st.table(existing_tables if existing_tables else ["No datasets loaded yet"])

# st.divider()

# # ==========================================================
# # SECTION 2: FILE UPLOAD & INGESTION
# # ==========================================================
# st.subheader("⬆️ Upload Dataset (CSV / Excel)")

# uploaded_file = st.file_uploader(
#     "Upload a CSV or Excel file",
#     type=["csv", "xlsx"]
# )

# if uploaded_file:
#     dataset_id = uuid.uuid4().hex[:8]
#     file_path = UPLOAD_DIR / f"{dataset_id}_{uploaded_file.name}"

#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     df = load_file(file_path)

#     st.write("### 🔍 Data Preview")
#     st.dataframe(df.head(), use_container_width=True)

#     table_name = "dataset"

#     if st.button("📥 Store Dataset in SQLite"):
#         dataframe_to_sqlite(df, table_name)
#         schema = get_table_schema(table_name)

#         st.success("✅ Dataset stored successfully")

#         st.write("### 📐 SQL Schema")
#         st.table(schema)

# st.divider()

# # ==========================================================
# # SECTION 3: LLM SQL AGENT (READ + WRITE)
# # ==========================================================
# st.subheader("🧠 LLM SQL Agent (Read + Write)")

# if not DB_PATH.exists():
#     st.warning("No database found. Please upload a dataset first.")
# else:
#     user_query = st.text_area(
#         "Describe what you want to do with the data",
#         placeholder=(
#             "Examples:\n"
#             "- Handle missing values intelligently\n"
#             "- Remove duplicate customers\n"
#             "- Add a churn risk column\n"
#             "- Clean data and show churn rate by contract type"
#         ),
#         height=160
#     )

#     if st.button("🚀 Run SQL Agent"):
#         try:
#             sql_query = generate_sql(
#                 user_query=user_query,
#                 table_name="dataset"
#             )

#             st.write("### 🧾 Generated SQL")
#             st.code(sql_query, language="sql")

#             result = execute_sql(sql_query)

#             if result["rows"] is not None:
#                 st.write("### 📊 Query Result")
#                 st.dataframe(
#                     result["rows"],
#                     use_container_width=True
#                 )
#             else:
#                 st.success("✅ SQL executed successfully. Dataset updated.")

#         except Exception as e:
#             st.error(f"❌ Error: {str(e)}")

#     st.divider()

#     # ======================================================
#     # SECTION 4: DOWNLOAD UPDATED DATASET
#     # ======================================================
#     st.subheader("⬇️ Download Updated Dataset")

#     if st.button("Download Latest CSV"):
#         path = export_table("dataset")

#         with open(path, "rb") as f:
#             st.download_button(
#                 label="📥 Download CSV",
#                 data=f,
#                 file_name=path.name,
#                 mime="text/csv"
#             )



import streamlit as st
from pathlib import Path
import uuid

# ------------------------
# Ingestion imports
# ------------------------
from ingestion.file_loader import load_file
from ingestion.csv_excel_to_sqlite import dataframe_to_sqlite
from ingestion.schema_utils import (
    get_table_schema,
    list_all_tables
)
from ingestion.db_config import DB_PATH

# ------------------------
# SQL Agent imports
# ------------------------
from agent.sql_agent import generate_sql
from agent.sql_executor import execute_sql

# ------------------------
# Export
# ------------------------
from ingestion.export_utils import export_table

# ------------------------
# Streamlit Config
# ------------------------
st.set_page_config(
    page_title="Data Automation – SQL Agent",
    layout="centered"
)

st.title("📊 Data Automation Platform")
st.caption("CSV / Excel / TXT → SQLite → LLM-powered SQL → Updated Dataset")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==========================================================
# SECTION 1: DATABASE STATUS
# ==========================================================
st.subheader("🗄️ Database Status")

st.info(f"SQLite DB Path: {DB_PATH}")
st.info(f"Database Exists: {DB_PATH.exists()}")

existing_tables = list_all_tables()
st.write("### 📚 Available Tables")
st.table(existing_tables if existing_tables else ["No datasets loaded yet"])

st.divider()

# ==========================================================
# SECTION 2: FILE UPLOAD & INGESTION
# ==========================================================
st.subheader("⬆️ Upload Dataset (CSV / Excel / TXT)")

uploaded_file = st.file_uploader(
    "Upload a CSV, Excel or TXT file",
    type=["csv", "xlsx", "txt"]
)

delimiter = None

if uploaded_file:
    dataset_id = uuid.uuid4().hex[:8]
    file_path = UPLOAD_DIR / f"{dataset_id}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # -----------------------
    # TXT delimiter options
    # -----------------------
    if uploaded_file.name.lower().endswith(".txt"):
        st.write("### TXT Parsing Options")

        delimiter_option = st.selectbox(
            "Select delimiter (if structured file)",
            [
                "None (Unstructured text)",
                "Comma (,)",
                "Tab (\\t)",
                "Pipe (|)",
                "Semicolon (;)"
            ]
        )

        delimiter_map = {
            "Comma (,)": ",",
            "Tab (\\t)": "\t",
            "Pipe (|)": "|",
            "Semicolon (;)": ";"
        }

        delimiter = delimiter_map.get(delimiter_option, None)

    # -----------------------
    # Load file
    # -----------------------
    try:
        df = load_file(file_path, delimiter=delimiter)

        st.write("### 🔍 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        table_name = "dataset"

        if st.button("📥 Store Dataset in SQLite"):
            dataframe_to_sqlite(df, table_name)
            schema = get_table_schema(table_name)

            st.success("✅ Dataset stored successfully")
            st.write("### 📐 SQL Schema")
            st.table(schema)

    except Exception as e:
        st.error(f"❌ {str(e)}")

st.divider()

# ==========================================================
# SECTION 3: LLM SQL AGENT
# ==========================================================
st.subheader("🧠 LLM SQL Agent (Read + Write)")

if not DB_PATH.exists():
    st.warning("No database found. Please upload a dataset first.")
else:
    user_query = st.text_area(
        "Describe what you want to do with the data",
        placeholder=(
            "Examples:\n"
            "- Handle missing values intelligently\n"
            "- Remove duplicate customers\n"
            "- Add a churn risk column\n"
            "- Clean data and show churn rate by contract type"
        ),
        height=160
    )

    if st.button("🚀 Run SQL Agent"):
        try:
            sql_query = generate_sql(
                user_query=user_query,
                table_name="dataset"
            )

            st.write("### 🧾 Generated SQL")
            st.code(sql_query, language="sql")

            result = execute_sql(sql_query)

            if result["rows"] is not None:
                st.write("### 📊 Query Result")
                st.dataframe(result["rows"], use_container_width=True)
            else:
                st.success("✅ SQL executed successfully. Dataset updated.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.divider()

    # ======================================================
    # SECTION 4: DOWNLOAD UPDATED DATASET
    # ======================================================
    st.subheader("⬇️ Download Updated Dataset")

    if st.button("Download Latest CSV"):
        path = export_table("dataset")

        with open(path, "rb") as f:
            st.download_button(
                label="📥 Download CSV",
                data=f,
                file_name=path.name,
                mime="text/csv"
            )
