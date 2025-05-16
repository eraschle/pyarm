"""
Interfaces for the validation system.

This module defines the protocols (interfaces) used for the validation system.
"""

from typing import Protocol

from pyarm.interfaces.component import IComponentModel
from pyarm.validation.errors import ValidationResult


class IValidator[TElement: IComponentModel](Protocol):
    """
    Protocol for components that can validate data.
    """

    def can_validate(self, element: TElement) -> bool:
        """
        Checks if this validator can validate the specified element type.

        Parameters
        ----------
        element : TElement
            The element to validate

        Returns
        -------
        bool
            True if this validator can validate the element type
        """
        ...

    def validate(self, element: TElement) -> ValidationResult:
        """
        Validates instance data for specific Process.

        Parameters
        ----------
        element : TElement
            The element to validate

        Returns
        -------
        ValidationResult
            The validation result
        """
        ...
