# PYM-Data: Setup und Konfigurationsanleitung

Diese Anleitung beschreibt die Installation und Konfiguration des PYM-Data Systems für die Verarbeitung von Infrastrukturdaten aus verschiedenen Quellen.

## Systemvoraussetzungen

- Python 3.10 oder höher
- Pip (Python-Paketmanager)
- Git (für das Klonen des Repositories)

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/username/pym_data.git
cd pym_data
```

### 2. Virtuelle Umgebung erstellen und aktivieren

```bash
# Unter Linux/macOS
python -m venv venv
source venv/bin/activate

# Unter Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

## Konfiguration

### Grundlegende Konfiguration

Die Basiskonfiguration erfolgt über die Datei `config/default_client_config.json`. Diese enthält standardmäßige Einstellungen für alle Clients:

```json
{
  "repository": {
    "path": "./data/repository",
    "format": "json"
  },
  "output": {
    "path": "./data/output",
    "format": "json"
  },
  "logging": {
    "level": "INFO",
    "file": "./logs/pym_data.log"
  }
}
```

### Client-spezifische Konfiguration

Für jeden Client kann eine spezifische Konfiguration erstellt werden. Diese überschreibt die Standardeinstellungen:

```json
{
  "client_id": "clientA",
  "repository": {
    "path": "./data/clientA/repository"
  },
  "reader": {
    "csv_delimiter": ",",
    "encoding": "utf-8",
    "skip_rows": 0
  },
  "converter": {
    "preset": "project1"
  }
}
```

## Plugin-Registrierung

Neue Plugins müssen registriert werden, damit das System sie finden kann. Dies geschieht in der Datei `code/plugin_registry.py`:

```python
from clients.clientA.code.reader import ClientAJsonReader, ClientACsvReader
from clients.clientA.code.converter import ClientAConverter
from clients.clientB.code.reader import ClientBCsvReader, ClientBExcelReader
from clients.clientB.code.converter import ClientBConverter
from clients.clientC.code.reader import ClientCSqlReader
from clients.clientC.code.converter import ClientCConverter

# Reader-Registry
readers = [
    ClientAJsonReader(),
    ClientACsvReader(),
    ClientBCsvReader(),
    ClientBExcelReader(),
    ClientCSqlReader()
]

# Converter-Registry
converters = [
    ClientAConverter(),
    ClientBConverter(),
    ClientCConverter()
]
```

## Client-Verzeichnisstruktur

Für jeden neuen Client sollte folgende Verzeichnisstruktur angelegt werden:

```
clients/
  └── clientX/
      ├── code/
      │   ├── __init__.py
      │   ├── reader.py       # Implementierung der Reader
      │   └── converter.py    # Implementierung der Converter
      └── projects/
          └── ...             # Client-spezifische Daten
```

## Ausführung

### Datenimport

```bash
# Client A, Projekt 1
python -m code.main import --client clientA --project project1 --input clients/clientA/project1

# Client B
python -m code.main import --client clientB --input clients/clientB/projects

# Client C
python -m code.main import --client clientC --input clients/clientC/projects
```

### Prozessausführung

```bash
# Visualisierung
python -m code.main run --process visualization --output ./output/visualization

# Berechnung
python -m code.main run --process calculation --output ./output/calculation

# Beide Prozesse
python -m code.main run --process all --output ./output
```

## Hinzufügen eines neuen Client-Plugins

### 1. Reader implementieren

Erstellen Sie eine Klasse, die das `IDataReader`-Protokoll implementiert:

```python
# clients/newclient/code/reader.py
from pathlib import Path
from typing import Dict, Any, List

class NewClientReader:
    """Reader für den neuen Client."""
    
    @property
    def name(self) -> str:
        return "NewClientReader"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_formats(self) -> List[str]:
        return ["format"]
    
    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".format" and "newclient" in str(path)
    
    def read_data(self, file_path: str) -> Dict[str, Any]:
        # Implementierung des Datenlesens
        ...
```

### 2. Converter implementieren

Erstellen Sie eine Klasse, die das `IDataConverter`-Protokoll implementiert:

```python
# clients/newclient/code/converter.py
from typing import Dict, Any, List
from ...code.common.models.base_models import InfrastructureElement

class NewClientConverter:
    """Converter für den neuen Client."""
    
    @property
    def name(self) -> str:
        return "NewClientConverter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_types(self) -> List[str]:
        return ["type1", "type2"]
    
    def can_convert(self, data: Dict[str, Any]) -> bool:
        # Prüfen, ob die Daten konvertiert werden können
        ...
    
    def convert(self, data: Dict[str, Any]) -> List[InfrastructureElement]:
        # Konvertieren der Daten in InfrastructureElement-Objekte
        ...
```

### 3. Plugin registrieren

Fügen Sie Ihre neuen Plugins zur Registry hinzu:

```python
# code/plugin_registry.py
from clients.newclient.code.reader import NewClientReader
from clients.newclient.code.converter import NewClientConverter

# Bestehende Registrierungen...

# Neue Reader hinzufügen
readers.append(NewClientReader())

# Neue Converter hinzufügen
converters.append(NewClientConverter())
```

## Fehlerbehebung

### Häufige Probleme

1. **Reader kann Datei nicht lesen**
   - Prüfen Sie die `can_handle`-Methode des Readers
   - Prüfen Sie den Dateipfad und die Dateiendung

2. **Converter kann Daten nicht konvertieren**
   - Prüfen Sie die `can_convert`-Methode des Converters
   - Prüfen Sie die Ausgabe des Readers

3. **Elemente werden nicht im Repository gefunden**
   - Prüfen Sie, ob die UUIDs korrekt gesetzt sind
   - Prüfen Sie den Repository-Pfad in der Konfiguration

4. **Parameter werden nicht richtig gemappt**
   - Prüfen Sie die ProcessEnum-Zuordnung im Converter
   - Prüfen Sie, ob die Parameter in der known_params-Map vorhanden sind
EOF < /dev/null