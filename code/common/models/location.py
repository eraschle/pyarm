"""
Module für Lokationsmodelle und Komponenten.
Diese Modelle werden verwendet, um die Position und Orientierung von Elementen zu beschreiben.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Union

from ..enums.process_enums import ProcessEnum, UnitEnum


class CoordinateSystem(str, Enum):
    """Unterstützte Koordinatensysteme."""
    CARTESIAN = "cartesian"  # x, y, z Koordinaten
    GEOGRAPHIC = "geographic"  # Latitude, Longitude, Altitude
    RELATIVE = "relative"  # Relativ zu einem Referenzelement


class LocationType(str, Enum):
    """Typen von Lokationen."""
    POINT = "point"  # Einzelner Punkt
    LINE = "line"  # Linie zwischen zwei Punkten
    AREA = "area"  # Fläche (durch Punkte definiert)
    VOLUME = "volume"  # Volumen


@dataclass
class CoordinateLocation:
    """Repräsentiert einen Standort oder eine Position im 3D-Raum."""
    
    x: float  # X-Koordinate (Ost)
    y: float  # Y-Koordinate (Nord)
    z: float  # Z-Koordinate (Höhe)
    
    coordinate_system: CoordinateSystem = CoordinateSystem.CARTESIAN
    reference_id: Optional[str] = None  # Bei relativen Koordinaten: ID des Referenzelements
    
    # Optionale Attribute für die Ausrichtung
    azimuth: Optional[float] = None  # Azimut in Grad
    rotation_x: Optional[float] = None  # Rotation um die X-Achse in Grad
    rotation_y: Optional[float] = None  # Rotation um die Y-Achse in Grad
    rotation_z: Optional[float] = None  # Rotation um die Z-Achse in Grad
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Location in ein Dictionary."""
        result = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "coordinate_system": self.coordinate_system.value,
        }
        
        if self.reference_id:
            result["reference_id"] = self.reference_id
            
        if self.azimuth is not None:
            result["azimuth"] = self.azimuth
            
        if self.rotation_x is not None:
            result["rotation_x"] = self.rotation_x
            
        if self.rotation_y is not None:
            result["rotation_y"] = self.rotation_y
            
        if self.rotation_z is not None:
            result["rotation_z"] = self.rotation_z
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoordinateLocation":
        """Erstellt eine Location aus einem Dictionary."""
        coord_system = CoordinateSystem.CARTESIAN
        if "coordinate_system" in data:
            try:
                coord_system = CoordinateSystem(data["coordinate_system"])
            except ValueError:
                coord_system = CoordinateSystem.CARTESIAN
                
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0)),
            coordinate_system=coord_system,
            reference_id=data.get("reference_id"),
            azimuth=data.get("azimuth"),
            rotation_x=data.get("rotation_x"),
            rotation_y=data.get("rotation_y"),
            rotation_z=data.get("rotation_z"),
        )
    
    @classmethod
    def from_infrastructure_element(cls, element: Any) -> "CoordinateLocation":
        """Erstellt eine Location aus einem InfrastructureElement."""
        x = element.get_param(ProcessEnum.X_COORDINATE, 0.0)
        y = element.get_param(ProcessEnum.Y_COORDINATE, 0.0)
        z = element.get_param(ProcessEnum.Z_COORDINATE, 0.0)
        azimuth = element.get_param(ProcessEnum.AZIMUTH)
        rotation_x = element.get_param(ProcessEnum.ROTATION_X)
        rotation_y = element.get_param(ProcessEnum.ROTATION_Y)
        rotation_z = element.get_param(ProcessEnum.ROTATION_Z)
        
        return cls(
            x=x,
            y=y,
            z=z,
            azimuth=azimuth,
            rotation_x=rotation_x,
            rotation_y=rotation_y,
            rotation_z=rotation_z,
        )


