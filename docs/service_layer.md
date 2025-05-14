# Service-Layer in PyArm

Die Service-Layer in PyArm bildet eine wichtige Architekturschicht, die zwischen der Anwendungslogik und der Datenrepräsentation vermittelt. Sie implementiert prozessspezifische Operationen wie Visualisierung, Berechnung und Datenexport.

## Architektur der Service-Layer

```mermaid
classDiagram
    class IService {
        <<Interface>>
        +process(data) Result
    }
    
    class VisualizationService {
        -repository: IElementRepository
        -visualization_config: Dict
        +__init__(repository, config)
        +process_element(element) Dict
        +process_elements(elements) List[Dict]
        +process_by_id(uuid) Dict
        +process_by_type(element_type) List[Dict]
        +customize_visualization(element, options) Dict
    }
    
    class CalculationService {
        -repository: IElementRepository
        -calculation_config: Dict
        +__init__(repository, config)
        +calculate_element(element) Dict
        +calculate_elements(elements) List[Dict]
        +calculate_by_id(uuid) Dict
        +calculate_by_type(element_type) List[Dict]
        +custom_calculation(element, formula) Dict
    }
    
    class ExportService {
        -repository: IElementRepository
        -export_config: Dict
        +__init__(repository, config)
        +export_element(element, format) bytes
        +export_elements(elements, format) bytes
        +export_by_id(uuid, format) bytes
        +export_by_type(element_type, format) bytes
    }
    
    IService <|-- VisualizationService
    IService <|-- CalculationService
    IService <|-- ExportService
    
    class IElementRepository {
        <<Interface>>
        +get_all() List[InfrastructureElement]
        +get_by_id(uuid) Optional[InfrastructureElement]
        +get_by_type(element_type) List[InfrastructureElement]
    }
    
    VisualizationService --> IElementRepository : verwendet
    CalculationService --> IElementRepository : verwendet
    ExportService --> IElementRepository : verwendet
    
    class InfrastructureElement {
        +name: str
        +element_type: ElementType
        +uuid: UUID
        +parameters: List[Parameter]
        +components: Dict[str, Component]
    }
    
    IElementRepository --> InfrastructureElement : liefert
```

## Service Layer im Gesamtsystem

```mermaid
flowchart TB
    subgraph "Client-Schicht"
        ClientApp[Client-Anwendung]
        WebApp[Web-Anwendung]
        CLI[Kommandozeile]
    end
    
    subgraph "Service-Schicht"
        VisualizationSvc[Visualisierungsdienst]
        CalculationSvc[Berechnungsdienst]
        ExportSvc[Exportdienst]
        ValidationSvc[Validierungsdienst]
    end
    
    subgraph "Repository-Schicht"
        Repo[Element-Repository]
    end
    
    subgraph "Modell-Schicht"
        Elements[Infrastrukturelemente]
    end
    
    ClientApp & WebApp & CLI -->|Anfrage| VisualizationSvc & CalculationSvc & ExportSvc
    
    VisualizationSvc & CalculationSvc & ExportSvc -->|Datenzugriff| Repo
    ValidationSvc -->|validiert| Elements
    Repo -->|liefert| Elements
    
    VisualizationSvc & CalculationSvc & ExportSvc -->|gibt zurück| ClientApp & WebApp & CLI
    
    classDef client fill:#f9f,stroke:#333,stroke-width:1px
    classDef service fill:#bbf,stroke:#333,stroke-width:1px
    classDef repo fill:#bfb,stroke:#333,stroke-width:1px
    classDef model fill:#fbb,stroke:#333,stroke-width:1px
    
    class ClientApp,WebApp,CLI client
    class VisualizationSvc,CalculationSvc,ExportSvc,ValidationSvc service
    class Repo repo
    class Elements model
```

## Prozessspezifische Dienste

### Visualisierungsdienst

Der Visualisierungsdienst wandelt Elemente in visuell darstellbare Formate um:

```mermaid
sequenceDiagram
    participant Client as Client
    participant VisSvc as VisualizationService
    participant Repo as ElementRepository
    participant Renderer as VisualizationRenderer
    
    Client->>VisSvc: process_element(element_id)
    VisSvc->>Repo: get_by_id(element_id)
    Repo-->>VisSvc: element
    
    VisSvc->>VisSvc: prepare_visualization_data(element)
    
    alt 3D-Visualisierung
        VisSvc->>Renderer: render_3d(visualization_data)
        Renderer-->>VisSvc: 3d_model
    else 2D-Visualisierung
        VisSvc->>Renderer: render_2d(visualization_data)
        Renderer-->>VisSvc: 2d_drawing
    end
    
    VisSvc-->>Client: visualization_result
```

