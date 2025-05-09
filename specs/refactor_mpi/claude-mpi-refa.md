# Refactoring-Plan: Multi-Client-Datenintegration für Revit-Plugin

**Datum:** 2023-10-27
**Version:** 1.0

## 1. Einleitung und Ziele

Dieses Dokument beschreibt das geplante Refactoring der bestehenden `app`-Anwendung. Ziel ist es, die Anwendung so zu erweitern, dass sie Daten aus unterschiedlichen Quellen und Formaten verschiedener Kunden verarbeiten kann. Die aufbereiteten Daten sollen weiterhin vom bestehenden Revit-`plugin` genutzt werden, um 3D-Elemente (punkt- oder linienbasiert) mit minimalen Änderungen am Plugin-Code selbst zu erstellen.

Die aktuelle Implementierung ist stark auf die spezifischen Datenformate und -strukturen eines einzelnen Kunden zugeschnitten (erkennbar an Begriffen wie "DFA", "Punktehimmel" und spezifischen Spaltennamen in den Prozessoren). Das Refactoring soll eine modulare und konfigurierbare Architektur schaffen, die es ermöglicht, neue Kunden und deren Datenformate effizient zu integrieren.

**Hauptziele:**

1.  **Entkopplung:** Trennung der Dateneingangslogik von der Kernverarbeitungslogik.
2.  **Konfigurierbarkeit:** Ermöglichen der Definition von Datenquellen, Formaten und Feldzuordnungen pro Kunde über Konfigurationsdateien.
3.  **Erweiterbarkeit:** Einfaches Hinzufügen neuer Reader für unterschiedliche Dateiformate und neuer Mapper für kundenspezifische Datenstrukturen.
4.  **Stabilität des Plugins:** Die Schnittstelle (JSON-Struktur) zum Revit-Plugin soll unverändert bleiben.
5.  **Wartbarkeit:** Verbesserte Code-Struktur und Lesbarkeit.

## 2. Analyse der aktuellen Architektur und Datenflüsse

### 2.1 Aktuelle Architektur (`app`)

*   **`projectfiles/input.py` (ProjectFolderReader):** Liest hartkodierte Dateipfade und -typen (z.B. `../data/dfa`, `Punktehimmel.xlsx`, `DGM.xml`).
*   **`dfa/reports.py` (Reader):** Verarbeitet Excel-Dateien ("DFA-Berichte"), filtert basierend auf einer GeoJSON-Projektgrenze und normalisiert Namen. Enthält kundenspezifische Logik zur Namensfindung und Spaltenannahmen (E, N, E2, N2, DFA-ID).
*   **`dtm.py` (DTMReader):** Spezialisiert auf LandXML-Format.
*   **`pointcloud.py` (PointCloud):** Verarbeitet Daten (wahrscheinlich aus Excel) mit spezifischen Spaltenannahmen (z, Code, E, N).
*   **`azimut.py` (DXFBase):** Verarbeitet DXF-Dateien; Layer-Namen werden oft direkt in Prozessoren verwendet.
*   **`dfa/base.py` (ProcessorBase):** Basisklasse für Prozessoren. Attribute wie `DFA_NAME_COL`, `TYPE_COL`, `PC_CODE` sind kundenspezifisch. Verwendet `dfa_dict` mit der Annahme fester Schlüsselnamen.
*   **`dfa/processors.py` (Spezifische Prozessoren):** Erben von `ProcessorBase`. Enthalten hartkodierte Spaltennamen des aktuellen Kunden (z.B. `"Breite (mm)"`, `"Funktion Hydraulisch"`). `PC_CODE`, `DXF_LAYERS` sind ebenfalls spezifisch.
*   **`mapping.py` (DfaToRfaMapping):** Mappt "DFA Name" und "DFA Category" auf RFA-Dateien.
*   **`main.py`:** Orchestriert den aktuellen Single-Client-Workflow.
*   **`projectfiles/ouput.py` (ProcessedDataWriter):** Schreibt die verarbeiteten Daten in eine JSON-Datei.

### 2.2 Schnittstelle zum Revit-Plugin (`plugin`)

