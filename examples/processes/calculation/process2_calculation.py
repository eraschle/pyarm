"""
Prozess 2: Berechnung von Infrastrukturelementen.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from pyarm.core.enums.process_enums import ElementType
from pyarm.repository.json_repository import JsonElementRepository
from pyarm.services.calculation_service import CalculationService


class CalculationProcess:
    """
    Prozess für die Berechnung von Infrastrukturelementen.
    """

    def __init__(self, repository_path: str, output_path: str):
        """
        Initialisiert den Prozess.

        Args:
            repository_path: Pfad zum Repository
            output_path: Pfad für die Ausgabe
        """
        self.repository = JsonElementRepository(repository_path)
        self.service = CalculationService(self.repository)
        self.output_path = Path(output_path)

        # Output-Verzeichnis erstellen
        os.makedirs(self.output_path, exist_ok=True)

    def run(self) -> None:
        """
        Führt den Berechnungsprozess aus.
        """
        print("Starte Berechnungsprozess...")

        # Alle Elemente für die Berechnung vorbereiten
        calculation_elements = self.service.get_all_elements()

        # Daten nach Elementtyp gruppieren
        elements_by_type = {}
        for element in calculation_elements:
            element_type = element.element_type
            if element_type not in elements_by_type:
                elements_by_type[element_type] = []
            elements_by_type[element_type].append(element.to_dict())

        # Für jeden Elementtyp eine Datei erstellen
        for element_type, elements in elements_by_type.items():
            file_path = self.output_path / f"{element_type}_calculation.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(elements, f, indent=2)

            print(f"Berechnungsdaten für {element_type} gespeichert: {file_path}")

        # Gesamtübersicht erstellen
        overview = {
            "element_counts": {
                element_type: len(elements) for element_type, elements in elements_by_type.items()
            },
            "total_elements": len(calculation_elements),
        }

        overview_path = self.output_path / "calculation_overview.json"
        with open(overview_path, "w", encoding="utf-8") as f:
            json.dump(overview, f, indent=2)

        print(f"Berechnungsprozess abgeschlossen. Übersicht gespeichert: {overview_path}")

    def process_element(self, element_id: str) -> Dict[str, Any]:
        """
        Verarbeitet ein einzelnes Element für die Berechnung.

        Args:
            element_id: ID des Elements

        Returns:
            Berechnungsdaten für das Element

        Raises:
            ValueError: Wenn das Element nicht gefunden wurde
        """
        element = self.service.get_element(element_id)
        if not element:
            raise ValueError(f"Element {element_id} nicht gefunden")

        result = element.to_dict()

        # Berechnung der Strukturlast, falls möglich
        try:
            load_data = self.service.calculate_structure_load(element_id)
            result["load_calculation"] = load_data.get("load_case", {})
        except ValueError:
            # Keine Strukturlastberechnung möglich
            pass

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"element_{element_id}_calculation.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Berechnungsdaten für Element {element_id} gespeichert: {file_path}")

        return result

    def process_elements_by_type(self, element_type: ElementType) -> List[Dict[str, Any]]:
        """
        Verarbeitet alle Elemente eines bestimmten Typs für die Berechnung.

        Args:
            element_type: Typ der zu verarbeitenden Elemente

        Returns:
            Liste der Berechnungsdaten für die Elemente
        """
        calculation_elements = self.service.get_elements_by_type(element_type)
        results = [element.to_dict() for element in calculation_elements]

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"{element_type.value}_calculation.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(
            f"Berechnungsdaten für {len(results)} Elemente vom Typ {element_type.value} gespeichert: {file_path}"
        )

        return results

    def calculate_track_forces(self, element_id: str, speed: float, load: float) -> Dict[str, Any]:
        """
        Berechnet Kräfte auf einem Gleis.

        Args:
            element_id: ID des Elements
            speed: Geschwindigkeit in m/s
            load: Last in kN/m

        Returns:
            Berechnete Kräfte

        Raises:
            ValueError: Wenn das Element kein Gleis ist
        """
        result = self.service.calculate_track_forces(element_id, speed, load)

        # Ausgabe in Datei speichern
        file_path = self.output_path / f"element_{element_id}_forces.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"Gleiskräfte für Element {element_id} gespeichert: {file_path}")

        return result


if __name__ == "__main__":
    # Beispielaufruf
    process = CalculationProcess(
        repository_path="../repository/data", output_path="../output/calculation"
    )
    process.run()
