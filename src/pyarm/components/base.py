"""
Komponenten-Modelle für Infrastrukturelemente.
Diese Komponenten können flexibel zu den Hauptelementen hinzugefügt werden,
um die Redundanz im Modell zu reduzieren und die Erweiterbarkeit zu verbessern.
"""

from enum import Enum


class ComponentType(str, Enum):
    """Typen von Komponenten, die an Elementen angehängt werden können."""

    UNKNWOWN = "UNKNWOWN"  # Position im Raum
    LOCATION = "location"  # Position im Raum
    DIMENSION = "dimension"  # Abmessungen
    MATERIAL = "material"  # Materialeigenschaften
    REFERENCE = "reference"  # Referenz zu einem anderen Element
    PHYSICAL = "physical"  # Physikalische Eigenschaften (Gewicht, Dichte, etc.)
    VISUAL = "visual"  # Visuelle Eigenschaften (Farbe, Textur, etc.)
    CUSTOM = "custom"  # Benutzerdefinierte Komponente


class Component:
    """Basisklasse für alle Komponenten."""

    def __init__(self, name: str, component_type: ComponentType):
        self.name = name
        self.component_type = component_type
