from typing import TYPE_CHECKING

from pyarm.components.base import Component, ComponentType
from pyarm.components.descriptor import ParameterDescriptor
from pyarm.models.process_enums import ProcessEnum

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement


class Dimension(Component):
    """Komponente für die Abmessungen eines Elements."""

    width: float = ParameterDescriptor(ProcessEnum.WIDTH)  # pyright: ignore[reportAssignmentType]
    height: float = ParameterDescriptor(ProcessEnum.HEIGHT)  # pyright: ignore[reportAssignmentType]
    depth: float = ParameterDescriptor(ProcessEnum.DEPTH)  # pyright: ignore[reportAssignmentType]
    diameter: float = ParameterDescriptor(ProcessEnum.DIAMETER)  # pyright: ignore[reportAssignmentType]
    radius: float = ParameterDescriptor(ProcessEnum.RADIUS)  # pyright: ignore[reportAssignmentType]
    length: float = ParameterDescriptor(ProcessEnum.LENGTH)  # pyright: ignore[reportAssignmentType]

    def __init__(self, element: "InfrastructureElement"):
        super().__init__(name="dimension", component_type=ComponentType.DIMENSION)
        self.element = element

    @property
    def has_width(self) -> bool:
        """Check if the element of the dimensions has a width.

        Returns:
            bool: True if the element has a width, False otherwise.
        """
        return ProcessEnum.WIDTH in self.element.known_params

    @property
    def has_height(self) -> bool:
        """Check if the element of the dimensions has a height.

        Returns:
            bool: True if the element has a height, False otherwise.
        """
        return ProcessEnum.HEIGHT in self.element.known_params

    @property
    def has_depth(self) -> bool:
        """Check if the element of the dimensions has a depth.

        Returns:
            bool: True if the element has a depth, False otherwise.
        """
        return ProcessEnum.DEPTH in self.element.known_params

    @property
    def has_length(self) -> bool:
        """Check if the element of the dimensions has a length.

        Returns:
            bool: True if the element has a length, False otherwise.
        """
        return ProcessEnum.LENGTH in self.element.known_params

    @property
    def has_diameter(self) -> bool:
        """Check if the element of the dimensions has a diameter.
        Returns:
            bool: True if the element has a diameter, False otherwise.
        """
        return ProcessEnum.DIAMETER in self.element.known_params

    @property
    def has_radius(self) -> bool:
        """Check if the element of the dimensions has a radius.

        Returns:
            bool: True if the element has a radius, False otherwise.
        """
        return ProcessEnum.RADIUS in self.element.known_params

    def __str__(self) -> str:
        dimensions = []
        if self.has_length:
            dimensions.append(f"L={self.length:.2f}")
        if self.has_width:
            dimensions.append(f"B={self.width:.2f}")
        if self.has_diameter:
            dimensions.append(f"D={self.diameter:.2f}")
        if self.has_radius:
            dimensions.append(f"R={self.radius:.2f}")
        if self.has_height:
            dimensions.append(f"H={self.height:.2f}")
        if self.has_depth:
            dimensions.append(f"T={self.depth:.2f}")

        return ", ".join(dimensions) if dimensions else "keine Dimensionen"
