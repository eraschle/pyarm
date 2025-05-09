"""
Test für den SQL-Reader und Converter von Client C.
"""

import sys
from pathlib import Path
from typing import Any

# Pfad zum Wurzelverzeichnis hinzufügen, um relative Importe zu ermöglichen
sys.path.append(str(Path(__file__).parent.parent.parent))

from clients.clientC.code.converter import ClientCConverter
from clients.clientC.code.reader import ClientCSqlReader


def test_sql_reader():
    """Testet den ClientCSqlReader."""
    # Pfad zur SQL-Datei
    current_dir = Path(__file__).parent
    project_dir = current_dir.parent / "projects"
    sql_file = project_dir / "infrastructure.sql"

    # Reader instanziieren
    reader = ClientCSqlReader()

    # Prüfen, ob der Reader die Datei verarbeiten kann
    if not reader.can_handle(str(sql_file)):
        print(f"FEHLER: Der Reader kann die Datei {sql_file} nicht verarbeiten!")
        return

    # Daten lesen
    data = reader.read_data(str(sql_file))

    # Verfügbare Elementtypen anzeigen
    element_types = [et for et, items in data.items() if items]
    print(f"Verfügbare Elementtypen: {', '.join(element_types)}")

    # Anzahl der Elemente pro Typ anzeigen
    for et in element_types:
        items = data[et]
        print(f"  {et}: {len(items)} Elemente")

    return data


def test_converter(data: dict[str, list[dict[str, Any]]]):
    """
    Testet den ClientCConverter.

    Args:
        data: Vom Reader gelesene Daten
    """
    # Converter instanziieren
    converter = ClientCConverter()

    # Für jeden Elementtyp konvertieren
    all_elements = []
    for element_type, items in data.items():
        if not items:
            continue

        # Daten für den Converter aufbereiten
        type_data = {"element_type": element_type, "data": items}

        # Prüfen, ob der Converter die Daten verarbeiten kann
        if not converter.can_convert(type_data):
            print(f"FEHLER: Der Converter kann den Typ {element_type} nicht konvertieren!")
            continue

        # Daten konvertieren
        elements = converter.convert(type_data)
        all_elements.extend(elements)

        # Ergebnis anzeigen
        print(f"Konvertiert {len(elements)} {element_type}-Elemente:")
        for i, element in enumerate(elements, 1):
            print(f"  {i}. {element.element_type.value}: {element.name} (UUID: {element.uuid})")
            print(f"     Parameter: {len(element.parameters)}")
            # Ein paar Parameter als Beispiel anzeigen
            for j, param in enumerate(element.parameters[:3], 1):
                print(f"       {j}. {param.name}: {param.value} {param.unit.value}")
            if len(element.parameters) > 3:
                print(f"       ... und {len(element.parameters) - 3} weitere Parameter")

    return all_elements


if __name__ == "__main__":
    # Reader testen
    print("\n=== Test des SQL-Readers ===")
    data = test_sql_reader()

    if data:
        # Converter testen
        print("\n=== Test des Converters ===")
        elements = test_converter(data)

        # Anzahl der konvertierten Elemente anzeigen
        print(f"\nInsgesamt wurden {len(elements)} Elemente konvertiert.")
