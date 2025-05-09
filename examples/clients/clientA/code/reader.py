"""
Client A spezifischer Datenleser.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List


class ClientAJsonReader:
    """
    Leser für JSON-Dateien des Clients A.
    """

    @property
    def name(self) -> str:
        return "ClientAJsonReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["json"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".json" and ("clientA" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest JSON-Daten aus der angegebenen Datei.

        Args:
            file_path: Pfad zur JSON-Datei

        Returns:
            Dictionary mit den gelesenen Daten
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ermitteln des Elementtyps aus dem Dateinamen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        if "project1" in str(path):
            project_id = "project1"
        elif "project2" in str(path):
            project_id = "project2"
        else:
            project_id = "unknown"

        return {"element_type": element_type, "project_id": project_id, "data": data}


class ClientACsvReader:
    """
    Leser für CSV-Dateien des Clients A.
    """

    @property
    def name(self) -> str:
        return "ClientACsvReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["csv"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".csv" and ("clientA" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest CSV-Daten aus der angegebenen Datei.

        Args:
            file_path: Pfad zur CSV-Datei

        Returns:
            Dictionary mit den gelesenen Daten
        """
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        # Ermitteln des Elementtyps aus dem Dateinamen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        if "project1" in str(path):
            project_id = "project1"
        elif "project2" in str(path):
            project_id = "project2"
        else:
            project_id = "unknown"

        return {"element_type": element_type, "project_id": project_id, "data": data}
