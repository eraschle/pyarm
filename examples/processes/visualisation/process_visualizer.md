# Visualisierungs-Tool für importierte Client-Daten

Dieses Tool konvertiert die importierten Client-Daten in ein einheitliches Format für die Visualisierung und ermöglicht so die konsistente Darstellung von Infrastrukturelementen unabhängig vom Client.

## Übersicht

Der Prozess-Visualizer nimmt die JSON-Ausgabedateien der Import-Tools (für ClientA, ClientB und ClientC) und wandelt sie in ein gemeinsames Visualisierungsformat um. Dieses Format ist kompatibel mit der Ausgabe des Visualisierungsprozesses im Hauptsystem und kann für 3D-Darstellungen und andere Visualisierungen verwendet werden.

## Verwendung

```bash
python process_visualizer.py --input_file <Pfad zur importierten JSON-Datei> --client_type <Client-Typ> --output_dir <Ausgabeverzeichnis>
```

Parameter:
- `--input_file`: Pfad zur importierten JSON-Datei (Ausgabe der Import-Tools)
- `--client_type`: Client-Typ (clientA, clientB, clientC oder clientC_fdk)
- `--output_dir`: Verzeichnis für die Ausgabe

Beispiel:
```bash
python process_visualizer.py --input_file ./test_output_clientA/clientA_data.json --client_type clientA --output_dir ./visualizer_output
```

## Unterstützte Client-Typen

1. **clientA**: Visualisiert die Ausgabe von `import_clientA.py` mit Projektzuordnungen
2. **clientB**: Visualisiert die Ausgabe von `import_clientB.py`
3. **clientC_fdk**: Visualisiert die Ausgabe von `fdk_import_script.py` mit IFC-Daten und Bauphasen

## Ausgabeformat

Die Ausgabe folgt diesem einheitlichen Format:

```json
{
  "scene": {
    "name": "Client X Infrastrukturszene",
    "elements": [
      {
        "type": "element_type",
        "id": "element_id",
        "name": "Element Name",
        "geometry": {
          "type": "geometry_type",
          "parameters": "..."
        },
        "material": {
          "name": "Material Name",
          "color": [r, g, b],
          "roughness": 0.x
        },
        "properties": {
          "key": "value"
        }
      }
    ]
  },
  "meta": { "..." }
}
```

## Element-Typen

Der Visualizer unterstützt folgende Elementtypen:

1. **foundation**: Fundamente (dargestellt als Boxen)
2. **mast**: Masten (dargestellt als Zylinder)
3. **track**: Gleise (dargestellt als Linien)
4. **curved_track**: Kurvengleise (dargestellt als Kurven mit Klothoidenparametern)
5. **joch**: Joche zwischen Masten (dargestellt als Linien)
6. **drainage_pipe**: Entwässerungsleitungen (dargestellt als Rohre)
7. **drainage_shaft**: Entwässerungsschächte (dargestellt als Zylinder)

## Zusätzliche Funktionen für ClientC FDK

Für ClientC FDK-Daten enthält die Ausgabe zusätzliche Informationen:

1. **IFC-Daten**: GlobalIDs, Elementtypen, Materialtypen und Kategorien für BIM-Integration
2. **Bauphasen**: Zeitliche Zuordnung von Elementen zu definierten Bauphasen
3. **Metadaten**: Projektinformationen und Versionsdaten

## Workflow für eine vollständige Datenverarbeitung

1. **Import**: Verarbeitung der Client-Daten mit dem jeweiligen Import-Tool
   ```bash
   python import_clientA.py --input_dir ./clients --output_dir ./import_output
   ```

2. **Visualisierung**: Konvertierung der importierten Daten in das Visualisierungsformat
   ```bash
   python process_visualizer.py --input_file ./import_output/clientA_data.json --client_type clientA --output_dir ./visualizer_output
   ```

3. **3D-Darstellung**: Verwendung der Visualisierungsdaten in einem 3D-Tool oder einem Web-Viewer
   (In einer vollständigen Implementierung würde dieser Schritt die Visualisierungsdaten in ein 3D-Format wie GLTF oder eine Web-basierte Darstellung konvertieren)

## Fehlerbehandlung

Der Visualizer enthält umfangreiche Fehlerbehandlung für unvollständige oder inkonsistente Daten:

- Fehlende oder ungültige Koordinaten werden durch Standardwerte ersetzt
- Ungültige numerische Werte werden erkannt und sicher behandelt
- Fehlende Elementattribute werden durch sinnvolle Standardwerte ergänzt

Diese robuste Implementierung ermöglicht die Verarbeitung realer Datensätze, die häufig Inkonsistenzen oder Fehler enthalten.