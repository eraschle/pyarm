# Komponenten-System für Infrastrukturelemente

Diese Dokumentation beschreibt das Komponenten-System, das für die Modellierung von Infrastrukturelementen verwendet wird. 
Das System ermöglicht eine flexible, erweiterbare und typ-sichere Modellierung von Elementen mit unterschiedlichen Eigenschaften und Beziehungen.

## Überblick

Das Komponenten-System basiert auf dem Prinzip der Komposition statt Vererbung. Anstatt spezifische Attribute in abgeleiteten Klassen zu definieren, 
werden gemeinsam genutzte Funktionalitäten in wiederverwendbare Komponenten ausgelagert. Diese Komponenten können dann dynamisch zu Elementen hinzugefügt
werden.

Vorteile dieses Ansatzes:
- **Flexibilität**: Elemente können zur Laufzeit mit verschiedenen Komponenten ausgestattet werden
- **Wartbarkeit**: Änderungen an Komponenten wirken sich automatisch auf alle Elemente aus, die diese verwenden
- **Erweiterbarkeit**: Neue Komponentenarten können hinzugefügt werden, ohne bestehenden Code zu ändern
- **Reduzierte Redundanz**: Gemeinsam genutzte Funktionalität wird an einem Ort definiert

## Komponententypen

Das System unterstützt verschiedene Arten von Komponenten:

1. **Location**: Repräsentiert die Position eines Elements im Raum
   - `CoordinateLocation`: Einfache Position mit X, Y, Z-Koordinaten
   - `LineLocation`: Linienförmige Position mit Start- und Endpunkten

2. **Dimension**: Repräsentiert die Abmessungen eines Elements
   - Unterstützt gemeinsame Eigenschaften wie Breite, Höhe, Tiefe
   - Spezifische Eigenschaften wie Durchmesser, Radius und Länge

3. **Material**: Repräsentiert die Materialeigenschaften eines Elements
   - Materialname
   - Physikalische Eigenschaften wie Elastizitätsmodul, Dichte, etc.

4. **Reference**: Repräsentiert eine Beziehung zu einem anderen Element
   - Referenztyp (z.B. "foundation", "mast")
   - UUID des referenzierten Elements
   - Bidirektionale oder unidirektionale Beziehung

5. **Custom**: Benutzerdefinierte Komponenten für spezielle Anwendungsfälle

## Verwendung des Komponenten-Systems

### Erstellen und Arbeiten mit Elementen

Das grundlegende Muster für die Arbeit mit dem Komponenten-System ist:

1. **Erstellen eines Elements**:
   ```python
   element = Foundation(name="Mein Fundament")
   ```

2. **Parameter setzen**:
   ```python
   # Parameter mit Einheit setzen
   element.set_param(ProcessEnum.FOUNDATION_WIDTH, 1.5, UnitEnum.METER)
   element.set_param(ProcessEnum.FOUNDATION_HEIGHT, 1.0, UnitEnum.METER)
   element.set_param(ProcessEnum.X_COORDINATE, 2600000.0, UnitEnum.METER)
   ```

3. **Komponenten zugreifen**:
   ```python
   # Auf Position zugreifen
   if element.position:
       x = element.position.x
       y = element.position.y
       
   # Auf Dimensionen zugreifen
   if element.dimensions:
       width = element.dimensions.width
       height = element.dimensions.height
   ```

4. **Komponenten direkt manipulieren**:
   ```python
   # Komponente direkt ändern
   if element.position:
       element.position.x = 2600010.0
       element.position.y = 1200020.0
   ```

5. **Komponenten hinzufügen**:
   ```python
   # Neues Material hinzufügen
   material = MaterialProperties(
       material_name="Beton",
       name="material",
       component_type=ComponentType.MATERIAL,
       density=2.4,
       youngs_modulus=30.0
   )
   element.add_component(material)
   ```

6. **Referenzen verwalten**:
   ```python
   # Referenz zu einem anderen Element hinzufügen
   element.add_reference("mast", mast_uuid)
   
   # Referenzen abrufen
   mast_refs = element.get_references("mast")
   ```

### Verwenden der Factory-Funktionen

Für komplexere Anwendungsfälle bietet die Factory-Klasse Methoden zum Erstellen von Elementen:

1. **Element aus Dictionary erstellen**:
   ```python
   element_data = {
       "name": "Mein Fundament",
       "element_type": "foundation",
       "parameters": [
           {
               "name": "Breite",
               "value": 1.5,
               "process": "foundation_width",
               "datatype": "float",
               "unit": "m"
           },
           # weitere Parameter...
       ]
   }
   element = create_element(element_data)
   ```