Das Plugin erwartet eine JSON-Datei, die von `app/projectfiles/ouput.py` generiert wird. Die Schlüsselstruktur dieser JSON-Datei ist entscheidend.

**Datenmodell für das Plugin (basierend auf `plugin/src/position_object.py`):**

Eine Liste von Objekten pro Kategorie. Jedes Objekt (`object_data`) hat folgende Struktur:

*   **MUSS-Felder:**
    *   `family_name`: `string` (Name der Revit-Familie)
    *   `type_name`: `string` (Name des Revit-Familientyps, z.B. "0.200" oder "ANDERE")
    *   `point_1`: `dict`
        *   `easting`: `float`
        *   `northing`: `float`
        *   `altitude`: `float`
        *   `data_source`: `string` (Herkunft der Höheninformation, z.B. "_build_height_dtm")
    *   `project_parameters`: `dict`
        *   `"Identity Data"`: `list` von `dict`
            *   `name`: `"UUID"`
            *   `value_type`: `"str"`
            *   `value`: `string` (UUID-Wert)
            *   `is_internal`: `False`
        *   `"Geolocation"`: `list` von `dict` (Parameter für `easting`, `northing`, `altitude`, `altitude_src` von `point_1` und optional `point_2`)

*   **OPTIONALE Felder:**
    *   `point_2`: `dict` (gleiche Struktur wie `point_1`) - für linienbasierte Elemente.
    *   `azimuth`: `float` (Rotation in Grad) - für die Ausrichtung von Elementen.
    *   `type_parameters`: `dict` (z.B. `{"Dimensions": [{"name": "Diameter", "value_type": "float", "value": 0.2, "is_internal": True}]}`) - für Typ-Parameter der Revit-Familie.
    *   `custom_parameters`: `dict` (z.B. `{"Dimensions": [{"name": "Height", ...}]}`) - für Instanz-Parameter.

**Diese JSON-Struktur ist das Zielformat, das die refaktorierte `app` für jeden Kunden generieren muss.**


FÜGE DEN INHALT AUS DEINER ANTWORT HINZU ODER ERGÄNZE IN GEMÄSS DEINEM CONTEXT INFORMATIONEN


### 2.3 Diagramm: Aktueller Datenfluss (vereinfacht)


FÜGE DEN INHALT AUS DEINER ANTWORT HINZU ODER ERGÄNZE IN GEMÄSS DEINEM CONTEXT INFORMATIONEN


## 3. Vorgeschlagene Architektur und Datenfluss

Die neue Architektur führt eine Konfigurationsebene und Abstraktionen für das Lesen und Transformieren von Daten ein.

### 3.1 Komponenten der neuen Architektur

1.  **Client-Konfiguration (`client_config.json/yaml`):**
    *   Pro Kunde eine Konfigurationsdatei.
    *   Definiert:
        *   Zu lesende Dateitypen und deren Pfade/Muster.
        *   Mappings von kundenspezifischen Spalten-/Feldnamen zu internen, kanonischen Namen (z.B. `client_field_A` -> `canonical_width`).
        *   Regeln zur Ableitung von `family_name` und `type_name`.
        *   Spezifische Werte wie `PC_CODE`, `DXF_LAYERS` (wenn nicht direkt aus Daten ableitbar).
        *   Informationen, welcher Reader und welcher Satz von Mapping-Regeln/Prozessoren zu verwenden ist.

2.  **Abstrakte Datenleser (`AbstractReader`):**
    *   Basisklasse `AbstractReader`.
    *   Spezifische Implementierungen (`ExcelReader`, `XmlReader`, `DxfReader`, `GeoJsonReader`).
    *   Nutzen die Client-Konfiguration, um Rohdaten zu laden und in ein generisches Zwischenformat zu überführen (z.B. eine Liste von Dictionaries, wobei die Schlüssel die originalen Spaltennamen des Kunden sind).

3.  **Daten-Mapper/Transformations-Service:**
    *   Nimmt die Rohdaten von den Readern und die Client-Konfiguration entgegen.
    *   Wendet Mapping-Regeln an, um kundenspezifische Feldnamen auf ein **kanonisches internes Datenmodell** abzubilden. Dieses Modell enthält alle potenziell benötigten Felder in einem neutralen Format (z.B. `internal_diameter_mm`, `source_object_type`, `raw_coordinates_list`).
    *   Leitet die transformierten Daten an die (jetzt generischeren) Prozessoren weiter.

