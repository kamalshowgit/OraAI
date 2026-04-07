# ORA AI Data Platform

This project is a data platform that lets users upload data, preview tables, connect SQLite databases, and query data with AI-generated SQL.

## Features

- **Upload Data:** Upload CSV, Excel, and text files.
- **Connect to Databases:** Attach SQLite database files and inspect tables.
- **Explore Data:** View table schemas and preview datasets.
- **AI Assistant:** Ask questions in natural language; the AI generates SQL and executes it.
- **Query History:** Track past queries for reuse.
- **Download Data:** Export query results and tables as CSV.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip`

### Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd OraAI
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run locally:
    ```bash
    uvicorn main:app --reload
    ```

### Render Deployment

This repository includes a `render.yaml` file so Render can deploy your app as a Python web service.

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Set `GROQ_API_KEY` in Render environment variables.

## Project Structure

- `main.py`: Primary FastAPI application entrypoint.
- `agent/`: AI agent and SQL generation logic.
- `db/`: Database helper modules.
- `exports/`: Exported CSV files.
- `ingestion/`: File ingestion and schema utilities.
- `static/`: Static assets if used.
- `templates/`: HTML templates.
- `uploads/`: Uploaded source files.
- `render.yaml`: Render deployment configuration.

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss your plan.