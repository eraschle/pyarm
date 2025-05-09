# Refactoring Bericht: Verbesserung der Modellierungsprozesse

## Übersicht

Dieses Dokument beschreibt die geplanten Refactoring-Maßnahmen zur Verbesserung der Modellierungsprozesse im Projekt. Das Hauptziel ist die Erweiterung der aktuellen, kundenspezifischen Implementierung, um verschiedene Dateiformate von unterschiedlichen Kunden einlesen und verarbeiten zu können. Die extrahierten Daten werden durch die `/app/`-Komponente verarbeitet und anschließend für das Revit-Plugin aufbereitet, welches Punkt- oder linienbasierte Elemente mit UUID und Koordinateninformationen erstellt.

## Ausgangslage

Die aktuelle Implementierung ist auf einen spezifischen Kunden ausgerichtet und kann nur ein bestimmtes Datenformat einlesen. Die Verarbeitung erfolgt durch eine Vielzahl kundenspezifischer Prozessoren, die von `ProcessorBase` erben. Die Datenextraktion und -aufbereitung ist fest mit dem Kundendatenformat verknüpft, was die Erweiterung für andere Kunden erschwert.

Schlüsselprobleme der aktuellen Implementierung:

1. Starke Kopplung zwischen Datenextraktion und Datenverarbeitung
2. Kundenspezifische Datenstrukturen und Prozessoren (DfA, Punkthimmel etc.)
3. Keine klare Trennung zwischen allgemeiner Funktionalität und kundenspezifischer Logik
4. Fehlende standardisierte interne Datenrepräsentation

## Arbeitspaket 1: Definition eines kanonischen internen Datenmodells

### Ausgangslage
Die aktuelle Implementierung verwendet verschiedene kundenspezifische Datenstrukturen, die direkt in den Prozessoren verarbeitet werden. Es gibt keine einheitliche Datenrepräsentation, was die Erweiterung für andere Kunden erschwert.

### Beschreibung der Arbeit
- Analyse der aktuell verwendeten Datenstrukturen in allen Prozessoren
- Identifikation der gemeinsamen und kundenspezifischen Datenfelder
- Definition eines kanonischen internen Datenmodells (bereits in `base.py` als `CanonicalObjectData` und `CanonicalAttributes` begonnen)
- Erweiterung der Datenmodelle, um alle notwendigen Informationen aus verschiedenen Kundenformaten abzubilden

### MUSS-Zustand nach diesem Schritt
- Vollständig definiertes kanonisches Datenmodell in `app/dfa/base.py`
- Dokumentation der Felder und ihrer Bedeutung
- Klare Trennung zwischen geometrischen Daten (Punkte, Ausrichtung) und Attributdaten
- Zuordnung der bestehenden Kundenformate zu den kanonischen Feldern

### Optionale Aufgaben
- Erstellung von Validierungsfunktionen für das kanonische Datenmodell
- Entwicklung von Unit-Tests für die Datenkonvertierung

### Aufwandschätzung
- 2-3 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 2: Implementierung von generischen Datenlesern

### Ausgangslage
Die aktuelle Implementierung kann nur ein spezifisches Datenformat einlesen (DfA-Reports, Punkthimmel, etc.). Die Datenextraktion ist eng mit der Datenverarbeitung verbunden.

### Beschreibung der Arbeit
- Entwicklung einer Abstraktion für Datenleser (`DataReader` Interface)
- Implementierung spezifischer Leser für verschiedene Datenformate (Excel, CSV, JSON, XML, etc.)
- Integration von Mapping-Funktionalität, um kundenspezifische Felder auf das kanonische Datenmodell abzubilden
- Erweiterung der `ProjectFolderReader`-Klasse, um flexible Konfiguration der Dateipfade und -formate zu ermöglichen

### MUSS-Zustand nach diesem Schritt
- Modulare Datenleser für verschiedene Formate
- Konfigurierbare Mapping-Mechanismen von Kundendatenformaten zum kanonischen Modell
- Erweiterung der Konfigurationsdatei (`default_client_config.json`), um kundenspezifische Lesekonfigurationen zu unterstützen

### Optionale Aufgaben
- Implementierung von Validierungsmechanismen für eingelesene Daten
- Entwicklung einer Vorschaufunktion zur Überprüfung der Datenmappings

### Aufwandschätzung
- 4-5 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 3: Refactoring der Höhenextraktion

### Ausgangslage
Die aktuelle Implementierung verwendet eine Prioritätsliste für Höhenquellen (Punkthimmel, DfA, DTM, API). Diese Logik ist in `ProcessorBase` implementiert und eng mit den kundenspezifischen Datenstrukturen verknüpft.

