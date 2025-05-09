# PYM-Data: Plugin-basiertes Infrastruktur-Modellierungssystem

Dieses Projekt demonstriert eine flexible, erweiterbare Architektur zur Verarbeitung von Infrastrukturdaten aus verschiedenen Quellen und in unterschiedlichen Formaten. Durch die Verwendung eines plugin-basierten Designs können neue Datenquellen und Formatkonverter einfach hinzugefügt werden, ohne den Kerncode zu ändern.

## Überblick

Das System ist darauf ausgelegt, Infrastrukturdaten (Fundamente, Masten, Gleise usw.) aus verschiedenen Kundenformaten einzulesen, in ein einheitliches kanonisches Modell zu konvertieren und für unterschiedliche Prozesse wie Visualisierung und Berechnung bereitzustellen.

```mermaid
graph TD
    A[Client-Daten] -->|Reader Plugins| B[Roh-Daten]
    B -->|Converter Plugins| C[Kanonisches Modell]
    C -->|Repository| D[Datenspeicher]
    D -->|Service| E1[Prozess 1: Visualisierung]
    D -->|Service| E2[Prozess 2: Berechnung]

    subgraph "Flexible Datenquellen"
        A
    end

    subgraph "Plugin-System"
        B
        C
    end

    subgraph "Speicherschicht"
        D
    end

    subgraph "Prozess-Schichten"
        E1
        E2
    end
```

## Architektur

Das System basiert auf einer mehrschichtigen Architektur mit klaren Verantwortlichkeiten:

### Komponenten-Übersicht

```mermaid
classDiagram
    class IDataReader {
        <<interface>>
        +name() str
        +version() str
        +supported_formats() list[str]
        +can_handle(file_path) bool
        +read_data(file_path) dict
    }

    class IDataConverter {
        <<interface>>
        +name() str
        +version() str
        +supported_types() list[str]
        +can_convert(data) bool
        +convert(data) list[InfrastructureElement]
    }

    class IElementRepository {
        <<interface>>
        +get_all() list[InfrastructureElement]
        +get_by_id(uuid) InfrastructureElement
        +get_by_type(element_type) list[InfrastructureElement]
        +save(element) void
        +save_all(elements) void
        +delete(uuid) void
    }

    class IElementService {
        <<interface>>
        +get_element(uuid) InfrastructureElement
        +get_elements_by_type(element_type) list[InfrastructureElement]
        +create_element(element_data) InfrastructureElement
        +update_element(uuid, element_data) InfrastructureElement
        +delete_element(uuid) bool
    }

    class InfrastructureElement {
        +name: str
        +uuid: UUID
        +element_type: ElementType
        +parameters: list[Parameter]
        +known_params: dict[ProcessEnum, Any]
        +get_param(process_enum) Any
        +set_param(process_enum, value) void
    }

    IDataReader <|.. ClientAJsonReader: implementiert
    IDataReader <|.. ClientACsvReader: implementiert
    IDataReader <|.. ClientBCsvReader: implementiert
    IDataReader <|.. ClientBExcelReader: implementiert
    IDataReader <|.. ClientCSqlReader: implementiert

    IDataConverter <|.. ClientAConverter: implementiert
    IDataConverter <|.. ClientBConverter: implementiert
    IDataConverter <|.. ClientCConverter: implementiert

    IElementRepository <|.. JsonElementRepository: implementiert

    IElementService <|.. VisualizationService: implementiert
    IElementService <|.. CalculationService: implementiert

    ClientAConverter ..> InfrastructureElement: erzeugt
    ClientBConverter ..> InfrastructureElement: erzeugt
    ClientCConverter ..> InfrastructureElement: erzeugt

    JsonElementRepository o-- InfrastructureElement: speichert

    VisualizationService o-- IElementRepository: verwendet
    CalculationService o-- IElementRepository: verwendet,

```

### Datenfluss

```mermaid
flowchart LR
    A[Client-Daten]
    B{Reader}
    C{Converter}
    D[(Repository)]
    E{Service}
    F1[Visualisierung]
    F2[Berechnung]

    A -->|1. Datei einlesen| B
    B -->|2. Rohdaten| C
    C -->|3. Kanonisches Modell| D
    D -->|4. Daten abrufen| E
    E -->|5a. Aufbereitete Daten| F1
    E -->|5b. Aufbereitete Daten| F2

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F1 fill:#fbb,stroke:#333,stroke-width:2px
    style F2 fill:#fbb,stroke:#333,stroke-width:2px
```

## Schlüsselkonzepte

### Plugin-System mit Protokollen