4.  **Generische Prozessoren (angepasste `ProcessorBase` und Kinder):**
    *   Die Prozessoren greifen nicht mehr direkt auf `dfa_dict["Kundenspalte"]` zu, sondern auf Felder des kanonischen internen Datenmodells (z.B. `self.get_canonical_field("diameter_mm")`).
    *   Die Logik zur Berechnung von Werten (z.B. `build_type_name`) bleibt, greift aber auf die kanonischen Felder zu.
    *   Spezifische Werte wie `PC_CODE` werden über die Konfiguration geladen oder sind Teil des kanonischen Modells.

5.  **Orchestrierung (`main.py`):**
    *   Lädt die Client-Konfiguration.
    *   Instanziiert die passenden Reader und den Transformations-Service.
    *   Der `ProcessedDataWriter` bleibt bestehen und schreibt das finale JSON im für das Plugin erwarteten Format.

### 3.2 Diagramm: Vorgeschlagener Datenfluss

FÜGE DEN INHALT AUS DEINER ANTWORT HINZU ODER ERGÄNZE IN GEMÄSS DEINEM CONTEXT INFORMATIONEN

### 3.3 Prozess-Diagramm (vereinfacht)

FÜGE DEN INHALT AUS DEINER ANTWORT HINZU ODER ERGÄNZE IN GEMÄSS DEINEM CONTEXT INFORMATIONEN


## 4. Arbeitspakete (APs)

Die Aufteilung berücksichtigt einen Vollzeit-Entwickler (VZ) und 1-2 Teilzeit-Entwickler (TZ) mit Programmierkenntnissen.

---

### AP 1: Konfigurationssystem und Kanonisches Datenmodell

*   **Ausgangslage:** Hartkodierte Pfade, Dateinamen und Feldnamen in der gesamten Anwendung. Kein zentrales Konfigurationsmanagement.
*   **Beschreibung der Arbeit:**
    1.  Definition der Struktur für Client-Konfigurationsdateien (z.B. JSON oder YAML). Diese soll Dateipfade, Typen, Feldmappings (Kundenfeld -> Kanonisches Feld) und prozessorspezifische Parameter (z.B. `PC_CODE_LIST`) enthalten.
    2.  Entwurf eines **kanonischen internen Datenmodells**. Dieses Modell repräsentiert ein generisches Objekt mit allen Attributen, die potenziell von verschiedenen Kunden geliefert und von den Prozessoren oder dem Plugin benötigt werden (z.B. `object_id`, `primary_geometry_points`, `secondary_geometry_points`, `attributes: {width_mm: 100, material: 'steel'}` etc.).
    3.  Implementierung einer Ladefunktion für diese Konfigurationsdateien.
    4.  Anpassung von `app/main.py` zur initialen Verwendung des Konfigurationssystems (z.B. Auswahl der Client-Konfiguration per Kommandozeilenparameter).
*   **Soll-Zustand (MUSS):**
    *   Eine klare Struktur für Client-Konfigurationen ist definiert und dokumentiert.
    *   Ein kanonisches internes Datenmodell ist definiert und dokumentiert.
    *   Die Anwendung kann eine Client-spezifische Konfigurationsdatei laden und deren Inhalte programmatisch nutzen.
    *   Die bestehenden hartkodierten Pfade in `ProjectFolderReader` werden durch Werte aus der Konfiguration ersetzt (für den ersten Kunden).
*   **Optionale Tasks:**
    *   Schema-Validierung für Konfigurationsdateien.
*   **Aufwandsschätzung:** 5-7 Personentage (VZ: 3-4 Tage, TZ: 2-3 Tage Unterstützung bei Definition/Tests)
*   **Vorteile:** Grundlage für alle weiteren Schritte, zentrale Steuerung.
*   **Nachteile:** Initiale Komplexität bei der Definition des richtigen Abstraktionslevels.

---

### AP 2: Implementierung Abstrakter Datenleser

