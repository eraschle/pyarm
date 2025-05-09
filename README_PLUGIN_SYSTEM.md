# PyArm Plugin-System

PyArm (Python Architecture Restructuring Model) ist ein komponentenbasiertes Framework für die Modellierung von Infrastrukturelementen. Es verwendet ein Plugin-System, das eine parallele Entwicklung von Plugins und dem Core ermöglicht.

## Architektur

Das PyArm-System ist in mehrere Module gegliedert:

```
src/
└── pyarm/               # Hauptpaket
    ├── core/            # Kernfunktionalität
    │   ├── models/      # Basis-Modelle
    │   └── enums/       # Enumerationen
    ├── interfaces/      # Schnittstellen für Plugins
    ├── utils/           # Hilfsfunktionen
    └── plugins/         # Plugin-Management
```

Daneben gibt es Verzeichnisse für externe Plugins:

```
plugins/                 # Eingebaute Plugins
client_plugins/          # Kundenspezifische Plugins
```

## Plugin-Entwicklung

### 1. Plugin-Schnittstelle

Jedes Plugin muss die `PluginInterface`-Schnittstelle implementieren:

```python
from pyarm.interfaces.plugin import PluginInterface

class MyPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "My Plugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialisierung des Plugins
        return True
    
    def get_supported_element_types(self) -> List[str]:
        return ["my_element_type"]
    
    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        # Element-Konvertierung
        return converted_data
```

### 2. Plugin-Verzeichnisstruktur

Ein Plugin kann auf mehrere Arten integriert werden:

#### a) Als eingebautes Plugin

```
plugins/
└── my_plugin/
    └── __init__.py  # Enthält die Plugin-Klasse
```

#### b) Als Kundenspezifisches Plugin

```
client_plugins/
└── client_a/
    └── __init__.py  # Enthält die Plugin-Klasse
```

#### c) Als eigenständiges Paket

```
my_plugin_package/
├── setup.py
└── my_plugin/
    └── __init__.py  # Enthält die Plugin-Klasse
```

Mit `setup.py`:

```python
setup(
    name="pyarm-plugin-my-plugin",
    packages=["my_plugin"],
    entry_points={
        "pyarm.plugins": [
            "my_plugin = my_plugin",
        ],
    },
)
```

### 3. Plugin-Entdeckung

PyArm entdeckt Plugins auf drei Arten:

1. **Eingebaute Plugins**: Plugins im `plugins/`-Verzeichnis
2. **Kundenspezifische Plugins**: Plugins im `client_plugins/`-Verzeichnis und anderen Verzeichnissen, die in `PYARM_PLUGIN_PATHS` definiert sind
3. **Installierte Plugins**: Plugins, die über `entry_points` registriert sind

## Verwendung

### 1. Installation

Entwicklungsmodus:

```bash
# Für das Core-Paket
pip install -e .

# Für ein Plugin-Paket
pip install -e my_plugin_package/
```

### 2. Plugin-Verwendung

```python
from pyarm.core.app import Application

# Initialisiere die Anwendung
app = Application()

# Lade alle verfügbaren Plugins
app.load_plugins({
    "My Plugin": {
        "option1": "value1"
    }
})

# Verwende ein Plugin
result = app.convert_element(data, "my_element_type")
```

### 3. Plugin-Entwicklung

Das Skript `examples/create_client_plugin.py` kann verwendet werden, um ein neues Plugin zu erstellen:

```bash
python examples/create_client_plugin.py "Client A"
```

## Entwicklungsumgebung

### 1. Verzeichnisstruktur

Die src-Struktur bietet mehrere Vorteile:

- Klare Trennung zwischen Paket- und Projektdateien
- Konsistente Import-Struktur
- Bessere Interaktion mit Typcheckern

### 2. Typprüfung

Die Konfiguration in `pyrightconfig.json` sorgt dafür, dass Typchecker die Plugin-Struktur verstehen.

### 3. Import-Strategie

Für Plugins wird empfohlen, absolute Imports zu verwenden:

```python
# Gut für Plugins
from pyarm.interfaces.plugin import PluginInterface

# Statt relativer Imports
from ...interfaces.plugin import PluginInterface
```

## Entwicklungsworkflow

1. **Core-Entwicklung**:
   - Arbeiten im `src/pyarm`-Verzeichnis
   - Fokus auf Schnittstellen und gemeinsamer Funktionalität

2. **Plugin-Entwicklung**:
   - Arbeiten in `plugins/` oder `client_plugins/`
   - Implementierung spezifischer Konvertierungen

3. **Tests**:
   - Paralleles Testen von Core und Plugins mit `examples/test_plugin.py`

## Vorteile des Aufbaus

1. **Unabhängige Entwicklung**: Core und Plugins können unabhängig entwickelt werden
2. **Klare Schnittstellen**: Gut definierte Plugin-Schnittstelle
3. **Flexible Erweiterbarkeit**: Einfaches Hinzufügen neuer Plugins
4. **Typunterstützung**: Volle IDE-Unterstützung und Typprüfung
5. **Mehrere Integrationsoptionen**: Plugins können auf verschiedene Arten integriert werden

## Beispiele

Weitere Beispiele finden sich im `examples/`-Verzeichnis:

- `test_plugin.py`: Zeigt, wie Plugins geladen und verwendet werden
- `create_client_plugin.py`: Erstellt ein neues Client-Plugin