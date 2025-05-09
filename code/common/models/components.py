"""
Komponenten-Modelle für Infrastrukturelemente.
Diese Komponenten können flexibel zu den Hauptelementen hinzugefügt werden,
um die Redundanz im Modell zu reduzieren und die Erweiterbarkeit zu verbessern.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from ..enums.process_enums import ProcessEnum, UnitEnum


class ComponentType(str, Enum):
    """Typen von Komponenten, die an Elementen angehängt werden können."""
    
    LOCATION = "location"  # Position im Raum
    DIMENSION = "dimension"  # Abmessungen
    MATERIAL = "material"  # Materialeigenschaften
    REFERENCE = "reference"  # Referenz zu einem anderen Element
    PHYSICAL = "physical"  # Physikalische Eigenschaften (Gewicht, Dichte, etc.)
    VISUAL = "visual"  # Visuelle Eigenschaften (Farbe, Textur, etc.)
    CUSTOM = "custom"  # Benutzerdefinierte Komponente


@dataclass
class Component:
    """Basisklasse für alle Komponenten."""
    
    component_type: ComponentType
    name: str = "unnamed"


@dataclass
class CoordinateLocation(Component):
    """Komponente für die Position eines Elements im Raum."""
    
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    
    def __post_init__(self):
        self.component_type = ComponentType.LOCATION
        
    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"


@dataclass
class LineLocation(Component):
    """Komponente für linienförmige Elemente mit Start- und Endpunkt."""
    
    start: CoordinateLocation = field(default_factory=lambda: CoordinateLocation(None, None, None))
    end: CoordinateLocation = field(default_factory=lambda: CoordinateLocation(None, None, None))
    
    def __post_init__(self):
        self.component_type = ComponentType.LOCATION
        
    def __str__(self) -> str:
        return f"{self.start} -> {self.end}"


@dataclass
class Dimension(Component):
    """Komponente für die Abmessungen eines Elements."""
    
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    
    # Spezifische Dimensionen für spezifische Elemente
    diameter: Optional[float] = None
    radius: Optional[float] = None
    length: Optional[float] = None
    
    def __post_init__(self):
        self.component_type = ComponentType.DIMENSION
        
    def __str__(self) -> str:
        dimensions = []
        if self.width is not None:
            dimensions.append(f"B={self.width:.2f}")
        if self.height is not None:
            dimensions.append(f"H={self.height:.2f}")
        if self.depth is not None:
            dimensions.append(f"T={self.depth:.2f}")
        if self.diameter is not None:
            dimensions.append(f"D={self.diameter:.2f}")
        if self.radius is not None:
            dimensions.append(f"R={self.radius:.2f}")
        if self.length is not None:
            dimensions.append(f"L={self.length:.2f}")
        
        return ", ".join(dimensions) if dimensions else "keine Dimensionen"


@dataclass
class MaterialProperties(Component):
    """Komponente für die Materialeigenschaften eines Elements."""
    
    material_name: str = "unbekannt"
    density: Optional[float] = None  # kg/m³
    youngs_modulus: Optional[float] = None  # GPa
    poissons_ratio: Optional[float] = None
    thermal_expansion: Optional[float] = None  # 1/K
    
    # Spezifische Materialeigenschaften
    tensile_strength: Optional[float] = None  # MPa
    compressive_strength: Optional[float] = None  # MPa
    
    def __post_init__(self):
        self.component_type = ComponentType.MATERIAL
        
    def __str__(self) -> str:
        return f"{self.material_name}"


@dataclass
class ElementReference(Component):
    """Komponente für die Referenz zu einem anderen Element."""

    component_type: ComponentType
    reference_type: str  # z.B. "foundation", "mast", etc.
    referenced_uuid: UUID
    name: str = "reference"
    bidirectional: bool = False  # Ob das referenzierte Element auch auf dieses verweist

    def __post_init__(self):
        self.component_type = ComponentType.REFERENCE
        
    def __str__(self) -> str:
        return f"{self.reference_type}: {self.referenced_uuid}"


class ComponentFactory:
    """Factory für die Erstellung von Komponenten aus Parametern."""
    
    @classmethod
    def create_location_from_params(cls, params: Dict[ProcessEnum, Any]) -> Optional[CoordinateLocation]:
        """Erstellt eine Location-Komponente aus Parametern."""
        x = params.get(ProcessEnum.X_COORDINATE)
        y = params.get(ProcessEnum.Y_COORDINATE)
        z = params.get(ProcessEnum.Z_COORDINATE)
        
        if any(coord is not None for coord in (x, y, z)):
            return CoordinateLocation(x=x, y=y, z=z, name="main_location")
        
        return None
    
    @classmethod
    def create_line_location_from_params(cls, params: Dict[ProcessEnum, Any]) -> Optional[LineLocation]:
        """Erstellt eine LineLocation-Komponente aus Parametern."""
        x1 = params.get(ProcessEnum.X_COORDINATE)
        y1 = params.get(ProcessEnum.Y_COORDINATE)
        z1 = params.get(ProcessEnum.Z_COORDINATE)
        x2 = params.get(ProcessEnum.X_COORDINATE_END)
        y2 = params.get(ProcessEnum.Y_COORDINATE_END)
        z2 = params.get(ProcessEnum.Z_COORDINATE_END)
        
        if any(coord is not None for coord in (x1, y1, z1, x2, y2, z2)):
            start = CoordinateLocation(x=x1, y=y1, z=z1)
            end = CoordinateLocation(x=x2, y=y2, z=z2)
            return LineLocation(start=start, end=end, name="line_location")
        
        return None
    
    @classmethod
    def create_foundation_dimension(cls, params: Dict[ProcessEnum, Any]) -> Optional[Dimension]:
        """Erstellt eine Dimension-Komponente für ein Fundament."""
        width = params.get(ProcessEnum.FOUNDATION_WIDTH)
        height = params.get(ProcessEnum.FOUNDATION_HEIGHT)
        depth = params.get(ProcessEnum.FOUNDATION_DEPTH)
        
        if any(dim is not None for dim in (width, height, depth)):
            return Dimension(width=width, height=height, depth=depth, name="foundation_dimension")
        
        return None
    
    @classmethod
    def create_mast_dimension(cls, params: Dict[ProcessEnum, Any]) -> Optional[Dimension]:
        """Erstellt eine Dimension-Komponente für einen Mast."""
        height = params.get(ProcessEnum.MAST_HEIGHT)
        diameter = params.get(ProcessEnum.DIAMETER)
        
        if any(dim is not None for dim in (height, diameter)):
            return Dimension(height=height, diameter=diameter, name="mast_dimension")
        
        return None
    
    @classmethod
    def create_pipe_dimension(cls, params: Dict[ProcessEnum, Any]) -> Optional[Dimension]:
        """Erstellt eine Dimension-Komponente für ein Rohr."""
        diameter = params.get(ProcessEnum.PIPE_DIAMETER)
        length = None
        
        # Berechne Länge, wenn Start- und Endpunkte vorhanden sind
        x1 = params.get(ProcessEnum.X_COORDINATE)
        y1 = params.get(ProcessEnum.Y_COORDINATE)
        z1 = params.get(ProcessEnum.Z_COORDINATE)
        x2 = params.get(ProcessEnum.X_COORDINATE_END)
        y2 = params.get(ProcessEnum.Y_COORDINATE_END)
        z2 = params.get(ProcessEnum.Z_COORDINATE_END)
        
        if all(coord is not None for coord in (x1, y1, z1, x2, y2, z2)):
            import math
            length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        
        if any(dim is not None for dim in (diameter, length)):
            return Dimension(diameter=diameter, length=length, name="pipe_dimension")
        
        return None
    
    @classmethod
    def create_shaft_dimension(cls, params: Dict[ProcessEnum, Any]) -> Optional[Dimension]:
        """Erstellt eine Dimension-Komponente für einen Schacht."""
        diameter = params.get(ProcessEnum.SHAFT_DIAMETER)
        depth = params.get(ProcessEnum.SHAFT_DEPTH)
        
        if any(dim is not None for dim in (diameter, depth)):
            return Dimension(diameter=diameter, depth=depth, name="shaft_dimension")
        
        return None
    
    @classmethod
    def create_track_dimension(cls, params: Dict[ProcessEnum, Any]) -> Optional[Dimension]:
        """Erstellt eine Dimension-Komponente für ein Gleis."""
        gauge = params.get(ProcessEnum.TRACK_GAUGE)
        length = None
        
        # Berechne Länge, wenn Start- und Endpunkte vorhanden sind
        x1 = params.get(ProcessEnum.X_COORDINATE)
        y1 = params.get(ProcessEnum.Y_COORDINATE)
        z1 = params.get(ProcessEnum.Z_COORDINATE)
        x2 = params.get(ProcessEnum.X_COORDINATE_END)
        y2 = params.get(ProcessEnum.Y_COORDINATE_END)
        z2 = params.get(ProcessEnum.Z_COORDINATE_END)
        
        if all(coord is not None for coord in (x1, y1, z1, x2, y2, z2)):
            import math
            length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
        
        if any(dim is not None for dim in (gauge, length)):
            return Dimension(width=gauge, length=length, name="track_dimension")
        
        return None
    
    @classmethod
    def create_material_from_params(cls, params: Dict[ProcessEnum, Any]) -> Optional[MaterialProperties]:
        """Erstellt eine Material-Komponente aus Parametern."""
        material_name = params.get(ProcessEnum.MATERIAL)
        
        if material_name:
            # Hier könnten weitere Materialparameter aus einer Materialdatenbank geladen werden
            return MaterialProperties(material_name=material_name, name="material")
        
        return None