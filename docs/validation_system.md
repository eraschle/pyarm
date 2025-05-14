# Validierungssystem in PyArm

Das Validierungssystem ist eine zentrale Komponente in PyArm, die dafür sorgt, dass die durch Plugins konvertierten Daten den Anforderungen des kanonischen Modells entsprechen. Es ermöglicht die Definition von Regeln, die Überprüfung der Daten und die Meldung von Fehlern und Warnungen.

## Architektur des Validierungssystems

```mermaid
classDiagram
    class IValidationService {
        <<Interface>>
        +register_validator(validator)
        +validate_element(data, element_type) ValidationResult
        +validate_collection(data, element_type) List[ValidationResult]
        +get_validation_summary(results) Dict
        +create_validation_report(element_type, results) Dict
    }
    
    class ValidationService {
        -_validators: List[IValidator]
        +register_validator(validator)
        +get_validators_for_type(element_type) List[IValidator]
        +validate_element(data, element_type) ValidationResult
        +validate_collection(data, element_type) List[ValidationResult]
        +get_validation_summary(results) Dict
        +create_validation_report(element_type, results) Dict
    }
    
    class IValidator {
        <<Interface>>
        +supported_element_types: List[ElementType]
        +can_validate(element_type) bool
        +validate(data, element_type) ValidationResult
    }
    
    class ElementValidator {
        -_schemas: Dict[ElementType, SchemaDefinition]
        +supported_element_types: List[ElementType]
        +can_validate(element_type) bool
        +validate(data, element_type) ValidationResult
        -_validate_specific(data, element_type, result, element_id) 
    }
    
    class ValidationResult {
        +errors: List[ValidationError]
        +warnings: List[ValidationWarning]
        +is_valid: bool
        +has_critical_errors: bool
        +has_errors: bool
        +has_warnings: bool
        +add_error(error)
        +add_warning(warning)
        +merge(other_result)
    }
    
    class SchemaDefinition {
        +element_type: ElementType
        +required_params: Set[ProcessEnum]
        +param_types: Dict[ProcessEnum, DataType]
        +param_units: Dict[ProcessEnum, UnitEnum]
        +constraints: Dict[ProcessEnum, List[Constraint]]
        +add_required_param(param)
        +add_param_type(param, type)
        +add_param_unit(param, unit)
        +add_constraint(param, constraint)
    }
    
    class Constraint {
        +constraint_type: ConstraintType
        +parameter: ProcessEnum
        +message: str
        +context: Dict
        +validate(value, element_type, element_id) Optional[ValidationError]
    }
    
    IValidationService <|-- ValidationService
    IValidator <|-- ElementValidator
    ElementValidator --> SchemaDefinition : verwendet
    ElementValidator --> ValidationResult : erzeugt
    SchemaDefinition --> Constraint : enthält
    Constraint --> ValidationResult : erzeugt Fehler für
    ValidationService --> IValidator : verwaltet
```

## Validierungsprozess

Der Validierungsprozess in PyArm folgt einem mehrschichtigen Ansatz:

```mermaid
flowchart TD
    SourceData[Quelldaten] --> PluginLayer
    
    subgraph PluginLayer[Plugin-Schicht]
        Plugin --> ValidatedPlugin[ValidatedPlugin]
    end
    
    subgraph ValidationLayer[Validierungsschicht]
        ValidatedPlugin --> ValidationService
        ValidationService --> ElementValidator
        ElementValidator --> SpecificValidator[Spezifische Validatoren]
    end
    
    subgraph SchemaLayer[Schema-Schicht]
        ElementValidator --> SchemaDefinition
        SchemaDefinition --> Constraints[Constraints]
    end
    
    subgraph ResultLayer[Ergebnisschicht]
        ValidationResult[ValidationResult]
        ValidationError[ValidationError]
        ValidationWarning[ValidationWarning]
    end
    
    ElementValidator --> ValidationResult
    SpecificValidator --> ValidationResult
    Constraints -->|Fehler/Warnungen| ValidationError & ValidationWarning
    ValidationError & ValidationWarning --> ValidationResult
    
    ValidationResult --> ValidatedPlugin
    ValidatedPlugin -->|Wenn valide| ConvertedData[Konvertierte Daten]
    ValidatedPlugin -->|Bei Fehlern| ErrorHandling[Fehlerbehandlung]
    
    style PluginLayer fill:#bbf,stroke:#333,stroke-width:1px
    style ValidationLayer fill:#bfb,stroke:#333,stroke-width:1px
    style SchemaLayer fill:#fbb,stroke:#333,stroke-width:1px
    style ResultLayer fill:#f9f,stroke:#333,stroke-width:1px
```

