from typing import TYPE_CHECKING

from pyarm.components.base import Component, ComponentType
from pyarm.components.descriptor import ParameterDescriptor
from pyarm.models.process_enums import ProcessEnum

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement


class Dimension(Component):
    """Komponente für die Abmessungen eines Elements."""

    height: float = ParameterDescriptor(ProcessEnum.HEIGHT)  # pyright: ignore[reportAssignmentType]
    length: float = ParameterDescriptor(ProcessEnum.LENGTH)  # pyright: ignore[reportAssignmentType]

    def __init__(self, element: "InfrastructureElement"):
        super().__init__(name="dimension", component_type=ComponentType.DIMENSION)
        self.element = element

    def _has_process_enum(self, process_enum: ProcessEnum) -> bool:
        """Check if the element of the dimensions has a specific process enum
        and its value is greater than 0.

        Args:
            process_enum (ProcessEnum): The process enum to check.

        Returns:
            bool: True if the element has the specified process enum, False otherwise.
        """
        if not self.element.has_param(process_enum):
            return False
        return self.element.get_param(process_enum).value > 0

    @property
    def has_height(self) -> bool:
        """Check if the element of the dimensions has a height.

        Returns:
            bool: True if the element has a height, False otherwise.
        """
        return self._has_process_enum(ProcessEnum.HEIGHT)

    @property
    def has_length(self) -> bool:
        """Check if the element of the dimensions has a length.

        Returns:
            bool: True if the element has a length, False otherwise.
        """
        return self._has_process_enum(ProcessEnum.LENGTH)


class RectangularDimension(Dimension):
    """Komponente für die Abmessungen eines Elements."""

    width: float = ParameterDescriptor(ProcessEnum.WIDTH)  # pyright: ignore[reportAssignmentType]
    depth: float = ParameterDescriptor(ProcessEnum.DEPTH)  # pyright: ignore[reportAssignmentType]

    @property
    def has_width(self) -> bool:
        """Check if the element of the dimensions has a width.

        Returns:
            bool: True if the element has a width, False otherwise.
        """
        return ProcessEnum.WIDTH in self.element.known_params

    @property
    def has_depth(self) -> bool:
        """Check if the element of the dimensions has a depth.

        Returns:
            bool: True if the element has a depth, False otherwise.
        """
        return ProcessEnum.DEPTH in self.element.known_params


class RoundDimension(Dimension):
    """Komponente für die Abmessungen eines Elements."""

    diameter: float = ParameterDescriptor(ProcessEnum.DIAMETER)  # pyright: ignore[reportAssignmentType]
    radius: float = ParameterDescriptor(ProcessEnum.RADIUS)  # pyright: ignore[reportAssignmentType]
    slope: float = ParameterDescriptor(ProcessEnum.SLOPE)  # pyright: ignore[reportAssignmentType]

    @property
    def has_diameter(self) -> bool:
        """Check if the element of the dimensions has a diameter.
        Returns:
            bool: True if the element has a diameter, False otherwise.
        """
        return self._has_process_enum(ProcessEnum.DIAMETER)

    @property
    def has_radius(self) -> bool:
        """Check if the element of the dimensions has a radius.

        Returns:
            bool: True if the element has a radius, False otherwise.
        """
        return self._has_process_enum(ProcessEnum.RADIUS)

    @property
    def has_slope(self) -> bool:
        """Check if the element of the dimensions has a slope.

        Returns:
            bool: True if the element has a slope, False otherwise.
        """
        return self._has_process_enum(ProcessEnum.SLOPE)
