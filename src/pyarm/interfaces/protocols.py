"""
Protocols (Interfaces) for the various components of the system.
"""

from typing import Any, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType, ProcessEnum

# Type variables for generic protocols
T = TypeVar("T", covariant=True)
TElement = TypeVar("TElement", bound=InfrastructureElement)


# Reader protocols
@runtime_checkable
class IDataReader(Protocol):
    """
    Protocol for components that can read data from a source.
    Different data sources implement this protocol.
    """

    @property
    def name(self) -> str:
        """Name of the reader"""
        ...

    @property
    def version(self) -> str:
        """Version of the reader"""
        ...

    @property
    def supported_formats(self) -> list[str]:
        """List of supported file formats"""
        ...

    def can_handle(self, file_path: str) -> bool:
        """
        Checks if this reader can handle the specified file.

        Parameters
        ----------
        file_path: str
            Path to the file

        Returns
        -------
        bool
            True if this reader can handle the file
        """
        ...

    def read_data(self, file_path: str) -> dict[str, Any]:
        """
        Reads data from the specified file.

        Parameters
        ----------
        file_path: str
            Path to the file

        Returns
        -------
        dict[str, Any]
            Dictionary with the read data
        """
        ...


# Converter protocols
@runtime_checkable
class IDataConverter(Protocol[T]):
    """
    Protocol for components that can convert data to another format.
    """

    @property
    def name(self) -> str:
        """Name of the converter"""
        ...

    @property
    def version(self) -> str:
        """Version of the converter"""
        ...

    @property
    def supported_types(self) -> list[str]:
        """List of supported data types"""
        ...

    def can_convert(self, data: dict[str, Any]) -> bool:
        """
        Checks if this converter can convert the specified data.

        Parameters
        ----------
        data: dict[str, Any]
            Data to be converted

        Returns
        -------
        bool
            True if this converter can convert the data
        """
        ...

    def convert(self, data: dict[str, Any]) -> T:
        """
        Converts the specified data.

        Parameters
        ----------
        data: dict[str, Any]
            Data to be converted

        Returns
        -------
        T
            Converted data
        """
        ...


# Repository protocols
@runtime_checkable
class IElementRepository(Protocol):
    """
    Protocol for components that can store and retrieve elements.
    """

    def get_all(self) -> list[InfrastructureElement]:
        """
        Retrieves all elements.

        Returns
        -------
        list[InfrastructureElement]
            List of all elements
        """
        ...

    def get_by_id(self, uuid: UUID | str) -> InfrastructureElement | None:
        """
        Retrieves an element by its UUID.

        Parameters
        ----------
        uuid: UUID | str
            UUID of the element

        Returns
        -------
        InfrastructureElement | None
            The found element or None
        """
        ...

    def get_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        """
        Retrieves elements of a specific type.

        Parameters
        ----------
        element_type: ElementType
            Type of elements to retrieve

        Returns
        -------
        list[InfrastructureElement]
            List of found elements
        """
        ...

    def save(self, element: InfrastructureElement) -> None:
        """
        Saves an element.

        Parameters
        ----------
        element: InfrastructureElement
            Element to be saved
        """
        ...

    def save_all(self, elements: list[InfrastructureElement]) -> None:
        """
        Saves multiple elements.

        Parameters
        ----------
        elements: list[InfrastructureElement]
            Elements to be saved
        """
        ...

    def delete(self, uuid: UUID | str) -> None:
        """
        Deletes an element.

        Parameters
        ----------
        uuid: UUID | str
            UUID of the element to be deleted
        """
        ...


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
