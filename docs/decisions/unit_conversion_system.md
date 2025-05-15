# Einheitenumrechnungssystem

**Datum**: 2025-05-15  
**Autor**: Claude (nach Nutzeranweisungen)  
**Status**: Implementiert

## Problem

Bei der Infrastrukturmodellierung arbeiten wir oft mit Messungen in verschiedenen Einheiten. Verschiedene Kunden, Standards und Domänen könnten unterschiedliche Einheitensysteme (metrisch) oder verschiedene Maßstäbe innerhalb desselben Systems (Millimeter vs. Meter) verwenden. Wir benötigen einen robusten Ansatz, um:

1. Verschiedene Arten von Einheiten darzustellen
2. Zwischen kompatiblen Einheiten umzurechnen
3. Einheitenumrechnungen in Parametern zu handhaben
4. Einheiten bei Bedarf zu standardisieren

## Entscheidung

Wir haben ein umfassendes Einheitenumrechnungssystem mit den folgenden Komponenten implementiert:

1. Ein `UnitCategory`-Enum zur Kategorisierung der Messarten
2. Ein erweitertes `UnitEnum` mit Kategorien für verschiedene Messungstypen
3. Ein hierarchisches Umrechnungssystem, das über Basiseinheiten konvertiert
4. Umrechnungsmethoden auf Parameter-Ebene
5. Integration mit der `ParameterFactory` für automatische Umrechnung während der Parametererstellung

### Einheitenkategorien

Einheiten sind in den folgenden Kategorien organisiert:

- Länge (m, cm, mm, km)
- Fläche (m², cm², mm², km², ha)
- Volumen (m³, cm³, mm³, L, mL)
- Masse (kg, g, mg, t)
- Kraft (N, kN, MN)
- Winkel (deg, rad, grad)
- Verhältnis (%, ‰, :)
- Zeit (s, min, h, d)
- Temperatur (°C, K)
- Druck (Pa, kPa, MPa, bar)
- Geschwindigkeit (m/s, km/h)

### Umrechnungsstrategie

Unsere Umrechnungsstrategie verwendet einen zweistufigen Ansatz:

1. Umrechnung von der Quelleinheit zur Basiseinheit (z.B. Zentimeter → Meter)
2. Umrechnung von der Basiseinheit zur Zieleinheit (z.B. Meter → Kilometer)

Basiseinheiten für jede Kategorie:
- Länge: Meter
- Fläche: Quadratmeter
- Volumen: Kubikmeter
- Masse: Kilogramm
- Kraft: Newton
- Winkel: Radiant
- Verhältnis: Dezimalzahl
- Zeit: Sekunden
- Temperatur: Kelvin
- Druck: Pascal
- Geschwindigkeit: Meter pro Sekunde

Dieser Ansatz vereinfacht die Implementierung und Wartung, da wir nur Umrechnungen zu und von Basiseinheiten definieren müssen, anstatt jede mögliche Kombination abzudecken.

## Implementierung

### UnitCategory-Enum

Ein neues `UnitCategory`-Enum wurde erstellt, um die Kategorien zu definieren:

```python
class UnitCategory(str, Enum):
    """Categories for units of measurement"""
    
    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    MASS = "mass"
    FORCE = "force"
    ANGLE = "angle"
    RATIO = "ratio"
    TIME = "time"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VELOCITY = "velocity"
    UNKNOWN = "unknown"
```

### Einheiten-Aufzählung

Das `UnitEnum` in `parameter.py` wurde erweitert, um einen umfassenden Satz von Einheiten zu enthalten, die nach Kategorie organisiert sind:

```python
class UnitEnum(str, Enum):
    """Units for parameters, organized by measurement type"""

    # Length units
    METER = "m"
    CENTIMETER = "cm"
    MILLIMETER = "mm"
    KILOMETER = "km"
    
    # Area units
    SQUARE_METER = "m²"
    SQUARE_CENTIMETER = "cm²"
    # ... weitere Einheiten ...
```

### Erkennung der Einheitenkategorie

Die Funktion `get_unit_category` wurde hinzugefügt, um die Kategorie einer Einheit zu identifizieren:

```python
def get_unit_category(unit: UnitEnum) -> UnitCategory:
    """Determines the category of a unit."""
    # Implementierung mit kategorisierten Listen
    # ...
```

### Umrechnungssystem

Das Umrechnungssystem verwendet spezialisierte Umrechnungsfunktionen für jede Kategorie:

```python
def convert_unit(value: int | float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Converts a value from one unit to another."""
    # Prüfen, ob Einheiten aus der gleichen Kategorie stammen
    from_category = get_unit_category(from_unit)
    to_category = get_unit_category(to_unit)
    
    if from_category != to_category:
        raise ValueError(
            f"Cannot convert between different unit categories: {from_category.value} and {to_category.value}"
        )
    
    # Delegieren an spezifische Umrechnungsfunktionen
    if from_category == UnitCategory.LENGTH:
        return _convert_length(value, from_unit, to_unit)
    # ... andere Kategorien ...
```

Jede Kategorie hat eine spezialisierte Umrechnungsfunktion wie `_convert_length`, `_convert_area` usw.

### Parameter-Ebene-Umrechnung

Wir haben dem `Parameter`-Objekt Methoden hinzugefügt, um Einheitenumrechnungen zu unterstützen:

```python
def convert_to(self, target_unit: UnitEnum) -> "Parameter":
    """Convert this parameter to a different unit."""
    # Implementierung...

def with_standard_unit(self) -> "Parameter":
    """Convert this parameter to the standard SI unit for its unit category."""
    # Implementierung...
```

