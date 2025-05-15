from typing import Optional, Protocol, Union
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType


class IElementRepository(Protocol):
    """
    Repository for storing infrastructure elements.
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

    def get_by_id(self, uuid: Union[UUID, str]) -> Optional[InfrastructureElement]:
        """
        Retrieves an element by its UUID.

        Parameters
        ----------
        uuid: Union[UUID, str]
            UUID of the element

        Returns
        -------
        Optional[InfrastructureElement]
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

    def delete(self, uuid: Union[UUID, str]) -> None:
        """
        Deletes an element.

        Parameters
        ----------
        uuid: Union[UUID, str]
            UUID of the element to be deleted
        """
        ...

    def clear(self) -> None:
        """
        Deletes all elements.
        """
        ...

    def backup(self) -> str:
        """
        Creates a backup of the repository.

        Returns
        -------
        str
            Path to the backup directory
        """
        ...
