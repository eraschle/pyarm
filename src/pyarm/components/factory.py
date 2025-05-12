from typing import TYPE_CHECKING, Type
from uuid import UUID

from pyarm.components.dimension import Dimension, RectangularDimension, RoundDimension
from pyarm.components.location import Coordinate, LineLocation, PointLocation
from pyarm.components.reference import ElementReference
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
        coord_2d = [params[coord] for coord in ("x", "y") if coord in params]
        if not all(element.has_param(coord) for coord in coord_2d):
            return None
        return Coordinate(element, params)

    @classmethod
    def create_location(cls, element: "InfrastructureElement") -> PointLocation | LineLocation:
        """Erstellt eine Location-Komponente aus Parametern."""
        point_enums = {
            "x": ProcessEnum.X_COORDINATE,
            "y": ProcessEnum.Y_COORDINATE,
            "z": ProcessEnum.Z_COORDINATE,
            "rotation_x": ProcessEnum.X_ROTATION,
            "rotation_y": ProcessEnum.Y_ROTATION,
            "rotation_z": ProcessEnum.Z_ROTATION,
        }
        point = cls._create_coordinate(element, point_enums)
        if point is None:
            raise ValueError("Element has no (start) point defined")
        end_enums = {
            "x": ProcessEnum.X_COORDINATE_END,
            "y": ProcessEnum.X_COORDINATE_END,
            "z": ProcessEnum.X_COORDINATE_END,
            "rotation_x": ProcessEnum.X_COORDINATE_END,
            "rotation_y": ProcessEnum.Y_COORDINATE_END,
            "rotation_z": ProcessEnum.Z_COORDINATE_END,
        }
        end_point = cls._create_coordinate(element, end_enums)
        if end_point is None:
            return PointLocation(location=point)
        return LineLocation(start=point, end=end_point)

    @classmethod
    def create_dimension(cls, element: "InfrastructureElement") -> Dimension:
        """Erstellt eine Dimension-Komponente für ein Rohr."""
        round_params = [ProcessEnum.DIAMETER, ProcessEnum.RADIUS]
        if any(element.has_param(param) for param in round_params):
            return RoundDimension(element=element)
        return RectangularDimension(element=element)

    @classmethod
    def create_reference(
        cls,
        reference_type: Type["InfrastructureElement"],
        referenced_uuid: UUID,
        bidirectional: bool = False,
    ) -> ElementReference:
        ref_name_prefix = reference_type.__name__
        component_name = f"{ref_name_prefix.lower()}_ref_to_{str(referenced_uuid)}"
        return ElementReference(
            name=component_name,
            referenced_uuid=referenced_uuid,
            reference_type=reference_type,
            bidirectional=bidirectional,
        )
