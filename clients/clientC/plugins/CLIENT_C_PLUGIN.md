# Client C - Implementation

Diese Implementierung ermöglicht die Verarbeitung von Daten des Clients C im PYM-Datensystem. Client C stellt seine Daten in Form von SQL-INSERT-Anweisungen bereit, die von unserem System geparst und in das kanonische Datenmodell konvertiert werden.

## Datenformat

Client C liefert seine Daten in SQL-Dateien (`.sql`), die INSERT-Anweisungen für verschiedene Tabellen enthalten:

- `foundations` - Fundamente
- `masts` - Masten
- `yokes` - Joche/Ausleger
- `tracks` - Gleise
- `curved_tracks` - Kurvengleise
- `drainage` - Entwässerungselemente (Rohre und Schächte)

## Besonderheiten

- **SQL-Format**: Daten werden als SQL-INSERT-Anweisungen bereitgestellt
- **Millimeter als Standardeinheit**: Dimensionen werden in Millimetern angegeben (im Gegensatz zu Metern bei anderen Clients)
- **NULL-Werte**: Einige Parameter können NULL sein (z.B. Koordinaten bei Schächten)
- **Englische Feldnamen**: Verwendung englischer Bezeichnungen mit Unterstrichen (z.B. `coord_x`, `diameter_mm`)
- **Koordinatensystem mit Indizes**: Unterscheidung zwischen Start- und Endpunkten durch Indizes (coord_x1, coord_x2)

## Komponenten

### SQL Reader

Die `ClientCSqlReader`-Klasse implementiert das `IDataReader`-Protokoll für SQL-Dateien:

```python
class ClientCSqlReader:
    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".sql" and ("clientC" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Daten nach Elementtyp gruppieren
        data = {
            "foundation": self._extract_table_data(sql_content, "foundations"),
            "mast": self._extract_table_data(sql_content, "masts"),
            # weitere Elementtypen
        }

        return data
```

Der Reader verwendet reguläre Ausdrücke, um die INSERT-Anweisungen zu parsen und die Daten zu extrahieren. Er gruppiert die Daten nach Elementtyp und stellt zusätzliche Methoden bereit, um auf die strukturierten Daten zuzugreifen.

### Converter

Der `ClientCConverter` implementiert das `IDataConverter`-Protokoll und konvertiert die client-spezifischen Daten in das kanonische Modell:

```python
class ClientCConverter:
    def convert(self, data: Dict[str, Any]) -> List[InfrastructureElement]:
        element_type = data.get("element_type", "").lower()
        raw_data = data.get("data", [])
        
        converter_method = getattr(self, f"_convert_{element_type}", None)
        if converter_method:
            return converter_method(raw_data)
        
        # Fallback auf generischen Konverter
        return self._convert_generic(raw_data, element_type)
```

Eine wichtige Besonderheit ist die Konvertierung von Millimetern in Meter für Dimensionsparameter:

```python
# Umrechnung von Millimetern in Meter
Parameter(name="width_mm", value=float(item.get("width_mm", 0))/1000, 
          process=ProcessEnum.FOUNDATION_WIDTH, unit=UnitEnum.METER)
```

## Unterstützte Elementtypen

Der Converter unterstützt folgende Elementtypen:

1. **Foundation** (Fundament)
   - Grundlegende Attribute: id, name, coord_x, coord_y, coord_z
   - Spezifische Attribute: type, width_mm, depth_mm, height_mm, material

2. **Mast** (Mast)
   - Grundlegende Attribute: id, name, coord_x, coord_y, coord_z
   - Spezifische Attribute: type, height_mm, azimuth, material, profile
   - Referenz: foundation_id

3. **Joch** (Joch/Ausleger)
   - Grundlegende Attribute: id, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2
   - Spezifische Attribute: type, span_mm, material
   - Referenzen: mast_id1, mast_id2

4. **Track** (Gleis)
   - Grundlegende Attribute: id, name, coord_x1, coord_y1, coord_z1, coord_x2, coord_y2, coord_z2
   - Spezifische Attribute: gauge_mm, type, cant_mm

