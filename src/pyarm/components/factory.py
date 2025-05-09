from typing import TYPE_CHECKING

from pyarm.components.dimension import Dimension
from pyarm.components.location import Coordinate, LineLocation, PointLocation
from pyarm.models.process_enums import ProcessEnum

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement


class ComponentFactory:
    """Factory für die Erstellung von Komponenten aus Parametern."""

    @classmethod
    def _create_coordinate(
        cls, element: "InfrastructureElement", params: dict[str, ProcessEnum]
    ) -> Coordinate | None:
        """Erstellt eine Location-Komponente aus Parametern."""
        params["rotation_x"] = ProcessEnum.ROTATION_X
        params["rotation_y"] = ProcessEnum.ROTATION_Y
        params["rotation_z"] = ProcessEnum.ROTATION_Z
        return Coordinate(element, params)

    @classmethod
    def create_location(cls, element: "InfrastructureElement") -> PointLocation | LineLocation:
        """Erstellt eine Location-Komponente aus Parametern."""
        point_enums = {
            "x": ProcessEnum.X_COORDINATE,
            "y": ProcessEnum.Y_COORDINATE,
            "z": ProcessEnum.Z_COORDINATE,
        }
        point = cls._create_coordinate(element, point_enums)
        if point is None:
            raise ValueError("Invalid point or start point values")
        end_enums = {
            "x": ProcessEnum.X_COORDINATE_END,
            "y": ProcessEnum.X_COORDINATE_END,
            "z": ProcessEnum.X_COORDINATE_END,
        }
        end_point = cls._create_coordinate(element, end_enums)
        if end_point is None:
            return PointLocation(location=point)
        return LineLocation(start=point, end=end_point)

    @classmethod
    def create_dimension(cls, element: "InfrastructureElement") -> Dimension:
        """Erstellt eine Dimension-Komponente für ein Rohr."""
        dimension_param = {
            "width": ProcessEnum.WIDTH,
            "height": ProcessEnum.HEIGHT,
            "depth": ProcessEnum.DEPTH,
            "diameter": ProcessEnum.DIAMETER,
            "radius": ProcessEnum.RADIUS,
            "length": ProcessEnum.LENGTH,
        }
        return Dimension(element=element)
