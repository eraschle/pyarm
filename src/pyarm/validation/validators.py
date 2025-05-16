"""
Validators for the validation system.

This module contains implementations of validators for various
element types and a generic validator that serves as a base for specific
validators.
"""

import abc
import logging
from typing import Optional

from pyarm.interfaces.validator import IValidator
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.parameter import Parameter
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.errors import (
    ErrorSeverity,
    ValidationError,
    ValidationResult,
    ValidationWarning,
)
from pyarm.validation.parameter_constraints import get_parameter_constraints
from pyarm.validation.schema import ConstraintType, SchemaDefinition


log = logging.getLogger(__name__)


class ParameterValidator(IValidator[Parameter]):
    """Validator für Parameter basierend auf den definierten Validierungsregeln."""

    def can_validate(self, element: Parameter) -> bool:
        return super().can_validate(element)

    def validate(self, element: Parameter) -> ValidationResult:
        """
        Validiert einen Parameter basierend auf den definierten Regeln.

        Parameters
        ----------
        param : Parameter
            Der zu validierende Parameter
        process_name : Optional[str], optional
            Name des Prozesses, falls prozessspezifische Regeln angewendet werden sollen

        Returns
        -------
        ValidationResult
            Das Ergebnis der Validierung
        """
        result = ValidationResult()

        if element.process is None:
            # Keine Validierung für Parameter ohne ProcessEnum
            return result

        # Validierungsregeln abrufen
        constraint_def = get_parameter_constraints(element.process)

        # Datentyp prüfen
        if element.datatype != constraint_def.data_type:
            result.add_error(
                ValidationError(
                    message=f"Parameter {element.name} hat falschen Datentyp: "
                    f"{element.datatype.value}, erwartet: {constraint_def.data_type.value}",
                    severity=ErrorSeverity.ERROR,
                    parameter_name=element.name,
                )
            )

        # Einheit prüfen, falls definiert
        if constraint_def.unit and element.unit != constraint_def.unit:
            result.add_error(
                ValidationError(
                    message=f"Parameter {element.name} hat falsche Einheit: "
                    f"{element.unit.value}, erwartet: {constraint_def.unit.value}",
                    severity=ErrorSeverity.WARNING,
                    parameter_name=element.name,
                )
            )

        # Constraints prüfen
        for constraint in constraint_def.constraints:
            if not constraint.validate(element.value):
                result.add_error(
                    ValidationError(
                        message=constraint.get_error_message(element.name, element.value),
                        severity=ErrorSeverity.ERROR,
                        parameter_name=element.name,
                    )
                )

        return result


class GenericValidator[TElement: InfrastructureElement](abc.ABC, IValidator[TElement]):
    """
    Base class for validators that provides general validation functionality.
    """

    def __init__(self, element_types: list[ElementType]):
        """
        Initializes the validator.

        Parameters
        ----------
        element_types : list[ElementType]
            The supported element types
        """
        self._element_types = element_types
        self._schemas: dict[ElementType, SchemaDefinition] = {}

    @property
    def supported_element_types(self) -> list[ElementType]:
        """Returns the supported element types."""
        return self._element_types

    def register_schema(self, schema: SchemaDefinition) -> None:
        """
        Registers a schema for an element type.

        Parameters
        ----------
        schema : SchemaDefinition
            The schema to register
        """
        self._schemas[schema.element_type] = schema

    def can_validate(self, element: TElement) -> bool:
        try:
            element_enum = element.element_type
            return element_enum in self._element_types
        except ValueError:
            return False

    def validate(self, element: TElement) -> ValidationResult:
        result = ValidationResult()

        element_type = element.element_type
        # Prüfen, ob ein Schema für diesen Elementtyp registriert ist
        schema = self._schemas.get(element_type)
        if not schema:
            result.add_warning(
                ValidationWarning(
                    message=f"No validation schema registered for element type {element_type}",
                    context={"element_type": element_type},
                )
            )
            return result

        # Basis-Struktur prüfen
        if not isinstance(element, InfrastructureElement):
            result.add_error(
                ValidationError(
                    message="Data must be a dictionary",
                    context={"data_type": type(element).__name__},
                    severity=ErrorSeverity.CRITICAL,
                    element_type=element_type,
                )
            )
            return result

        # Element-ID extrahieren für Fehlermeldungen
        element_info = f"{element.name} [{element.uuid}]"
        # Alle erforderlichen Parameter und ihre Constraints prüfen
        for process_enum, constraints in schema.constraints.items():
            param_name = process_enum.value
            # Parameter-Wert suchen
            if not element.has_param(process_enum):
                result.add_error(
                    ValidationError(
                        message=f"Parameter with ProcessEnum {param_name} not found",
                        context={"process_enum": param_name},
                        severity=ErrorSeverity.ERROR,
                        element_type=element_type,
                        element_id=element_info,
                        parameter_name=param_name,
                    )
                )
            parameter = element.get_param(process_enum)
            # Alle Constraints für diesen Parameter prüfen
            for constraint in constraints:
                if not constraint.validate(parameter.value):
                    error_message = constraint.get_error_message(param_name, parameter.value)

                    # Bestimmen des Schweregrads basierend auf dem Constraint-Typ
                    severity = ErrorSeverity.ERROR
                    if constraint.constraint_type == ConstraintType.REQUIRED:
                        severity = ErrorSeverity.CRITICAL

                    result.add_error(
                        ValidationError(
                            message=error_message,
                            context={"param_name": param_name, "value": parameter.value},
                            severity=severity,
                            element_type=element_type,
                            element_id=element_info,
                            parameter_name=param_name,
                        )
                    )

        # Zusätzliche spezifische Validierung durchführen
        self._validate_specific(element, result)

        return result

    def _create_default_schema(self, element_type: ElementType) -> SchemaDefinition:
        """
        Creates a default schema for the specified element type.

        Parameters
        ----------
        element_type : ElementType
            The element type for which to create the schema

        Returns
        -------
        SchemaDefinition
            The created schema
        """
        schema = SchemaDefinition(element_type=element_type)

        # Allgemeine erforderliche Parameter für alle Elementtypen
        schema.required_params = {
            ProcessEnum.UUID,
            ProcessEnum.NAME,
            ProcessEnum.ELEMENT_TYPE,
        }

        return schema
