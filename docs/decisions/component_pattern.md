# Component Pattern für Infrastrukturelemente

- **Datum**: 2023-05-13
- **Autor**: PyArm Team
- **Status**: Implementiert

## Problem Statement
  
Infrastrukturelemente wie Maste, Fundamente und Gleise haben verschiedene Aspekte, die modelliert werden müssen:
- Geometrische Eigenschaften (Position, Dimension, Orientierung)
- Beziehungen zu anderen Elementen (Referenzen)
- Spezifische Attribute je nach Elementtyp und Anwendungsfall
- Zusätzliche, prozessspezifische Informationen (Visualisierung, Berechnung)

Eine monolithische Implementierung würde zu Klassen mit zu vielen Verantwortlichkeiten führen:
- Schwer zu erweitern
- Geringe Wiederverwendbarkeit
- Hohe Kopplung zwischen verschiedenen Aspekten
- Schlechte Testbarkeit

## Struktur des Component Patterns

Das folgende Klassendiagramm zeigt die Struktur des Component Patterns in PyArm:

```mermaid
classDiagram
    class Component {
        <<abstract>>
        +name: str
        +component_type: ComponentType
        +to_dict() Dict
    }
    
    class ComponentType {
        <<enum>>
        LOCATION
        DIMENSION
        REFERENCE
        METADATA
        PHYSICAL
        VISUAL
        CUSTOM
        BUILDING_PHASE
    }
    
    class InfrastructureElement {
        +name: str
        +element_type: ElementType
        +uuid: UUID
        +parameters: List[Parameter]
        +components: Dict[str, Component]
        +get_component(name: str) Component
        +get_components_by_type(type: ComponentType) List[Component]
        +add_component(component: Component) void
        +remove_component(name: str) bool
    }
    
    class Location {
        <<abstract>>
    }
    
    class PointLocation {
        +x: float
        +y: float
        +z: float
    }
    
    class LineLocation {
        +points: List[Tuple[float, float, float]]
    }
    
    class Dimension {
        <<abstract>>
    }
    
    class RectangularDimension {
        +width: float
        +depth: float
        +height: float
    }
    
    class CylindricalDimension {
        +diameter: float
        +height: float
    }
    
    class ElementReference {
        +reference_type: str
        +referenced_uuid: UUID
        +bidirectional: bool
    }
    
    class ComponentFactory {
        +{static} create_location(element) Location
        +{static} create_dimension(element) Dimension
        +{static} create_reference(...) ElementReference
    }
    
    Component -- ComponentType
    Component <|-- Location
    Component <|-- Dimension
    Component <|-- ElementReference
    
    Location <|-- PointLocation
    Location <|-- LineLocation
    
    Dimension <|-- RectangularDimension
    Dimension <|-- CylindricalDimension
    
    InfrastructureElement o-- "*" Component : enthält
    
    ComponentFactory ..> Component : erzeugt >
    ComponentFactory ..> Location : erzeugt >
    ComponentFactory ..> Dimension : erzeugt >
    ComponentFactory ..> ElementReference : erzeugt >
```

## Chosen Approach: Component Pattern

Das Component Pattern wurde implementiert, um diese Herausforderungen zu adressieren:

```python
class Component:
    """Basisklasse für alle Komponenten."""
    
    def __init__(self, name: str, component_type: ComponentType):
        self.name = name
        self.component_type = component_type
```

Infrastrukturelemente (wie `Foundation`, `Mast`, etc.) enthalten Komponenten für verschiedene Aspekte:

```python
@dataclass
class InfrastructureElement[TDimension: Dimension]:
    """Base class for all infrastructure elements."""
    
    # Basisattribute
    name: str
    element_type: ElementType
    uuid: UUID = field(default_factory=uuid4)
    
    # Parameter für prozessspezifische Daten
    parameters: list[Parameter] = field(default_factory=list)
    known_params: dict[ProcessEnum, Parameter] = field(default_factory=dict)
    
    # Komponenten für verschiedene Aspekte des Elements
    components: dict[str, "Component"] = field(default_factory=dict)
```

## Implementierte Komponententypen

### Location-Komponente
    
Verwaltet die räumliche Position eines Elements:

```python
class Location(Component):
    """Abstrakte Basisklasse für Positionierungskomponenten."""
    
    def __init__(self, name: str, component_type: ComponentType = ComponentType.LOCATION):
        super().__init__(name=name, component_type=component_type)
        
class PointLocation(Location):
    """Punktpositionierung im 3D-Raum."""
    
    def __init__(self, name: str, x: float, y: float, z: float = 0.0):
        super().__init__(name=name)
        self.x = x
        self.y = y
        self.z = z
        
class LineLocation(Location):
    """Lineare Positionierung im 3D-Raum, definiert durch mehrere Punkte."""
    
    def __init__(self, name: str, points: List[Tuple[float, float, float]]):
        super().__init__(name=name)
        self.points = points
```

### Dimension-Komponente

Verwaltet die physikalischen Abmessungen eines Elements:

```python
class Dimension(Component):
    """Abstrakte Basisklasse für Dimensionskomponenten."""
    
    def __init__(self, name: str, component_type: ComponentType = ComponentType.DIMENSION):
        super().__init__(name=name, component_type=component_type)
        
class RectangularDimension(Dimension):
    """Rechteckige Abmessungen."""
    
    def __init__(self, name: str, width: float, depth: float, height: float):
        super().__init__(name=name)
        self.width = width
        self.depth = depth
        self.height = height
        
class CylindricalDimension(Dimension):
    """Zylindrische Abmessungen."""
    
    def __init__(self, name: str, diameter: float, height: float):
        super().__init__(name=name)
        self.diameter = diameter
        self.height = height
```

### Reference-Komponente

Verwaltet Beziehungen zu anderen Elementen:

```python
class ElementReference(Component):
    """Komponente für die Referenz zu einem anderen Element."""

    def __init__(
        self,
        name: str,
        referenced_uuid: UUID,
        reference_type: str,
        bidirectional: bool = False,
        component_type: ComponentType = ComponentType.REFERENCE,
    ):
        super().__init__(name=name, component_type=component_type)
        self.referenced_uuid = referenced_uuid
        self.reference_type = reference_type
        self.bidirectional = bidirectional
```

## Factory für Komponenten

Eine Factory-Klasse vereinfacht die Erstellung von Komponenten:

```python
class ComponentFactory:
    """Factory für die Erstellung von Komponenten."""
    
    @staticmethod
    def create_location(element: InfrastructureElement) -> Location:
        """Erstellt eine Location-Komponente basierend auf den Parametern des Elements."""
        try:
            x = element.get_param(ProcessEnum.X_COORDINATE).value
            y = element.get_param(ProcessEnum.Y_COORDINATE).value
            z = element.get_param(ProcessEnum.Z_COORDINATE).value
            return PointLocation("location", x, y, z)
        except PyArmParameterError:
            # Fallback für Elemente ohne Koordinaten
            return PointLocation("location", 0, 0, 0)
            
    @staticmethod
    def create_reference(
        reference_type: str, 
        referenced_uuid: UUID,
        bidirectional: bool = False
    ) -> ElementReference:
        """Erstellt eine ElementReference-Komponente."""
        return ElementReference(
            name=f"reference_to_{reference_type}",
            referenced_uuid=referenced_uuid,
            reference_type=reference_type,
            bidirectional=bidirectional,
        )
```

## Laufzeitbeispiel: Element mit Komponenten

Das folgende Objektdiagramm zeigt ein konkretes Beispiel eines Fundament-Elements mit seinen Komponenten:

