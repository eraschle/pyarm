# Repository-System in PyArm

Das Repository-System in PyArm bietet eine abstrakte Schicht zum Speichern und Abrufen von Infrastrukturelementen, wobei ein datenträgerbezogenes Caching-System für optimale Leistung verwendet wird.

## Architektur des Repository-Systems

```mermaid
classDiagram
    class IElementRepository {
        <<Interface>>
        +get_all() List[InfrastructureElement]
        +get_by_id(uuid) Optional[InfrastructureElement]
        +get_by_type(element_type) List[InfrastructureElement]
        +save(element) None
        +save_all(elements) None
        +delete(uuid) None
        +clear() None
    }
    
    class JsonElementRepository {
        -repository_path: Path
        -_elements_cache: Dict[str, InfrastructureElement]
        -_cache_loaded: bool
        +__init__(repository_path)
        +ensure_directory_exists()
        -_load_cache()
        -_save_cache()
        +get_all() List[InfrastructureElement]
        +get_by_id(uuid) Optional[InfrastructureElement]
        +get_by_type(element_type) List[InfrastructureElement]
        +save(element) None
        +save_all(elements) None
        +delete(uuid) None
        +clear() None
        +backup() str
    }
    
    class InfrastructureElement {
        +name: str
        +element_type: ElementType
        +uuid: UUID
        +parameters: List[Parameter]
        +components: Dict[str, Component]
        +to_dict() Dict
    }
    
    IElementRepository <|-- JsonElementRepository
    JsonElementRepository --> InfrastructureElement : verwaltet
    
    class ElementType {
        <<Enum>>
        +FOUNDATION
        +MAST
        +CANTILEVER
        +TRACK
        +CURVED_TRACK
        +JOCH
        +DRAINAGE
    }
    
    InfrastructureElement --> ElementType : hat
```

## Kernkonzepte

Das Repository-System basiert auf mehreren Kernkonzepten:

1. **Abstrakte Repository-Schnittstelle**: Eine gemeinsame Schnittstelle für alle Repositorys
2. **In-Memory-Caching**: Zwischenspeicherung für effiziente Abfragen
3. **Typsichere Operationen**: Abfragen nach UUID oder Elementtyp
4. **Persistenz**: Dauerhafte Speicherung von Daten in verschiedenen Formaten

## Datenflussmuster

```mermaid
flowchart TD
    subgraph "Anwendungsschicht"
        Application[Anwendung]
    end
    
    subgraph "Repository-Schicht"
        IRepo[IElementRepository]
        JsonRepo[JsonElementRepository]
        InMemCache[In-Memory-Cache]
        JsonStore[(JSON-Dateisystem)]
    end
    
    subgraph "Domänenmodell"
        Elements[InfrastructureElements]
    end
    
    Application -->|1. Anfrage Element| IRepo
    IRepo -->|2. Delegiert| JsonRepo
    JsonRepo -->|3. Prüft Cache| InMemCache
    
    InMemCache -->|4a. Cache-Treffer| JsonRepo
    InMemCache -->|4b. Cache-Fehler| JsonRepo
    
    JsonRepo -->|5. Lädt bei Cache-Fehler| JsonStore
    JsonStore -->|6. Lädt Rohdaten| JsonRepo
    JsonRepo -->|7. Wandelt um| Elements
    JsonRepo -->|8. Speichert in Cache| InMemCache
    
    JsonRepo -->|9. Gibt Element zurück| IRepo
    IRepo -->|10. Liefert Ergebnis| Application
    
    Application -->|11. Speichert Element| IRepo
    IRepo -->|12. Delegiert| JsonRepo
    JsonRepo -->|13. Aktualisiert Cache| InMemCache
    JsonRepo -->|14. Schreibt auf Datenträger| JsonStore
    
    style Application fill:#f9f,stroke:#333,stroke-width:1px
    style IRepo fill:#bbf,stroke:#333,stroke-width:1px
    style JsonRepo fill:#bbf,stroke:#333,stroke-width:1px
    style InMemCache fill:#bfb,stroke:#333,stroke-width:1px
    style JsonStore fill:#fbb,stroke:#333,stroke-width:1px
    style Elements fill:#ddd,stroke:#333,stroke-width:1px
```

## Hauptkomponenten

### IElementRepository-Schnittstelle