5. **CurvedTrack** (Kurvengleis)
   - Grundlegende Attribute wie Track
   - Zusätzliche Attribute: clothoid_param, start_radius_m, end_radius_m

6. **Drainage** (Entwässerung)
   - Unterstützt zwei Untertypen: pipe (Leitung) und shaft (Schacht)
   - Grundlegende Attribute: id, name, type, coord_x1, coord_y1, coord_z1
   - Spezifische Attribute für pipe: coord_x2, coord_y2, coord_z2, diameter_mm, slope_permille
   - Spezifische Attribute für shaft: diameter_mm

## SQL-Parser

Eine Besonderheit dieser Implementierung ist der SQL-Parser, der die INSERT-Anweisungen analysiert und strukturierte Daten extrahiert:

```python
def _extract_table_data(self, sql_content: str, table_name: str) -> List[Dict[str, Any]]:
    # Regex, um INSERT-Statements für die angegebene Tabelle zu finden
    pattern = rf"INSERT\s+INTO\s+{table_name}\s*\(([^)]+)\)\s*VALUES\s*((?:\([^;]+\),?)+);"
    match = re.search(pattern, sql_content, re.IGNORECASE | re.DOTALL)
    
    if not match:
        return []
        
    # Spalten extrahieren
    columns_str = match.group(1)
    columns = [col.strip() for col in columns_str.split(',')]
    
    # Werte extrahieren
    values_str = match.group(2)
    value_pattern = r'\(([^)]+)\)'
    value_matches = re.finditer(value_pattern, values_str)
    
    result = []
    for value_match in value_matches:
        values_row = value_match.group(1)
        values = self._parse_values(values_row)
        
        if len(columns) == len(values):
            row_data = dict(zip(columns, values))
            result.append(row_data)
    
    return result
```

Der Parser muss verschiedene Werttypen korrekt interpretieren:
- Zeichenketten in Anführungszeichen
- Numerische Werte
- NULL-Werte

## Umgang mit NULL-Werten

Ein wichtiger Aspekt der ClientC-Implementierung ist der korrekte Umgang mit NULL-Werten in den SQL-Daten:

```python
# Startradius behandeln (kann NULL sein)
start_radius = item.get("start_radius_m")
if start_radius is None:
    start_radius = float('inf')
```

Bei Elementen wie den Entwässerungsschächten werden fehlende Koordinaten für Endpunkte nicht in die Parameter aufgenommen.

## Integration ins Gesamtsystem

Die Reader und Converter für Client C werden über die Plugin-Architektur in das System integriert. Der SQL-basierte Ansatz demonstriert die Flexibilität des Systems für unterschiedliche Datenquellen.

## Beispiel-Workflow

1. Der `ClientCSqlReader` liest eine SQL-Datei und extrahiert die Daten für verschiedene Tabellen
2. Der Client-Code ruft für jeden Elementtyp den `get_data_for_type`-Methode auf
3. Der `ClientCConverter` konvertiert die Daten in das kanonische Modell
4. Das Repository speichert die konvertierten Elemente
5. Services und Prozesse können die Daten unabhängig vom Original-Format verarbeiten

## Beispielcode für die Verwendung

```python
# Reader und Converter erstellen
sql_reader = ClientCSqlReader()
converter = ClientCConverter()

# SQL-Datei einlesen
file_path = "/home/elyo/workspace/elyo/pym/pyarm/clients/clientC/projects/infrastructure.sql"
if sql_reader.can_handle(file_path):
    all_data = sql_reader.read_data(file_path)
    
    # Für jeden Elementtyp die Daten konvertieren
    for element_type in sql_reader.get_element_types(all_data):
        type_data = sql_reader.get_data_for_type(all_data, element_type)
        
        if converter.can_convert(type_data):
            elements = converter.convert(type_data)
            
            # Elemente im Repository speichern
            repository.save_all(elements)
```