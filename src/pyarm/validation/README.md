# Validierungssystem für PyArm Konverter

Diese Komponente bietet einen umfassenden Validierungsrahmen für Datenkonverter in PyArm, mit dem sichergestellt wird, dass alle Daten korrekt und konsistent sind, bevor sie in das kanonische Modell konvertiert werden.

## Überblick

Das Validierungssystem besteht aus mehreren Komponenten:

1. **Validierungsschema**: Definition der Anforderungen und Constraints für Elementtypen
2. **Validatoren**: Komponenten, die Daten gegen die Schemadefinitionen prüfen
3. **ValidationService**: Zentrale Komponente zur Koordination der Validierung
4. **Plugin-Integration**: Anbindung an das Plugin-System für nahtlose Validierung

## Architektur

```
[Client-Daten] → [Plugin] → [ValidationLayer] → [ValidationService] → [ElementValidator] → [Konvertierung]
```

Das System verwendet einen mehrschichtigen Ansatz:

- **Schemadefinitionen** beschreiben die Anforderungen für verschiedene Elementtypen
- **ElementValidator** prüft die Daten gegen die Schemadefinitionen
- **Spezialisierte Validatoren** bieten zusätzliche elementtypspezifische Validierungen
- **ValidationService** koordiniert die Validator-Komponenten
- **ValidatedPlugin** ist ein Wrapper für Plugins, der Validierung vor der Konvertierung durchführt

## Verwendung

### Basisvalidierung

```python
from pyarm.validation.service import ValidationService
from pyarm.validation.validators import ElementValidator
from pyarm.models.process_enums import ElementType

# ValidationService erstellen
validation_service = ValidationService()

# Validator erstellen und registrieren
foundation_validator = ElementValidator(ElementType.FOUNDATION)
validation_service.register_validator(foundation_validator)

# Element validieren
result = validation_service.validate_element(foundation_data, "foundation")
if result.is_valid:
    print("Validierung erfolgreich!")
else:
    print("Validierungsfehler:", result)
```

### Plugin-Integration

```python
from pyarm.validation.service import ValidationService
from pyarm.validation.plugin_integration import ValidationPluginWrapper
from plugins.client_a import ClientAPlugin

# ValidationService erstellen und Validatoren registrieren
validation_service = ValidationService()
# ... Validatoren registrieren ...

# Plugin laden
client_plugin = ClientAPlugin()

# Plugin mit Validierung umhüllen
validated_plugin = ValidationPluginWrapper.wrap_plugin(client_plugin, validation_service)

# Plugin initialisieren
config = {
    "validation": {
        "strict_mode": True,   # Bei Validierungsfehlern abbrechen
        "ignore_warnings": False,  # Warnungen berücksichtigen
        "log_level": "INFO"    # Logging-Level
    },
    "other_config": "..."
}
validated_plugin.initialize(config)

# Daten konvertieren (mit Validierung)
result = validated_plugin.convert_element(data, "foundation")
```

### Eigene Validatoren erstellen

Für spezifische Validierungsregeln können eigene Validatoren implementiert werden:

```python
from pyarm.validation.validators import ElementValidator
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.schema import Constraint, ConstraintType

class CustomFoundationValidator(ElementValidator):
    def __init__(self):
        super().__init__(ElementType.FOUNDATION)
        
        # Schema aus der Basisklasse erweitern
        schema = self._schemas[ElementType.FOUNDATION]
        
        # Zusätzliche Constraints hinzufügen
        schema.add_range_constraint(
            ProcessEnum.WIDTH,
            min_value=0.5,
            max_value=10.0,
            message="Foundation-Breite muss zwischen 0.5m und 10m liegen"
        )
        
    def _validate_specific(self, data, element_type, result, element_id=None):
        super()._validate_specific(data, element_type, result, element_id)
        
        # Eigene spezifische Validierungslogik implementieren
        # ...
```

## Funktionen

### Validierungsergebnisse

Das System liefert detaillierte Validierungsergebnisse mit:

- Fehlermeldungen und Warnungen mit unterschiedlichen Schweregraden
- Kontextinformationen für jedes Problem
- Element- und Parameter-Bezug für einfache Nachverfolgung

### Validierungsberichte

Der ValidationService kann Berichte erstellen:

```python
results = validation_service.validate_collection(elements_data, "foundation")
report = validation_service.create_validation_report("foundation", results)
print(json.dumps(report, indent=2))
```

### Konfiguration

Das Validierungssystem ist konfigurierbar:

- **Strict Mode**: Bricht die Konvertierung bei Fehlern ab
- **Ignore Warnings**: Ignoriert Warnungen und berücksichtigt nur Fehler
- **Log Level**: Konfiguriert die Ausführlichkeit der Protokollierung

## Integration in bestehende Systeme

Das System kann leicht in bestehende Anwendungen integriert werden:

1. Validatoren für die benötigten Elementtypen erstellen
2. ValidationService erstellen und Validatoren registrieren
3. Plugins mit ValidationPluginWrapper umhüllen oder direkt ValidationService verwenden
4. Mit Plugin- oder Validierungskonfiguration anpassen