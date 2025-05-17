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


def create_client_plugin(client_name: str, destination: str = "clients"):
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
    plugin_dir = Path(destination) / plugin_name / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # Erstelle __init__.py
    init_content = f'''"""
Client-Plugin für {client_name}.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pyarm.interfaces.plugin import PluginInterface, ConversionResult
from pyarm.linking.element_linker import ElementLinker
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType

log = logging.getLogger(__name__)


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
        """Initialisiert das Plugin mit der Konfiguration."""
        log.info(f"Initialisiere {{self.name}} v{{self.version}}")
        log.debug(f"Konfiguration: {{config}}")
        
        # ElementLinker für die Verbindung von Elementen basierend auf Attributen erstellen
        self._element_linker = None
        self._data_directory = None
        return True
    
    def get_supported_element_types(self) -> List[ElementType]:
        """Gibt die unterstützten Elementtypen zurück."""
        return [ElementType.FOUNDATION, ElementType.MAST]
    
    def load_data_from_directory(self, directory_path: Union[str, Path]) -> None:
        """
        Lädt alle relevanten Daten aus dem angegebenen Verzeichnis und speichert sie intern im Plugin.
        Das Plugin ist für die Erkennung und das Lesen aller notwendigen Dateien verantwortlich.

        Parameters
        ----------
        directory_path: Union[str, Path]
            Pfad zum Verzeichnis mit den Dateien
        """
        self._data_directory = Path(directory_path)
        log.info(f"Daten aus Verzeichnis {{self._data_directory}} geladen")
    
    def convert_element(self, element_type: ElementType) -> Optional[ConversionResult]:
        """
        Konvertiert intern gespeicherte Daten in Elemente des angegebenen Typs.

        Parameters
        ----------
        element_type: ElementType
            Typ der zu erstellenden Elemente

        Returns
        -------
        Optional[ConversionResult]
            Konversionsergebnis mit den erstellten Elementen und ihrem Typ
        """
        if element_type not in self.get_supported_element_types():
            log.warning(f"Elementtyp {{element_type}} wird nicht unterstützt")
            return None
            
        # Ergebnisliste für konvertierte Elemente
        elements = []
        
        # Hier würde die tatsächliche Implementierung der Konvertierung erfolgen
        log.info(f"Konvertiere Elemente vom Typ {{element_type}}")
        
        # Beispielimplementierung: Erstellen eines leeren Ergebnisses
        return ConversionResult(
            elements=elements,
            element_type=element_type,
            plugin_name=self.name
        )
        
    def define_element_links(self, linker_manager: ElementLinker) -> None:
        """
        Definiert Elementverknüpfungen mit dem bereitgestellten Linker-Manager.
        Diese Methode sollte nach der Konvertierung aller Elemente aufgerufen werden.

        Parameters
        ----------
        linker_manager: ElementLinker
            Der zu verwendende Linker-Manager für die Definition von Elementverknüpfungen
        """
        # Hier würden spezifische Verknüpfungen definiert
        log.info("Verknüpfungen definiert")
        
    def get_process_name(self) -> str:
        """
        Gibt den Namen des Prozesses zurück.
        Standardmäßig wird der Plugin-Name zurückgegeben.

        Returns
        -------
        str
            Name des Prozesses
        """
        return f"{client_name} Process"
'''

    # Schreibe __init__.py
    with open(plugin_dir / "__init__.py", "w") as f:
        f.write(init_content)

    # Erstelle auch ein README.md im Plugin-Verzeichnis
    readme_content = f'''# {client_name} Plugin für PyArm

Dieses Plugin ermöglicht die Konvertierung von {client_name}-spezifischen Daten in das kanonische Datenmodell des PyArm-Systems.

## Übersicht

Das Plugin unterstützt:

- Lesen und Konvertieren von Daten aus dem {client_name}-Format
- Konvertierung verschiedener Infrastrukturelemente (Fundamente, Masten, etc.)
- Bidirektionale Referenzen zwischen Elementen

## Unterstützte Elementtypen

- `foundation` - Fundamente
- `mast` - Masten

## Plugin-Integration

```python
from pyarm.app import Application

# Plugin laden
app = Application()
app.load_plugins()

# Plugin verwenden (neues Interface)
app.plugin_manager.load_data_from_directory("path/to/{plugin_name}/data")
result = app.plugin_manager.convert_element(ElementType.FOUNDATION)
```

## Parameter-Mapping

Das Plugin wandelt {client_name}-spezifische Parameter in das kanonische Modell um.

## Komponenten

Die konvertierten Elemente erhalten automatisch verschiedene Komponenten:

- **Location**: Positionsinformationen
- **Dimension**: Abmessungen des Elements
- **Reference**: Verweise auf andere Elemente

## Fehlerbehandlung

Das Plugin protokolliert Fehler und Warnungen über das Logging-System.
'''

    # Schreibe README.md
    with open(plugin_dir / "README.md", "w") as f:
        f.write(readme_content)

    # Erstelle ein import_client.py Script im client Verzeichnis
    import_script = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import-Skript für {client_name}-Daten.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Projekt-Root zum Pfad hinzufügen
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pyarm.models.process_enums import ElementType
from pyarm.app import Application
from pyarm.repository.json.elements import JsonElementRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def parse_args():
    """Kommandozeilenargumente parsen."""
    parser = argparse.ArgumentParser(description="Import {client_name} Daten")
    parser.add_argument(
        "--input-dir",
        type=str,
        required=True,
        help="Eingabeverzeichnis mit {client_name}-Daten"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/{plugin_name}",
        help="Ausgabeverzeichnis für konvertierte Daten"
    )
    return parser.parse_args()


