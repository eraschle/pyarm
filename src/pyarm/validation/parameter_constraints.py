"""
Validation rules for parameters based on ProcessEnum.
This file defines the standard validation rules for all parameters.
"""

from typing import Any, Dict, List, Optional

from pyarm.models.parameter import DataType, UnitEnum
from pyarm.models.process_enums import ProcessEnum
from pyarm.validation.schema import Constraint, ConstraintType


class ParameterConstraintDefinition:
    """Definition of validation rules for a parameter."""

    def __init__(
        self,
        data_type: DataType,
        unit: Optional[UnitEnum] = None,
        constraints: Optional[List[Constraint]] = None,
    ):
        self.data_type = data_type
        self.unit = unit
        self.constraints = constraints or []

    def to_dict(self) -> Dict[str, Any]:
        """Converts the definition to a dictionary."""
        result = {
            "data_type": self.data_type.value,
            "constraints": [c.to_dict() for c in self.constraints],
        }
        if self.unit:
            result["unit"] = self.unit.value
        return result


# Standard-Validierungsregeln für alle ProcessEnums
PARAMETER_CONSTRAINTS: Dict[ProcessEnum, ParameterConstraintDefinition] = {
    # Identifikation und Grunddaten
    ProcessEnum.UUID: ParameterConstraintDefinition(
        data_type=DataType.STRING,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.REGEX,
                value=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                message="UUID must be in format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            ),
        ],
    ),
    ProcessEnum.NAME: ParameterConstraintDefinition(
        data_type=DataType.STRING,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_LENGTH,
                value=2,
                message="Name must be at least 2 characters long",
            ),
        ],
    ),
    ProcessEnum.ELEMENT_TYPE: ParameterConstraintDefinition(
        data_type=DataType.STRING,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_LENGTH,
                value=0,
                message="Element type cannot be empty",
            ),
        ],
    ),
    ProcessEnum.DOMAIN: ParameterConstraintDefinition(
        data_type=DataType.STRING,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_LENGTH,
                value=0,
                message="Domain cannot be empty",
            ),
        ],
    ),
    # Koordinaten
    ProcessEnum.X_COORDINATE: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="X coordinate must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.Y_COORDINATE: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Y coordinate must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.Z_COORDINATE: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Z coordinate must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.X_COORDINATE_END: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="END-X coordinate must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.Y_COORDINATE_END: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="END-Y coordinate must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.Z_COORDINATE_END: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="END-Z coordinate must be greater than or equal to 0",
            )
        ],
    ),
    # Abmessungen
    ProcessEnum.LENGTH: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Length must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.WIDTH: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Width must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.HEIGHT: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Height must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.DEPTH: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Depth must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.DIAMETER: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Diameter must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.RADIUS: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Radius must be greater than or equal to 0",
            ),
        ],
    ),
    ProcessEnum.SHAFT_MANHOLE_DIAMETER: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.METER,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Manhole cover diameter must be greater than or equal to 0",
            ),
        ],
    ),
    # Winkel
    ProcessEnum.ANGLE: ParameterConstraintDefinition(
        data_type=DataType.FLOAT,
        unit=UnitEnum.DEGREE,
        constraints=[
            Constraint(
                constraint_type=ConstraintType.MIN_VALUE,
                value=0.0,
                message="Angle must be greater than or equal to 0",
            ),
            Constraint(
                constraint_type=ConstraintType.MAX_VALUE,
                value=360.0,
                message="Angle must not be greater than 360 degrees",
            ),
        ],
    ),
}


def get_parameter_constraints(process_enum: ProcessEnum) -> ParameterConstraintDefinition:
    """
    Returns the validation rules for a parameter.

    Parameters
    ----------
    process_enum : ProcessEnum
        The ProcessEnum of the parameter

    Returns
    -------
    ParameterConstraintDefinition
        The validation rules for the parameter
    """
    if process_enum in PARAMETER_CONSTRAINTS:
        return PARAMETER_CONSTRAINTS[process_enum]

    # Standardwerte für unbekannte ProcessEnums
    if process_enum.name.endswith("_COORDINATE"):
        return ParameterConstraintDefinition(
            data_type=DataType.FLOAT,
            unit=UnitEnum.METER,
            constraints=[],
        )

    # Generischer Fallback
    return ParameterConstraintDefinition(
        data_type=DataType.STRING,
        constraints=[],
    )


def export_constraints_to_json(file_path: str) -> None:
    """
    Exports all validation rules to a JSON file.

    Parameters
    ----------
    file_path : str
        Path to the JSON file
    """
    import json

    constraints_dict = {
        enum.value: definition.to_dict() for enum, definition in PARAMETER_CONSTRAINTS.items()
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(constraints_dict, f, indent=2, ensure_ascii=False)