2. **Element mit Komponenten erstellen**:
   ```python
   # Position-Komponente erstellen
   position = CoordinateLocation(
       x=2600000.0,
       y=1200000.0,
       z=456.78,
       name="main_location"
   )
   
   # Dimensions-Komponente erstellen
   dimension = Dimension(
       width=1.5,
       height=1.0,
       depth=2.0,
       name="foundation_dimension"
   )
   
   # Element mit Komponenten erstellen
   element = create_component_based_element(
       name="Mein Fundament", 
       element_type=ElementType.FOUNDATION,
       position=position,
       dimension=dimension
   )
   ```

## Erweitern des Systems

Das Komponenten-System ist erweiterbar durch:

1. **Hinzufügen neuer Komponententypen**:
   - Neue Klasse definieren, die von `Component` erbt
   - Komponententyp definieren (bestehenden verwenden oder neuen erstellen)
   - Spezialisierte Eigenschaften und Methoden implementieren

2. **Erweitern der Factory-Methoden**:
   - Factory-Methoden können angepasst werden, um neue Komponententypen zu unterstützen
   - Neue `create_*_component` Methoden für spezialisierte Komponenten

3. **Anpassen der Element-Klassen**:
   - Neue Methoden hinzufügen, die mit Komponenten arbeiten
   - Property-Wrapper für häufig verwendete Komponenten-Eigenschaften

## Bewährte Praktiken

1. **Parameter vs. Komponenten**:
   - Parameter verwenden für einfache Werte und Meta-Informationen
   - Komponenten verwenden für zusammengehörige Eigenschaften und Verhalten

2. **Rückwärtskompatibilität**:
   - Attribute-Getter als Property für wichtige Komponenten-Eigenschaften bereitstellen
   - Parameter aktualisieren, wenn Komponenten geändert werden

3. **Typsicherheit**:
   - `Optional`-Typen für Komponenten-Eigenschaften verwenden
   - Null-Checks durchführen, bevor auf Komponenten-Eigenschaften zugegriffen wird

4. **Fehlerbehandlung**:
   - Fehlende Komponenten behandeln
   - Defaults für fehlende Werte bereitstellen

## Migrationshinweise

Beim Migrieren von einer attribut-basierten zu einer komponenten-basierten Architektur:

1. Identifizieren Sie Gruppen von zusammengehörigen Attributen, die zu Komponenten werden könnten
2. Erstellen Sie Komponenten-Klassen für diese Gruppen
3. Fügen Sie Property-Getter/-Setter hinzu, um die Rückwärtskompatibilität zu gewährleisten
4. Aktualisieren Sie Code, der direkt auf Attribute zugreift, um stattdessen Komponenten zu verwenden
5. Aktualisieren Sie die Factory-Methoden, um Komponenten zu erstellen und zu initialisieren

## Beispielimplementierungen

### Beispiel: Arbeiten mit Positions-Komponente

```python
# Element erstellen
foundation = Foundation(name="F1")

# Koordinaten über Parameter setzen
foundation.set_param(ProcessEnum.X_COORDINATE, 2600000.0, UnitEnum.METER)
foundation.set_param(ProcessEnum.Y_COORDINATE, 1200000.0, UnitEnum.METER)
foundation.set_param(ProcessEnum.Z_COORDINATE, 456.78, UnitEnum.METER)

# Über Komponente zugreifen
if foundation.position:
    print(f"Position: ({foundation.position.x}, {foundation.position.y}, {foundation.position.z})")

# Komponente direkt ändern
if foundation.position:
    foundation.position.x += 10.0  # Verschieben um 10 Meter nach Osten
```

### Beispiel: Arbeiten mit Referenzen

```python
# Fundament erstellen
foundation = Foundation(name="F1")

# Mast erstellen
mast = Mast(name="M1")

# Referenz hinzufügen
mast.add_reference("foundation", foundation.uuid)

# Alle Referenzen zum Fundament abrufen
foundation_refs = mast.get_references("foundation")
```

### Beispiel: Komponente erstellen und hinzufügen

```python
# Material-Komponente erstellen
material = MaterialProperties(
    material_name="Stahl",
    name="material",
    component_type=ComponentType.MATERIAL,
    density=7.85,
    youngs_modulus=210.0
)

# Zu Element hinzufügen
element.add_component(material)

# Auf Material zugreifen
if element.material:
    print(f"Material: {element.material.material_name}")
    print(f"Dichte: {element.material.density} g/cm³")
```