```mermaid
graph TD
    subgraph foundation ["foundation: Foundation"]
        name["name = 'Fundament F123'"]
        element_type["element_type = ElementType.FOUNDATION"]
        uuid["uuid = '550e8400-e29b-41d4-a716-446655440000'"]
    end
    
    subgraph location ["location: PointLocation"]
        loc_name["name = 'location'"]
        component_type_loc["component_type = ComponentType.LOCATION"]
        x["x = 123.45"]
        y["y = 678.90"]
        z["z = 10.25"]
    end
    
    subgraph dimension ["dimension: RectangularDimension"]
        dim_name["name = 'dimension'"]
        component_type_dim["component_type = ComponentType.DIMENSION"]
        width["width = 2.50"]
        height["height = 1.80"]
        depth["depth = 3.00"]
    end
    
    subgraph ref_mast ["ref_mast: ElementReference"]
        ref_name["name = 'ref_mast_550e8400-e29b-41d4-a716-446655440001'"]
        component_type_ref["component_type = ComponentType.REFERENCE"]
        referenced_uuid["referenced_uuid = '550e8400-e29b-41d4-a716-446655440001'"]
        reference_type["reference_type = 'mast'"]
        bidirectional["bidirectional = true"]
    end
    
    foundation -->|components["location"]| location
    foundation -->|components["dimension"]| dimension
    foundation -->|components["ref_mast_..."]| ref_mast
    
    classDef elementClass fill:#bbf,stroke:#333,stroke-width:1px
    classDef componentClass fill:#bfb,stroke:#333,stroke-width:1px
    
    class foundation elementClass
    class location,dimension,ref_mast componentClass
```

## Verwendung von Komponenten in Infrastrukturelementen

Elemente können Komponenten abfragen und mit ihnen interagieren:

```python
# Komponente nach Typ abfragen
location = element.get_components_by_type(ComponentType.LOCATION)[0]

# Komponente nach Name abfragen
dimension = element.get_component("dimension")

# Referenzen verwalten
element.add_reference(
    reference_type="mast",
    referenced_uuid=mast_uuid,
    bidirectional=True
)

# Alle Referenzen eines bestimmten Typs abrufen
mast_references = [ref for ref in element.get_components_by_type(ComponentType.REFERENCE)
                  if ref.reference_type == "mast"]
```

## Vorteile des Component Patterns

1. **Separation of Concerns**: Jeder Aspekt (Position, Dimension, Referenzen) wird in einer eigenen Komponente gekapselt
2. **Modularität**: Komponenten können unabhängig voneinander entwickelt, getestet und wiederverwendet werden
3. **Erweiterbarkeit**: Neue Komponentenarten können hinzugefügt werden, ohne bestehende Elementtypen zu ändern
4. **Flexibilität**: Komponenten können dynamisch hinzugefügt oder entfernt werden
5. **Polymorphismus**: Unterschiedliche Implementierungen für den gleichen Komponententyp (z.B. PointLocation vs. LineLocation)

## Alternativen zum Component Pattern

### 1. Vererbungshierarchie

Eine Alternative wäre eine tiefe Vererbungshierarchie mit spezialisierten Klassen für jede Kombination von Eigenschaften.

**Nachteile:**
- Explosion der Anzahl an Klassen
- Mehrfachvererbung bei überlappenden Eigenschaften
- Schwierigkeiten beim Hinzufügen neuer Eigenschaften

### 2. Entity-Component-System (ECS)

Ein vollständiges ECS wäre eine andere Alternative, bei der Komponenten nur Daten enthalten und Systeme die Logik implementieren.

**Nachteile:**
- Komplexe Architektur für die einfachen Anforderungen
- Übermäßige Trennung von Daten und Verhalten
- Steiler Lernkurve für Entwickler

### 3. Mixin-Klassen

Mixins könnten verwendet werden, um Verhalten zu verschiedenen Elementtypen hinzuzufügen.

**Nachteile:**
- Komplexe Methodenauflösungsreihenfolge
- Implizite Abhängigkeiten zwischen Mixins
- Schwierigere Typisierung in statisch typisierten Sprachen

## Schlussfolgerung

Das Component Pattern bietet die beste Balance zwischen:
- Flexibilität für unterschiedliche Elementtypen
- Modularität und Wiederverwendbarkeit
- Erweiterbarkeit für neue Anforderungen
- Einfachheit der Implementierung

Es ermöglicht eine klare Trennung von Verantwortlichkeiten und gleichzeitig eine intuitive Objektstruktur, die der Domäne entspricht.

## Zukünftige Erweiterungen

- **Komponentenevents**: Komponenten könnten Events auslösen, wenn sich ihr Zustand ändert
- **Komponenten-Validatoren**: Validierung von Komponenten bei Hinzufügen zu einem Element
- **Kompozite Komponenten**: Komponenten, die selbst andere Komponenten enthalten
- **Dependency Injection**: Abhängigkeiten zwischen Komponenten explizit verwalten
- **Serialisierung**: Vollständige Serialisierung/Deserialisierung von Komponenten