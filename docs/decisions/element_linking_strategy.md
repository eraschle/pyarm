# Element Linking Strategy mit Component Pattern

- **Datum**: 2023-05-13
- **Autor**: PyArm Team
- **Status**: Implementiert

## Problem Statement

Fundamente und Masten sind in den Client-Daten oft nicht über UUIDs miteinander verbunden, sondern über proprietäre IDs oder andere Attribute. Ein Mechanismus wurde benötigt, um diese Verbindungen während des Imports herzustellen und danach die UUIDs für die Referenzen zu verwenden.

## Prozessübersicht

Der Element-Linking-Prozess läuft wie folgt ab:

```mermaid
sequenceDiagram
    participant Plugin as Client-Plugin
    participant Linker as ElementLinker
    participant Cache as Element-Cache
    participant Element as Infrastruktur-Element
    
    Note over Plugin,Element: Importphase beginnt
    
    Plugin->>Linker: register_link_definition(source: Foundation, target: Mast, params: "MastID" -> "ID")
    Plugin->>Linker: register_element(foundation)
    Linker->>Cache: Speichere Element unter seinen Attributwerten
    Plugin->>Linker: register_element(mast)
    Linker->>Cache: Speichere Element unter seinen Attributwerten
    
    Plugin->>Linker: process_element_links(foundation)
    Linker->>Cache: Suche Mast mit ID = foundation.MastID
    Cache-->>Linker: Gefundenes Mast-Element
    Linker->>Element: foundation.add_reference(Mast, mast.uuid, bidirectional=true)
    
    Note over Plugin,Element: Bei bidirektionaler Verknüpfung
    Linker->>Element: mast.add_reference(Foundation, foundation.uuid)
    
    Note over Plugin,Element: Importphase endet
```

## Chosen Approach: ElementLinker mit LinkDefinitions und Component Pattern

Der bestehende Plugin-Mechanismus wurde erweitert, um eine flexible Verbindung zwischen Elementen basierend auf beliebigen Client-Attributen zu ermöglichen. Dabei wird das Component Pattern genutzt, um Referenzen als Komponenten zu modellieren:

- Ein `ElementLinker` verwaltet Verknüpfungen zwischen Elementen
- `LinkDefinition`-Objekte definieren, welche Parameter für die Verknüpfung verwendet werden
- Die Verknüpfung erfolgt während der Importphase innerhalb des Plugin-Bereichs
- Nach dem Finden einer Verknüpfung werden `ElementReference`-Komponenten erstellt
- Diese Komponenten werden den Elementen hinzugefügt und verwenden die UUIDs als stabile Referenzen

Das Component Pattern ermöglicht eine klare Trennung zwischen:
1. Der Identität eines Elements (UUID)
2. Den Attributen eines Elements (Parameter)
3. Den Beziehungen eines Elements zu anderen Elementen (Reference-Komponenten)

## Implementation

### Component Pattern für Referenzen

Im Kern des Designs steht die `ElementReference`-Komponente, die das Component Pattern implementiert:

```python
class ElementReference(Component):
    """Komponente für die Referenz zu einem anderen Element."""

    def __init__(
        self,
        name: str,
        referenced_uuid: UUID,
        reference_type: Type["InfrastructureElement"],
        bidirectional: bool = False,
        component_type: ComponentType = ComponentType.REFERENCE,
    ):
        """Initialisiert eine ElementReference-Komponente."""
        super().__init__(name=name, component_type=component_type)
        self.referenced_uuid = referenced_uuid
        self.reference_type = reference_type
        self.bidirectional = bidirectional
```

Diese Komponente wird den Elementen hinzugefügt, wenn eine Verknüpfung gefunden wird:

```python
def add_reference(
    self,
    reference_type: Type["InfrastructureElement"],
    referenced_uuid: UUID,
    bidirectional: bool = False,
) -> None:
    """Fügt eine Referenz zu einem anderen Element hinzu."""
    reference = ComponentFactory.create_reference(
        reference_type, referenced_uuid, bidirectional
    )
    self.add_component(reference)
```

### Link Definition

Die LinkDefinition definiert, wie Elemente verknüpft werden sollen:

```mermaid
classDiagram
    class LinkDefinition {
        +source_type: Type[InfrastructureElement]
        +target_type: Type[InfrastructureElement]
        +source_param_name: str
        +target_param_name: str
        +source_process_enum: Optional[ProcessEnum]
        +target_process_enum: Optional[ProcessEnum]
        +bidirectional: bool
        +__init__(source_type, target_type, ...)
        +get_source_param_value(element) Any
        +get_target_param_value(element) Any
    }
    
    class ElementLinker {
        -link_definitions: List[LinkDefinition]
        -element_cache: Dict[str, Dict[str, List[InfrastructureElement]]]
        -uuid_cache: Dict[str, InfrastructureElement]
        -processed_elements: Set[UUID]
        -links_created: int
        +register_link_definition(link_definition)
        +register_element(element)
        +process_element_links(element)
        -_create_reference(source, target, link_def)
    }
    
    class InfrastructureElement {
        +name: str
        +element_type: ElementType
        +uuid: UUID
        +parameters: List[Parameter]
        +components: Dict[str, Component]
    }
    
    LinkDefinition --> InfrastructureElement : definiert Beziehung
    ElementLinker --> LinkDefinition : verwendet
    ElementLinker --> InfrastructureElement : verknüpft
```

### ElementLinker Integration

Der ElementLinker wird im Plugin während der Initialisierung eingerichtet:

```python
def initialize(self, config: Dict[str, Any]) -> bool:
    """Initialisiert das Plugin mit der Konfiguration."""
    log.info(f"Initialisiere {self.name} v{self.version}")
    log.debug(f"Konfiguration: {config}")
    
    try:
        from pyarm.linking.element_linker import ElementLinker
        self._element_linker = ElementLinker()
        
        # Link-Definitionen basierend auf der Konfiguration registrieren
        self._configure_element_links(config)
        log.info("ElementLinker wurde erfolgreich initialisiert")
    except ImportError:
        log.warning("ElementLinker konnte nicht importiert werden.")
        self._element_linker = None
    
    return True
```

Während der Konvertierung werden Elemente im Linker registriert und Verknüpfungen hergestellt:

```python
# Konvertierte Elemente zum ElementLinker hinzufügen für die spätere Verknüpfung
if self._element_linker:
    # Elemente im Linker registrieren
    for element in converted_elements:
        self._element_linker.register_element(element)
        
    # Verarbeite Verknüpfungen für die neuen Elemente
    for element in converted_elements:
        self._element_linker.process_element_links(element)
```

Der ElementLinker selbst verarbeitet die Verknüpfungen und erstellt Reference-Komponenten:

```mermaid
flowchart TD
    subgraph Plugin["Plugin-Initialisierung"]
        Initialize["Plugin.initialize()"] --> ConfigureLinks["_configure_element_links()"]
        ConfigureLinks --> RegisterLinks["element_linker.register_link_definition()"]
    end
    
    subgraph ImportPhase["Import-Phase"]
        Convert["Plugin.convert_element()"] --> RegisterElement["element_linker.register_element()"]
        RegisterElement --> ProcessLinks["element_linker.process_element_links()"]
    end
    
    subgraph ElementLinker["ElementLinker"]
        ProcessLinks --> FindLinks["Suche passende LinkDefinition"]
        FindLinks --> CheckCache["Suche Ziel-Element im Cache"]
        CheckCache -->|Gefunden| CreateRef["Erstelle Referenz-Komponente"]
        CreateRef --> AddComponent["element.add_component(reference)"]
    end
    
    style Plugin fill:#bbf,stroke:#333,stroke-width:1px
    style ImportPhase fill:#bfb,stroke:#333,stroke-width:1px
    style ElementLinker fill:#fbb,stroke:#333,stroke-width:1px
```

## Konfiguration der Verknüpfungen

Die Verknüpfungsdefinitionen können in der Plugin-Konfiguration angegeben werden:

```json
{
  "plugin_config": {
    "ClientA Plugin": {
      "element_links": {
        "project1": {
          "foundation_mast": {
            "source_type": "foundation",
            "target_type": "mast",
            "source_param": "MastID",
            "target_param": "ID"
          }
        }
      }
    }
  }
}
```

## Alternatives Considered

### 1. Nachträgliche Verknüpfung außerhalb des Plugins

Eine Alternative wäre, die Verknüpfung nach dem Import in einem separaten Prozess durchzuführen. Dies hätte jedoch mehrere Nachteile:
- Getrennte Verantwortlichkeiten führen zu höherem Integrationsaufwand
- Client-spezifisches Wissen müsste an zwei Stellen verwaltet werden
- Kein direkter Zugriff auf die internen Strukturen der Client-Daten