## Komponenten des Validierungssystems

### ValidationService

Der ValidationService ist die zentrale Komponente des Validierungssystems und koordiniert die Validierung:

```mermaid
sequenceDiagram
    participant Client as Client
    participant ValidationSvc as ValidationService
    participant Validators as Validators
    participant Schema as SchemaDefinitions
    
    Client->>ValidationSvc: validate_element(data, "foundation")
    ValidationSvc->>ValidationSvc: get_validators_for_type("foundation")
    ValidationSvc->>Validators: für jeden Validator: validate(data, "foundation")
    
    loop For each validator
        Validators->>Schema: Validiere gegen Schema
        Schema-->>Validators: Validierungsergebnisse
    end
    
    Validators-->>ValidationSvc: ValidationResult
    ValidationSvc->>ValidationSvc: Ergebnisse zusammenführen
    ValidationSvc-->>Client: Finales ValidationResult
```

### SchemaDefinition

Die SchemaDefinition definiert die Anforderungen für einen bestimmten Elementtyp:

```mermaid
classDiagram
    class SchemaDefinition {
        +element_type: ElementType
        +required_params: Set[ProcessEnum]
        +param_types: Dict[ProcessEnum, DataType]
        +param_units: Dict[ProcessEnum, UnitEnum]
        +constraints: Dict[ProcessEnum, List[Constraint]]
    }
    
    class ProcessEnum {
        <<Enum>>
        +UUID
        +NAME
        +ELEMENT_TYPE
        +X_COORDINATE
        +Y_COORDINATE
        +Z_COORDINATE
        +FOUNDATION_WIDTH
        +FOUNDATION_DEPTH
        +...
    }
    
    class DataType {
        <<Enum>>
        +STRING
        +FLOAT
        +INTEGER
        +BOOLEAN
        +DATE
        +DATETIME
        +DICT
        +LIST
    }
    
    class UnitEnum {
        <<Enum>>
        +NONE
        +METER
        +MILLIMETER
        +KILOGRAM
        +NEWTON
        +DEGREE
        +...
    }
    
    class ConstraintType {
        <<Enum>>
        +REQUIRED
        +TYPE
        +UNIT
        +MIN_VALUE
        +MAX_VALUE
        +RANGE
        +REGEX
        +ENUM
        +CUSTOM
    }
    
    SchemaDefinition --> ProcessEnum : verwendet
    SchemaDefinition --> DataType : verwendet
    SchemaDefinition --> UnitEnum : verwendet
    Constraint --> ConstraintType : verwendet
    SchemaDefinition --> Constraint : enthält
```

### Constraint-Typen

Das Validierungssystem unterstützt verschiedene Arten von Constraints:

```mermaid
graph TD
    subgraph Schema[Schema-Definition]
        Required[Required<br>Parameter muss vorhanden sein]
        Type[Type<br>Parameter muss Typ entsprechen]
        Unit[Unit<br>Parameter muss Einheit entsprechen]
        MinValue[MinValue<br>Parameter muss über Mindestwert liegen]
        MaxValue[MaxValue<br>Parameter darf Maximalwert nicht überschreiten]
        Range[Range<br>Parameter muss in Bereich liegen]
        Regex[Regex<br>Parameter muss Pattern entsprechen]
        EnumVal[Enum<br>Parameter muss in Aufzählung sein]
        Custom[Custom<br>Benutzerdefinierte Validierung]
    end
    
    Required & Type & Unit & MinValue & MaxValue & Range & Regex & EnumVal & Custom -->|Angewendet auf| Parameters[Parameter-Validierung]
    
    Parameters -->|Erfüllt| Valid[Validierung erfolgreich]
    Parameters -->|Nicht erfüllt| Invalid[Validierungsfehler]
    
    style Schema fill:#bbf,stroke:#333,stroke-width:1px
    style Required,Type,Unit,MinValue,MaxValue,Range,Regex,EnumVal,Custom fill:#f9f,stroke:#333
    style Valid fill:#bfb,stroke:#333
    style Invalid fill:#fbb,stroke:#333
```

