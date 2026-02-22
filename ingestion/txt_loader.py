import pandas as pd
from pathlib import Path


class TXTLoader:
    """
    Robust TXT loader.
    Handles:
    - Delimited tabular data
    - Line-based unstructured text
    """

    @staticmethod
    def load(
        file_path: str | Path,
        delimiter: str | None = None,
        encoding: str = "utf-8"
    ) -> pd.DataFrame:

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() != ".txt":
            raise ValueError("Only .txt files are supported")

        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = [line.rstrip("\n") for line in f if line.strip()]
        except UnicodeDecodeError:
            raise RuntimeError(
                "Encoding error. Try a different encoding (e.g., latin-1)"
            )

        if not lines:
            raise ValueError("TXT file is empty or contains only blank lines")

        # -------------------------------
        # Attempt tabular parsing
        # -------------------------------
        if delimiter:
            split_lines = [line.split(delimiter) for line in lines]
            col_counts = {len(row) for row in split_lines}

            if len(col_counts) == 1 and list(col_counts)[0] > 1:
                df = pd.DataFrame(split_lines)
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
                df.columns = df.columns.astype(str).str.strip()
                return df

        # -------------------------------
        # Fallback: unstructured text
        # -------------------------------
        return pd.DataFrame({
            "line_number": range(1, len(lines) + 1),
            "text": lines
        })
