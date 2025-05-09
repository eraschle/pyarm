"""
Helper functions for commonly used operations in PyArm.
These functions reduce code duplication and improve maintainability.
"""

import logging
from typing import Any

from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum

logger = logging.getLogger(__name__)


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

    return Parameter(
        name=name,
        value=value,
        process=process,
        datatype=datatype,
        unit=unit,
    )


def convert_unit(value: int | float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """
    Converts a value from one unit to another.

    Parameters
    ----------
    value: int | float
        The value to be converted
    from_unit: UnitEnum
        Source unit
    to_unit: UnitEnum
        Target unit

    Returns
    -------
    float
        The converted value

    Raises
    ------
    ValueError
        If the conversion is not supported
    """
    # Length units
    length_conversions = {
        (UnitEnum.MILLIMETER, UnitEnum.METER): lambda x: x / 1000,
        (UnitEnum.METER, UnitEnum.MILLIMETER): lambda x: x * 1000,
        (UnitEnum.CENTIMETER, UnitEnum.METER): lambda x: x / 100,
        (UnitEnum.METER, UnitEnum.CENTIMETER): lambda x: x * 100,
    }

    # If units are the same, no conversion necessary
    if from_unit == to_unit:
        return float(value)

    # Look up conversion
    conversion_key = (from_unit, to_unit)
    if conversion_key in length_conversions:
        return length_conversions[conversion_key](value)

    # Unsupported conversion
    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not supported")


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
    # Normalize and map common variants
    normalized = type_str.lower().strip()

    mappings = {
        "mast": ElementType.MAST,
        "pole": ElementType.MAST,
        "fundament": ElementType.FOUNDATION,
        "foundation": ElementType.FOUNDATION,
        "joch": ElementType.JOCH,
        "yoke": ElementType.JOCH,
        "drainage": ElementType.DRAINAGE_PIPE,
        "drainagepipe": ElementType.DRAINAGE_PIPE,
        "pipe": ElementType.DRAINAGE_PIPE,
        "leitung": ElementType.DRAINAGE_PIPE,
        "drain": ElementType.DRAINAGE_PIPE,
        "shaft": ElementType.DRAINAGE_SHAFT,
        "schacht": ElementType.DRAINAGE_SHAFT,
        "drainageschacht": ElementType.DRAINAGE_SHAFT,
        "drainageshaft": ElementType.DRAINAGE_SHAFT,
        "gleis": ElementType.TRACK,
        "track": ElementType.TRACK,
        "rail": ElementType.TRACK,
        "ausleger": ElementType.CANTILEVER,
        "cantilever": ElementType.CANTILEVER,
    }

    # Direct comparison with enum values
    try:
        return ElementType(normalized)
    except ValueError:
        # Use mapping
        if normalized in mappings:
            return mappings[normalized]

        # Partial comparison
        for key, element_type in mappings.items():
            if key in normalized or normalized in key:
                return element_type

    # Fallback if no match
    logger.warning(
        f"Could not resolve ElementType for '{type_str}', using {ElementType.UNDEFINED}"
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
            logger.warning(f"Could not convert value '{value}' to type '{expected_type}': {e}")
            return default

    # Unit conversion, if specified
    if unit_conversion and isinstance(value, (int, float)):
        from_unit, to_unit = unit_conversion
        try:
            value = convert_unit(value, from_unit, to_unit)
        except ValueError as e:
            logger.warning(f"Unit conversion failed: {e}")

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
    return {
        "name": name,
        "element_type": element_type.value,
        "parameters": []
        if parameters is None
        else [
            {
                "name": param.name,
                "value": param.value,
                "datatype": param.datatype,
                "unit": param.unit.value,
                "process": param.process.value if param.process else None,
            }
            for param in parameters
        ],
    }