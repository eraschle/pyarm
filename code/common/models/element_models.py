"""
Spezialisierte Modelle für verschiedene Arten von Infrastrukturelementen.
Diese Modelle bauen auf der Basisklasse InfrastructureElement auf und fügen
elementspezifische Funktionalität hinzu.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID

from ..enums.process_enums import ElementType, ProcessEnum, UnitEnum
from .base_models import InfrastructureElement, Parameter
from .components import ComponentType, CoordinateLocation, ElementReference


# Aliasing for backward compatibility
InfrastructureElementBase = InfrastructureElement
# Additional compatibility alias
PipeElement = InfrastructureElement


@dataclass
class LinearElement(InfrastructureElement):
    """
    Basisklasse für alle linienförmigen Elemente (Gleise, Rohre, etc.).
    """

    def __post_init__(self):
        super().__post_init__()

    @property
    def start_point(self) -> Optional[CoordinateLocation]:
        """Start-Koordinate des Elements."""
        if self.location:
            return self.location.start
        return None

    @property
    def end_point(self) -> Optional[CoordinateLocation]:
        """End-Koordinate des Elements."""
        if self.location:
            return self.location.end
        return None

    @property
    def length(self) -> Optional[float]:
        """Länge des Elements."""
        if self.dimensions:
            return self.dimensions.length

        # Berechnen aus Start- und Endpunkt
        if self.start_point and self.end_point:
            if all(
                coord is not None
                for coord in (
                    self.start_point.x,
                    self.start_point.y,
                    self.start_point.z,
                    self.end_point.x,
                    self.end_point.y,
                    self.end_point.z,
                )
            ):
                import math

                return math.sqrt(
                    (self.end_point.x - self.start_point.x) ** 2
                    + (self.end_point.y - self.start_point.y) ** 2
                    + (self.end_point.z - self.start_point.z) ** 2
                )

        return None


@dataclass
class NodeElement(InfrastructureElement):
    """
    Basisklasse für alle punktförmigen Elemente (Fundamente, Masten, Schächte, etc.).
    """

    def __post_init__(self):
        super().__post_init__()

    def add_reference(
        self, reference_type: str, referenced_uuid: UUID, bidirectional: bool = False
    ) -> None:
        """
        Fügt eine Referenz zu einem anderen Element hinzu.

        Args:
            reference_type: Typ der Referenz (z.B. "foundation", "mast")
            referenced_uuid: UUID des referenzierten Elements
            bidirectional: Ob die Referenz bidirektional ist
        """
        reference = ElementReference(
            referenced_uuid=referenced_uuid,
            reference_type=reference_type,
            bidirectional=bidirectional
        )
        reference.name = f"{reference_type}_reference"  # Set name after initialization
        reference.component_type = ComponentType.REFERENCE  # Ensure proper component type
        self.add_component(reference)

    def get_references(self, reference_type: Optional[str] = None) -> List[ElementReference]:
        """
        Gibt alle Referenzen oder nur Referenzen eines bestimmten Typs zurück.

        Args:
            reference_type: Optional der Typ der Referenzen

        Returns:
            Liste der Referenzen
        """
        references = self.get_components_by_type(ComponentType.REFERENCE)
        if reference_type:
            return [
                cast(ElementReference, ref)
                for ref in references
                if isinstance(ref, ElementReference) and ref.reference_type == reference_type
            ]
        return [
            cast(ElementReference, ref) for ref in references if isinstance(ref, ElementReference)
        ]


# Spezialisierte Elementklassen


@dataclass
class Foundation(NodeElement):
    """Fundament-Element."""

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.FOUNDATION
        super().__post_init__()


@dataclass
class Mast(NodeElement):
    """Mast-Element mit optionaler Referenz zum Fundament."""

    foundation_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.MAST
        super().__post_init__()

        # Referenz zum Fundament hinzufügen, wenn vorhanden
        if self.foundation_uuid:
            self.add_reference("foundation", self.foundation_uuid)


@dataclass
class Cantilever(NodeElement):
    """Ausleger-Element mit Referenz zum Mast."""

    mast_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.CANTILEVER
        super().__post_init__()

        # Referenz zum Mast hinzufügen, wenn vorhanden
        if self.mast_uuid:
            self.add_reference("mast", self.mast_uuid)


@dataclass
class Joch(LinearElement):
    """Joch-Element mit Referenzen zu zwei Masten."""

    mast_uuid_1: Optional[UUID] = None
    mast_uuid_2: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.JOCH
        super().__post_init__()

        # Referenzen zu den Masten hinzufügen, wenn vorhanden
        if self.mast_uuid_1:
            self.add_reference("mast", self.mast_uuid_1)
        if self.mast_uuid_2:
            self.add_reference("mast", self.mast_uuid_2)


@dataclass
class Track(LinearElement):
    """Gleis-Element."""

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.TRACK
        super().__post_init__()


@dataclass
class CurvedTrack(Track):
    """Kurvengleis-Element mit Klothoidenparametern."""

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Sleeper(NodeElement):
    """Schwellen-Element mit Referenz zum Gleis."""

    track_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.SLEEPER
        super().__post_init__()

        # Referenz zum Gleis hinzufügen, wenn vorhanden
        if self.track_uuid:
            self.add_reference("track", self.track_uuid)


@dataclass
class DrainagePipe(LinearElement):
    """Entwässerungsrohr-Element."""

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.DRAINAGE_PIPE
        super().__post_init__()


@dataclass
class DrainageShaft(NodeElement):
    """Entwässerungsschacht-Element."""

    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.DRAINAGE_SHAFT
        super().__post_init__()