### Beschreibung der Arbeit
- Extraktion der Höhenberechnung in separate, spezialisierte Klassen
- Implementierung einer Strategie-Schnittstelle für Höhenextraktion
- Unterstützung verschiedener Höhenquellen und Prioritätsstrategien
- Konfigurierbare Höhenkorrekturen (ADD_TO_HEIGHT) pro Kunde und Objekttyp

### MUSS-Zustand nach diesem Schritt
- Modulare Höhenextraktionsstrategie
- Konfigurierbare Prioritätsreihenfolge für Höhenquellen
- Unterstützung kundenspezifischer Höhenkorrekturen

### Optionale Aufgaben
- Caching-Mechanismus für Höhendaten zur Performanceverbesserung
- Visualisierung der Höhenquellen zur Qualitätskontrolle

### Aufwandschätzung
- 3-4 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 4: Refactoring der Prozessoren

### Ausgangslage
Die aktuellen Prozessoren sind stark kundenspezifisch und direkt mit den Datenformaten verbunden. Es gibt viele überlappende Implementierungen und redundante Logik.

### Beschreibung der Arbeit
- Umstellung der Prozessoren auf das kanonische Datenmodell
- Extraktion gemeinsamer Funktionalität in Basisklassen
- Entwicklung einer modularen Prozessor-Factory
- Trennung von allgemeinen und kundenspezifischen Verarbeitungsschritten

### MUSS-Zustand nach diesem Schritt
- Prozessoren arbeiten mit dem kanonischen Datenmodell
- Klare Trennung zwischen gemeinsamer und kundenspezifischer Logik
- Konfigurierbare Prozessor-Factory basierend auf Objekttypen

### Optionale Aufgaben
- Implementierung von Validierungslogik für Prozessor-Outputs
- Entwicklung eines Feedback-Mechanismus für fehlerhafte Daten

### Aufwandschätzung
- 5-7 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 5: Erweiterung der Konfigurationsmechanismen

### Ausgangslage
Die aktuelle Implementierung verwendet eine einfache JSON-Konfiguration für Pfade und Mappings, bietet aber keine Möglichkeit für umfassende kundenspezifische Konfigurationen.

### Beschreibung der Arbeit
- Entwicklung eines umfassenden Konfigurationsmodells
- Implementierung von kundenspezifischen Konfigurationsprofilen
- Unterstützung von Überschreibungen und Vererbung in der Konfiguration
- Integration einer Validierung für Konfigurationen

### MUSS-Zustand nach diesem Schritt
- Umfassendes Konfigurationsmodell für alle kundenspezifischen Aspekte
- Unterstützung mehrerer Kundenprofile in einer einzigen Installation
- Einfache Erweiterbarkeit für neue Kundenanforderungen

### Optionale Aufgaben
- Entwicklung einer Benutzeroberfläche für Konfigurationsanpassungen
- Version-Tracking für Konfigurationsänderungen

### Aufwandschätzung
- 4-5 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 6: Erweiterung des Revit-Plugins

### Ausgangslage
Das aktuelle Plugin ist relativ simpel und erwartet Daten in einem spezifischen Format.

### Beschreibung der Arbeit
- Anpassung des Plugins an das neue Datenformat
- Minimale Änderungen, um die Kompatibilität mit den aufbereiteten Daten zu gewährleisten
- Mögliche Erweiterungen für verbesserte Fehlerbehandlung

### MUSS-Zustand nach diesem Schritt
- Plugin funktioniert mit der neuen Datenstruktur
- Minimale Änderungen gemäß der Anforderung

### Optionale Aufgaben
- Verbesserte Fehlerbehandlung und Benutzerrückmeldung
- Fortschrittsanzeige während der Datenverarbeitung

### Aufwandschätzung
- 2-3 Tage für einen Vollzeit-Entwickler

## Arbeitspaket 7: Testabdeckung und Dokumentation

### Ausgangslage
Die aktuelle Testabdeckung ist begrenzt und konzentriert sich hauptsächlich auf einige Basiskomponenten.

### Beschreibung der Arbeit
- Entwicklung von umfassenden Tests für alle neuen Komponenten
- Integration von End-to-End-Tests für verschiedene Kundenszenarien
- Erstellung detaillierter Dokumentation für die neue Architektur
- Entwicklung von Beispielkonfigurationen für verschiedene Kundentypen

### MUSS-Zustand nach diesem Schritt
- Umfassende Testabdeckung für alle Kernkomponenten
- Ausführliche Dokumentation der Architektur und Erweiterungsmöglichkeiten
- Beispielkonfigurationen für verschiedene Szenarien

### Optionale Aufgaben
- Automatisierte Performance-Tests
- Entwicklung einer Onboarding-Dokumentation für neue Entwickler

### Aufwandschätzung
- 4-6 Tage für einen Vollzeit-Entwickler

