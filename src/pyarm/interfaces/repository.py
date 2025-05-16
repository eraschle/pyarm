"""
Protocols (Interfaces) for the various components of the system.
"""

from typing import Protocol, TypeVar, runtime_checkable
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType

TElement = TypeVar("TElement", bound=InfrastructureElement)


# Repository protocols
@runtime_checkable
class IElementRepository(Protocol[TElement]):
    """
    Protocol for components that can store and retrieve elements.
    """

    def get_all(self) -> list[TElement]:
        """
        Retrieves all elements.

        Returns
        -------
        list[InfrastructureElement]
            List of all elements
        """
        ...

    def get_by_id(self, uuid: UUID | str) -> TElement | None:
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

    def get_by_type(self, element_type: ElementType) -> list[TElement]:
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

    def save(self, element: TElement) -> None:
        """
        Saves an element.

        Parameters
        ----------
        element: InfrastructureElement
            Element to be saved
        """
        ...

    def save_all(self, elements: list[TElement]) -> None:
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