### Berechnungsdienst

Der Berechnungsdienst führt prozessspezifische Berechnungen für Elemente durch:

```mermaid
flowchart TD
    Start[Element einlesen] --> PrepareData[Berechnungsdaten vorbereiten]
    PrepareData --> FetchParams[Parameter abrufen]
    
    FetchParams --> CheckParams{Alle notwendigen<br>Parameter vorhanden?}
    CheckParams -->|Nein| HandleMissing[Fehlende Parameter behandeln]
    HandleMissing --> ApproxParams[Approximieren oder<br>Standardwerte verwenden]
    ApproxParams --> PerformCalc
    
    CheckParams -->|Ja| PerformCalc[Berechnung durchführen]
    
    PerformCalc --> ValidateResult{Ergebnis<br>plausibel?}
    ValidateResult -->|Nein| ApplyConstraints[Beschränkungen anwenden]
    ApplyConstraints --> FormatResult
    
    ValidateResult -->|Ja| FormatResult[Ergebnis formatieren]
    FormatResult --> ReturnResult[Ergebnis zurückgeben]
    
    style FetchParams fill:#bbf,stroke:#333
    style PerformCalc fill:#bfb,stroke:#333
    style FormatResult fill:#fbb,stroke:#333
```

### Exportdienst

Der Exportdienst konvertiert Elemente in verschiedene Ausgabeformate:

```mermaid
graph TD
    subgraph Eingabe[Eingabe]
        Elements[Infrastrukturelemente]
    end
    
    subgraph Formate[Exportformate]
        JSON[JSON]
        XML[XML]
        CSV[CSV]
        IFC[IFC]
        CAD[CAD]
        PDF[PDF-Bericht]
    end
    
    subgraph Konfiguration[Exportkonfiguration]
        FormatConfig[Formateinstellungen]
        SchemaConfig[Schemaeinstellungen]
        FilterConfig[Filtereinstellungen]
    end
    
    Elements --> ExportService
    FormatConfig & SchemaConfig & FilterConfig --> ExportService
    
    ExportService --> JSON
    ExportService --> XML
    ExportService --> CSV
    ExportService --> IFC
    ExportService --> CAD
    ExportService --> PDF
    
    classDef inputClass fill:#bbf,stroke:#333
    classDef formatClass fill:#bfb,stroke:#333
    classDef configClass fill:#fbb,stroke:#333
    
    class Elements inputClass
    class JSON,XML,CSV,IFC,CAD,PDF formatClass
    class FormatConfig,SchemaConfig,FilterConfig configClass
```

## Implementierungsbeispiel: Visualisierungsdienst

```python
class VisualizationService:
    """Service für die Visualisierung von Infrastrukturelementen."""
    
    def __init__(self, repository: IElementRepository, config: Optional[Dict[str, Any]] = None):
        """Initialisiert den VisualizationService."""
        self.repository = repository
        self.config = config or {}
        
    def process_element(self, element: InfrastructureElement) -> Dict[str, Any]:
        """Verarbeitet ein einzelnes Element zur Visualisierung."""
        # Visualisierungsdaten vorbereiten
        visualization_data = self._prepare_visualization_data(element)
        
        # Komponenten extrahieren und hinzufügen
        if location := element.get_component("location"):
            visualization_data["position"] = {
                "x": location.x,
                "y": location.y,
                "z": location.z
            }
            
        if dimension := element.get_component("dimension"):
            if hasattr(dimension, "width"):  # RectangularDimension
                visualization_data["dimensions"] = {
                    "width": dimension.width,
                    "depth": dimension.depth,
                    "height": dimension.height,
                    "type": "rectangular"
                }
            elif hasattr(dimension, "diameter"):  # CylindricalDimension
                visualization_data["dimensions"] = {
                    "diameter": dimension.diameter,
                    "height": dimension.height,
                    "type": "cylindrical"
                }
        
        # Prozessspezifische Parameter
        for param in element.parameters:
            if param.process and param.process.value.startswith("VIS_"):
                visualization_data["parameters"][param.process.value] = {
                    "name": param.name,
                    "value": param.value,
                    "unit": param.unit.value if param.unit else None
                }
        
        # Element-Typ-spezifische Visualisierung
        if element.element_type == ElementType.FOUNDATION:
            self._enhance_foundation_visualization(element, visualization_data)
        elif element.element_type == ElementType.MAST:
            self._enhance_mast_visualization(element, visualization_data)
        # Weitere Elementtypen...
            
        return visualization_data
    
    def process_by_id(self, uuid: Union[UUID, str]) -> Optional[Dict[str, Any]]:
        """Verarbeitet ein Element anhand seiner UUID."""
        element = self.repository.get_by_id(uuid)
        if not element:
            return None
        return self.process_element(element)
    
    def process_by_type(self, element_type: ElementType) -> List[Dict[str, Any]]:
        """Verarbeitet alle Elemente eines bestimmten Typs."""
        elements = self.repository.get_by_type(element_type)
        return [self.process_element(element) for element in elements]
```

