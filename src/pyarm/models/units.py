"""
Helper functions for commonly used operations in PyArm.
These functions reduce code duplication and improve maintainability.
"""

import logging

from pyarm.models.parameter import DataType, Parameter, UnitCategory, UnitEnum

logger = logging.getLogger(__name__)


def get_unit_category(unit: UnitEnum) -> UnitCategory:
    """
    Determines the category of a unit.

    Parameters
    ----------
    unit: UnitEnum
        The unit to categorize

    Returns
    -------
    UnitCategory
        The category of the unit
    """
    length_units = [UnitEnum.METER, UnitEnum.CENTIMETER, UnitEnum.MILLIMETER, UnitEnum.KILOMETER]

    area_units = [
        UnitEnum.SQUARE_METER,
        UnitEnum.SQUARE_CENTIMETER,
        UnitEnum.SQUARE_MILLIMETER,
        UnitEnum.SQUARE_KILOMETER,
        UnitEnum.HECTARE,
    ]

    volume_units = [
        UnitEnum.CUBIC_METER,
        UnitEnum.CUBIC_CENTIMETER,
        UnitEnum.CUBIC_MILLIMETER,
        UnitEnum.LITER,
        UnitEnum.MILLILITER,
    ]

    mass_units = [UnitEnum.KILOGRAM, UnitEnum.GRAM, UnitEnum.MILLIGRAM, UnitEnum.TON]

    force_units = [UnitEnum.NEWTON, UnitEnum.KILONEWTON, UnitEnum.MEGANEWTON]

    angle_units = [UnitEnum.DEGREE, UnitEnum.RADIAN, UnitEnum.GRAD]

    ratio_units = [UnitEnum.PERCENT, UnitEnum.PROMILLE, UnitEnum.RATIO]

    time_units = [UnitEnum.SECOND, UnitEnum.MINUTE, UnitEnum.HOUR, UnitEnum.DAY]

    temperature_units = [UnitEnum.CELSIUS, UnitEnum.KELVIN]

    pressure_units = [UnitEnum.PASCAL, UnitEnum.KILOPASCAL, UnitEnum.MEGAPASCAL, UnitEnum.BAR]

    velocity_units = [UnitEnum.METER_PER_SECOND, UnitEnum.KILOMETER_PER_HOUR]

    if unit in length_units:
        return UnitCategory.LENGTH
    elif unit in area_units:
        return UnitCategory.AREA
    elif unit in volume_units:
        return UnitCategory.VOLUME
    elif unit in mass_units:
        return UnitCategory.MASS
    elif unit in force_units:
        return UnitCategory.FORCE
    elif unit in angle_units:
        return UnitCategory.ANGLE
    elif unit in ratio_units:
        return UnitCategory.RATIO
    elif unit in time_units:
        return UnitCategory.TIME
    elif unit in temperature_units:
        return UnitCategory.TEMPERATURE
    elif unit in pressure_units:
        return UnitCategory.PRESSURE
    elif unit in velocity_units:
        return UnitCategory.VELOCITY
    else:
        return UnitCategory.UNKNOWN


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
        If the conversion is not supported or units are from different categories
    """
    # If units are the same, no conversion necessary
    if from_unit == to_unit:
        return float(value)

    # Check if units are from the same category
    from_category = get_unit_category(from_unit)
    to_category = get_unit_category(to_unit)

    if from_category != to_category:
        raise ValueError(
            f"Cannot convert between different unit categories: "
            f"{from_category.value} and {to_category.value}"
        )

    # Handle each category with its specific conversion logic
    if from_category == UnitCategory.LENGTH:
        return _convert_length(value, from_unit, to_unit)
    elif from_category == UnitCategory.AREA:
        return _convert_area(value, from_unit, to_unit)
    elif from_category == UnitCategory.VOLUME:
        return _convert_volume(value, from_unit, to_unit)
    elif from_category == UnitCategory.MASS:
        return _convert_mass(value, from_unit, to_unit)
    elif from_category == UnitCategory.FORCE:
        return _convert_force(value, from_unit, to_unit)
    elif from_category == UnitCategory.ANGLE:
        return _convert_angle(value, from_unit, to_unit)
    elif from_category == UnitCategory.RATIO:
        return _convert_ratio(value, from_unit, to_unit)
    elif from_category == UnitCategory.TIME:
        return _convert_time(value, from_unit, to_unit)
    elif from_category == UnitCategory.TEMPERATURE:
        return _convert_temperature(value, from_unit, to_unit)
    elif from_category == UnitCategory.PRESSURE:
        return _convert_pressure(value, from_unit, to_unit)
    elif from_category == UnitCategory.VELOCITY:
        return _convert_velocity(value, from_unit, to_unit)
    else:
        raise ValueError(f"Conversion for {from_category.value} units is not supported")


def _convert_length(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert length units to meters first, then to target unit."""
    # Convert to meters (base unit)
    meters = value
    if from_unit == UnitEnum.MILLIMETER:
        meters = value / 1000
    elif from_unit == UnitEnum.CENTIMETER:
        meters = value / 100
    elif from_unit == UnitEnum.KILOMETER:
        meters = value * 1000

    # Convert from meters to target unit
    if to_unit == UnitEnum.METER:
        return meters
    elif to_unit == UnitEnum.MILLIMETER:
        return meters * 1000
    elif to_unit == UnitEnum.CENTIMETER:
        return meters * 100
    elif to_unit == UnitEnum.KILOMETER:
        return meters / 1000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_area(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert area units to square meters first, then to target unit."""
    # Convert to square meters (base unit)
    sq_meters = value
    if from_unit == UnitEnum.SQUARE_MILLIMETER:
        sq_meters = value / 1_000_000
    elif from_unit == UnitEnum.SQUARE_CENTIMETER:
        sq_meters = value / 10_000
    elif from_unit == UnitEnum.SQUARE_KILOMETER:
        sq_meters = value * 1_000_000
    elif from_unit == UnitEnum.HECTARE:
        sq_meters = value * 10_000

    # Convert from square meters to target unit
    if to_unit == UnitEnum.SQUARE_METER:
        return sq_meters
    elif to_unit == UnitEnum.SQUARE_MILLIMETER:
        return sq_meters * 1_000_000
    elif to_unit == UnitEnum.SQUARE_CENTIMETER:
        return sq_meters * 10_000
    elif to_unit == UnitEnum.SQUARE_KILOMETER:
        return sq_meters / 1_000_000
    elif to_unit == UnitEnum.HECTARE:
        return sq_meters / 10_000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_volume(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert volume units to cubic meters first, then to target unit."""
    # Convert to cubic meters (base unit)
    cubic_meters = value
    if from_unit == UnitEnum.CUBIC_MILLIMETER:
        cubic_meters = value / 1_000_000_000
    elif from_unit == UnitEnum.CUBIC_CENTIMETER:
        cubic_meters = value / 1_000_000
    elif from_unit == UnitEnum.LITER:
        cubic_meters = value / 1000
    elif from_unit == UnitEnum.MILLILITER:
        cubic_meters = value / 1_000_000

    # Convert from cubic meters to target unit
    if to_unit == UnitEnum.CUBIC_METER:
        return cubic_meters
    elif to_unit == UnitEnum.CUBIC_MILLIMETER:
        return cubic_meters * 1_000_000_000
    elif to_unit == UnitEnum.CUBIC_CENTIMETER:
        return cubic_meters * 1_000_000
    elif to_unit == UnitEnum.LITER:
        return cubic_meters * 1000
    elif to_unit == UnitEnum.MILLILITER:
        return cubic_meters * 1_000_000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_mass(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert mass units to kilograms first, then to target unit."""
    # Convert to kilograms (base unit)
    kg = value
    if from_unit == UnitEnum.GRAM:
        kg = value / 1000
    elif from_unit == UnitEnum.MILLIGRAM:
        kg = value / 1_000_000
    elif from_unit == UnitEnum.TON:
        kg = value * 1000

    # Convert from kilograms to target unit
    if to_unit == UnitEnum.KILOGRAM:
        return kg
    elif to_unit == UnitEnum.GRAM:
        return kg * 1000
    elif to_unit == UnitEnum.MILLIGRAM:
        return kg * 1_000_000
    elif to_unit == UnitEnum.TON:
        return kg / 1000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_force(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert force units to newtons first, then to target unit."""
    # Convert to newtons (base unit)
    newtons = value
    if from_unit == UnitEnum.KILONEWTON:
        newtons = value * 1000
    elif from_unit == UnitEnum.MEGANEWTON:
        newtons = value * 1_000_000

    # Convert from newtons to target unit
    if to_unit == UnitEnum.NEWTON:
        return newtons
    elif to_unit == UnitEnum.KILONEWTON:
        return newtons / 1000
    elif to_unit == UnitEnum.MEGANEWTON:
        return newtons / 1_000_000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_angle(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert angle units to radians first, then to target unit."""
    # Convert to radians (base unit)
    radians = value
    if from_unit == UnitEnum.DEGREE:
        import math

        radians = value * (math.pi / 180)
    elif from_unit == UnitEnum.GRAD:
        import math

        radians = value * (math.pi / 200)

    # Convert from radians to target unit
    if to_unit == UnitEnum.RADIAN:
        return radians
    elif to_unit == UnitEnum.DEGREE:
        import math

        return radians * (180 / math.pi)
    elif to_unit == UnitEnum.GRAD:
        import math

        return radians * (200 / math.pi)

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_ratio(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert ratio units to decimal first, then to target unit."""
    # Convert to decimal ratio (base unit)
    decimal = value
    if from_unit == UnitEnum.PERCENT:
        decimal = value / 100
    elif from_unit == UnitEnum.PROMILLE:
        decimal = value / 1000
    elif from_unit == UnitEnum.RATIO:
        # Assume value is already decimal for ratio as we don't have context
        decimal = value

    # Convert from decimal to target unit
    if to_unit == UnitEnum.PERCENT:
        return decimal * 100
    elif to_unit == UnitEnum.PROMILLE:
        return decimal * 1000
    elif to_unit == UnitEnum.RATIO:
        return decimal

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_time(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert time units to seconds first, then to target unit."""
    # Convert to seconds (base unit)
    seconds = value
    if from_unit == UnitEnum.MINUTE:
        seconds = value * 60
    elif from_unit == UnitEnum.HOUR:
        seconds = value * 3600
    elif from_unit == UnitEnum.DAY:
        seconds = value * 86400

    # Convert from seconds to target unit
    if to_unit == UnitEnum.SECOND:
        return seconds
    elif to_unit == UnitEnum.MINUTE:
        return seconds / 60
    elif to_unit == UnitEnum.HOUR:
        return seconds / 3600
    elif to_unit == UnitEnum.DAY:
        return seconds / 86400

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_temperature(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """
    Convert temperature units with special handling for non-linear relationships.
    """
    # Special case for temperature conversions due to offsets
    if from_unit == to_unit:
        return value

    # First convert to Kelvin (base unit)
    kelvin = value
    if from_unit == UnitEnum.CELSIUS:
        kelvin = value + 273.15

    # Then convert from Kelvin to target unit
    if to_unit == UnitEnum.KELVIN:
        return kelvin
    elif to_unit == UnitEnum.CELSIUS:
        return kelvin - 273.15

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_pressure(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert pressure units to pascals first, then to target unit."""
    # Convert to pascals (base unit)
    pascals = value
    if from_unit == UnitEnum.KILOPASCAL:
        pascals = value * 1000
    elif from_unit == UnitEnum.MEGAPASCAL:
        pascals = value * 1_000_000
    elif from_unit == UnitEnum.BAR:
        pascals = value * 100_000

    # Convert from pascals to target unit
    if to_unit == UnitEnum.PASCAL:
        return pascals
    elif to_unit == UnitEnum.KILOPASCAL:
        return pascals / 1000
    elif to_unit == UnitEnum.MEGAPASCAL:
        return pascals / 1_000_000
    elif to_unit == UnitEnum.BAR:
        return pascals / 100_000

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def _convert_velocity(value: float, from_unit: UnitEnum, to_unit: UnitEnum) -> float:
    """Convert velocity units to meters per second first, then to target unit."""
    # Convert to meters per second (base unit)
    mps = value
    if from_unit == UnitEnum.KILOMETER_PER_HOUR:
        mps = value * (1000 / 3600)

    # Convert from meters per second to target unit
    if to_unit == UnitEnum.METER_PER_SECOND:
        return mps
    elif to_unit == UnitEnum.KILOMETER_PER_HOUR:
        return mps * (3600 / 1000)

    raise ValueError(f"Conversion from {from_unit.value} to {to_unit.value} not implemented")


def convert_parameter_unit(parameter: "Parameter", to_unit: UnitEnum) -> "Parameter":
    """
    Convert a parameter to a different unit and return a new parameter with the converted value.

    Parameters
    ----------
    parameter : Parameter
        The parameter to convert
    to_unit : UnitEnum
        The target unit

    Returns
    -------
    Parameter
        A new parameter with the same name but converted value and unit

    Raises
    ------
    ValueError
        If the conversion is not supported
    """
    from pyarm.models.parameter import Parameter

    # No conversion needed if units are the same
    if parameter.unit == to_unit:
        return parameter

    # Check if the value is numeric
    if parameter.datatype not in (DataType.FLOAT, DataType.INTEGER):
        raise ValueError(
            f"Cannot convert non-numeric parameter: {parameter.name} with type {parameter.datatype}"
        )

    # Convert the value
    converted_value = convert_unit(parameter.value, parameter.unit, to_unit)
    return Parameter(
        name=parameter.name,
        value=converted_value,
        datatype=parameter.datatype,
        process=parameter.process,
        unit=to_unit,
        components=parameter.components.copy(),
    )


def convert_parameter_list_units(
    parameters: list["Parameter"], unit_map: dict[UnitEnum, UnitEnum]
) -> list["Parameter"]:
    """
    Convert units of parameters in a list according to a mapping.

    Parameters
    ----------
    parameters : list[Parameter]
        List of parameters to convert
    unit_map : dict[UnitEnum, UnitEnum]
        Mapping from source units to target units

    Returns
    -------
    list[Parameter]
        New list of parameters with converted units where applicable
    """
    result = []

    for param in parameters:
        if param.unit in unit_map:
            try:
                converted = convert_parameter_unit(param, unit_map[param.unit])
                result.append(converted)
            except ValueError as e:
                # Log error but keep original parameter
                logger.warning(f"Could not convert parameter {param.name}: {e}")
                result.append(param)
        else:
            # No conversion needed, keep original
            result.append(param)

    return result


def standardize_units(parameters: list["Parameter"]) -> list["Parameter"]:
    """
    Convert all parameters to standard SI units.

    Parameters
    ----------
    parameters : list[Parameter]
        List of parameters to standardize

    Returns
    -------
    list[Parameter]
        New list of parameters with standardized units
    """
    # Define standard units for each category
    standard_units = {
        # Length: convert to meters
        UnitEnum.MILLIMETER: UnitEnum.METER,
        UnitEnum.CENTIMETER: UnitEnum.METER,
        UnitEnum.KILOMETER: UnitEnum.METER,
        # Area: convert to square meters
        UnitEnum.SQUARE_MILLIMETER: UnitEnum.SQUARE_METER,
        UnitEnum.SQUARE_CENTIMETER: UnitEnum.SQUARE_METER,
        UnitEnum.SQUARE_KILOMETER: UnitEnum.SQUARE_METER,
        UnitEnum.HECTARE: UnitEnum.SQUARE_METER,
        # Volume: convert to cubic meters
        UnitEnum.CUBIC_MILLIMETER: UnitEnum.CUBIC_METER,
        UnitEnum.CUBIC_CENTIMETER: UnitEnum.CUBIC_METER,
        UnitEnum.LITER: UnitEnum.CUBIC_METER,
        UnitEnum.MILLILITER: UnitEnum.CUBIC_METER,
        # Mass: convert to kilograms
        UnitEnum.GRAM: UnitEnum.KILOGRAM,
        UnitEnum.MILLIGRAM: UnitEnum.KILOGRAM,
        UnitEnum.TON: UnitEnum.KILOGRAM,
        # Force: convert to newtons
        UnitEnum.KILONEWTON: UnitEnum.NEWTON,
        UnitEnum.MEGANEWTON: UnitEnum.NEWTON,
        # Angle: convert to radians
        UnitEnum.DEGREE: UnitEnum.RADIAN,
        UnitEnum.GRAD: UnitEnum.RADIAN,
        # Ratio: convert to decimal (NONE)
        UnitEnum.PERCENT: UnitEnum.NONE,
        UnitEnum.PROMILLE: UnitEnum.NONE,
        UnitEnum.RATIO: UnitEnum.NONE,
        # Time: convert to seconds
        UnitEnum.MINUTE: UnitEnum.SECOND,
        UnitEnum.HOUR: UnitEnum.SECOND,
        UnitEnum.DAY: UnitEnum.SECOND,
        # Temperature: convert to kelvin
        UnitEnum.CELSIUS: UnitEnum.KELVIN,
        # Pressure: convert to pascals
        UnitEnum.KILOPASCAL: UnitEnum.PASCAL,
        UnitEnum.MEGAPASCAL: UnitEnum.PASCAL,
        UnitEnum.BAR: UnitEnum.PASCAL,
        # Velocity: convert to meters per second
        UnitEnum.KILOMETER_PER_HOUR: UnitEnum.METER_PER_SECOND,
    }

    return convert_parameter_list_units(parameters, standard_units)