### Plugin-Integration

Die Integration des Validierungssystems in Plugins erfolgt über den ValidatedPlugin-Wrapper:

```mermaid
sequenceDiagram
    participant Client as Client
    participant ValidPlugin as ValidatedPlugin
    participant Plugin as Plugin
    participant ValidationSvc as ValidationService
    
    Client->>ValidPlugin: convert_element(data, "foundation")
    
    ValidPlugin->>ValidationSvc: validate_element(data, "foundation")
    ValidationSvc-->>ValidPlugin: ValidationResult
    
    alt Validierung erfolgreich
        ValidPlugin->>Plugin: convert_element(data, "foundation")
        Plugin-->>ValidPlugin: Konvertiertes Element
        ValidPlugin-->>Client: Konvertiertes Element
    else Validierung fehlgeschlagen bei strict_mode=true
        ValidPlugin-->>Client: Validierungsfehler
    else Validierung mit Warnungen bei ignore_warnings=true
        ValidPlugin->>Plugin: convert_element(data, "foundation")
        Plugin-->>ValidPlugin: Konvertiertes Element
        ValidPlugin-->>Client: Konvertiertes Element
    end
```

## Implementierung eines benutzerdefinierten Validators

Beispielcode für einen benutzerdefinierten Validator:

```python
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.validators import ElementValidator
from pyarm.validation.schema import Constraint, ConstraintType, SchemaDefinition
from pyarm.models.parameter import DataType, UnitEnum

class FoundationValidator(ElementValidator):
    """Spezialisierter Validator für Fundamente."""
    
    def __init__(self):
        super().__init__()
        
        # Schema für Fundamente definieren
        schema = SchemaDefinition(element_type=ElementType.FOUNDATION)
        
        # Erforderliche Parameter
        schema.add_required_param(ProcessEnum.X_COORDINATE)
        schema.add_required_param(ProcessEnum.Y_COORDINATE)
        schema.add_required_param(ProcessEnum.Z_COORDINATE)
        schema.add_required_param(ProcessEnum.FOUNDATION_WIDTH)
        schema.add_required_param(ProcessEnum.FOUNDATION_DEPTH)
        schema.add_required_param(ProcessEnum.FOUNDATION_HEIGHT)
        
        # Parametertypen festlegen
        schema.add_param_type(ProcessEnum.X_COORDINATE, DataType.FLOAT)
        schema.add_param_type(ProcessEnum.Y_COORDINATE, DataType.FLOAT)
        schema.add_param_type(ProcessEnum.Z_COORDINATE, DataType.FLOAT)
        schema.add_param_type(ProcessEnum.FOUNDATION_WIDTH, DataType.FLOAT)
        schema.add_param_type(ProcessEnum.FOUNDATION_DEPTH, DataType.FLOAT)
        schema.add_param_type(ProcessEnum.FOUNDATION_HEIGHT, DataType.FLOAT)
        
        # Einheiten festlegen
        schema.add_param_unit(ProcessEnum.X_COORDINATE, UnitEnum.METER)
        schema.add_param_unit(ProcessEnum.Y_COORDINATE, UnitEnum.METER)
        schema.add_param_unit(ProcessEnum.Z_COORDINATE, UnitEnum.METER)
        schema.add_param_unit(ProcessEnum.FOUNDATION_WIDTH, UnitEnum.METER)
        schema.add_param_unit(ProcessEnum.FOUNDATION_DEPTH, UnitEnum.METER)
        schema.add_param_unit(ProcessEnum.FOUNDATION_HEIGHT, UnitEnum.METER)
        
        # Constraints hinzufügen
        schema.add_constraint(
            ProcessEnum.FOUNDATION_WIDTH,
            Constraint(
                constraint_type=ConstraintType.RANGE,
                parameter=ProcessEnum.FOUNDATION_WIDTH,
                context={"min_value": 0.5, "max_value": 10.0},
                message="Fundamentbreite muss zwischen 0,5m und 10m liegen"
            )
        )
        
        schema.add_constraint(
            ProcessEnum.FOUNDATION_DEPTH,
            Constraint(
                constraint_type=ConstraintType.RANGE,
                parameter=ProcessEnum.FOUNDATION_DEPTH,
                context={"min_value": 0.5, "max_value": 10.0},
                message="Fundamenttiefe muss zwischen 0,5m und 10m liegen"
            )
        )
        
        schema.add_constraint(
            ProcessEnum.FOUNDATION_HEIGHT,
            Constraint(
                constraint_type=ConstraintType.RANGE,
                parameter=ProcessEnum.FOUNDATION_HEIGHT,
                context={"min_value": 0.3, "max_value": 5.0},
                message="Fundamenthöhe muss zwischen 0,3m und 5m liegen"
            )
        )
        
        # Schema registrieren
        self._schemas[ElementType.FOUNDATION] = schema
        
    def _validate_specific(self, data, element_type, result, element_id=None):
        """Spezifische Validierungslogik für Fundamente."""
        super()._validate_specific(data, element_type, result, element_id)
        
        # Zusätzliche, komplexere Validierungslogik
        if element_type == ElementType.FOUNDATION:
            # Beispiel: Prüfen, ob das Volumen in einem sinnvollen Bereich liegt
            width = data.get("width", 0)
            depth = data.get("depth", 0)
            height = data.get("height", 0)
            
            volume = width * depth * height
            
            if volume > 50:  # 50 m³
                result.add_warning(
                    ValidationWarning(
                        message=f"Fundamentvolumen ist sehr groß: {volume} m³",
                        element_type=element_type,
                        element_id=element_id,
                        context={"volume": volume, "max_expected": 50}
                    )
                )
```