## Koordination der Dienste im Gesamtsystem

```mermaid
sequenceDiagram
    participant App as Anwendung
    participant Repo as ElementRepository
    participant VisSvc as VisualizationService
    participant CalcSvc as CalculationService
    participant ExpSvc as ExportService
    
    App->>Repo: Repository initialisieren
    App->>VisSvc: Visualisierungsdienst initialisieren
    App->>CalcSvc: Berechnungsdienst initialisieren
    App->>ExpSvc: Exportdienst initialisieren
    
    Note over App,ExpSvc: Workflow: Visualisierung und Berechnung
    
    App->>VisSvc: process_by_type(ElementType.FOUNDATION)
    VisSvc->>Repo: get_by_type(ElementType.FOUNDATION)
    Repo-->>VisSvc: Liste von Foundation-Elementen
    VisSvc-->>App: Visualisierungsdaten
    
    App->>CalcSvc: calculate_by_type(ElementType.FOUNDATION)
    CalcSvc->>Repo: get_by_type(ElementType.FOUNDATION)
    Repo-->>CalcSvc: Liste von Foundation-Elementen
    CalcSvc-->>App: Berechnungsergebnisse
    
    Note over App,ExpSvc: Workflow: Export der kombinierten Ergebnisse
    
    App->>App: Kombiniere Visualisierungs- und Berechnungsdaten
    App->>ExpSvc: export_data(kombinierte_daten, "PDF")
    ExpSvc-->>App: PDF-Datei
    
    Note over App,ExpSvc: Workflow: Speichern von Änderungen
    
    App->>Repo: save_all(aktualisierte_elemente)
    Repo-->>App: Bestätigung
```

## Vorteile der Service-Layer

1. **Separation of Concerns**: Klare Trennung von Geschäftslogik und Datenzugriff
2. **Wiederverwendbarkeit**: Dienste können von verschiedenen Anwendungen genutzt werden
3. **Testbarkeit**: Services sind leicht zu testen, da sie keine UI-Abhängigkeiten haben
4. **Flexibilität**: Neue Dienste können hinzugefügt werden, ohne bestehenden Code zu ändern
5. **Unabhängige Entwicklung**: Entwicklungsteams können an verschiedenen Diensten parallel arbeiten

## Konfiguration der Dienste

Dienste können über Konfigurationsdateien oder programmatisch konfiguriert werden:

```mermaid
graph TD
    ConfigFile[Konfigurationsdatei] -->|Laden| Config
    ProgramConfig[Programmatische Konfiguration] -->|Überschreiben| Config
    EnvVars[Umgebungsvariablen] -->|Überschreiben| Config
    
    subgraph Config[Dienstkonfiguration]
        VisualizationConfig[Visualisierungseinstellungen]
        CalculationConfig[Berechnungseinstellungen]
        ExportConfig[Exporteinstellungen]
    end
    
    Config -->|Anwenden auf| Services
    
    subgraph Services[Service-Schicht]
        VisualizationService
        CalculationService
        ExportService
    end
    
    classDef configClass fill:#bbf,stroke:#333
    classDef serviceClass fill:#bfb,stroke:#333
    
    class ConfigFile,ProgramConfig,EnvVars,VisualizationConfig,CalculationConfig,ExportConfig configClass
    class VisualizationService,CalculationService,ExportService serviceClass
```

## Fazit

Die Service-Layer in PyArm folgt dem bewährten Service-Layer-Pattern und bietet:

1. Eine klare Trennung von Geschäftslogik und Datenzugriff
2. Prozessspezifische Dienste für verschiedene Aspekte der Anwendung
3. Eine erweiterbare Architektur, die neue Funktionalitäten unterstützt
4. Eine flexible Konfiguration für verschiedene Anwendungsszenarien

Diese Architektur ermöglicht es, komplexe Anwendungslogik in managebaren, fokussierten Komponenten zu organisieren und fördert die Wartbarkeit und Erweiterbarkeit des Systems.