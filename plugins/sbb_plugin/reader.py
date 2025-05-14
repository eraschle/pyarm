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

            # If there's only one sheet, use it
            if len(sheets) == 1:
                df = next(iter(sheets.values()))
            # If there are multiple sheets, concatenate them
            elif len(sheets) > 1:
                df = pd.concat(sheets.values(), ignore_index=True)
            else:
                raise ValueError("No data found in Excel file")

            # Basic metadata
            metadata = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "sheet_names": list(sheets.keys()),
            }

            # Element type counts based on Family column
            if "Family" in df.columns:
                family_counts = df["Family"].value_counts().to_dict()
                metadata["element_types"] = family_counts

            return {"excel_data": df, "metadata": metadata}

        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}") from None

    @staticmethod
    def filter_by_element_type(df: pd.DataFrame, element_type: str) -> pd.DataFrame:
        """
        Filter DataFrame by element type based on 'Family' column.

        Args:
            df: Input DataFrame
            element_type: Element type to filter for

        Returns:
            Filtered DataFrame
        """
        if "Family" not in df.columns:
            raise ValueError("DataFrame does not have a 'Family' column")

        # Map element type to the corresponding family name pattern
        element_type_map = {
            "abwasser_haltung": "Abwasser - Leitung",
            "abwasser_schacht": "Abwasser - Normschacht",
            "kabelschacht": "Kabelschacht",
            "mast": "Mast",
            "ausleger": "Ausleger",
            "fundament": "Fundament",
        }

        family_pattern = element_type_map.get(element_type.lower())
        if not family_pattern:
            raise ValueError(f"Unknown element type: {element_type}")

        # Filter DataFrame
        if isinstance(family_pattern, list):
            # Multiple patterns
            filtered_df = df[df["Family"].isin(family_pattern)]
        else:
            # Single pattern (exact or contains)
            if family_pattern.endswith("*"):
                # Contains pattern
                pattern = family_pattern[:-1]
                filtered_df = df[df["Family"].str.contains(pattern, na=False)]
            else:
                # Exact match
                filtered_df = df[df["Family"] == family_pattern]

        return filtered_df