## Validierungsergebnisse und Reporting

Das Validierungssystem erzeugt detaillierte Berichte:

```mermaid
graph TD
    Results[Validierungsergebnisse]
    
    Results --> Summary[Zusammenfassung]
    Results --> ErrorTypes[Fehlertypen]
    Results --> Examples[Beispiele]
    
    subgraph Summary["Zusammenfassung"]
        TotalElements[Gesamtzahl der Elemente]
        ValidElements[Gültige Elemente]
        InvalidElements[Ungültige Elemente]
        ValidationRate[Validierungsrate]
        ErrorCounts[Fehleranzahl nach Schweregrad]
    end
    
    subgraph ErrorTypes["Fehlertypen (sortiert nach Häufigkeit)"]
        ErrorType1[Fehlertyp 1: Nachricht + Anzahl]
        ErrorType2[Fehlertyp 2: Nachricht + Anzahl]
        ErrorType3[Fehlertyp 3: Nachricht + Anzahl]
    end
    
    subgraph Examples["Beispiele für jeden Fehlertyp"]
        Example1[Beispiel 1: Element-ID + Kontext]
        Example2[Beispiel 2: Element-ID + Kontext]
        Example3[Beispiel 3: Element-ID + Kontext]
    end
    
    style Results fill:#bbf,stroke:#333,stroke-width:1px
    style Summary fill:#bfb,stroke:#333,stroke-width:1px
    style ErrorTypes fill:#fbb,stroke:#333,stroke-width:1px
    style Examples fill:#f9f,stroke:#333,stroke-width:1px
```

Ein Beispiel für einen Validierungsbericht:

```json
{
  "element_type": "foundation",
  "summary": {
    "total_elements": 100,
    "valid_elements": 85,
    "invalid_elements": 15,
    "validation_rate": 0.85,
    "error_counts": {
      "CRITICAL": 2,
      "ERROR": 8,
      "WARNING": 10
    }
  },
  "error_types": [
    {
      "message": "Fundamentbreite muss zwischen 0,5m und 10m liegen",
      "count": 5,
      "severity": "ERROR",
      "examples": [
        {
          "element_index": 12,
          "element_type": "foundation",
          "element_id": "F12345",
          "parameter": "foundation_width",
          "context": {
            "value": 12.5,
            "min_value": 0.5,
            "max_value": 10.0
          }
        }
      ]
    },
    {
      "message": "Fundamentvolumen ist sehr groß",
      "count": 3,
      "severity": "WARNING",
      "examples": [
        {
          "element_index": 23,
          "element_type": "foundation",
          "element_id": "F67890",
          "context": {
            "volume": 65.2,
            "max_expected": 50
          }
        }
      ]
    }
  ]
}
```

## Konfiguration des Validierungssystems

Das Validierungssystem kann über die Konfiguration angepasst werden:

