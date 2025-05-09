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
from .components import (
    Component, 
    ComponentType, 
    CoordinateLocation, 
    LineLocation, 
    Dimension,
    ElementReference
)


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
            if all(coord is not None for coord in (
                self.start_point.x, self.start_point.y, self.start_point.z,
                self.end_point.x, self.end_point.y, self.end_point.z
            )):
                import math
                return math.sqrt(
                    (self.end_point.x - self.start_point.x) ** 2 +
                    (self.end_point.y - self.start_point.y) ** 2 +
                    (self.end_point.z - self.start_point.z) ** 2
                )
        
        return None


@dataclass
class NodeElement(InfrastructureElement):
    """
    Basisklasse für alle punktförmigen Elemente (Fundamente, Masten, Schächte, etc.).
    """
    
    def __post_init__(self):
        super().__post_init__()
    
    def add_reference(self, reference_type: str, referenced_uuid: UUID, bidirectional: bool = False) -> None:
        """
        Fügt eine Referenz zu einem anderen Element hinzu.
        
        Args:
            reference_type: Typ der Referenz (z.B. "foundation", "mast")
            referenced_uuid: UUID des referenzierten Elements
            bidirectional: Ob die Referenz bidirektional ist
        """
        reference = ElementReference(
            component_type=ComponentType.REFERENCE,
            name=f"{reference_type}_reference",
            reference_type=reference_type,
            referenced_uuid=referenced_uuid,
            bidirectional=bidirectional
        )
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
                cast(ElementReference, ref) for ref in references
                if isinstance(ref, ElementReference) and ref.reference_type == reference_type
            ]
        return [cast(ElementReference, ref) for ref in references if isinstance(ref, ElementReference)]


# Spezialisierte Elementklassen

@dataclass
class Foundation(NodeElement):
    """Fundament-Element."""
    
    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.FOUNDATION
        super().__post_init__()
    
    @property
    def width(self) -> Optional[float]:
        """Breite des Fundaments."""
        if self.dimensions:
            return self.dimensions.width
        return self.get_param(ProcessEnum.FOUNDATION_WIDTH)
    
    @width.setter
    def width(self, value: float) -> None:
        """Setzt die Breite des Fundaments."""
        self.set_param(ProcessEnum.FOUNDATION_WIDTH, value, UnitEnum.METER)
    
    @property
    def height(self) -> Optional[float]:
        """Höhe des Fundaments."""
        if self.dimensions:
            return self.dimensions.height
        return self.get_param(ProcessEnum.FOUNDATION_HEIGHT)
    
    @height.setter
    def height(self, value: float) -> None:
        """Setzt die Höhe des Fundaments."""
        self.set_param(ProcessEnum.FOUNDATION_HEIGHT, value, UnitEnum.METER)
    
    @property
    def depth(self) -> Optional[float]:
        """Tiefe des Fundaments."""
        if self.dimensions:
            return self.dimensions.depth
        return self.get_param(ProcessEnum.FOUNDATION_DEPTH)
    
    @depth.setter
    def depth(self, value: float) -> None:
        """Setzt die Tiefe des Fundaments."""
        self.set_param(ProcessEnum.FOUNDATION_DEPTH, value, UnitEnum.METER)


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
    
    @property
    def height(self) -> Optional[float]:
        """Höhe des Masts."""
        if self.dimensions:
            return self.dimensions.height
        return self.get_param(ProcessEnum.MAST_HEIGHT)
    
    @height.setter
    def height(self, value: float) -> None:
        """Setzt die Höhe des Masts."""
        self.set_param(ProcessEnum.MAST_HEIGHT, value, UnitEnum.METER)
    
    @property
    def diameter(self) -> Optional[float]:
        """Durchmesser des Masts."""
        if self.dimensions:
            return self.dimensions.diameter
        return self.get_param(ProcessEnum.DIAMETER)
    
    @diameter.setter
    def diameter(self, value: float) -> None:
        """Setzt den Durchmesser des Masts."""
        self.set_param(ProcessEnum.DIAMETER, value, UnitEnum.METER)


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
    
    @property
    def length(self) -> Optional[float]:
        """Länge des Auslegers."""
        if self.dimensions:
            return self.dimensions.length
        return self.get_param(ProcessEnum.CANTILEVER_LENGTH)
    
    @length.setter
    def length(self, value: float) -> None:
        """Setzt die Länge des Auslegers."""
        self.set_param(ProcessEnum.CANTILEVER_LENGTH, value, UnitEnum.METER)


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
            self.add_reference("mast1", self.mast_uuid_1)
        if self.mast_uuid_2:
            self.add_reference("mast2", self.mast_uuid_2)
    
    @property
    def span(self) -> Optional[float]:
        """Spannweite des Jochs."""
        # Erst aus der Dimension holen
        if self.dimensions and self.dimensions.length:
            return self.dimensions.length
        
        # Dann aus dem Parameter
        span = self.get_param(ProcessEnum.JOCH_SPAN)
        if span is not None:
            return span
        
        # Sonst aus der Länge berechnen
        return self.length


