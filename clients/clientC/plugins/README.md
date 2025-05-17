# Client C Plugin für PyArm

Dieses Plugin ermöglicht die Konvertierung von Client C-spezifischen Daten in das kanonische Datenmodell des PyArm-Systems. Es unterstützt zwei Datenformate:

1. **SQL-Format**: Daten in Form von SQL-INSERT-Anweisungen
2. **FDK-Format** (Facility Digital Kernel): Daten im JSON-Format für Bahnanlagen

## Übersicht

Das Plugin unterstützt:

- Lesen und Konvertieren von SQL-INSERT-Anweisungen
- Lesen und Konvertieren von FDK-JSON-Daten
- Konvertierung verschiedener Infrastrukturelemente (Fundamente, Masten, Joche, Gleise, etc.)
- Extraktion von IFC-Daten für BIM-Integration
- Extraktion von Bauphasen-Informationen für zeitliche Planung
- Bidirektionale Referenzen zwischen Elementen

## Unterstützte Elementtypen

- `foundation` - Fundamente
- `mast` - Masten
- `yoke` - Joche/Ausleger
- `track` - Gleise
- `curved_track` - Kurvengleise mit Clothoiden
- `drainage` - Entwässerungselemente (Leitungen und Schächte)
- `fdk` - FDK-Gesamtdaten mit allen Elementtypen und Metadaten

## SQL-Format Besonderheiten

- **Millimeter als Standardeinheit**: Dimensionen werden in Millimetern angegeben (im Gegensatz zu Metern bei anderen Clients)
- **NULL-Werte**: Einige Parameter können NULL sein (z.B. Koordinaten bei Schächten)
- **Englische Feldnamen**: Verwendung englischer Bezeichnungen mit Unterstrichen (z.B. `coord_x`, `diameter_mm`)
- **Koordinatensystem mit Indizes**: Unterscheidung zwischen Start- und Endpunkten durch Indizes (coord_x1, coord_x2)

## FDK-Format Besonderheiten

- **Hierarchische Struktur**: Daten in hierarchischer JSON-Struktur mit Metadaten
- **Bauphasen-Management**: Definition von Bauphasen mit Zeiträumen
- **IFC-Integration**: IFC-kompatible Daten für BIM-Integration
- **Standorte mit Kilometrierung**: Standortinformationen in Form von Kilometrierungen statt absoluten Koordinaten
- **Gleisreferenzierung**: Positionsangaben relativ zu Gleisnetzwerk

## Parameter-Mapping

Das Plugin wandelt clientspezifische Parameter in das kanonische Modell um:

### SQL-Format Beispiel (Foundation)

```
"id" -> ProcessEnum.UUID
"name" -> ProcessEnum.NAME
"coord_x" -> ProcessEnum.X_COORDINATE
"coord_y" -> ProcessEnum.Y_COORDINATE
"coord_z" -> ProcessEnum.Z_COORDINATE
"width_mm" -> ProcessEnum.WIDTH (mit Umrechnung von mm in m)
"depth_mm" -> ProcessEnum.DEPTH (mit Umrechnung von mm in m)
"height_mm" -> ProcessEnum.HEIGHT (mit Umrechnung von mm in m)
"type" -> ProcessEnum.FOUNDATION_TYPE
"material" -> ProcessEnum.IFC_MATERIAL
```

### FDK-Format Beispiel (Mast)

```
"id" -> ProcessEnum.UUID
"typ" -> ProcessEnum.MAST_TYPE
"höhe" -> ProcessEnum.HEIGHT
"material" -> ProcessEnum.IFC_MATERIAL
"standort.kilometerLage" -> ProcessEnum.KILOMETER_POSITION
"standort.gleisId" -> ProcessEnum.TRACK_REFERENCE
"standort.abstand" -> ProcessEnum.DISTANCE
"fundamentId" -> ProcessEnum.MAST_TO_FOUNDATION_UUID
"ifcDaten.globalId" -> ProcessEnum.IFC_GLOBAL_ID
"ifcDaten.elementTyp" -> ProcessEnum.IFC_TYPE
"ifcDaten.kategorie" -> ProcessEnum.IFC_CATEGORY
"bauphasenId" -> ProcessEnum.CONSTRUCTION_PHASE_ID
```

## Verwendung

### SQL-Format

```python
from pyarm.clients.clientC.plugins import ClientCPlugin

# Plugin initialisieren
plugin = ClientCPlugin()
plugin.initialize({})

# SQL-Daten konvertieren
data = {
    "element_type": "foundation",
    "project_id": "project1",
    "data": [foundation_data]
}

result = plugin.convert_element(data, "foundation")
```

### FDK-Format

```python
from pyarm.clients.clientC.plugins import ClientCPlugin

# Plugin initialisieren
plugin = ClientCPlugin()
plugin.initialize({})

# FDK-Datei konvertieren
data = {
    "fdk_file": "/home/elyo/workspace/elyo/pym/pyarm/clients/clientC/FDK/anlagen_daten.json"
}

result = plugin.convert_element(data, "fdk")
```

## Komponenten

Die konvertierten Elemente erhalten automatisch verschiedene Komponenten:

- **Location**: Positionsinformationen (Punkt oder Linie)
- **Dimension**: Abmessungen des Elements
- **Reference**: Verweise auf andere Elemente
- **IFC**: IFC-Daten für BIM-Integration
- **Construction Phase**: Bauphasen-Informationen

## Fehlerbehandlung

Das Plugin protokolliert Fehler und Warnungen über das Logging-System. Fehlerhafte Elemente werden übersprungen, um die Konvertierung der übrigen Elemente nicht zu beeinträchtigen.

Typische Fehlerquellen:
- Fehlende Pflichtparameter wie Koordinaten
- Ungültige Werte (nicht konvertierbar in Zahlen)
- Fehlende Referenzen zu anderen Elementen

## Autor

Entwickelt für das PyArm-System zur Integration von Client C-Daten in das kanonische Infrastrukturmodell.