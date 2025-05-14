"""
Interfaces for the validation system.

This module defines the protocols (interfaces) used for the validation system.
"""

from typing import Any, Dict, List, Protocol, runtime_checkable

from pyarm.models.process_enums import ElementType
from pyarm.validation.errors import ValidationResult


@runtime_checkable
class IValidator(Protocol):
    """
    Protocol for components that can validate data.
    """

    @property
    def supported_element_types(self) -> List[ElementType]:
        """Returns the supported element types."""
        ...

    def can_validate(self, element_type: str) -> bool:
        """
        Checks if this validator can validate the specified element type.

        Parameters
        ----------
        element_type : str
            The element type to check

        Returns
        -------
        bool
            True if this validator can validate the element type
        """
        ...

    def validate(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        """
        Validates data for the specified element type.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to validate
        element_type : str
            The element type

        Returns
        -------
        ValidationResult
            The validation result
        """
        ...


@runtime_checkable
class IValidationService(Protocol):
    """
    Protocol for a service that coordinates and performs validation.
    """

    def register_validator(self, validator: IValidator) -> None:
        """
        Registers a validator with the service.

        Parameters
        ----------
        validator : IValidator
            The validator to register
        """
        ...

    def validate_element(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        """
        Validates a single element.

        Parameters
        ----------
        data : Dict[str, Any]
            The element data to validate
        element_type : str
            The element type

        Returns
        -------
        ValidationResult
            The validation result
        """
        ...

    def validate_collection(
        self, data: List[Dict[str, Any]], element_type: str
    ) -> List[ValidationResult]:
        """
        Validates a collection of elements.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            The elements to validate
        element_type : str
            The element type

        Returns
        -------
        List[ValidationResult]
            The validation results for each element
        """
        ...
        
    def create_validation_report(
        self, element_type: str, results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """
        Creates a detailed validation report.

        Parameters
        ----------
        element_type : str
            The element type
        results : List[ValidationResult]
            The validation results

        Returns
        -------
        Dict[str, Any]
            Detailed validation report
        """
        ...
