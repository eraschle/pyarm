"""
Komponenten-Modelle für Infrastrukturelemente.
Diese Komponenten können flexibel zu den Hauptelementen hinzugefügt werden,
um die Redundanz im Modell zu reduzieren und die Erweiterbarkeit zu verbessern.
i
"""

from enum import Enum
from typing import Any, Dict


class ComponentType(str, Enum):
    """Typen von Komponenten, die an Elementen angehängt werden können."""

    UNKNWOWN = "UNKNWOWN"  # Position im Raum
    LOCATION = "location"  # Position im Raum
    DIMENSION = "dimension"  # Abmessungen
    REFERENCE = "reference"  # Referenz zu einem anderen Element
    CUSTOM = "custom"  # Benutzerdefinierte Komponente
    METADATA = "metadata"  # Metadaten
    PROJECT_PHASE = "building_phase"  # Bauphasen
    IFC_CONFIG = "ifc_config"  # IFC-Konfiguration


class Component:
    """Basisklasse für alle Komponenten."""

    def __init__(self, name: str, component_type: ComponentType):
        self.name = name
        self.component_type = component_type

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to a dictionary for serialization.

        Returns
        -------
        dict
            Dictionary representation of the component
        """
        return {"name": self.name, "component_type": self.component_type.value}
