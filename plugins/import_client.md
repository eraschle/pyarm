# Client-Daten Import Tool

Diese Dokumentation beschreibt die eigenständigen Import-Tools für die verschiedenen Client-Daten im pym_data-System.

## Übersicht

Für jeden Client wurde ein eigenständiges Import-Tool entwickelt, das unabhängig vom Hauptsystem funktioniert und keine komplexen Abhängigkeiten hat:

1. **ClientA Import**: Verarbeitet JSON- und CSV-Dateien mit Projektzuordnung
2. **ClientB Import**: Verarbeitet CSV- und Excel-Dateien 
3. **ClientC Import**: Verarbeitet SQL-Dateien und das neue FDK-JSON-Format

## ClientA Import Tool

Das ClientA Import Tool verarbeitet Daten aus verschiedenen Projekten und unterstützt sowohl JSON- als auch CSV-Dateien.

### Verwendung

```bash
python import_clientA.py --input_dir <Eingabeverzeichnis> --output_dir <Ausgabeverzeichnis> [--project <Projektname>]
```

Parameter:
- `--input_dir`: Verzeichnis mit den Client-Daten (enthält den clientA-Ordner)
- `--output_dir`: Verzeichnis für die Ausgabe
- `--project`: Optionaler Parameter für das zu verarbeitende Projekt (project1, project2 oder all)

Beispiel:
```bash
python import_clientA.py --input_dir ./clients --output_dir ./output --project project1
```

## ClientB Import Tool

Das ClientB Import Tool verarbeitet CSV-Dateien sowie .excel-Dateien (die tatsächlich im CSV-Format mit Semikolon als Trennzeichen vorliegen).

### Verwendung

```bash
python import_clientB.py --input_dir <Eingabeverzeichnis> --output_dir <Ausgabeverzeichnis>
```

Parameter:
- `--input_dir`: Verzeichnis mit den Client-Daten (enthält den clientB-Ordner)
- `--output_dir`: Verzeichnis für die Ausgabe

Beispiel:
```bash
python import_clientB.py --input_dir ./clients --output_dir ./output
```

## ClientC Import Tool

Für ClientC wurden zwei Import-Tools entwickelt:

1. **Standard SQL Import**: Über das Hauptsystem mit `main.py`
2. **FDK JSON Import**: Eigenständiges Tool für das neue FDK-Format

### FDK-Format Import

Das FDK-Format enthält erweiterte Daten wie IFC-Informationen und Bauphasen-Definitionen.

```bash
python fdk_import_script.py --fdk_file <Pfad zur FDK-JSON-Datei> --output_dir <Ausgabeverzeichnis>
```

Parameter:
- `--fdk_file`: Pfad zur FDK-JSON-Datei
- `--output_dir`: Verzeichnis für die Ausgabe

Beispiel:
```bash
python fdk_import_script.py --fdk_file ./clients/clientC/FDK/anlagen_daten.json --output_dir ./output
```

## Ausgabeformat

Alle Import-Tools erzeugen JSON-Dateien mit einer einheitlichen Struktur:

- Elementinformationen, gruppiert nach Elementtyp
- Statistiken zur Anzahl der verarbeiteten Elemente
- Metadaten und Kontextinformationen

## Besonderheiten bei ClientC FDK-Daten

Das FDK-Format für ClientC enthält zusätzlich:

1. **IFC-Daten**: GlobalIDs, Elementtypen und Kategorien für BIM-Integration
2. **Bauphasen**: Zeitliche Planung von Infrastrukturelementen
3. **Verknüpfungen**: Referenzen zwischen Elementen (z.B. Mast zu Fundament)

## Gemeinsame Nutzung mit dem Hauptsystem

Die Import-Tools können auch als Vorstufe zur Nutzung mit dem Hauptsystem verwendet werden:

1. Import und Datenbereinigung mit den eigenständigen Tools
2. Manuelle Übernahme der bereinigten Daten in das Repository-Verzeichnis
3. Ausführung der Visualisierungs- und Berechnungsprozesse auf den importierten Daten

## Bekannte Einschränkungen

- Die Import-Tools sind nicht in das Typprüfungssystem des Hauptprogramms integriert
- Keine automatische Validierung der Daten gegen das kanonische Modell
- Kein direktes Umwandeln in InfrastructureElement-Objekte