```mermaid
graph TD
    subgraph ValidatedPluginConfig[ValidatedPlugin-Konfiguration]
        StrictMode[strict_mode:<br>Bei Fehlern abbrechen?]
        IgnoreWarnings[ignore_warnings:<br>Warnungen ignorieren?]
        LogLevel[log_level:<br>Ausführlichkeit der Protokollierung]
    end
    
    subgraph ValidationConfig[Validierungskonfiguration]
        EnabledValidations[enabled_validations:<br>Aktivierte Validierungen]
        CustomConstraints[custom_constraints:<br>Benutzerdefinierte Constraints]
        ThresholdValues[threshold_values:<br>Schwellenwerte]
    end
    
    StrictMode & IgnoreWarnings & LogLevel --> ValidatedPlugin
    EnabledValidations & CustomConstraints & ThresholdValues --> ValidationService
    
    ValidatedPlugin --> ValidationService
    ValidationService --> ElementValidator
    
    style ValidatedPluginConfig fill:#bbf,stroke:#333,stroke-width:1px
    style ValidationConfig fill:#bfb,stroke:#333,stroke-width:1px
```

Beispiel für eine Konfiguration:

```json
{
  "plugins": {
    "ClientAPlugin": {
      "validation": {
        "strict_mode": true,
        "ignore_warnings": false,
        "log_level": "INFO",
        "enabled_validations": ["foundation", "mast", "track"],
        "custom_constraints": {
          "foundation": {
            "foundation_width": {
              "min_value": 0.8,
              "max_value": 8.0
            }
          }
        },
        "threshold_values": {
          "foundation_volume_warning": 40,
          "foundation_volume_error": 60
        }
      }
    }
  }
}
```

## Vorteile des Validierungssystems

1. **Datenqualität**: Stellt sicher, dass alle konvertierten Daten den Anforderungen entsprechen
2. **Frühzeitige Fehlererkennung**: Identifiziert Probleme bereits während der Konvertierung
3. **Flexible Validierungsregeln**: Unterstützt verschiedene Arten von Constraints
4. **Erweiterbarkeit**: Einfaches Hinzufügen neuer Validierungsregeln und Validator-Typen
5. **Detailliertes Reporting**: Bietet umfassende Berichte über Validierungsprobleme
6. **Konfigurierbarkeit**: Anpassbar an verschiedene Anforderungen und Szenarien

## Integration in den Konvertierungsprozess

```mermaid
flowchart LR
    RawData[Rohdaten] --> Plugin
    
    subgraph Plugin[Plugin]
        Reader[Daten-Reader] --> RawConverter[Rohkonverter]
    end
    
    subgraph Validation[Validierungssystem]
        ValidatedPlugin[ValidatedPlugin]
        ValidationService[ValidationService]
        Validators[Validator-Pool]
        SchemaDefinitions[Schema-Definitionen]
    end
    
    Plugin --> ValidatedPlugin
    ValidatedPlugin --> ValidationService
    ValidationService --> Validators
    Validators --> SchemaDefinitions
    
    ValidatedPlugin -->|Bei erfolgreicher Validierung| CanonicalModel[Kanonisches Modell]
    ValidatedPlugin -->|Bei Validierungsfehlern| ErrorReport[Fehlerbericht]
    
    classDef pluginClass fill:#bbf,stroke:#333
    classDef validationClass fill:#bfb,stroke:#333
    classDef modelClass fill:#fbb,stroke:#333
    
    class Plugin,Reader,RawConverter pluginClass
    class Validation,ValidatedPlugin,ValidationService,Validators,SchemaDefinitions validationClass
    class CanonicalModel,ErrorReport modelClass
```

## Fazit

Das Validierungssystem in PyArm ist eine leistungsstarke Komponente, die sicherstellt, dass alle Daten, die in das kanonische Modell konvertiert werden, den definierten Anforderungen entsprechen. Es bietet:

1. Eine flexible Schema-Definition für verschiedene Elementtypen
2. Verschiedene Arten von Constraints für umfassende Validierung
3. Detaillierte Fehlerberichte und Warnungen
4. Nahtlose Integration in das Plugin-System
5. Konfigurierbarkeit für verschiedene Anwendungsszenarien

Diese Architektur ermöglicht es, Probleme frühzeitig zu erkennen und zu beheben, bevor sie in nachgelagerten Prozessen zu Fehlern führen können, und trägt so wesentlich zur Datenqualität und Zuverlässigkeit des Systems bei.