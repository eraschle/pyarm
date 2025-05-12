#!/usr/bin/env python3
"""
Eigenständiges Skript zum Testen der SQL-Konvertierung.
"""

import json
import logging
import os
import sys
import re
from typing import Any, Dict, List

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def extract_sql_foundation_data(sql_file: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Foundation-Daten aus SQL-Daten für Testzwecke.
    """
    try:
        # SQL-Datei lesen
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Fundament-Daten extrahieren
        pattern = r"INSERT\s+INTO\s+foundations\s*\(([^)]+)\)\s*VALUES\s*((?:\([^;]+\),?)+);"
        match = re.search(pattern, sql_content, re.IGNORECASE | re.DOTALL)

        if not match:
            logger.error("Keine Foundation-Daten in SQL-Datei gefunden")
            return []

        # Spalten extrahieren
        columns_str = match.group(1)
        columns = [col.strip() for col in columns_str.split(",")]

        # Werte extrahieren
        values_str = match.group(2)
        value_pattern = r"\(([^)]+)\)"
        value_matches = re.finditer(value_pattern, values_str)

        result = []
        for value_match in value_matches:
            values_row = value_match.group(1)
            # Werte parsen
            values = []

            # Einfaches Parsen für Testzwecke
            current_value = ""
            in_quotes = False
            for char in values_row:
                if char == "'" and (len(current_value) == 0 or current_value[-1] != "\\"):
                    in_quotes = not in_quotes
                elif char == "," and not in_quotes:
                    # Wert bereinigen
                    if current_value.startswith("'") and current_value.endswith("'"):
                        current_value = current_value[1:-1]
                    elif current_value.upper() == "NULL":
                        current_value = None
                    elif current_value.replace(".", "", 1).isdigit():
                        try:
                            current_value = (
                                float(current_value) if "." in current_value else int(current_value)
                            )
                        except ValueError:
                            pass

                    values.append(current_value)
                    current_value = ""
                else:
                    current_value += char

            # Letzten Wert hinzufügen
            if current_value:
                if current_value.startswith("'") and current_value.endswith("'"):
                    current_value = current_value[1:-1]
                elif current_value.upper() == "NULL":
                    current_value = None
                elif current_value.replace(".", "", 1).isdigit():
                    try:
                        current_value = (
                            float(current_value) if "." in current_value else int(current_value)
                        )
                    except ValueError:
                        pass

                values.append(current_value)

            if len(columns) == len(values):
                row_data = dict(zip(columns, values))
                result.append(row_data)

        return result
    except Exception as e:
        logger.error(f"Fehler beim Extrahieren der Foundation-Daten: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return []


def convert_foundation_data(foundation_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Konvertiert SQL Foundation-Daten in ein kanonisches Format.
    """
    try:
        result = []

        for item in foundation_data:
            # Kanonisches Format für ein Fundament
            foundation = {
                "id": item.get("id", ""),
                "name": item.get("name", "Unbenanntes Fundament"),
                "element_type": "foundation",
                "parameters": [],
            }

            # Parameter hinzufügen
            foundation["parameters"].extend(
                [
                    {
                        "name": "ID",
                        "value": item.get("id", ""),
                        "process": "uuid",
                        "datatype": "string",
                        "unit": "none",
                    },
                    {
                        "name": "Name",
                        "value": item.get("name", "Unbenanntes Fundament"),
                        "process": "name",
                        "datatype": "string",
                        "unit": "none",
                    },
                    {
                        "name": "coord_x",
                        "value": float(item.get("coord_x", 0)),
                        "process": "x",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "coord_y",
                        "value": float(item.get("coord_y", 0)),
                        "process": "y",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "coord_z",
                        "value": float(item.get("coord_z", 0)),
                        "process": "z",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "width_mm",
                        "value": float(item.get("width_mm", 0)) / 1000,
                        "process": "width",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "depth_mm",
                        "value": float(item.get("depth_mm", 0)) / 1000,
                        "process": "depth",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "height_mm",
                        "value": float(item.get("height_mm", 0)) / 1000,
                        "process": "height",
                        "datatype": "float",
                        "unit": "meter",
                    },
                    {
                        "name": "type",
                        "value": item.get("type", ""),
                        "process": "foundation_type",
                        "datatype": "string",
                        "unit": "none",
                    },
                    {
                        "name": "material",
                        "value": item.get("material", ""),
                        "process": "ifc_material",
                        "datatype": "string",
                        "unit": "none",
                    },
                ]
            )

            result.append(foundation)

        return result
    except Exception as e:
        logger.error(f"Fehler bei der Konvertierung der Foundation-Daten: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return []


def test_sql_conversion(sql_file: str, output_dir: str) -> bool:
    """
    Testet die SQL-Datenkonvertierung.
    """
    try:
        # Ausgabeverzeichnis erstellen
        os.makedirs(output_dir, exist_ok=True)

        # Foundation-Daten extrahieren
        logger.info(f"Extrahiere Foundation-Daten aus SQL-Datei: {sql_file}")
        foundation_data = extract_sql_foundation_data(sql_file)

        if not foundation_data:
            logger.error("Keine Foundation-Daten gefunden")
            return False

        logger.info(f"{len(foundation_data)} Foundation-Datensätze extrahiert")

        # Daten konvertieren
        logger.info("Konvertiere Foundation-Daten...")
        converted_data = convert_foundation_data(foundation_data)

        if not converted_data:
            logger.error("Konvertierung fehlgeschlagen")
            return False

        logger.info(f"{len(converted_data)} Foundation-Elemente konvertiert")

        # Ergebnis speichern
        result = {
            "element_type": "foundation",
            "project_id": "client_c",
            "elements": converted_data,
            "converted_by": "SQL Foundation Converter",
        }

        output_file = os.path.join(output_dir, "foundation_converted.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Konvertiertes Ergebnis in {output_file} gespeichert")

        return True
    except Exception as e:
        logger.error(f"Fehler bei der SQL-Konvertierung: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main():
    """Hauptfunktion."""
    if len(sys.argv) < 2:
        print("Verwendung: test_sql_conversion.py <sql_file> [output_dir]")
        sys.exit(1)

    sql_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "tests/output/client-c-test"

    logger.info(f"Teste SQL-Konvertierung für Datei: {sql_file}")
    if test_sql_conversion(sql_file, output_dir):
        logger.info("SQL-Konvertierungstest erfolgreich abgeschlossen")
    else:
        logger.error("SQL-Konvertierungstest fehlgeschlagen")
        sys.exit(1)


if __name__ == "__main__":
    main()
