#!/usr/bin/env python3
"""
Testskript für das Client C Plugin.
"""

import os
import sys
import json
import logging
from typing import Any, Dict

# Python-Pfad um das aktuelle Verzeichnis erweitern
current_dir = os.path.dirname(os.path.abspath(__file__))
# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, current_dir)

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Jetzt können wir die Importe durchführen
from plugins.client_c import SimplifiedClientCPlugin as ClientCPlugin


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Liest eine JSON-Datei und gibt deren Inhalt zurück.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Dictionary mit dem Inhalt der Datei
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return {}


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Speichert Daten als JSON-Datei.

    Args:
        file_path: Pfad zum Speichern der Datei
        data: Zu speichernde Daten

    Returns:
        True, wenn erfolgreich, sonst False
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Datei {file_path}: {e}")
        return False


def test_fdk_conversion():
    """
    Testet die Konvertierung von FDK-Daten.
    """
    logger.info("Teste FDK-Datenkonvertierung...")

    # Plugin initialisieren
    plugin = ClientCPlugin()
    plugin.initialize({})

    # FDK-Datei vorbereiten
    fdk_file = "examples/clients/clientC/FDK/anlagen_daten.json"

    # Daten zur Konvertierung vorbereiten
    data = {"fdk_file": fdk_file}

    # Konvertieren
    logger.info(f"Konvertiere FDK-Datei: {fdk_file}")
    result = plugin.convert_element_simplified(data, "fdk")

    if not result:
        logger.error("Konvertierung fehlgeschlagen")
        assert False, "Konvertierung fehlgeschlagen"

    # Ergebnis speichern
    output_file = "tests/output/client-c-plugin/fdk_converted.json"
    if save_json_file(output_file, result):
        logger.info(f"Konvertiertes Ergebnis in {output_file} gespeichert")

    # Statistik anzeigen
    elements = result.get("elements", [])
    element_count = len(elements)
    logger.info(f"Erfolgreich {element_count} Elemente konvertiert")


def extract_sql_foundation_data():
    """
    Extrahiert Foundation-Daten aus SQL-Daten für Testzwecke.
    Für den Testfall werden Mock-Daten erzeugt, da die RegEx-Extraktion kompliziert ist.
    """
    logger.info("Erzeuge Foundation-Test-Daten")

    # Testdaten direkt erzeugen
    test_data = [
        {
            "id": "F001",
            "name": "Fundament 1",
            "coord_x": 2600000.0,
            "coord_y": 1200000.0,
            "coord_z": 456.78,
            "type": "Typ A",
            "width_mm": 1500,
            "depth_mm": 2000,
            "height_mm": 1000,
            "material": "Beton",
            "creation_date": "2023-05-15",
            "status": "active"
        },
        {
            "id": "F002",
            "name": "Fundament 2",
            "coord_x": 2600050.0,
            "coord_y": 1200010.0,
            "coord_z": 457.12,
            "type": "Typ B",
            "width_mm": 1800,
            "depth_mm": 2200,
            "height_mm": 1200,
            "material": "Beton",
            "creation_date": "2023-05-15",
            "status": "active"
        },
        {
            "id": "F003",
            "name": "Fundament 3",
            "coord_x": 2600100.0,
            "coord_y": 1200020.0,
            "coord_z": 457.45,
            "type": "Typ A",
            "width_mm": 1500,
            "depth_mm": 2000,
            "height_mm": 1000,
            "material": "Beton",
            "creation_date": "2023-05-15",
            "status": "active"
        }
    ]

    return test_data


def test_sql_conversion():
    """
    Testet die Konvertierung von SQL-Daten.
    """
    logger.info("Teste SQL-Datenkonvertierung...")

    # Plugin initialisieren
    plugin = ClientCPlugin()
    plugin.initialize({})

    # Testdaten extrahieren
    foundation_data = extract_sql_foundation_data()

    if not foundation_data:
        logger.error("Keine Testdaten gefunden")
        assert False, "Keine Testdaten gefunden"

    # Map column names expected by the plugin
    mapped_foundation_data = []
    for foundation in foundation_data:
        mapped_foundation = {
            "id": foundation.get("id"),
            "name": foundation.get("name"),
            "x_coord": foundation.get("coord_x"),
            "y_coord": foundation.get("coord_y"),
            "z_coord": foundation.get("coord_z"),
            "width": foundation.get("width_mm"),
            "length": foundation.get("depth_mm"),  # Note: depth_mm is used as length
            "height": foundation.get("height_mm")
        }
        mapped_foundation_data.append(mapped_foundation)

    # Daten zur Konvertierung vorbereiten
    data = {"element_type": "foundation", "project_id": "client_c", "data": mapped_foundation_data}

    # Konvertieren
    logger.info("Konvertiere Foundation-Daten")
    result = plugin.convert_element_simplified(data, "foundation")

    if not result:
        logger.error("Konvertierung fehlgeschlagen")
        assert False, "Konvertierung fehlgeschlagen"

    # Ergebnis speichern
    output_file = "tests/output/client-c-plugin/foundation_converted.json"
    if save_json_file(output_file, result):
        logger.info(f"Konvertiertes Ergebnis in {output_file} gespeichert")

    # Statistik anzeigen
    elements = result.get("elements", [])
    logger.info(f"Erfolgreich {len(elements)} Foundation-Elemente konvertiert")


def main():
    """Hauptfunktion."""
    logger.info("Teste Client C Plugin...")

    # Ausgabeverzeichnis erstellen
    os.makedirs("tests/output/client-c-plugin", exist_ok=True)

    # Tests ausführen
    test_fdk_conversion()
    test_sql_conversion()

    logger.info("Alle Tests erfolgreich abgeschlossen")


if __name__ == "__main__":
    main()
