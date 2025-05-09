#!/usr/bin/env python3
"""
Eigenstaendiges Skript fuer den ClientA-Import.
"""

import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from typing import Any

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="ClientA-Daten importieren")

    parser.add_argument(
        "--input_dir", type=str, required=True, help="Verzeichnis mit ClientA-Dateien"
    )
    parser.add_argument(
        "--project",
        type=str,
        choices=["project1", "project2", "all"],
        default="all",
        help="Zu verarbeitendes Projekt (project1, project2 oder all)",
    )
    parser.add_argument("--output_dir", type=str, required=True, help="Verzeichnis fuer die Ausgabe")

    return parser.parse_args()


def read_json_data(file_path: str) -> dict[str, Any]:
    """
    Liest JSON-Daten aus der angegebenen Datei.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        dictionary mit den gelesenen Daten
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Elementtyp und Projekt-ID aus dem Pfad bestimmen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        project_id = "unknown"
        if "project1" in str(path):
            project_id = "project1"
        elif "project2" in str(path):
            project_id = "project2"

        return {"element_type": element_type, "project_id": project_id, "data": data}
    except Exception as e:
        logger.error(f"Fehler beim Lesen der JSON-Datei {file_path}: {str(e)}")
        return {"element_type": "unknown", "project_id": "unknown", "data": []}


def read_csv_data(file_path: str) -> dict[str, Any]:
    """
    Liest CSV-Daten aus der angegebenen Datei.

    Args:
        file_path: Pfad zur CSV-Datei

    Returns:
        dictionary mit den gelesenen Daten
    """
    try:
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        # Elementtyp und Projekt-ID aus dem Pfad bestimmen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        project_id = "unknown"
        if "project1" in str(path):
            project_id = "project1"
        elif "project2" in str(path):
            project_id = "project2"

        return {"element_type": element_type, "project_id": project_id, "data": data}
    except Exception as e:
        logger.error(f"Fehler beim Lesen der CSV-Datei {file_path}: {str(e)}")
        return {"element_type": "unknown", "project_id": "unknown", "data": []}


def process_client_a_files(input_dir: str, project: str) -> dict[str, Any]:
    """
    Verarbeitet alle ClientA-Dateien im angegebenen Verzeichnis.

    Args:
        input_dir: Verzeichnis mit ClientA-Dateien
        project: Zu verarbeitendes Projekt (project1, project2 oder all)

    Returns:
        dictionary mit den verarbeiteten Daten
    """
    try:
        input_path = Path(input_dir)
        client_a_path = input_path / "clientA"

        if not client_a_path.exists():
            logger.error(f"ClientA-Verzeichnis nicht gefunden: {client_a_path}")
            return {}

        # Bestimme die zu verarbeitenden Projekte
        projects_to_process = []
        if project == "all":
            projects_to_process = ["project1", "project2"]
        else:
            projects_to_process = [project]

        # Daten verarbeiten
        processed_data = {"projects": {}}

        # Jedes Projekt verarbeiten
        for proj in projects_to_process:
            project_path = client_a_path / proj

            if not project_path.exists():
                logger.warning(f"Projekt-Verzeichnis nicht gefunden: {project_path}")
                continue

            logger.info(f"Verarbeite Projekt: {proj}")

            # JSON-Dateien finden
            json_files = list(project_path.glob("*.json"))
            logger.info(f"{len(json_files)} JSON-Dateien gefunden")

            # CSV-Dateien finden
            csv_files = list(project_path.glob("*.csv"))
            logger.info(f"{len(csv_files)} CSV-Dateien gefunden")

            # Projekt-Dictionary initialisieren
            if proj not in processed_data["projects"]:
                processed_data["projects"][proj] = {"elements": {}}

            # JSON-Dateien verarbeiten
            for file_path in json_files:
                logger.info(f"Verarbeite JSON-Datei: {file_path}")
                data = read_json_data(str(file_path))

                element_type = data["element_type"]
                if element_type not in processed_data["projects"][proj]["elements"]:
                    processed_data["projects"][proj]["elements"][element_type] = []

                processed_data["projects"][proj]["elements"][element_type].extend(data["data"])

            # CSV-Dateien verarbeiten
            for file_path in csv_files:
                logger.info(f"Verarbeite CSV-Datei: {file_path}")
                data = read_csv_data(str(file_path))

                element_type = data["element_type"]
                if element_type not in processed_data["projects"][proj]["elements"]:
                    processed_data["projects"][proj]["elements"][element_type] = []

                processed_data["projects"][proj]["elements"][element_type].extend(data["data"])

            # Statistiken fuer das Projekt hinzufuegen
            processed_data["projects"][proj]["statistics"] = {
                "total_elements": sum(
                    len(elements)
                    for elements in processed_data["projects"][proj]["elements"].values()
                ),
                "element_counts": {
                    element_type: len(elements)
                    for element_type, elements in processed_data["projects"][proj][
                        "elements"
                    ].items()
                },
            }

        # Gesamtstatistiken hinzufuegen
        total_elements = sum(
            proj_data["statistics"]["total_elements"]
            for proj_data in processed_data["projects"].values()
        )

        processed_data["statistics"] = {
            "total_elements": total_elements,
            "projects_processed": len(processed_data["projects"]),
            "project_names": list(processed_data["projects"].keys()),
        }

        return processed_data
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung von ClientA-Dateien: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return {}


def run_client_a_import(input_dir: str, project: str, output_dir: str) -> bool:
    """
    Fuehrt den ClientA-Import-Prozess aus.

    Args:
        input_dir: Verzeichnis mit ClientA-Dateien
        project: Zu verarbeitendes Projekt (project1, project2 oder all)
        output_dir: Ausgabeverzeichnis

    Returns:
        True, wenn der Import erfolgreich war
    """
    try:
        # Ausgabeverzeichnis erstellen
        os.makedirs(output_dir, exist_ok=True)

        # ClientA-Dateien verarbeiten
        logger.info(f"Verarbeite ClientA-Dateien aus {input_dir} fuer Projekt {project}...")
        processed_data = process_client_a_files(input_dir, project)

        if not processed_data or not processed_data.get("projects"):
            logger.error("Keine gueltigen ClientA-Daten gefunden.")
            return False

        # Statistiken anzeigen
        stats = processed_data["statistics"]
        logger.info(
            f"Insgesamt {stats['total_elements']} Elemente in {stats['projects_processed']} Projekten verarbeitet"
        )

        for proj_name, proj_data in processed_data["projects"].items():
            proj_stats = proj_data["statistics"]
            logger.info(f"Projekt {proj_name}: {proj_stats['total_elements']} Elemente")
            for element_type, count in proj_stats["element_counts"].items():
                logger.info(f"  - {element_type}: {count} Elemente")

        # Ausgabedatei speichern
        output_file = os.path.join(output_dir, "clientA_data.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Verarbeitete Daten in {output_file} gespeichert.")

        return True
    except Exception as e:
        logger.error(f"Fehler beim ClientA-Import: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()

    # ClientA-Import-Prozess ausfuehren
    if run_client_a_import(args.input_dir, args.project, args.output_dir):
        logger.info("ClientA-Import-Prozess erfolgreich abgeschlossen")
    else:
        logger.error("ClientA-Import-Prozess fehlgeschlagen")
        sys.exit(1)


if __name__ == "__main__":
    main()
