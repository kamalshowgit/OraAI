# ORA AI Data Platform

This project is a data platform that allows users to upload data, explore it, and interact with it using an AI-powered assistant.

## Features

- **Upload Data:** Users can upload CSV, Excel, and text files.
- **Connect to Databases:** Users can connect to SQLite databases.
- **Explore Data:** Users can view the schema of their tables and preview the data.
- **AI Assistant:** Users can ask questions in natural language, and the AI will generate and execute SQL queries.
- **Query History:** All queries are saved for future reference.
- **Download Data:** Users can download the data as a CSV file.

## Getting Started

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    uvicorn app:app --reload
    ```

## Project Structure

- `app.py`: The main FastAPI application file.
- `agent/`: Contains the AI agent logic.
- `db/`: Stores user-specific SQLite databases.
- `exports/`: Stores exported data.
- `ingestion/`: Handles data ingestion from various sources.
- `static/`: Contains static files (CSS, JavaScript, images).
- `templates/`: Contains HTML templates.
- `uploads/`: Stores uploaded files.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
