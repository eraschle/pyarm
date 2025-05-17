# Client B Plugin

Dieses Verzeichnis enthält die spezifischen Implementierungen für die Verarbeitung von Daten des Clients B
im Rahmen des Infrastruktur-Datenverarbeitungssystems.

## Unterstützte Datenformate

Client B stellt seine Daten in folgenden Formaten bereit:

1. **CSV-Dateien** (`.csv`) - Semikolon-getrennte Daten mit Komma als Dezimaltrennzeichen
2. **Excel-Dateien** (`.excel`) - Tatsächlich CSV-Dateien mit spezieller Endung

## Unterstützte Element-Typen

Die Konverter-Implementierung unterstützt folgende Elementtypen:

- **Fundament** (foundation.csv) - Fundamente für Masten
- **Mast** (mast.csv) - Masten mit Referenzen zu Fundamenten
- **Entwässerung** (drainage.excel) - Rohre und Schächte für Entwässerungssysteme

## Implementierung

### Reader

Es wurden zwei Reader-Klassen implementiert:

1. **ClientBCsvReader**
   - Liest CSV-Dateien mit Semikolon als Trennzeichen
   - Konvertiert Dezimalzahlen vom deutschen Format (Komma) ins englische Format (Punkt)
   - Bestimmt den Elementtyp anhand des Dateinamens

2. **ClientBExcelReader**
   - Funktional identisch mit dem CSV-Reader
   - Unterstützt Dateien mit der Endung `.excel`

### Konverter

Die **ClientBConverter**-Klasse konvertiert die gelesenen Daten in das kanonische Datenmodell:

- Zuordnung der Client-spezifischen Feldnamen zu ProcessEnum-Werten
- Spezifische Konverter für jeden Elementtyp
- Einheiten-Konvertierung (z.B. mm zu m für Durchmesser)
- Automatische Typumwandlung
- Generischer Fallback-Konverter für unbekannte Typen

## Besonderheiten von Client B Daten

- **Semikolon-getrennte Werte**: Im Gegensatz zu Standard-CSV mit Komma
- **Deutsches Zahlenformat**: Dezimalzahlen werden mit Komma statt Punkt geschrieben
- **Spezielle Dateiendungen**: `.excel` für Excel-Dateien, obwohl es sich um CSV-Dateien handelt
- **Differenzierung bei Drainage**: Unterscheidung zwischen "Pipe" und "Shaft" durch das `typ`-Feld

## Beispiele

### Beispiel für Foundation-Daten:

```csv
id;bezeichnung;x_wert;y_wert;z_wert;fundament_typ;breite_m;tiefe_m;hoehe_m;material
F001;Fundament 1;2600000.0;1200000.0;456.78;Typ A;1,5;2,0;1,0;Beton
```

### Beispiel für Mast-Daten:

```csv
id;bezeichnung;x_wert;y_wert;z_wert;mast_typ;hoehe_m;azimut_grad;material;profil_typ;fundament_id
M001;Mast 1;2600000.0;1200000.0;456.78;DP20;8,5;45,0;Stahl;HEB;F001
```

### Beispiel für Drainage-Daten:

```csv
id;typ;bezeichnung;x_wert;y_wert;z_wert;x_wert_ende;y_wert_ende;z_wert_ende;durchmesser_mm;material;gefaelle_promille
D001;Pipe;Entwässerungsleitung 1;2600015.0;1200025.0;456.28;2600115.0;1200045.0;455.78;300;PVC;10
D002;Shaft;Entwässerungsschacht 1;2600015.0;1200025.0;456.28;;;;800;Beton;
```