Diese Methoden machen es einfach, einzelne Parameter ohne manuelle Berechnungen umzurechnen.

### Parametererstellung mit Einheitenumrechnung

Die `ParameterFactory` wurde erweitert, um Einheitenumrechnungen während der Parametererstellung zu verarbeiten:

```python
def create(cls, name: str, process_enum: Optional[ProcessEnum], value: Any) -> Parameter:
    # ...
    # Umgang mit unterschiedlichen Einheiten zwischen benutzerdefinierten 
    # und Standard-Parametern
    if custom_param.unit != UnitEnum.NONE and custom_param.unit != parameter.unit:
        # Implementierung mit Einheitenumrechnung...
    # ...
```

Dies ermöglicht die nahtlose Verwendung verschiedener Einheiten in Parameterdefinitionen und tatsächlichen Parameterwerten.

### Listen-Ebene-Umrechnung

Für Batch-Operationen haben wir Funktionen hinzugefügt, um mehrere Parameter gleichzeitig umzurechnen:

```python
def convert_parameter_list_units(
    parameters: list["Parameter"], 
    unit_map: dict[UnitEnum, UnitEnum]
) -> list["Parameter"]:
    """Konvertiert Einheiten von Parametern in einer Liste gemäß einer Zuordnung."""
    # Implementierung...

def standardize_units(parameters: list["Parameter"]) -> list["Parameter"]:
    """Konvertiert alle Parameter in Standard-SI-Einheiten."""
    # Implementierung...
```

## Betrachtete Alternativen

### Einfacheres System mit festen Einheiten

Wir haben erwogen, ein einziges Einheitensystem (z.B. nur SI-Einheiten) im gesamten Codebase zu erzwingen. Dies würde die Implementierung vereinfachen, wäre aber weniger flexibel für Benutzer, die mit verschiedenen Einheitensystemen arbeiten.

### Lookup-Tabellen-Ansatz

Wir haben eine direkte Lookup-Tabelle für alle möglichen Einheitenumrechnungen in Betracht gezogen. Dies wäre für einige wenige Einheitentypen einfacher, würde aber unhandlich werden, wenn mehr Einheiten hinzugefügt werden (Komplexität O(n²)).

## Vorteile des gewählten Ansatzes

1. **Wartbarkeit**: Durch die zweistufige Umrechnung über Basiseinheiten ist das Hinzufügen neuer Einheiten unkompliziert.
2. **Typsicherheit**: Die Verwendung von Enums bietet Compile-Zeit-Sicherheit und Autovervollständigungsunterstützung.
3. **Flexibilität**: Das System ermöglicht die nahtlose Arbeit mit verschiedenen Einheitensystemen.
4. **Integration**: Das Umrechnungssystem ist eng in unser Parametermodell integriert.
5. **Leistung**: Die Implementierung ist leichtgewichtig und leistungsstark, ohne externe Abhängigkeiten.

## Einschränkungen

1. **Nicht alle Einheiten abgedeckt**: Während wir viele gängige Einheiten einbezogen haben, könnten spezialisierte Domänen Einheiten verwenden, die noch nicht unterstützt werden.
2. **Keine Dimensionsanalyse**: Im Gegensatz zu speziellen Einheitenbibliotheken erzwingt unser System keine Dimensionskonsistenz zur Compile-Zeit.
3. **Keine Unsicherheitsfortpflanzung**: Wir verfolgen keine Messunsicherheiten durch Umrechnungen.

## Codebeispiele

### Umrechnung zwischen Einheiten

```python
from pyarm.models.parameter import UnitEnum
from pyarm.utils.helpers import convert_unit

# 1 Meter in Zentimeter umrechnen
cm_value = convert_unit(1, UnitEnum.METER, UnitEnum.CENTIMETER)  # 100.0

# 0°C in Kelvin umrechnen
kelvin_value = convert_unit(0, UnitEnum.CELSIUS, UnitEnum.KELVIN)  # 273.15
```

### Parameter-Umrechnung

```python
from pyarm.models.parameter import Parameter, DataType, UnitEnum
from pyarm.models.process_enums import ProcessEnum

# Parameter mit Zentimetern erstellen
length_param = Parameter(
    name="Länge",
    value=100.0,
    datatype=DataType.FLOAT,
    process=ProcessEnum.LENGTH,
    unit=UnitEnum.CENTIMETER
)

# In Meter umrechnen
meters_param = length_param.convert_to(UnitEnum.METER)  # value = 1.0

# In Standardeinheit umrechnen (Meter für Länge)
standard_param = length_param.with_standard_unit()  # Dasselbe wie oben
```

### Standardisierung von Einheiten

```python
from pyarm.utils.helpers import standardize_units

# Liste von Parametern in verschiedenen Einheiten
mixed_units_params = [
    Parameter(name="Länge", value=100.0, datatype=DataType.FLOAT, unit=UnitEnum.CENTIMETER),
    Parameter(name="Masse", value=1000.0, datatype=DataType.FLOAT, unit=UnitEnum.GRAM)
]

# Alle in Standard-SI-Einheiten umrechnen
standardized = standardize_units(mixed_units_params)
# Länge: 1.0 m, Masse: 1.0 kg
```

## Zukünftige Überlegungen

1. Unterstützung für weitere spezialisierte Einheiten nach Bedarf hinzufügen
2. Unterstützung für zusammengesetzte Einheiten (z.B. kg/m²) hinzufügen
3. Dimensionsanalyse hinzufügen, um ungültige Umrechnungen zur Laufzeit zu verhindern
4. Unterstützung für Unsicherheitsfortpflanzung bei Messungen hinzufügen