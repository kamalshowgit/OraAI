import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import agent.sql_executor as sql_executor
import ingestion.csv_excel_to_sqlite as csv_excel_to_sqlite
import ingestion.db_config as db_config
import ingestion.export_utils as export_utils
import ingestion.schema_utils as schema_utils
import main


CSV_FIXTURE = b"region,amount\nWest,10\nEast,20\nNorth,30\n"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    data_root = tmp_path / "ora-data"
    db_dir = data_root / "db"
    export_dir = data_root / "exports"
    upload_dir = data_root / "uploads"
    db_path = db_dir / "datasets.db"

    for directory in (db_dir, export_dir, upload_dir):
        directory.mkdir(parents=True, exist_ok=True)

    path_overrides = [
        (db_config, "DATA_ROOT", data_root),
        (db_config, "DB_PATH", db_path),
        (db_config, "EXPORT_DIR", export_dir),
        (db_config, "UPLOAD_DIR", upload_dir),
        (main, "DATA_ROOT", data_root),
        (main, "DB_PATH", db_path),
        (main, "EXPORT_DIR", export_dir),
        (main, "UPLOAD_DIR", upload_dir),
        (csv_excel_to_sqlite, "DB_PATH", db_path),
        (schema_utils, "DB_PATH", db_path),
        (export_utils, "DB_PATH", db_path),
        (export_utils, "DATA_ROOT", data_root),
        (sql_executor, "DB_PATH", db_path),
    ]

    for module, attr, value in path_overrides:
        monkeypatch.setattr(module, attr, value)

    with TestClient(main.app) as test_client:
        yield test_client


def upload_csv(client: TestClient, table_name: str = "sales"):
    return client.post(
        "/upload",
        files={"file": ("sales.csv", CSV_FIXTURE, "text/csv")},
        data={"table_name": table_name},
    )


def create_sqlite_database(path: Path):
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE imported_data (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO imported_data (name) VALUES ('Ada')")
        conn.execute("INSERT INTO imported_data (name) VALUES ('Grace')")
        conn.commit()


def test_health_check(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ORA AI API is running"
    assert data["database_exists"] is False
    assert data["tables"] == []
    assert data["active_table"] is None


def test_html_routes_serve_expected_pages(client: TestClient):
    landing = client.get("/")
    app_page = client.get("/app")

    assert landing.status_code == 200
    assert "text/html" in landing.headers["content-type"]
    assert "ORA AI" in landing.text
    assert 'href="app"' in landing.text

    assert app_page.status_code == 200
    assert "text/html" in app_page.headers["content-type"]
    assert "ORA AI Data Workspace" in app_page.text
    assert "Visualize Table" in app_page.text
    assert "Preferred Table (optional context)" in app_page.text


def test_tables_are_empty_without_database(client: TestClient):
    response = client.get("/tables")

    assert response.status_code == 200
    assert response.json() == {"tables": [], "active_table": None}


def test_upload_schema_table_and_download_routes(client: TestClient):
    upload_response = upload_csv(client)
    upload_payload = upload_response.json()

    assert upload_response.status_code == 200
    assert upload_payload["table_name"] == "sales"
    assert upload_payload["rows"] == 3
    assert upload_payload["tables"] == ["sales"]

    tables_response = client.get("/tables")
    assert tables_response.status_code == 200
    assert tables_response.json() == {"tables": ["sales"], "active_table": "sales"}

    schema_response = client.get("/schema", params={"table_name": "sales"})
    assert schema_response.status_code == 200
    assert schema_response.json()["table_name"] == "sales"
    assert [column["name"] for column in schema_response.json()["schema"]] == ["region", "amount"]

    table_response = client.get("/table", params={"table_name": "sales", "limit": 2})
    table_payload = table_response.json()
    assert table_response.status_code == 200
    assert table_payload["table_name"] == "sales"
    assert table_payload["columns"] == ["region", "amount"]
    assert table_payload["rows"] == [["West", 10], ["East", 20]]

    download_response = client.get("/download", params={"table_name": "sales"})
    assert download_response.status_code == 200
    assert "text/csv" in download_response.headers["content-type"]
    assert "attachment" in download_response.headers["content-disposition"]
    assert "region,amount" in download_response.text
    assert "North,30" in download_response.text


def test_upload_recreates_missing_upload_directory(client: TestClient):
    main.UPLOAD_DIR.rmdir()

    response = upload_csv(client, table_name="recreated_upload")

    assert response.status_code == 200
    payload = response.json()
    assert payload["table_name"] == "recreated_upload"
    assert payload["rows"] == 3
    assert main.UPLOAD_DIR.exists() is True


def test_connect_sqlite_route(client: TestClient, tmp_path):
    source_db = tmp_path / "external.sqlite"
    create_sqlite_database(source_db)

    with source_db.open("rb") as handle:
        response = client.post(
            "/connect/sqlite",
            files={"file": ("external.sqlite", handle, "application/octet-stream")},
            data={"active_table": "imported_data"},
        )

    payload = response.json()
    assert response.status_code == 200
    assert payload["active_table"] == "imported_data"
    assert payload["tables"] == ["imported_data"]
    assert [column["name"] for column in payload["schema"]] == ["id", "name"]

    tables_response = client.get("/tables")
    assert tables_response.json() == {"tables": ["imported_data"], "active_table": "imported_data"}


def test_connect_recreates_missing_upload_directory(client: TestClient, tmp_path):
    source_db = tmp_path / "external.sqlite"
    create_sqlite_database(source_db)
    main.UPLOAD_DIR.rmdir()

    with source_db.open("rb") as handle:
        response = client.post(
            "/connect/sqlite",
            files={"file": ("external.sqlite", handle, "application/octet-stream")},
            data={"active_table": "imported_data"},
        )

    assert response.status_code == 200
    assert response.json()["active_table"] == "imported_data"
    assert main.UPLOAD_DIR.exists() is True


def test_sql_and_query_routes_return_result_sets(client: TestClient, monkeypatch):
    upload_csv(client)

    sql_response = client.post(
        "/sql",
        json={
            "sql": 'SELECT region, amount FROM "sales" ORDER BY amount DESC',
            "input_type": "sql",
            "active_table": "sales",
        },
    )
    sql_payload = sql_response.json()

    assert sql_response.status_code == 200
    assert sql_payload["mode"] == "sql"
    assert sql_payload["has_result_set"] is True
    assert sql_payload["columns"] == ["region", "amount"]
    assert sql_payload["rows"][0] == ["North", 30]

    monkeypatch.setattr(
        main,
        "generate_sql",
        lambda query, table_name=None: 'SELECT region, amount FROM "sales" ORDER BY amount DESC',
    )

    query_response = client.post(
        "/query",
        json={"query": "Show me the top sales regions", "table_name": "sales"},
    )
    query_payload = query_response.json()

    assert query_response.status_code == 200
    assert query_payload["mode"] == "ai"
    assert query_payload["generated_sql"] == 'SELECT region, amount FROM "sales" ORDER BY amount DESC'
    assert query_payload["has_result_set"] is True
    assert query_payload["columns"] == ["region", "amount"]
    assert query_payload["rows"][0] == ["North", 30]


def test_cleanup_route_removes_database_and_files(client: TestClient):
    upload_csv(client)
    client.get("/download", params={"table_name": "sales"})

    response = client.post("/cleanup")

    assert response.status_code == 200
    assert response.json()["message"] == "Database and files cleaned up successfully"
    assert client.get("/tables").json() == {"tables": [], "active_table": None}
