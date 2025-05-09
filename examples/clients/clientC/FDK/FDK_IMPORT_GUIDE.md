# FDK Import Tool - Anleitung

## Überblick

Das FDK (Facility Digital Kernel) Import Tool ermöglicht das Einlesen und Verarbeiten von FDK-Daten im JSON-Format. Es extrahiert Informationen über Infrastrukturelemente wie Gleise, Masten, Fundamente und Entwässerungssysteme, sowie Metadaten und Bauphasen-Informationen.

Das Tool bietet zwei Implementierungen:

1. **Vollständige Integration** (komplexer): Integration mit dem bestehenden Datenmodell und Repository-System
2. **Eigenständige Version** (einfacher): Eigenständiges Skript, das unabhängig von anderen Komponenten funktioniert

## Eigenständiges Import-Tool

Der einfachste Weg, FDK-Daten zu importieren, ist das eigenständige Skript `fdk_import_script.py`. Es hat weniger Abhängigkeiten und ist leichter zu verwenden.

### Verwendung

```bash
python fdk_import_script.py --fdk_file <Pfad zur FDK-JSON-Datei> --output_dir <Ausgabeverzeichnis>
```

Beispiel:
```bash
python fdk_import_script.py --fdk_file ./clients/clientC/FDK/anlagen_daten.json --output_dir ./output
```

### Erzeugte Ausgaben

Das Skript erzeugt zwei JSON-Dateien im angegebenen Ausgabeverzeichnis:

1. **fdk_visualization.json**: Enthält alle extrahierten Elemente, organisiert nach Typ, mit IFC-Daten und Bauphasen-Informationen
2. **fdk_metadata.json**: Enthält Metadaten über das Projekt und Bauphasen-Definitionen

## Vollständige Integration

Die vollständige Integration nutzt den Prozess `process3_fdk_import.py`, der die FDK-Daten in das kanonische Datenmodell konvertiert und im Repository speichert. Diese Variante unterstützt auch die Generierung von Visualisierungen.

### Verwendung

```bash
python main.py --client clientC --input_dir <Eingabeverzeichnis> --repository_dir <Repository-Verzeichnis> --output_dir <Ausgabeverzeichnis> --process fdk_import --fdk_file <Pfad zur FDK-JSON-Datei>
```

Beispiel:
```bash
python main.py --client clientC --input_dir ./clients --repository_dir ./repository --output_dir ./output --process fdk_import --fdk_file ./clients/clientC/FDK/anlagen_daten.json
```

**Hinweis**: Aufgrund von Abhängigkeitsproblemen empfehlen wir derzeit die Verwendung des eigenständigen Skripts. Die vollständige Integration wird in einer zukünftigen Version stabilisiert.

## Alternative: Separater Import

Für einen besseren Import ohne Abhängigkeitsprobleme wurde ein zweites eigenständiges Skript erstellt:

```bash
python fdk_import.py --fdk_file <Pfad zur FDK-JSON-Datei> --repository_dir <Repository-Verzeichnis> --output_dir <Ausgabeverzeichnis>
```

## FDK-Dateiformat

Die FDK-Daten werden im JSON-Format erwartet und sollten folgende Struktur haben:

```json
{
  "anlagenDaten": {
    "meta": { ... },
    "bauphasen": [ ... ],
    "ifcGebäude": { ... },
    "gleisAnlagen": [ ... ],
    "masten": [ ... ],
    "fundamente": [ ... ],
    "entwässerungssysteme": [ ... ]
  }
}
```

Jedes Element sollte mindestens eine eindeutige ID sowie typspezifische Attribute enthalten.

## Vorteile der FDK-Integration

Die Integration von FDK-Daten bietet folgende Vorteile:

1. **IFC-Integration**: Unterstützung für BIM-konforme Daten mit GlobalIDs und Typinformationen
2. **Bauphasen-Management**: Zeitliche Planung und Gruppierung von Elementen nach Bauphasen
3. **Konsistente Beziehungen**: Referenzen zwischen Elementen (z.B. Mast zu Fundament) werden erhalten
4. **Metadaten**: Projektnamen, Versionierung und andere Metadaten werden importiert

## Bekannte Einschränkungen

- Die vollständige Integration (mit dem Repository) hat derzeit Probleme mit Python-Abhängigkeiten
- Kreisförmige Referenzen zwischen Elementen können nicht importiert werden
- Sehr große Datenmengen können die Verarbeitungszeit erhöhen
- IFC-Geometriedaten werden nicht vollständig unterstützt