## Gesamtprojektplanung

### Zeitrahmen
- Gesamtaufwand: ~24-33 Arbeitstage für einen Vollzeit-Entwickler
- Bei einem Team von einem Vollzeit- und zwei Teilzeit-Entwicklern kann das Projekt in 2-3 Monaten abgeschlossen werden.

### Empfohlene Reihenfolge der Arbeitspakete
1. Definition des kanonischen internen Datenmodells (AP1) - Grundlage für alle weiteren Änderungen
2. Implementierung von generischen Datenlesern (AP2) - Ermöglicht die Unterstützung verschiedener Kundenformate
3. Refactoring der Höhenextraktion (AP3) - Wichtige Komponente für die korrekte Datenaufbereitung
4. Refactoring der Prozessoren (AP4) - Kernkomponente für die Datenverarbeitung
5. Erweiterung der Konfigurationsmechanismen (AP5) - Ermöglicht kundenspezifische Anpassungen
6. Erweiterung des Revit-Plugins (AP6) - Minimale Anpassungen für die Integration
7. Testabdeckung und Dokumentation (AP7) - Sicherstellung der Qualität und Wartbarkeit

### Abhängigkeiten und Parallelisierung
- AP1 muss vor allen anderen Arbeitspaketen abgeschlossen sein
- AP2 und AP3 können parallel bearbeitet werden
- AP4 erfordert den Abschluss von AP1, AP2 und AP3
- AP5 kann teilweise parallel zu AP4 bearbeitet werden
- AP6 erfordert den Abschluss von AP4
- AP7 kann kontinuierlich während des gesamten Projekts bearbeitet werden

### Ressourcenplanung
- Vollzeit-Entwickler: Primär verantwortlich für AP1, AP4 und AP6
- Teilzeit-Entwickler 1: Primär verantwortlich für AP2 und AP5
- Teilzeit-Entwickler 2: Primär verantwortlich für AP3 und AP7

## Vorteile der neuen Architektur

1. **Erweiterbarkeit**: Einfache Integration neuer Kundenformate und Datenquellen
2. **Wartbarkeit**: Klare Trennung von Verantwortlichkeiten und modulare Struktur
3. **Testbarkeit**: Verbesserte Testbarkeit durch isolierte Komponenten
4. **Konfigurierbarkeit**: Umfassende Konfigurationsmöglichkeiten für verschiedene Kundenanforderungen
5. **Wiederverwendbarkeit**: Gemeinsame Funktionalität kann über Kundenprojekte hinweg wiederverwendet werden

## Architekturdiagramm

```
┌─────────────────────────────┐
│ Kundenspezifische Daten     │
│ (Excel, CSV, JSON, etc.)    │
└───────────────┬─────────────┘
                │
┌───────────────▼─────────────┐
│ DataReaders                 │
│ - ExcelReader               │
│ - CSVReader                 │
│ - JSONReader                │
│ - XMLReader                 │
└───────────────┬─────────────┘
                │
┌───────────────▼─────────────┐
│ Kanonisches Datenmodell     │
│ (CanonicalObjectData)       │
└───────────────┬─────────────┘
                │
┌───────────────▼─────────────┐
│ Prozessoren                 │
│ - Basisklassen              │
│ - Kundenspezifische Klassen │
└───────────────┬─────────────┘
                │
┌───────────────▼─────────────┐
│ Output für Revit-Plugin     │
│ (ProcessedOutput)           │
└───────────────┬─────────────┘
                │
┌───────────────▼─────────────┐
│ Revit-Plugin                │
│                             │
└─────────────────────────────┘
```

## Risiken und Herausforderungen

1. **Komplexität der Migration**: Die Umstellung bestehender kundenspezifischer Prozessoren auf das neue Datenmodell könnte komplex sein.
2. **Abwärtskompatibilität**: Sicherstellung, dass bestehende Kundenprojekte weiterhin funktionieren.
3. **Leistungsaspekte**: Die zusätzliche Abstraktionsebene könnte die Leistung beeinflussen.
4. **Ressourcenverfügbarkeit**: Die geschätzte Zeitlinie setzt die kontinuierliche Verfügbarkeit der Entwickler voraus.

## Zusammenfassung

Das vorgeschlagene Refactoring wird die Fähigkeit des Systems erheblich verbessern, mit verschiedenen Kundenformaten zu arbeiten, während die Kernfunktionalität erhalten bleibt. Durch die Einführung eines kanonischen Datenmodells, modularer Datenleser und verbesserter Konfigurationsmechanismen wird das System flexibler, wartbarer und leichter erweiterbar. Die Arbeit kann in überschaubaren Paketen organisiert werden, die den verfügbaren Ressourcen entsprechen und eine kontinuierliche Weiterentwicklung des Systems ermöglichen.