@dataclass
class LineLocation:
    """Repräsentiert eine Linie im 3D-Raum mit Start- und Endpunkt."""
    
    start: CoordinateLocation
    end: CoordinateLocation
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die LineLocation in ein Dictionary."""
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineLocation":
        """Erstellt eine LineLocation aus einem Dictionary."""
        start_data = data.get("start", {})
        end_data = data.get("end", {})
        
        start = CoordinateLocation.from_dict(start_data)
        end = CoordinateLocation.from_dict(end_data)
        
        return cls(start=start, end=end)
    
    @classmethod
    def from_infrastructure_element(cls, element: Any) -> "LineLocation":
        """Erstellt eine LineLocation aus einem InfrastructureElement."""
        start = CoordinateLocation.from_infrastructure_element(element)
        
        end_x = element.get_param(ProcessEnum.X_COORDINATE_END, 0.0)
        end_y = element.get_param(ProcessEnum.Y_COORDINATE_END, 0.0)
        end_z = element.get_param(ProcessEnum.Z_COORDINATE_END, 0.0)
        
        end = CoordinateLocation(
            x=end_x,
            y=end_y,
            z=end_z,
            coordinate_system=start.coordinate_system,
            reference_id=start.reference_id,
        )
        
        return cls(start=start, end=end)


@dataclass
class Dimension:
    """Repräsentiert die Dimensionen eines Elements."""
    
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    length: Optional[float] = None
    diameter: Optional[float] = None
    radius: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert die Dimension in ein Dictionary."""
        result = {}
        
        if self.width is not None:
            result["width"] = self.width
            
        if self.height is not None:
            result["height"] = self.height
            
        if self.depth is not None:
            result["depth"] = self.depth
            
        if self.length is not None:
            result["length"] = self.length
            
        if self.diameter is not None:
            result["diameter"] = self.diameter
            
        if self.radius is not None:
            result["radius"] = self.radius
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dimension":
        """Erstellt eine Dimension aus einem Dictionary."""
        return cls(
            width=data.get("width"),
            height=data.get("height"),
            depth=data.get("depth"),
            length=data.get("length"),
            diameter=data.get("diameter"),
            radius=data.get("radius"),
        )
    
    @classmethod
    def from_infrastructure_element(cls, element: Any) -> "Dimension":
        """Erstellt eine Dimension aus einem InfrastructureElement."""
        # Generische Dimensionen
        width = element.get_param(ProcessEnum.WIDTH)
        height = element.get_param(ProcessEnum.HEIGHT)
        depth = element.get_param(ProcessEnum.DEPTH)
        length = element.get_param(ProcessEnum.LENGTH)
        diameter = element.get_param(ProcessEnum.DIAMETER)
        
        # Spezifische Dimensionen (falls generische nicht vorhanden)
        if width is None:
            width = element.get_param(ProcessEnum.FOUNDATION_WIDTH)
            
        if height is None:
            height = element.get_param(ProcessEnum.FOUNDATION_HEIGHT)
            if height is None:
                height = element.get_param(ProcessEnum.MAST_HEIGHT)
                
        if depth is None:
            depth = element.get_param(ProcessEnum.FOUNDATION_DEPTH)
            if depth is None:
                depth = element.get_param(ProcessEnum.SHAFT_DEPTH)
                
        if length is None:
            length = element.get_param(ProcessEnum.CANTILEVER_LENGTH)
            
        if diameter is None:
            diameter = element.get_param(ProcessEnum.PIPE_DIAMETER)
            if diameter is None:
                diameter = element.get_param(ProcessEnum.SHAFT_DIAMETER)
                
        # Radius für Kurven
        radius = None
        if element.get_param(ProcessEnum.START_RADIUS) is not None:
            radius = element.get_param(ProcessEnum.START_RADIUS)
        elif element.get_param(ProcessEnum.END_RADIUS) is not None:
            radius = element.get_param(ProcessEnum.END_RADIUS)
            
        return cls(
            width=width,
            height=height,
            depth=depth,
            length=length,
            diameter=diameter,
            radius=radius,
        )