*   **Ausgangslage:** `ProjectFolderReader` ist spezifisch. Andere Leseoperationen sind in spezifischen Klassen (DTMReader) oder ad-hoc implementiert.
*   **Beschreibung der Arbeit:**
    1.  Definition einer Basisklasse `AbstractReader` mit einer Methode wie `read_data(config) -> List[Dict]`.
    2.  Erstellung spezifischer Reader-Implementierungen (z.B. `ExcelReader`, `XmlReader`, `GeoJsonReader`, `DxfWrapper`) die von `AbstractReader` erben.
    3.  Diese Reader nutzen die Client-Konfiguration, um zu wissen, *welche* Dateien wie zu lesen sind (z.B. Excel-Sheet-Name, relevante XML-Tags, GeoJSON-Feature-Pfade).
    4.  Die Reader geben eine Liste von Dictionaries zurück, wobei die Schlüssel die *originalen* Feldnamen des Kunden sind.
    5.  Integration der Reader in `app/main.py`, sodass basierend auf der Konfiguration die korrekten Reader instanziiert werden.
    6.  Refactoring von `app/projectfiles/input.py`, `app/dtm.py` (DTMReader), `app/pointcloud.py` (Initialisierung), `app/dfa/reports.py` (Excel-Teil) um die neue Reader-Struktur zu nutzen.
*   **Soll-Zustand (MUSS):**
    *   `AbstractReader` und mindestens Implementierungen für Excel und XML sind vorhanden.
    *   Die Anwendung kann Rohdaten aus verschiedenen, konfigurierten Quellen laden.
    *   Die bisherige Funktionalität für den bestehenden Kunden ist über die neuen Reader abgedeckt.
*   **Optionale Tasks:**
    *   Reader für weitere Formate (CSV, spezifische Textformate).
    *   Caching-Mechanismen für gelesene Daten.
*   **Aufwandsschätzung:** 8-12 Personentage (VZ: 5-7 Tage, TZ: 3-5 Tage für spezifische Reader)
*   **Vorteile:** Saubere Trennung der Datenbeschaffung, einfachere Erweiterung für neue Formate.
*   **Nachteile:** Aufwand, alle bestehenden Ladelogiken zu migrieren.

---

### AP 3: Daten-Mapper und Transformations-Service

*   **Ausgangslage:** Prozessoren erwarten `dfa_dict` mit hartkodierten Schlüsseln.
*   **Beschreibung der Arbeit:**
    1.  Entwicklung eines "DataMapper-Service". Dieser Service nimmt die Rohdaten (Liste von Dictionaries mit Kunden-Schlüsseln) von den Readern und die Feldmapping-Definitionen aus der Client-Konfiguration entgegen.
    2.  Der Mapper transformiert die Rohdaten in eine Liste von Objekten des in AP 1 definierten **kanonischen internen Datenmodells**. (z.B. `kunden_dict["Breite (mm)"]` wird zu `kanonisches_objekt.attributes["width_mm"]`).
    3.  Dieser Service behandelt auch einfache Datentypkonvertierungen, falls in der Konfiguration definiert.
*   **Soll-Zustand (MUSS):**
    *   Ein DataMapper-Service ist implementiert.
    *   Die Anwendung kann Rohdaten basierend auf der Client-Konfiguration in das kanonische interne Datenmodell überführen.
    *   Die Logik aus `app/dfa/reports.py` zur Namensfindung und Filterung wird hier (oder im Reader) konfigurierbar integriert.
*   **Optionale Tasks:**
    *   Komplexere Transformationsregeln (z.B. Zusammenführen von Feldern, bedingte Mappings).
    *   Plugin-System für benutzerdefinierte Mapping-Funktionen.
*   **Aufwandsschätzung:** 7-10 Personentage (VZ: 4-6 Tage, TZ: 3-4 Tage für Mapping-Logik)
*   **Vorteile:** Entscheidender Schritt zur Entkopplung der Prozessoren von Kundendatenstrukturen.
*   **Nachteile:** Mapping-Logik kann komplex werden.

---

### AP 4: Refactoring der Prozessoren (`ProcessorBase` und abgeleitete Klassen)

