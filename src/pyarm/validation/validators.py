"""
Validators for the validation system.

This module contains implementations of validators for various
element types and a generic validator that serves as a base for specific
validators.
"""

import abc
import logging
from typing import Any, Dict, List, Optional

from pyarm.models.parameter import DataType, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.errors import (
    ErrorSeverity,
    ValidationError,
    ValidationResult,
    ValidationWarning,
)
from pyarm.validation.interfaces import IValidator
from pyarm.validation.schema import Constraint, ConstraintType, SchemaDefinition

log = logging.getLogger(__name__)


class GenericValidator(abc.ABC, IValidator):
    """
    Base class for validators that provides general validation functionality.
    """

    def __init__(self, element_types: List[ElementType]):
        """
        Initializes the validator.

        Parameters
        ----------
        element_types : List[ElementType]
            The supported element types
        """
        self._element_types = element_types
        self._schemas: Dict[ElementType, SchemaDefinition] = {}

    @property
    def supported_element_types(self) -> List[ElementType]:
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
        try:
            element_enum = ElementType(element_type)
            return element_enum in self._element_types
        except ValueError:
            return False

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
        result = ValidationResult()

        try:
            element_enum = ElementType(element_type)
        except ValueError:
            result.add_error(
                ValidationError(
                    message=f"Invalid element type: {element_type}",
                    context={"element_type": element_type},
                    severity=ErrorSeverity.CRITICAL,
                )
            )
            return result

        # Prüfen, ob ein Schema für diesen Elementtyp registriert ist
        schema = self._schemas.get(element_enum)
        if not schema:
            result.add_warning(
                ValidationWarning(
                    message=f"No validation schema registered for element type {element_type}",
                    context={"element_type": element_type},
                )
            )
            return result

        # Basis-Struktur prüfen
        if not isinstance(data, dict):
            result.add_error(
                ValidationError(
                    message="Data must be a dictionary",
                    context={"data_type": type(data).__name__},
                    severity=ErrorSeverity.CRITICAL,
                    element_type=element_type,
                )
            )
            return result

        # Element-ID extrahieren für Fehlermeldungen
        element_id = data.get("id", data.get("uuid", data.get("ID", None)))

        # Parameter validieren
        params_data = data.get("parameters", [])
        if not isinstance(params_data, list):
            # Wenn die Daten flach sind (nicht in einer parameters-Liste),
            # verwenden wir die Daten direkt
            params_data = [{"name": k, "value": v} for k, v in data.items()]

        # Parameter in ein Dictionary umwandeln für einfacheren Zugriff
        params_dict: Dict[str, Dict[str, Any]] = {}
        for param in params_data:
            if not isinstance(param, dict):
                continue
            param_name = param.get("name")
            if not param_name:
                continue
            params_dict[param_name] = param

        # Alle erforderlichen Parameter und ihre Constraints prüfen
        for param_enum, constraints in schema.constraints.items():
            param_name = param_enum.value

            # Parameter-Wert suchen
            param_value = None
            param_data = params_dict.get(param_name)

            if param_data:
                param_value = param_data.get("value")

            # Alle Constraints für diesen Parameter prüfen
            for constraint in constraints:
                if not constraint.validate(param_value):
                    error_message = constraint.get_error_message(param_name, param_value)

                    # Bestimmen des Schweregrads basierend auf dem Constraint-Typ
                    severity = ErrorSeverity.ERROR
                    if constraint.constraint_type == ConstraintType.REQUIRED:
                        severity = ErrorSeverity.CRITICAL

                    result.add_error(
                        ValidationError(
                            message=error_message,
                            context={"param_name": param_name, "value": param_value},
                            severity=severity,
                            element_type=element_type,
                            element_id=element_id,
                            parameter_name=param_name,
                        )
                    )

        # Zusätzliche spezifische Validierung durchführen
        self._validate_specific(data, element_enum, result, element_id)

        return result

    @abc.abstractmethod
    def _validate_specific(
        self,
        data: Dict[str, Any],
        element_type: ElementType,
        result: ValidationResult,
        element_id: Optional[str] = None,
    ) -> None:
        """
        Performs specific validation for the given element type.
        This method can be overridden by derived classes.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to validate
        element_type : ElementType
            The element type
        result : ValidationResult
            The validation result to which errors and warnings can be added
        element_id : Optional[str]
            The ID of the element, if available
        """
        pass


