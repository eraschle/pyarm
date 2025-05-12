import abc
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from pyarm.components.base import Component, ComponentType
from pyarm.components.descriptor import AComponentDescriptor
from pyarm.models.process_enums import ProcessEnum
from pyarm.utils import coordinate as cs

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement

log = logging.getLogger(__name__)


class CoordinateDescriptor(AComponentDescriptor):
    def __init__(self, element_attr: str = "element") -> None:
        super().__init__(element_attr)

    # def _get_parameter(self, instance: Any) -> "Parameter":
    #     element = self._get_element(instance)
    #     process_enum = self._get_process_enum(instance)
    #     if process_enum not in element.known_params:
    #         from pyarm.models.parameter import Parameter

    #         unit = UnitEnum.METER
    #         if process_enum in [
    #             ProcessEnum.ROTATION_X,
    #             ProcessEnum.ROTATION_Y,
    #             ProcessEnum.ROTATION_Z,
    #         ]:
    #             unit = UnitEnum.DEGREE
    #         param = Parameter(
    #             name=self.name,
    #             value=0.0,
    #             process=process_enum,
    #             datatype="float",
    #             unit=unit,
    #         )
    #         element.set_param(process_enum=process_enum, value=param)
    #     return element.get_param(process_enum)

    def __set_name__(self, owner: Any, name: str) -> None:
        log.debug(f"Setting name {name} for {owner.__name__}")
        self.name = name

    def _get_process_enum(self, instance: Any) -> ProcessEnum:
        if not isinstance(instance, Coordinate):
            raise TypeError(f"{self.name} must be defined in a Coordinate class")
        process_param = instance.attr_map.get(self.name)
        if process_param is None:
            raise AttributeError(f"Unknown attribute {self.name}")
        return process_param


class Coordinate:
    """Komponente für die Position eines Elements im Raum."""

    x: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]
    y: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]
    z: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]
    rotation_x: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]
    rotation_y: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]
    rotation_z: float = CoordinateDescriptor()  # pyright: ignore[reportAssignmentType]

    def __init__(self, element: "InfrastructureElement", attr_map: dict[str, ProcessEnum]):
        self.element = element
        self.attr_map = attr_map

    def distance_to(self, other: "Coordinate") -> float:
        """Berechnet die Distanz zu einem anderen Koordinatenpunkt."""
        distance = cs.calculate_length(self.as_tuple(), other.as_tuple())
        return float("inf") if distance is None else distance

    def as_tuple(self) -> tuple[float, ...]:
        return self.x, self.y, self.z

    def __str__(self) -> str:
        return f"Coordinate(x={self.x}, y={self.y}, z={self.z})"


@dataclass
class Location(Component):
    name: str = field(init=False)
    component_type: ComponentType = field(init=False, repr=False)

    def __post_init__(self):
        self.name = "location"
        self.component_type = ComponentType.LOCATION

    @property
    @abc.abstractmethod
    def point(self) -> Coordinate:
        """Returns the coordinates of the point."""
        pass

    @property
    def end_point(self) -> Coordinate:
        """
        Returns the coordinates of the end point. If the location is not a line,
        this will return the same as the point property.
        """
        raise NotImplementedError("Component does not have an end point")

    @property
    def has_end_point(self) -> bool:
        """
        Checks if the location is of line based elements with a start and end point.

        Returns
        -------
        bool
            True if the location has an end point, otherwise False
        """
        try:
            end_point = self.end_point
            return end_point is not None
        except NotImplementedError:
            return False

    @property
    def distance(self) -> float:
        """Returns the distance to the end point if available, otherwise to itself."""
        if self.has_end_point:
            return self.point.distance_to(self.end_point)
        return 0.0

    def as_tuple(self, flatten: bool = False) -> tuple:
        if self.has_end_point:
            if flatten:
                return self.point.as_tuple() + self.end_point.as_tuple()
            return self.point.as_tuple(), self.end_point.as_tuple()
        return self.point.as_tuple()

    def __str__(self) -> str:
        if self.has_end_point:
            return f"{self.point} -> {self.end_point}"
        return str(self.point)


@dataclass
class PointLocation(Location, Component):
    location: Coordinate

    @property
    def point(self) -> Coordinate:
        return self.location


@dataclass
class LineLocation(Location, Component):
    """Komponente für linienförmige Elemente mit Start- und Endpunkt."""

    start: Coordinate
    end: Coordinate

    @property
    def point(self) -> Coordinate:
        return self.start

    @property
    def end_point(self) -> Coordinate:
        return self.end
