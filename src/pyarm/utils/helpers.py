"""
Helper functions for commonly used operations in PyArm.
These functions reduce code duplication and improve maintainability.
"""

import logging
from typing import Any
import uuid

from pyarm.models import units
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum

log = logging.getLogger(__name__)


def create_parameter_from(param_data: dict[str, Any]) -> "Parameter":
    """

    Creates a Parameter object from a dictionary.

    Parameters
    ----------
    param_data: dict[str, Any]
        Dictionary with parameter data

    Returns
    -------
    Parameter
        Parameter object
    """
    name = extract_value(param_data, "name", "", str)
    value = extract_value(param_data, "value")
    datatype = extract_value(param_data, "datatype", expected_type=DataType)
    unit = extract_value(param_data, "unit", default=UnitEnum.NONE, expected_type=UnitEnum)
    process = extract_value(param_data, "process", default=None, expected_type=ProcessEnum)
    components = extract_value(param_data, "components", default=None, expected_type=list)

    return Parameter(
        name=name,
        value=value,
        process=process,
        datatype=datatype,
        unit=unit,
        components=components,
    )


def resolve_element_type(type_str: str) -> ElementType:
    """
    Converts a string to an ElementType enum.

    Parameters
    ----------
    type_str: str
        String representation of the ElementType

    Returns
    -------
    ElementType
        The corresponding ElementType enum or ElementType.NONE if not found
    """
    normalized = type_str.lower().strip()
    try:
        return ElementType(normalized)
    except ValueError as exc:
        log.warning(
            f"Could not resolve ElementType for '{type_str}', using {ElementType.UNDEFINED}", exc
        )
        return ElementType.UNDEFINED


def create_coordinate(
    x: float, y: float, z: float | None = None, suffix: str = ""
) -> list[Parameter]:
    """
    Creates parameters for X, Y, Z coordinates.

    Parameters
    ----------
    x: float
        X-coordinate
    y: float
        Y-coordinate
    z: float | None
        Z-coordinate (optional)
    suffix: str
        Optional suffix for parameter names

    Returns
    -------
    list[Parameter]
        List of parameters for the coordinates
    """
    params = []

    x_name = f"X{suffix}" if suffix else "X"
    x_process = ProcessEnum.X_COORDINATE if not suffix else ProcessEnum.X_COORDINATE_END
    y_name = f"Y{suffix}" if suffix else "Y"
    y_process = ProcessEnum.Y_COORDINATE if not suffix else ProcessEnum.Y_COORDINATE_END
    z_name = f"Z{suffix}" if suffix else "Z"
    z_process = ProcessEnum.Z_COORDINATE if not suffix else ProcessEnum.Z_COORDINATE_END

    data_type = DataType.FLOAT
    unit = UnitEnum.METER

    params.append(Parameter(name=x_name, value=x, datatype=data_type, process=x_process, unit=unit))
    params.append(Parameter(name=y_name, value=y, datatype=data_type, process=y_process, unit=unit))
    if z is not None:
        params.append(
            Parameter(name=z_name, value=z, datatype=data_type, process=z_process, unit=unit)
        )

    return params


def extract_value(
    data: dict[str, Any],
    key: str,
    default: Any = None,
    expected_type: type | None = None,
    unit_conversion: tuple[UnitEnum, UnitEnum] | None = None,
) -> Any:
    """
    Extracts a value from a dictionary with type conversion and unit conversion.

    Parameters
    ----------
    data: dict[str, Any]
        Dictionary with the data
    key: str
        Key for the value to be extracted
    default: Any
        Default value if key is not found
    expected_type: type | None
        Expected type (for conversion)
    unit_conversion: tuple[UnitEnum, UnitEnum] | None
        Tuple (from_unit, to_unit) for unit conversion

    Returns
    -------
    Any
        The extracted value (converted if necessary)
    """
    # Extract value from dictionary, fallback to default value
    value = data.get(key, default)

    # If value is None, return directly
    if value is None:
        return default

    # Type conversion, if type is specified
    if expected_type is not None:
        try:
            if expected_type in (int, float) and isinstance(value, str):
                value = value.replace(",", ".")

            value = expected_type(value)
        except (ValueError, TypeError) as e:
            log.warning(f"Could not convert value '{value}' to type '{expected_type}': {e}")
            return default

    # Unit conversion, if specified
    if unit_conversion and isinstance(value, (int, float)):
        from_unit, to_unit = unit_conversion
        try:
            value = units.convert_unit(value, from_unit, to_unit)
        except ValueError as e:
            log.warning(f"Unit conversion failed: {e}")

    return value


def create_element_data_template(
    name: str, element_type: ElementType, parameters: list[Parameter] | None = None
) -> dict[str, Any]:
    """
    Creates a base dictionary for element data.

    Parameters
    ----------
    name: str
        Name of the element
    element_type: ElementType
        Type of the element
    parameters: list[Parameter] | None
        List of parameters (optional)

    Returns
    -------
    dict[str, Any]
        Dictionary with base element data
    """
    param_templates = []
    for param in parameters or []:
        param_templates.append(
            {
                "name": param.name,
                "value": param.value,
                "datatype": param.datatype,
                "unit": param.unit.value,
                "process": param.process.value if param.process else None,
                "components": param.components if param.components else None,
            }
        )
    return {
        "name": name,
        "uuid": str(uuid.uuid4()),
        "element_type": element_type.value,
        "parameters": param_templates,
    }