Das System verwendet Protokolle (Interfaces) als Vertragsgarantie zwischen Komponenten. Dies ermöglicht eine lose Kopplung und einfache Erweiterbarkeit.

```mermaid
classDiagram
    class Protocol {
        <<interface>>
        +Methoden-Signaturen ohne Implementierung
    }

    class ConcreteImplementation {
        +Implementierung der Protokoll-Methoden
    }

    Protocol <|.. ConcreteImplementation: implementiert

    note for Protocol "Protokolle definieren, WAS eine Komponente tun kann"
    note for ConcreteImplementation "Implementierungen definieren, WIE es getan wird"
```

### Zentrales Enum-System für Parameter

Ein zentrales Enum-System ermöglicht die konsistente Zuordnung von unterschiedlich benannten Parametern aus verschiedenen Kunden-Datenformaten zu einem einheitlichen Modell:

```mermaid
graph TD
    E[ProcessEnum]

    C1[Client A: Breite]
    C2[Client B: breite_m]
    C3[Client C: width_mm]

    C1 -->|map to| E
    C2 -->|map to| E
    C3 -->|map to| E

    E -->|standardize as| P[ProcessEnum.FOUNDATION_WIDTH]

    style E fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style P fill:#bfb,stroke:#333,stroke-width:2px, color:#000
```

Dieses Enum-System löst mehrere Probleme:

1. **Unterschiedliche Benennungen**: "Breite", "width_mm", "breite_m" werden alle einem Standardparameter zugeordnet
2. **Unterschiedliche Einheiten**: Automatische Umrechnung von mm nach m usw.
3. **Unterschiedliche Strukturen**: Parameter können an verschiedenen Stellen in der Kundendatenstruktur vorkommen

### Mehrstufige Datenspeicherung

Im kanonischen Modell werden Parameter sowohl als Liste (für Flexibilität) als auch als Dictionary (für schnellen Zugriff) gespeichert:

```python
class InfrastructureElement:
    # Grundlegende Attribute
    name: str
    uuid: UUID
    element_type: ElementType

    # Parameter-Speicherung
    parameters: list[Parameter]  # Flexible Speicherung
    known_params: dict[ProcessEnum, Any]  # Für schnellen Zugriff
```

## Unterstützte Client-Formate

Das System unterstützt derzeit drei verschiedene Clients mit unterschiedlichen Datenformaten:

### Client A

- **Formate**: JSON, CSV
- **Besonderheiten**:
  - Verschiedene Projektversionen mit unterschiedlichen Feldnamen
  - Deutschsprachige Parameter
  - Dateiendungen: .json, .csv

### Client B

- **Formate**: CSV, Excel
- **Besonderheiten**:
  - Semikolon-getrennte Werte
  - Einheiten im Feldnamen (z.B. "breite_m")
  - Dateiendungen: .csv, .excel

### Client C

- **Formate**: SQL
- **Besonderheiten**:
  - Daten als SQL-INSERT-Anweisungen
  - Millimeter als Standardeinheit
  - Englische Feldnamen mit Unterstrichen
  - Dateiendungen: .sql

## Flexibilität des Systems demonstriert

Die Implementierung demonstriert verschiedene Arten von Flexibilität:

```mermaid
graph TD
    A[Format-Flexibilität]
    B[Parameter-Flexibilität]
    C[Struktur-Flexibilität]
    D[Prozess-Flexibilität]

    A -->|JSON, CSV, SQL| A1[Unterschiedliche Dateiformate]
    B -->|Enum-Mapping| B1[Unterschiedliche Parameterbezeichnungen und Einheiten]
    C -->|Version-Converter| C1[Unterschiedliche Datenstrukturen und Versionierung]
    D -->|Service-Layer| D1[Unterschiedliche Prozess-Anforderungen]

    style A fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style B fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style C fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style D fill:#bbf,stroke:#333,stroke-width:2px, color:#000
```

## Projektstruktur

```
pym_data/
  ├── README.md                    # Diese Datei
  ├── config/                      # Konfigurationsdateien
  ├── code/
  │   ├── common/                  # Gemeinsame Komponenten
  │   │   ├── enums/               # Enums für Parameter usw.
  │   │   ├── interfaces/          # Protokolle für Plugins
  │   │   ├── models/              # Kanonisches Datenmodell
  │   │   └── utils/               # Hilfsfunktionen
  │   ├── repository/              # Datenspeicher-Implementierungen
  │   ├── services/                # Service-Implementierungen
  │   └── processes/               # Prozess-Implementierungen
  └── clients/                     # Client-spezifische Implementierungen
      ├── clientA/
      │   ├── code/                # Reader und Converter für Client A
      │   ├── project1/            # Beispieldaten für Projekt 1
      │   └── project2/            # Beispieldaten für Projekt 2
      ├── clientB/
      │   ├── code/                # Reader und Converter für Client B
      │   └── projects/            # Beispieldaten
      └── clientC/
          ├── code/                # Reader und Converter für Client C
          └── projects/            # Beispieldaten
```

