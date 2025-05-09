# Unit Tests für das SortDesk Infrastructure Modeling System

Dieser Ordner enthält Unit-Tests für die verschiedenen Komponenten des SortDesk Infrastructure Modeling Systems. Die Tests decken die zentralen Funktionalitäten der Anwendung ab und dienen als Dokumentation und Qualitätssicherung.

## Testübersicht

1. **`test_base_models.py`** - Tests für die grundlegenden Datenmodelle
   - Test der Parameter-Klasse
   - Test der InfrastructureElement-Basisklasse
   - Test von Gettern und Settern für Parameter
   - Test der Validierungsfunktionen

2. **`test_element_models.py`** - Tests für die spezialisierten Elementmodelle
   - Test der Foundation-Klasse
   - Test der Mast-Klasse
   - Test der Track-Klasse
   - Test der CurvedTrack-Klasse
   - Test der Joch-Klasse
   - Test der Cantilever-Klasse

3. **`test_enums.py`** - Tests für die Enum-Definitionen
   - Test der ProcessEnum-Werte
   - Test der ElementType-Werte
   - Test der UnitEnum-Werte

4. **`test_type_guards.py`** - Tests für die Type-Guards
   - Test der Typüberprüfungsfunktionen (is_foundation, is_mast, etc.)
   - Test der Capability-Prüfungen (has_clothoid_capability)

5. **`test_json_repository.py`** - Tests für das Repository
   - Test des Speicherns und Abrufens von Elementen
   - Test der get_by_type-Funktion
   - Test der delete-Funktion
   - Test der Dateistruktur

6. **`test_calculation_service.py`** - Tests für den Calculation-Service
   - Test der Berechnung von Kräften auf Gleisen
   - Test der Strukturlastberechnung
   - Test der elementspezifischen Berechnungen
   - Test der CalculationElement-Klasse

7. **`test_visualization_service.py`** - Tests für den Visualization-Service
   - Test der Aufbereitung von Elementen für die Visualisierung
   - Test der Berechnung von Klothoidenpunkten
   - Test elementspezifischer Visualisierungsattribute

8. **`test_visualization_process.py`** - Tests für den Visualization-Prozess
   - Test der Prozessausführung
   - Test der Verarbeitung einzelner Elemente
   - Test der Verarbeitung von Elementen nach Typ
   - Test der Ausgabedateien

9. **`test_factory.py`** - Tests für die Element-Factory
   - Test der Erstellung von Elementen aus Rohdaten
   - Test der Fehlerbehandlung

## Testausführung

Um alle Tests auszuführen, wechseln Sie in das Hauptverzeichnis des Projekts und führen Sie folgenden Befehl aus:

```bash
python -m unittest discover -s projekte/code/tests
```

Um einen spezifischen Test auszuführen, verwenden Sie:

```bash
python -m unittest projekte/code/tests/test_base_models.py
```

## Test-Design-Prinzipien

Die Tests folgen diesen Prinzipien:

1. **Isolation** - Tests sind unabhängig voneinander und können in beliebiger Reihenfolge ausgeführt werden.
2. **Mocking-Minimierung** - Die Tests verwenden so wenig Mocks wie möglich, um realistische Szenarien zu testen.
3. **Vollständige Abdeckung** - Die Tests decken alle wichtigen Funktionalitäten der Komponenten ab.
4. **Lesbarkeit** - Die Tests sind klar strukturiert und dienen auch als Dokumentation der erwarteten Verhaltensweisen.

## Hinzufügen neuer Tests

Beim Hinzufügen neuer Funktionalitäten zum System sollten entsprechende Tests erstellt werden:

1. Erstellen Sie eine neue Testdatei für neue Module.
2. Fügen Sie Tests für alle öffentlichen Methoden und wichtige interne Funktionalitäten hinzu.
3. Testen Sie sowohl normale Anwendungsfälle als auch Grenz- und Fehlerfälle.
4. Dokumentieren Sie die Tests in dieser README-Datei.