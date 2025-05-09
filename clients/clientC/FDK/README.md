# FDK-Daten Import für Client C

Dieses Verzeichnis enthält Daten im FDK-Format (Facility Digital Kernel) für Client C, ein spezialisiertes Format für die digitale Repräsentation von Bahnanlagen und -infrastruktur.

## Datenstruktur

Die FDK-Daten sind im JSON-Format strukturiert und enthalten folgende Hauptkomponenten:

- **Meta-Informationen**: Versionierung, Projektname, Erstellungsdatum
- **Bauphasen**: Definition verschiedener Bauphasen mit Zeiträumen
- **Gebäudedaten**: IFC-konforme Gebäudeinformationen
- **Gleisanlagen**: Gleise mit Parametern wie Länge, Spurweite und Bogenradius
- **Masten**: Masten für Fahrleitungen, Signale, etc.
- **Fundamente**: Fundamentdaten mit Referenzen zu Masten
- **Entwässerungssysteme**: Entwässerungsrohre und -schächte

Jedes Element enthält:
- ID-Parameter zur eindeutigen Identifikation
- Standortinformationen (km-Lage, Gleiszuordnung, etc.)
- Technische Parameter (Abmessungen, Material, etc.)
- IFC-Daten für BIM-Integration (GlobalId, Elementtyp, etc.)
- Bauphasen-Zuordnung für die zeitliche Planung

## Beispieldatei

Die Datei `anlagen_daten.json` enthält eine Beispielstruktur einer Bahnhofsanlage mit Gleisen, Masten, Fundamenten und Entwässerungssystemen.

## Import-Prozess

Zum Importieren der FDK-Daten nutzen Sie den spezialisierten FDK-Import-Prozess:

```bash
python main.py --client clientC --input_dir <Eingabeverzeichnis> --repository_dir <Repository-Verzeichnis> --output_dir <Ausgabeverzeichnis> --process fdk_import --fdk_file <Pfad zur FDK-JSON-Datei>
```

### Parameter

- `--client`: Muss `clientC` sein, da der FDK-Import Client-spezifisch ist
- `--input_dir`: Standardeingabeverzeichnis (wird für FDK-Import nicht genutzt)
- `--repository_dir`: Verzeichnis für das Repository
- `--output_dir`: Ausgabeverzeichnis für generierte Dateien
- `--process`: Muss `fdk_import` sein, um den FDK-Import-Prozess zu starten
- `--fdk_file`: Pfad zur FDK-JSON-Datei, die importiert werden soll

### Ausgaben

Der Import-Prozess generiert folgende Ausgaben:

1. **Kanonisches Datenmodell**: Konvertiert die FDK-Daten in das standardisierte Infrastruktur-Datenmodell
2. **Metadaten-Export**: Extrahiert Metadaten und Bauphasen-Informationen
3. **Visualisierungsdaten**: Generiert eine vereinfachte Visualisierung der importierten Daten

## IFC-Integration

Die FDK-Daten enthalten IFC-kompatible Informationen, die eine Integration mit BIM-Systemen ermöglichen. Für jedes Element werden folgende IFC-Daten gespeichert:

- **GlobalId**: Eindeutige IFC-ID
- **ElementTyp**: IFC-Elementtyp (z.B. IfcColumn, IfcRail)
- **MaterialTyp**: Material gemäß IFC-Klassifikation
- **Kategorie**: Kategorisierung im IFC-Schema

## Bauphasen-Integration

Die Integration von Bauphasen ermöglicht eine zeitliche Planung und Visualisierung:

- Jedes Element ist einer Bauphase zugeordnet
- Bauphasen haben definierte Start- und Endtermine
- Elemente können nach Bauphasen gefiltert werden