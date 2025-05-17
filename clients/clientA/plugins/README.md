# Client A Plugin für PyArm

Dieses Plugin ermöglicht die Konvertierung von Client A-spezifischen Daten in das kanonische Datenmodell des PyArm-Systems.

## Übersicht

Das Plugin unterstützt:

- Lesen und Konvertieren von JSON- und CSV-Daten
- Konvertierung verschiedener Infrastrukturelemente (Fundamente, Masten, Joche, Gleise, etc.)
- Projektversionsspezifische Konvertierer für unterschiedliche Datenstrukturen
- Bidirektionale Referenzen zwischen Elementen

## Unterstützte Elementtypen

- `foundation` - Fundamente
- `mast` - Masten
- `joch` - Joche (Verbindungen zwischen Masten)
- `track` - Gleise
- `curved_track` - Kurvengleise mit Clothoiden
- `drainage` - Entwässerungselemente (Leitungen und Schächte)

## Projektvarianten

Das Plugin unterstützt verschiedene Projektversionen mit unterschiedlichen Datenstrukturen:

- **Projekt 1**: Verwendet deutsche Bezeichner und einfache IDs
- **Projekt 2**: Verwendet englische Bezeichner und UUIDs

## Plugin-Integration

```python
from pyarm.core.app import Application

# Plugin laden
app = Application()
app.load_plugins()

# Plugin verwenden
data = {
    "element_type": "foundation",
    "project_id": "project1",
    "data": [...]
}

result = app.convert_element(data, "foundation")
```

## Parameter-Mapping

Das Plugin wandelt Client A-spezifische Parameter in das kanonische Modell um, basierend auf deren Bedeutung:

### Beispiel: Projekt 1 (Fundament)

```
"ID" -> ProcessEnum.UUID
"Bezeichnung" -> ProcessEnum.NAME
"E" -> ProcessEnum.X_COORDINATE
"N" -> ProcessEnum.Y_COORDINATE
"Z" -> ProcessEnum.Z_COORDINATE
"Breite" -> ProcessEnum.WIDTH
"Tiefe" -> ProcessEnum.DEPTH
"Höhe" -> ProcessEnum.HEIGHT
"Material" -> ProcessEnum.IFC_MATERIAL
"MastID" -> ProcessEnum.FOUNDATION_TO_MAST_UUID
```

### Beispiel: Projekt 2 (Fundament)

```
"UUID" -> ProcessEnum.UUID
"Name" -> ProcessEnum.NAME
"East" -> ProcessEnum.X_COORDINATE
"North" -> ProcessEnum.Y_COORDINATE
"Height" -> ProcessEnum.Z_COORDINATE
"Width" -> ProcessEnum.WIDTH
"Depth" -> ProcessEnum.DEPTH
"HeightFoundation" -> ProcessEnum.HEIGHT
"Material" -> ProcessEnum.IFC_MATERIAL
"MastReference" -> ProcessEnum.FOUNDATION_TO_MAST_UUID
```

## Komponenten

Die konvertierten Elemente erhalten automatisch verschiedene Komponenten:

- **Location**: Positionsinformationen (Punkt oder Linie)
- **Dimension**: Abmessungen des Elements
- **Reference**: Verweise auf andere Elemente (z.B. Mast zu Fundament)

## Fehlerbehandlung

Das Plugin protokolliert Fehler und Warnungen über das Logging-System. Fehlerhafte Elemente werden übersprungen, um die Konvertierung der übrigen Elemente nicht zu beeinträchtigen.