## Client-spezifische Implementierung

Jeder Client hat seine eigene Implementierung, die speziell auf seine Datenformate zugeschnitten ist. Beispiel für Client C (SQL-Daten):

```mermaid
classDiagram
    class IDataReader {
        <<interface>>
        +name() str
        +can_handle(file_path) bool
        +read_data(file_path) dict
    }

    class ClientCSqlReader {
        +name() str
        +can_handle(file_path) bool
        +read_data(file_path) dict
        -_extract_table_data(sql_content, table_name) list
        -_parse_values(values_str) list
    }

    class IDataConverter {
        <<interface>>
        +name() str
        +can_convert(data) bool
        +convert(data) list[InfrastructureElement]
    }

    class ClientCConverter {
        +name() str
        +can_convert(data) bool
        +convert(data) list[InfrastructureElement]
        -_convert_foundation(data) list[InfrastructureElement]
        -_convert_mast(data) list[InfrastructureElement]
        -_convert_drainage(data) list[InfrastructureElement]
    }

    IDataReader <|.. ClientCSqlReader: implementiert
    IDataConverter <|.. ClientCConverter: implementiert

    ClientCSqlReader --> ClientCConverter: Daten weiterleiten
```

## Prozess-spezifische Implementierung

Die gleichen Daten können für verschiedene Prozesse unterschiedlich aufbereitet werden:

```mermaid
graph TD
    R[(Repository)]
    VS[VisualizationService]
    CS[CalculationService]
    VP[Visualisierungsprozess]
    CP[Berechnungsprozess]

    R -->|getElement| VS
    R -->|getElement| CS

    VS -->|transformierteDaten| VP
    CS -->|transformierteDaten| CP

    VS -->|"prepareForVisualization()"| VD[Visualisierungsdaten:<br/>- Koordinaten<br/>- Farben<br/>- Geometrie]
    CS -->|"calculateForces()"| CD[Berechnungsdaten:<br/>- Lasten<br/>- Kräfte<br/>- Materialwerte]

    style R fill:#bfb,stroke:#333,stroke-width:2px, color:#000
    style VS fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style CS fill:#bbf,stroke:#333,stroke-width:2px, color:#000
    style VD fill:#fbb,stroke:#333,stroke-width:2px, color:#000
    style CD fill:#fbb,stroke:#333,stroke-width:2px, color:#000
```

## Vorteile der Architektur

1. **Erweiterbarkeit**: Neue Clients können einfach durch Hinzufügen neuer Reader und Converter integriert werden
2. **Wartbarkeit**: Klare Trennung der Verantwortlichkeiten, einfach zu verstehende Komponenten
3. **Testbarkeit**: Jede Komponente kann isoliert getestet werden
4. **Flexibilität**: Unterstützung für verschiedene Datenformate, Versionen und Prozesse
5. **Wiederverwendbarkeit**: Gemeinsame Komponenten wie das Repository können von verschiedenen Prozessen genutzt werden

## Weitere Dokumentation

Detaillierte Dokumentation zu den einzelnen Komponenten finden Sie in den spezialisierten Dokumentationsdateien:

- [Kanonisches Datenmodell & Enum-System](code/common/CANONICAL_MODEL.md) - Das Herzstück der Architektur
- [Repository Pattern](code/repository/REPOSITORY_PATTERN.md) - Details zur Datenspeicherung
- [Service Layer](code/services/SERVICE_LAYER.md) - Die vermittelnde Schicht zwischen Repository und Prozessen
- [Prozess-Implementierung](code/processes/PROCESS_IMPLEMENTATION.md) - Visualisierung & Berechnung
- [Client A Plugin](clients/clientA/code/CLIENT_A_PLUGIN.md) - JSON/CSV-basierte Implementierung
- [Client B Plugin](clients/clientB/code/CLIENT_B_PLUGIN.md) - CSV-mit-Semikolon-basierte Implementierung
- [Client C Plugin](clients/clientC/code/CLIENT_C_PLUGIN.md) - SQL-basierte Implementierung
- [Testing Strategie](code/tests/TESTING_STRATEGY.md) - Ansatz zum Testen der Komponenten
- [Setup Guide](SETUP.md) - Anleitung zur Installation und Konfiguration des Systems
