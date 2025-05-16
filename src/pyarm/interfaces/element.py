"""
Protocols (Interfaces) for the various components of the system.
"""

from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from pyarm.models.process_enums import ElementType, ProcessEnum


@runtime_checkable
class InfraElement(Protocol):
    name: str
    uuid: UUID
    element_type: ElementType


# Capability protocols (for specific functionalities)
@runtime_checkable
class HasClothoid(Protocol):
    """
    Protocol for elements that have clothoid functionality.
    Used for functional classification instead of inheritance.
    """

    @property
    def clothoid_parameter(self) -> float | None:
        """Clothoid parameter"""
        ...

    @property
    def start_radius(self) -> float | None:
        """Start radius"""
        ...

    @property
    def end_radius(self) -> float | None:
        """End radius"""
        ...

    def get_param(self, process_enum: ProcessEnum, default: Any = None) -> Any:
        """
        Returns the value of a parameter based on the process enum.

        Parameters
        ----------
        process_enum: ProcessEnum
            The ProcessEnum of the searched parameter
        default: Any
            Default value if the parameter is not found

        Returns
        -------
        Any
            The value of the parameter or the default value
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the element into a dictionary for serialization.

        Returns
        -------
        dict[str, Any]
            Dictionary with all attributes and parameters
        """
        ...
