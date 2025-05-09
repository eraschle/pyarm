"""
Client B spezifischer Datenleser.
"""

import csv
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class ClientBCsvReader:
    """
    Leser für CSV-Dateien des Clients B.
    Unterstützt Semikolon-getrennte CSV-Dateien.
    """

    @property
    def name(self) -> str:
        return "ClientBCsvReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["csv"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".csv" and ("clientB" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest CSV-Daten aus der angegebenen Datei. Verwendet Semikolon als Trennzeichen.

        Args:
            file_path: Pfad zur CSV-Datei

        Returns:
            Dictionary mit den gelesenen Daten
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # ClientB verwendet Komma als Dezimaltrennzeichen, daher konvertieren wir
                # numerische Werte, die als Strings mit Komma repräsentiert sind, in
                # Fließkommazahlen mit Punkt
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, str) and ',' in value and value.replace(',', '', 1).replace('.', '', 1).isdigit():
                        processed_row[key] = value.replace(',', '.')
                    else:
                        processed_row[key] = value
                data.append(processed_row)

        # Ermitteln des Elementtyps aus dem Dateinamen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        project_dir = path.parent.name
        
        return {"element_type": element_type, "project_id": project_dir, "data": data}

class ClientBExcelReader:
    """
    Leser für Excel-Dateien des Clients B.
    Unterstützt .excel-Dateien, die tatsächlich als CSV gespeichert sind.
    """

    @property
    def name(self) -> str:
        return "ClientBExcelReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["excel"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".excel" and ("clientB" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest Excel-Daten aus der angegebenen Datei. In diesem Fall sind .excel-Dateien
        ebenfalls als CSV gespeichert mit Semikolon als Trennzeichen.

        Args:
            file_path: Pfad zur Excel-Datei

        Returns:
            Dictionary mit den gelesenen Daten
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # ClientB verwendet Komma als Dezimaltrennzeichen, daher konvertieren wir
                # numerische Werte, die als Strings mit Komma repräsentiert sind, in
                # Fließkommazahlen mit Punkt
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, str) and ',' in value and value.replace(',', '', 1).replace('.', '', 1).isdigit():
                        processed_row[key] = value.replace(',', '.')
                    else:
                        processed_row[key] = value
                data.append(processed_row)

        # Ermitteln des Elementtyps aus dem Dateinamen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        project_dir = path.parent.name
        
        return {"element_type": element_type, "project_id": project_dir, "data": data}