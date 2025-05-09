#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beispiel für die Erstellung eines Client-Plugins.
"""

import os
import sys

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path


def create_client_plugin(client_name: str, destination: str = "client_plugins"):
    """
    Erstellt ein neues Client-Plugin.

    Args:
        client_name: Name des Clients
        destination: Zielverzeichnis
    """
    print(f"Erstelle Client-Plugin für '{client_name}'...")

    # Bereinige den Namen
    plugin_name = client_name.lower().replace(" ", "_")

    # Erstelle Verzeichnisstruktur
    plugin_dir = Path(destination) / plugin_name
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # Erstelle __init__.py
    init_content = f'''"""
Client-Plugin für {client_name}.
"""

from typing import Any, Dict, List, Optional

from pyarm.interfaces.plugin import PluginInterface


class {client_name.title().replace(" ", "")}Plugin(PluginInterface):
    """
    Client-Plugin für {client_name}.
    """
    
    @property
    def name(self) -> str:
        return "{client_name} Plugin"
        
    @property
    def version(self) -> str:
        return "0.1.0"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin."""
        print(f"{client_name} Plugin initialisiert mit Konfiguration: {{config}}")
        return True
    
    def get_supported_element_types(self) -> List[str]:
        """Gibt die unterstützten Element-Typen zurück."""
        return ["{plugin_name}_foundation", "{plugin_name}_mast"]
    
    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """Konvertiert Daten in ein Element."""
        if element_type not in self.get_supported_element_types():
            return None
            
        result = data.copy()
        result["element_type"] = element_type
        result["client"] = "{client_name}"
        result["converted_by"] = self.name
        return result
'''

    # Schreibe __init__.py
    with open(plugin_dir / "__init__.py", "w") as f:
        f.write(init_content)

    # Erstelle setup.py für die separate Installation
    setup_dir = Path(destination) / f"{plugin_name}_package"
    setup_dir.mkdir(parents=True, exist_ok=True)

    setup_content = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="pyarm-plugin-{plugin_name}",
    version="0.1.0",
    description="{client_name} Plugin for PyArm",
    packages=find_packages(),
    install_requires=[
        "pyarm",
    ],
    entry_points={{
        "pyarm.plugins": [
            "{plugin_name} = {plugin_name}",
        ],
    }},
)
'''

    # Schreibe setup.py
    with open(setup_dir / "setup.py", "w") as f:
        f.write(setup_content)

    # Erstelle ein Verzeichnis für das Paket
    package_dir = setup_dir / plugin_name
    package_dir.mkdir(parents=True, exist_ok=True)

    # Kopiere __init__.py in das Paket
    with open(package_dir / "__init__.py", "w") as f:
        f.write(init_content)

    print(f"Client-Plugin für '{client_name}' erstellt:")
    print(f"- Plugin-Verzeichnis: {plugin_dir}")
    print(f"- Paket-Verzeichnis: {setup_dir}")
    print("\nUm das Plugin zu verwenden:")
    print(f"1. Füge '{plugin_dir}' zum PYTHONPATH hinzu oder")
    print(f"2. Installiere das Paket mit 'pip install -e {setup_dir}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: create_client_plugin.py CLIENT_NAME [DESTINATION]")
        sys.exit(1)

    client_name = sys.argv[1]
    destination = sys.argv[2] if len(sys.argv) > 2 else "client_plugins"

    create_client_plugin(client_name, destination)