*   **Ausgangslage:** Prozessoren verwenden hartkodierte Feldnamen (z.B. `self.dfa_dict["Breite (mm)"]`) und spezifische Konstanten (`PC_CODE`, `DXF_LAYERS`).
*   **Beschreibung der Arbeit:**
    1.  Anpassung der `ProcessorBase` und aller abgeleiteten Prozessoren (`AbwasserHaltung`, `AlleKabelschaechte` etc.).
    2.  Die Prozessoren erhalten nun Objekte des kanonischen internen Datenmodells als Eingabe (anstelle des `dfa_dict`).
    3.  Zugriffe auf Daten erfolgen über Getter auf dem kanonischen Modell (z.B. `kanonisches_objekt.get_attribute("width_mm")` oder `kanonisches_objekt.primary_geometry_points[0].easting`).
    4.  Konstanten wie `PC_CODE`, `DXF_LAYERS` werden aus der Client-Konfiguration geladen und dem Prozessor übergeben oder sind Teil des kanonischen Modells.
    5.  Die Logik zur Erstellung von `family_name` und `type_name` wird flexibilisiert, um Regeln aus der Konfiguration zu nutzen (z.B. Mapping von `source_object_type` auf `family_name`).
    6.  Die Methode `process(self, kanonisches_objekt)` gibt weiterhin die für das Plugin benötigte JSON-Struktur zurück.
    7.  Die `model_mapping` Logik aus `app/mapping.py` wird Teil der Client-Konfiguration oder ein flexiblerer Mapping-Mechanismus.
*   **Soll-Zustand (MUSS):**
    *   Alle Prozessoren sind refaktorisiert und arbeiten mit dem kanonischen internen Datenmodell.
    *   Prozessoren sind frei von kundenspezifischen Feldnamen und Konstanten im Code.
    *   Die Funktionalität für den bestehenden Kunden ist vollständig über die refaktorisierten Prozessoren abgedeckt.
*   **Optionale Tasks:**
    *   Dynamische Auswahl von Prozessor-Logik-Teilen basierend auf Konfiguration (fortgeschritten).
*   **Aufwandsschätzung:** 10-15 Personentage (VZ: 6-9 Tage, TZ: 4-6 Tage für spezifische Prozessoren)
*   **Vorteile:** Prozessoren sind wiederverwendbar und kundenspezifische Logik ist in Konfigurationen ausgelagert.
*   **Nachteile:** Aufwendigstes AP, da viele Klassen betroffen sind.

---

### AP 5: Orchestrierung, Tests und Dokumentation

*   **Ausgangslage:** `app/main.py` ist auf den Single-Client-Workflow ausgerichtet. Tests und Dokumentation müssen aktualisiert werden.
*   **Beschreibung der Arbeit:**
    1.  Anpassung von `app/main.py` zur vollständigen Orchestrierung des neuen Workflows:
        *   Client-Konfiguration laden.
        *   Passende Reader instanziieren und Rohdaten laden.
        *   DataMapper-Service aufrufen.
        *   Passende Prozessoren aufrufen (ggf. eine Factory-Methode `create_processor` anpassen, um Konfigurationsdaten zu übergeben).
        *   `ProcessedDataWriter` mit den Ergebnissen füttern.
    2.  Anpassung bestehender Unit-Tests (`test_dfa_processors.py`, `test_projectfiles.py`) an die neue Struktur. Mocking der Konfiguration und des kanonischen Modells wird notwendig.
    3.  Erstellung neuer Tests für die Reader und den DataMapper-Service.
    4.  Aktualisierung der internen Entwicklerdokumentation.
    5.  Sicherstellung, dass die `ProcessedDataWriter` weiterhin das exakt gleiche JSON-Format für das Plugin erzeugt.
*   **Soll-Zustand (MUSS):**
    *   Der End-to-End-Prozess funktioniert für den ursprünglichen Kunden über die neue, konfigurierbare Architektur.
    *   Kritische Komponenten sind durch Unit-Tests abgedeckt.
    *   Die grundlegende Architektur und Nutzung sind dokumentiert.
*   **Optionale Tasks:**
    *   Integrationstests für den gesamten Datenfluss.
    *   Einrichtung eines Test-Frameworks für das einfache Hinzufügen von Testdaten neuer Kunden.