class ElementValidator(GenericValidator):
    """
    Validation class for InfrastructureElement objects.
    """

    def __init__(self, element_type: ElementType):
        super().__init__([element_type])

        # Standard-Schema für diesen Elementtyp erstellen und registrieren
        schema = self._create_default_schema(element_type)
        self.register_schema(schema)

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

        # Standort-Parameter (für geometrische Validierung)
        schema.required_params.update(
            {
                ProcessEnum.X_COORDINATE,
                ProcessEnum.Y_COORDINATE,
            }
        )

        # Typdefinitionen
        schema.param_types.update(
            {
                ProcessEnum.UUID: DataType.STRING,
                ProcessEnum.NAME: DataType.STRING,
                ProcessEnum.ELEMENT_TYPE: DataType.STRING,
                ProcessEnum.X_COORDINATE: DataType.FLOAT,
                ProcessEnum.Y_COORDINATE: DataType.FLOAT,
                ProcessEnum.Z_COORDINATE: DataType.FLOAT,
            }
        )

        # Einheitendefinitionen
        schema.param_units.update(
            {
                ProcessEnum.X_COORDINATE: UnitEnum.METER,
                ProcessEnum.Y_COORDINATE: UnitEnum.METER,
                ProcessEnum.Z_COORDINATE: UnitEnum.METER,
            }
        )
        # Minimumwerte für Dimensionen
        schema.add_constraint(
            ProcessEnum.X_COORDINATE,
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Width must be greater than 0",
            ),
        )
        schema.add_constraint(
            ProcessEnum.Y_COORDINATE,
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Height must be greater than 0",
            ),
        )
        schema.add_constraint(
            ProcessEnum.Z_COORDINATE,
            Constraint(
                constraint_type=ConstraintType.CUSTOM,
                message="Z-Coordinate is optional but must be greater than 0",
                custom_validator=lambda x: x is None or x > 0,
            ),
        )

        # Elementtyp-spezifische Parameter hinzufügen
        self._add_element_specific_constraints(element_type, schema)

        return schema

    def _add_element_specific_constraints(
        self, element_type: ElementType, schema: SchemaDefinition
    ) -> None:
        """
        Adds element type-specific constraints to the schema.
        This method can be overridden by derived classes.

        Parameters
        ----------
        element_type : ElementType
            The element type
        schema : SchemaDefinition
            The schema to which constraints should be added
        """
        # Gemeinsame Dimensionsparameter
        if element_type in [ElementType.FOUNDATION, ElementType.MAST]:
            schema.required_params.update(
                {
                    ProcessEnum.WIDTH,
                    ProcessEnum.HEIGHT,
                    ProcessEnum.DEPTH,
                }
            )
            schema.param_types.update(
                {
                    ProcessEnum.WIDTH: DataType.FLOAT,
                    ProcessEnum.HEIGHT: DataType.FLOAT,
                    ProcessEnum.DEPTH: DataType.FLOAT,
                }
            )
            schema.param_units.update(
                {
                    ProcessEnum.WIDTH: UnitEnum.METER,
                    ProcessEnum.HEIGHT: UnitEnum.METER,
                    ProcessEnum.DEPTH: UnitEnum.METER,
                }
            )

            # Minimumwerte für Dimensionen
            schema.add_constraint(
                ProcessEnum.WIDTH,
                Constraint(
                    constraint_type=ConstraintType.MIN_VALUE,
                    value=0.0,
                    message="Width must be greater than 0",
                ),
            )
            schema.add_constraint(
                ProcessEnum.HEIGHT,
                Constraint(
                    constraint_type=ConstraintType.MIN_VALUE,
                    value=0.0,
                    message="Height must be greater than 0",
                ),
            )
            schema.add_constraint(
                ProcessEnum.DEPTH,
                Constraint(
                    constraint_type=ConstraintType.MIN_VALUE,
                    value=0.0,
                    message="Depth must be greater than 0",
                ),
            )

        # Spezifische Parameter für Linienelemente
        if element_type in [ElementType.TRACK, ElementType.SEWER_PIPE]:
            schema.required_params.update(
                {
                    ProcessEnum.X_COORDINATE_END,
                    ProcessEnum.Y_COORDINATE_END,
                    ProcessEnum.Z_COORDINATE_END,
                }
            )
            schema.param_types.update(
                {
                    ProcessEnum.X_COORDINATE_END: DataType.FLOAT,
                    ProcessEnum.Y_COORDINATE_END: DataType.FLOAT,
                    ProcessEnum.Z_COORDINATE_END: DataType.FLOAT,
                }
            )
            schema.param_units.update(
                {
                    ProcessEnum.X_COORDINATE_END: UnitEnum.METER,
                    ProcessEnum.Y_COORDINATE_END: UnitEnum.METER,
                    ProcessEnum.Z_COORDINATE_END: UnitEnum.METER,
                }
            )
            # Minimumwerte für Dimensionen
            schema.add_constraint(
                ProcessEnum.X_COORDINATE_END,
                Constraint(
                    constraint_type=ConstraintType.MIN_VALUE,
                    value=0.0,
                    message="Width must be greater than 0",
                ),
            )
            schema.add_constraint(
                ProcessEnum.X_COORDINATE_END,
                Constraint(
                    constraint_type=ConstraintType.MIN_VALUE,
                    value=0.0,
                    message="Height must be greater than 0",
                ),
            )
            schema.add_constraint(
                ProcessEnum.X_COORDINATE_END,
                Constraint(
                    constraint_type=ConstraintType.CUSTOM,
                    message="Z-Coordinate is optional but must be greater than 0",
                    custom_validator=lambda x: x is None or x > 0,
                ),
            )

        # Spezifische Parameter für Fundamenttypen
        if element_type == ElementType.FOUNDATION:
            schema.required_params.add(ProcessEnum.FOUNDATION_TYPE)
            schema.param_types[ProcessEnum.FOUNDATION_TYPE] = DataType.STRING

        # Spezifische Parameter für Masttypen
        if element_type == ElementType.MAST:
            schema.required_params.add(ProcessEnum.MAST_TYPE)
            schema.param_types[ProcessEnum.MAST_TYPE] = DataType.STRING

    def _validate_specific(
        self,
        data: Dict[str, Any],
        element_type: ElementType,
        result: ValidationResult,
        element_id: Optional[str] = None,
    ) -> None:
        """
        Performs specific validation for the given element type.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to validate
        element_type : ElementType
            The element type
        result : ValidationResult
            The validation result to which errors and warnings can be added
        element_id : Optional[str]
            The ID of the element, if available
        """
        # Beispiel für eine spezifische Validierung:
        # Prüfen, ob Linienelemente Start- und Endpunkt unterscheiden
        if element_type in [ElementType.TRACK, ElementType.SEWER_PIPE]:
            # Parameter extrahieren
            params = data.get("parameters", [])

            # Koordinaten suchen
            x, y, z = None, None, None
            x_end, y_end, z_end = None, None, None

            for param in params:
                if isinstance(param, dict):
                    process = param.get("process")
                    value = param.get("value")

                    if process == ProcessEnum.X_COORDINATE.value:
                        x = value
                    elif process == ProcessEnum.Y_COORDINATE.value:
                        y = value
                    elif process == ProcessEnum.Z_COORDINATE.value:
                        z = value
                    elif process == ProcessEnum.X_COORDINATE_END.value:
                        x_end = value
                    elif process == ProcessEnum.Y_COORDINATE_END.value:
                        y_end = value
                    elif process == ProcessEnum.Z_COORDINATE_END.value:
                        z_end = value

            # Wenn Start- und Endpunkt identisch sind, ist das verdächtig
            if (
                x is not None
                and y is not None
                and z is not None
                and x_end is not None
                and y_end is not None
                and z_end is not None
            ):
                if x == x_end and y == y_end and z == z_end:
                    result.add_warning(
                        ValidationWarning(
                            message="Start and end points are identical",
                            context={"start": (x, y, z), "end": (x_end, y_end, z_end)},
                            element_type=element_type.value,
                            element_id=element_id,
                        )
                    )

        # Hier können weitere elementtyp-spezifische Validierungen hinzugefügt werden
