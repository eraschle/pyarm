"""
SBB DFA Excel Reader Module.
This module provides functionality to read and process DFA Excel data files.
"""

from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd


class DfaExcelReader:
    """
    Reader for DFA Excel files containing infrastructure data.
    """

    def __init__(self):
        """Initialize the DFA Excel reader."""
        pass

    @staticmethod
    def read_excel(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read DFA Excel file and return a dictionary with the data.

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary containing the data in the format:
            {
                "excel_data": pd.DataFrame with all data,
                "metadata": Dictionary with metadata
            }
        """
        try:
            # Convert to Path if string
            file_path = Path(file_path) if isinstance(file_path, str) else file_path

            # Read Excel file into pandas DataFrame
            # Use sheet_name=None to get all sheets as a dict of dataframes

            sheets = pd.read_excel(file_path, engine="openpyxl", sheet_name=None)

            if len(sheets) == 0:
                raise ValueError("No data found in Excel file")
            row_count = sum([len(df) for df in sheets.values()])
            columns = set()
            for df in sheets.values():
                columns.update(df.columns)
            element_types = set()
            for df in sheets.values():
                if "Family" not in df.columns:
                    continue
                element_types.update(df["Family"].unique())

            # Basic metadata
            metadata = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "row_count": row_count,
                "column_count": len(columns),
                "columns": sorted(columns),
                "sheet_names": list(sheets.keys()),
                "element_types": sorted(element_types),
            }

            return {"excel_data": sheets, "metadata": metadata}

        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}") from None