*   **Aufwandsschätzung:** 7-10 Personentage (VZ: 4-6 Tage, TZ: 3-4 Tage für Tests/Doku)
*   **Vorteile:** Sicherstellung der Funktionsfähigkeit, Wissenssicherung.
*   **Nachteile:** Tests für konfigurierbare Systeme können komplexer sein.

---

### AP 6: Onboarding eines zweiten (hypothetischen) Kunden

*   **Ausgangslage:** Das System ist refaktorisiert und funktioniert für den ersten Kunden.
*   **Beschreibung der Arbeit:**
    1.  Definition eines Satzes von Beispieldaten und Anforderungen für einen zweiten, hypothetischen Kunden mit abweichenden Formaten/Strukturen.
    2.  Erstellung einer neuen Client-Konfigurationsdatei für diesen Kunden.
    3.  Ggf. Implementierung eines neuen spezifischen Readers, falls ein bisher nicht unterstütztes Format benötigt wird.
    4.  Test des gesamten Datenflusses für den neuen Kunden.
    5.  Identifizierung und Behebung von Lücken oder Schwachstellen im Refactoring, die durch den neuen Anwendungsfall aufgedeckt werden.
*   **Soll-Zustand (MUSS):**
    *   Das System kann Daten von mindestens zwei unterschiedlichen (simulierten) Kundenkonfigurationen verarbeiten.
    *   Der Prozess zum Onboarding eines neuen Kunden ist erprobt und dokumentiert.
*   **Optionale Tasks:**
    *   Entwicklung eines "Client Onboarding Guides".
*   **Aufwandsschätzung:** 5-8 Personentage (VZ: 3-5 Tage, TZ: 2-3 Tage für Konfig/Tests)
*   **Vorteile:** Validierung des Refactorings, Aufdeckung von Schwachstellen.
*   **Nachteile:** Abhängig von der Komplexität des zweiten Kunden.

---

## 5. Zeitplan und Ressourcen

*   **Gesamtaufwand (geschätzt):** ca. 42 - 62 Personentage.
*   **Team:** 1 VZ-Entwickler, 1-2 TZ-Entwickler.
*   **Durchlaufzeit:** Bei optimaler Parallelisierung und Fokus könnte dies in 6-10 Wochen realisiert werden. Realistischer sind 3-4 Monate, um Raum für unvorhergesehene Probleme und andere Aufgaben zu lassen.

**Empfohlene Reihenfolge der APs:** AP1 -> AP2 -> AP3 -> AP4 -> AP5 -> AP6.
Die Teilzeit-Entwickler können parallel an spezifischen Readern (AP2), Mapping-Logiken (AP3), Prozessor-Anpassungen (AP4) oder Tests (AP5, AP6) arbeiten, während der Vollzeit-Entwickler die Kernarchitektur und -komponenten verantwortet.

## 6. Risiken

*   **Unterschätzung des Aufwands:** Das Refactoring bestehenden Codes ist oft komplexer als Neuentwicklungen.
*   **Komplexität des kanonischen Modells:** Ein zu detailliertes oder zu generisches Modell kann schwierig zu handhaben sein.
*   **Performance:** Viele Abstraktionsebenen könnten die Performance beeinflussen (wahrscheinlich vernachlässigbar bei den typischen Datenmengen, aber zu beobachten).
*   **Änderungen am Plugin doch notwendig:** Trotz aller Bemühungen könnten minimale Anpassungen am Plugin unumgänglich werden, wenn bestimmte Daten nicht anders aufbereitet werden können.
*   **Anforderungen neuer Kunden:** Sehr exotische Datenformate oder -logiken könnten den Rahmen der geplanten Abstraktionen sprengen.

## 7. Fazit

Das vorgeschlagene Refactoring ist ein signifikanter Eingriff, der jedoch unerlässlich ist, um die `app` zukunftsfähig und flexibel für verschiedene Kundenanforderungen zu machen. Durch die Einführung einer Konfigurationsebene und die Entkopplung der Komponenten wird die Wartbarkeit verbessert und das Onboarding neuer Kunden erheblich vereinfacht. Die Stabilität der Schnittstelle zum Revit-Plugin hat dabei höchste Priorität.