@dataclass
class Track(LinearElement):
    """Gleis-Element."""
    
    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.TRACK
        super().__post_init__()
    
    @property
    def gauge(self) -> Optional[float]:
        """Spurweite des Gleises."""
        if self.dimensions:
            return self.dimensions.width
        return self.get_param(ProcessEnum.TRACK_GAUGE)
    
    @gauge.setter
    def gauge(self, value: float) -> None:
        """Setzt die Spurweite des Gleises."""
        self.set_param(ProcessEnum.TRACK_GAUGE, value, UnitEnum.METER)
    
    @property
    def track_type(self) -> Optional[str]:
        """Typ des Gleises."""
        return self.get_param(ProcessEnum.TRACK_TYPE)
    
    @track_type.setter
    def track_type(self, value: str) -> None:
        """Setzt den Typ des Gleises."""
        self.set_param(ProcessEnum.TRACK_TYPE, value)
    
    @property
    def cant(self) -> Optional[float]:
        """Überhöhung des Gleises."""
        return self.get_param(ProcessEnum.TRACK_CANT)
    
    @cant.setter
    def cant(self, value: float) -> None:
        """Setzt die Überhöhung des Gleises."""
        self.set_param(ProcessEnum.TRACK_CANT, value, UnitEnum.MILLIMETER)


@dataclass
class CurvedTrack(Track):
    """Kurvengleis-Element mit Klothoidenparametern."""
    
    def __post_init__(self):
        super().__post_init__()
        
    @property
    def clothoid_parameter(self) -> Optional[float]:
        """Klothoidenparameter des Kurvengleises."""
        return self.get_param(ProcessEnum.CLOTHOID_PARAMETER)
    
    @clothoid_parameter.setter
    def clothoid_parameter(self, value: float) -> None:
        """Setzt den Klothoidenparameter des Kurvengleises."""
        self.set_param(ProcessEnum.CLOTHOID_PARAMETER, value)
    
    @property
    def start_radius(self) -> Optional[float]:
        """Startradius des Kurvengleises."""
        return self.get_param(ProcessEnum.START_RADIUS)
    
    @start_radius.setter
    def start_radius(self, value: float) -> None:
        """Setzt den Startradius des Kurvengleises."""
        self.set_param(ProcessEnum.START_RADIUS, value, UnitEnum.METER)
    
    @property
    def end_radius(self) -> Optional[float]:
        """Endradius des Kurvengleises."""
        return self.get_param(ProcessEnum.END_RADIUS)
    
    @end_radius.setter
    def end_radius(self, value: float) -> None:
        """Setzt den Endradius des Kurvengleises."""
        self.set_param(ProcessEnum.END_RADIUS, value, UnitEnum.METER)


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
    
    @property
    def sleeper_type(self) -> Optional[str]:
        """Typ der Schwelle."""
        return self.get_param(ProcessEnum.SLEEPER_TYPE)
    
    @sleeper_type.setter
    def sleeper_type(self, value: str) -> None:
        """Setzt den Typ der Schwelle."""
        self.set_param(ProcessEnum.SLEEPER_TYPE, value)


@dataclass
class DrainagePipe(LinearElement):
    """Entwässerungsrohr-Element."""
    
    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.DRAINAGE_PIPE
        super().__post_init__()
    
    @property
    def diameter(self) -> Optional[float]:
        """Durchmesser des Rohrs."""
        if self.dimensions:
            return self.dimensions.diameter
        return self.get_param(ProcessEnum.PIPE_DIAMETER)
    
    @diameter.setter
    def diameter(self, value: float) -> None:
        """Setzt den Durchmesser des Rohrs."""
        self.set_param(ProcessEnum.PIPE_DIAMETER, value, UnitEnum.MILLIMETER)
    
    @property
    def slope(self) -> Optional[float]:
        """Gefälle des Rohrs."""
        return self.get_param(ProcessEnum.PIPE_SLOPE)
    
    @slope.setter
    def slope(self, value: float) -> None:
        """Setzt das Gefälle des Rohrs."""
        self.set_param(ProcessEnum.PIPE_SLOPE, value, UnitEnum.PROMILLE)


@dataclass
class DrainageShaft(NodeElement):
    """Entwässerungsschacht-Element."""
    
    def __post_init__(self):
        if self.element_type == ElementType.NONE:
            self.element_type = ElementType.DRAINAGE_SHAFT
        super().__post_init__()
    
    @property
    def diameter(self) -> Optional[float]:
        """Durchmesser des Schachts."""
        if self.dimensions:
            return self.dimensions.diameter
        return self.get_param(ProcessEnum.SHAFT_DIAMETER)
    
    @diameter.setter
    def diameter(self, value: float) -> None:
        """Setzt den Durchmesser des Schachts."""
        self.set_param(ProcessEnum.SHAFT_DIAMETER, value, UnitEnum.MILLIMETER)
    
    @property
    def depth(self) -> Optional[float]:
        """Tiefe des Schachts."""
        if self.dimensions:
            return self.dimensions.depth
        return self.get_param(ProcessEnum.SHAFT_DEPTH)
    
    @depth.setter
    def depth(self, value: float) -> None:
        """Setzt die Tiefe des Schachts."""
        self.set_param(ProcessEnum.SHAFT_DEPTH, value, UnitEnum.METER)