```python
@runtime_checkable
class IElementRepository(Protocol):
    def get_all(self) -> list[InfrastructureElement]:
        """Ruft alle Elemente ab."""
        ...

    def get_by_id(self, uuid: UUID | str) -> InfrastructureElement | None:
        """Ruft ein Element anhand seiner UUID ab."""
        ...

    def get_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        """Ruft Elemente eines bestimmten Typs ab."""
        ...

    def save(self, element: InfrastructureElement) -> None:
        """Speichert ein Element."""
        ...

    def save_all(self, elements: list[InfrastructureElement]) -> None:
        """Speichert mehrere Elemente."""
        ...

    def delete(self, uuid: UUID | str) -> None:
        """Löscht ein Element."""
        ...
```

### JsonElementRepository

Die `JsonElementRepository`-Klasse implementiert die `IElementRepository`-Schnittstelle und bietet JSON-basierte Persistenz:

```python
class JsonElementRepository:
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self._elements_cache: dict[str, InfrastructureElement] = {}
        self._cache_loaded = False
        
    def _load_cache(self) -> None:
        # Elemente aus JSON-Dateien in den Speicher laden
        if self._cache_loaded:
            return
            
        self._elements_cache.clear()
        
        for file_path in self.repository_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                elements_data = json.load(f)
                
            for element_data in elements_data:
                element = factory.create_element(element_data)
                uuid_str = str(element.uuid)
                self._elements_cache[uuid_str] = element
                
        self._cache_loaded = True
```

## Cache-Management-Muster

```mermaid
stateDiagram-v2
    [*] --> Uninitialisiert
    Uninitialisiert --> Leer: Repository erstellen
    
    Leer --> CacheGeladen: _load_cache()
    CacheGeladen --> CacheGeladen: get_by_id()\nget_all()\nget_by_type()
    
    CacheGeladen --> CacheModifiziert: save()\nsave_all()\ndelete()
    CacheModifiziert --> CacheGeladen: _save_cache()
    
    CacheModifiziert --> Leer: clear()
    CacheGeladen --> Leer: clear()
    
    state CacheModifiziert {
        [*] --> ElementeGeändert
        ElementeGeändert --> AufDateiSystemGeschrieben: _save_cache()
        AufDateiSystemGeschrieben --> [*]
    }
```

## Besondere Merkmale

### Lazy Loading

Das Repository verwendet Lazy Loading, um die Leistung zu optimieren:

1. Der Cache wird erst bei der ersten Anfrage geladen
2. Alle weiteren Anfragen verwenden den Cache

```mermaid
sequenceDiagram
    participant App as Anwendung
    participant Repo as JsonElementRepository
    participant Cache as Cache
    participant FS as Dateisystem
    
    App->>Repo: get_by_id(uuid)
    Repo->>Repo: _load_cache()
    
    alt Cache nicht geladen
        Repo->>FS: Lade JSON-Dateien
        FS-->>Repo: JSON-Daten
        Repo->>Cache: Speichere Element-Objekte
    end
    
    Repo->>Cache: Suche nach UUID
    Cache-->>Repo: Element (oder None)
    Repo-->>App: Element (oder None)
```

### Gruppierung nach Elementtyp

Bei der Speicherung werden Elemente nach Typ gruppiert:

```mermaid
flowchart LR
    subgraph "Cache"
        element1["Element UUID1"]
        element2["Element UUID2"]
        element3["Element UUID3"]
        element4["Element UUID4"]
    end
    
    subgraph "Nach Typ gruppieren"
        groupByType[Gruppiere nach Elementtyp]
    end
    
    subgraph "JSON-Dateien"
        foundation[foundation.json]
        mast[mast.json]
        track[track.json]
    end
    
    element1 & element2 & element3 & element4 --> groupByType
    groupByType --> foundation & mast & track
    
    style groupByType fill:#bbf,stroke:#333
```

## Integration in die Anwendung

```python
# Repository erstellen
repository = JsonElementRepository("./data/repository")

# Elemente speichern
foundation = Foundation(name="Fundament 1")
repository.save(foundation)

# Element abrufen
retrieved_foundation = repository.get_by_id(foundation.uuid)

# Elemente nach Typ abrufen
masts = repository.get_by_type(ElementType.MAST)

# Backup erstellen
backup_path = repository.backup()
print(f"Backup wurde erstellt unter: {backup_path}")
```

## Vorteile

1. **Abstraktion**: Die Repository-Schnittstelle abstrahiert die Datenpersistenz
2. **Leistung**: In-Memory-Caching für schnelle Abfragen
3. **Typsicherheit**: Typisierte Methoden für sichere Operationen
4. **Sicherheit**: Automatische Backups und Fehlervermeidung
5. **Erweiterbarkeit**: Leicht um neue Repository-Implementierungen erweiterbar