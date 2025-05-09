"""
Prozess 1: Visualisierung von Infrastrukturelementen.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from pyarm.core.enums.process_enums import ElementType
from pyarm.repository.json_repository import JsonElementRepository
from pyarm.services.visualization_service import VisualizationService


class VisualizationProcess:
    """
    Prozess für die Visualisierung von Infrastrukturelementen.
    """

    def __init__(self, repository_path: str, output_path: str):
        """
        Initialisiert den Prozess.

        Args:
            repository_path: Pfad zum Repository
            output_path: Pfad für die Ausgabe
        """
        self.repository = JsonElementRepository(repository_path)
        self.service = VisualizationService(self.repository)
        self.output_path = Path(output_path)

        # Output-Verzeichnis erstellen
        os.makedirs(self.output_path, exist_ok=True)

    def run(self) -> None:
        """
        Führt den Visualisierungsprozess aus.
        """
        print("Starte Visualisierungsprozess...")

        # Alle Elemente für die Visualisierung vorbereiten
        visualization_data = self.service.get_all_elements()

        # Daten nach Elementtyp gruppieren
        elements_by_type = {}
        for element in visualization_data:
            element_type = element.get("type")
            if element_type not in elements_by_type:
                elements_by_type[element_type] = []
            elements_by_type[element_type].append(element)

        # Für jeden Elementtyp eine Datei erstellen
        for element_type, elements in elements_by_type.items():
            file_path = self.output_path / f"{element_type}_visualization.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(elements, f, indent=2)

            print(f"Visualisierungsdaten für {element_type} gespeichert: {file_path}")

        # Gesamtübersicht erstellen
        overview = {
            "element_counts": {
                element_type: len(elements) for element_type, elements in elements_by_type.items()
            },
            "total_elements": len(visualization_data),
        }

        overview_path = self.output_path / "visualization_overview.json"
        with open(overview_path, "w", encoding="utf-8") as f:
            json.dump(overview, f, indent=2)

        print(f"Visualisierungsprozess abgeschlossen. Übersicht gespeichert: {overview_path}")

    def process_element(self, element_id: str) -> Dict[str, Any]:
        """
        Verarbeitet ein einzelnes Element für die Visualisierung.

        Args:
            element_id: ID des Elements

        Returns:
            Visualisierungsdaten für das Element

        Raises:
            ValueError: Wenn das Element nicht gefunden wurde
        """
        result = self.service.get_element(element_id)
        if not result:
            raise ValueError(f"Element {element_id} nicht gefunden")

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"element_{element_id}_visualization.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Visualisierungsdaten für Element {element_id} gespeichert: {file_path}")

        return result

    def process_elements_by_type(self, element_type: ElementType) -> List[Dict[str, Any]]:
        """
        Verarbeitet alle Elemente eines bestimmten Typs für die Visualisierung.

        Args:
            element_type: Typ der zu verarbeitenden Elemente

        Returns:
            Liste der Visualisierungsdaten für die Elemente
        """
        results = self.service.get_elements_by_type(element_type)

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"{element_type.value}_visualization.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(
            f"Visualisierungsdaten für {len(results)} Elemente vom Typ {element_type.value} gespeichert: {file_path}"
        )

        return results

    def calculate_clothoid_points(
        self, element_id: str, start_station: float, end_station: float, step: float
    ) -> List[List[float]]:
        """
        Berechnet Punkte entlang einer Klothoide.

        Args:
            element_id: ID des Elements
            start_station: Startstation
            end_station: Endstation
            step: Schrittweite

        Returns:
            Liste von Punkten [x, y, z]

        Raises:
            ValueError: Wenn das Element keine Klothoidenfunktionalität hat
        """
        points = self.service.calculate_clothoid_points(
            element_id, start_station, end_station, step
        )

        # Für die Visualisierung konvertieren
        result = [[x, y, z] for x, y, z in points]

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"element_{element_id}_clothoid.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Klothoidenpunkte für Element {element_id} gespeichert: {file_path}")

        return result


if __name__ == "__main__":
    # Beispielaufruf
    process = VisualizationProcess(
        repository_path="../repository/data", output_path="../output/visualization"
    )
    process.run()