### 2. Festes Attribut-Mapping mit UUID-Konvertierung

Eine einfachere Lösung wäre, bei der Konvertierung direkt UUIDs basierend auf einem festen Attribut-Mapping zuzuweisen. Diese Lösung wäre jedoch weniger flexibel:
- Keine Unterstützung für unterschiedliche Projekte mit unterschiedlichen Attributnamen
- Schwieriger zu konfigurieren und zu erweitern
- Keine Möglichkeit, komplexere Verknüpfungslogik zu implementieren

## Reasoning

Die gewählte Lösung bietet mehrere Vorteile:

1. **Flexibilität**: Die Lösung kann mit verschiedenen Client-Daten-Formaten und Attributnamen umgehen
2. **Projektkonfiguration**: Spezifische Verknüpfungsregeln können pro Projekt definiert werden
3. **Plugin-Integration**: Die Verknüpfung erfolgt während der Importphase, was die Datenintegrität verbessert
4. **Bidirektionalität**: Unterstützt bidirektionale Referenzen für konsistente Datenmodelle
5. **Erweiterbarkeit**: Der Mechanismus kann leicht um weitere Elementtypen erweitert werden

### Vorteile des Component Patterns im Kontext der Referenzen

Das Component Pattern bietet spezifische Vorteile für die Verwaltung von Elementbeziehungen:

1. **Separation of Concerns**: Die Kernidentität eines Elements bleibt unabhängig von seinen Beziehungen
2. **Flexibles Hinzufügen/Entfernen**: Referenzen können dynamisch hinzugefügt oder entfernt werden, ohne das Element selbst zu ändern
3. **Typ-Sicherheit**: Referenzen enthalten Typinformationen über das referenzierte Element
4. **Zugriffskontrolle**: Komponenten bieten eine einheitliche Schnittstelle für den Zugriff auf Referenzen
5. **Selbstbeschreibend**: Die Komponenten-Struktur macht Referenzen explizit und dokumentiert

## Code Example

LinkDefinition-Registrierung für projektspezifische Verknüpfungen:

```python
# Für Projekt 1: Fundament -> Mast über "MastID" -> "ID"
self._element_linker.register_link_definition(
    LinkDefinition(
        source_type=Foundation,
        target_type=Mast,
        source_param_name="MastID",
        target_param_name="ID",
        source_process_enum=ProcessEnum.FOUNDATION_TO_MAST_UUID,
        target_process_enum=ProcessEnum.UUID,
        bidirectional=True,
    )
)

# Für Projekt 2: Joch -> Mast über "MastAnschlussID" -> "MastID"
self._element_linker.register_link_definition(
    LinkDefinition(
        source_type=Joch,
        target_type=Mast,
        source_param_name="MastAnschlussID",
        target_param_name="MastID",
        bidirectional=True,
    )
)
```

## Limitations and Future Considerations

- **Performance**: Bei sehr großen Datenmengen könnte die Cache-Verwaltung Optimierungen benötigen
- **Validierung**: Zusätzliche Validierungsmechanismen könnten eingebaut werden, um fehlerhafte Verknüpfungen zu erkennen
- **Konflikterkennung**: Derzeit werden Konflikte bei mehreren möglichen Verknüpfungen nicht explizit behandelt
- **Konfiguration**: Ein schema-basierter Konfigurationsmechanismus könnte die Definition von Verknüpfungsregeln vereinfachen

### Component Pattern Erweiterungen

Das Component Pattern könnte in Zukunft weiter ausgebaut werden:

- **Composite-Komponenten**: Komponenten könnten selbst wieder Komponenten enthalten, was komplexere Strukturen ermöglicht
- **Bedingte Komponenten**: Komponenten könnten basierend auf bestimmten Bedingungen aktiviert oder deaktiviert werden
- **Ereignisgesteuerte Komponenten**: Komponenten könnten auf Änderungen in anderen Komponenten reagieren
- **Shared Components**: Komponenten könnten zwischen mehreren Elementen geteilt werden, um gemeinsame Eigenschaften zu modellieren
- **Lazy Loading**: Referenzierte Elemente könnten bei Bedarf geladen werden, statt alle Referenzen sofort aufzulösen