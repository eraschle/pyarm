#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beispiel für die Verwendung des Plugin-Systems.
"""

import os
import sys
from pprint import pprint

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pyarm.core.app import Application


def main():
    """Hauptfunktion zum Testen des Plugin-Systems."""
    print("Starte PyArm Plugin-Test...")

    # Erstelle Anwendungsinstanz
    app = Application()

    # Lade alle verfügbaren Plugins
    app.load_plugins({"Example Plugin": {"option1": "value1", "option2": 42}})

    # Zeige geladene Plugins
    print("\nGeladene Plugins:")
    for name, plugin in app.plugins.items():
        print(f"- {name} v{plugin.version}")
        print(f"  Unterstützte Element-Typen: {', '.join(plugin.get_supported_element_types())}")

    # Teste Plugin-Konvertierung
    test_data = {"name": "Test-Element", "attributes": {"attr1": "value1", "attr2": 42}}

    print("\nTeste Konvertierung:")
    for element_type in ["foundation", "mast", "unknown_type"]:
        result = app.convert_element(test_data, element_type)
        print(f"\nElement-Typ: {element_type}")
        if result:
            print("Konvertierung erfolgreich:")
            pprint(result)
        else:
            print("Konvertierung fehlgeschlagen: Kein Plugin unterstützt diesen Element-Typ")


if __name__ == "__main__":
    main()
