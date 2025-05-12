import pandas as pd

from pathlib import Path


def read_excel(file_path: Path):
    """
    Reads an Excel file and returns a DataFrame.

    Args:
        file_path (Path): Path to the Excel file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the Excel file.
    """
    file_path = Path(file_path)
    df = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)
    return df
