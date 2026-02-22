# import pandas as pd
# from pathlib import Path

# SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}

# def load_file(file_path: Path) -> pd.DataFrame:
#     if file_path.suffix not in SUPPORTED_EXTENSIONS:
#         raise ValueError("Only CSV and Excel files are supported")

#     if file_path.suffix == ".csv":
#         return pd.read_csv(file_path)
#     return pd.read_excel(file_path)


import pandas as pd
from pathlib import Path
from ingestion.txt_loader import TXTLoader

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".txt"}

def load_file(file_path: Path, delimiter: str | None = None) -> pd.DataFrame:
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only CSV, Excel and TXT files are supported")

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)

    if suffix == ".xlsx":
        return pd.read_excel(file_path)

    if suffix == ".txt":
        return TXTLoader.load(file_path, delimiter=delimiter)

    raise ValueError("Unsupported file type")