def main():
    """Hauptfunktion."""
    args = parse_args()
    
    # Ausgabeverzeichnis erstellen
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Repository erstellen
    repository = JsonElementRepository(output_dir)
    
    # Anwendung initialisieren
    app = Application()
    app.load_plugins()
    
    # Prüfen, ob das Plugin geladen wurde
    plugin_name = "{client_name} Plugin"
    if plugin_name not in [p.name for p in app.plugin_manager.plugins]:
        log.error(f"Plugin '{{plugin_name}}' nicht gefunden!")
        return 1
    
    log.info(f"Importiere {client_name}-Daten aus {{args.input_dir}}")
    
    # Daten laden
    app.plugin_manager.load_data_from_directory(args.input_dir)
    
    # Elemente konvertieren und speichern
    for element_type in [ElementType.FOUNDATION, ElementType.MAST]:
        result = app.plugin_manager.convert_element(element_type)
        if result and result.elements:
            log.info(f"{{len(result.elements)}} Elemente vom Typ {{element_type}} konvertiert")
            repository.save_all(result.elements)
        else:
            log.warning(f"Keine Elemente vom Typ {{element_type}} gefunden")
    
    log.info(f"Import abgeschlossen. Daten in {{output_dir}} gespeichert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

    # Schreibe import_script
    client_dir = plugin_dir.parent
    with open(client_dir / f"import_{plugin_name}.py", "w") as f:
        f.write(import_script)
    
    # Mache das Script ausführbar
    os.chmod(client_dir / f"import_{plugin_name}.py", 0o755)

    # Informationen ausgeben
    print(f"Client-Plugin für '{client_name}' erstellt:")
    print(f"- Plugin-Verzeichnis: {plugin_dir}")
    print(f"- Import-Script: {client_dir / f'import_{plugin_name}.py'}")
    print("\nUm das Plugin zu verwenden:")
    print(f"1. Führe das Import-Script aus: python {client_dir / f'import_{plugin_name}.py'} --input-dir <Datenverzeichnis> --output-dir <Ausgabeverzeichnis>")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Verwendung: create_client_plugin.py CLIENT_NAME [DESTINATION]")
        sys.exit(1)

    client_name = sys.argv[1]
    destination = sys.argv[2] if len(sys.argv) > 2 else "clients"

    create_client_plugin(client_name, destination)
