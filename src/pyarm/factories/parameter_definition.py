from typing import Any, Iterable

from numpy import nan

from pyarm.factories.parameter import ParameterDefinition
from pyarm.models.parameter import DataType, UnitEnum
from pyarm.utils import types

FLOAT_TYPES_PARTS = [
    "km",
    "kilometer",
    "länge",
    "laenge",
    "length",
    "breite",
    "width",
    "höhe",
    "hoehe",
    "height",
    "tiefe",
    "depth",
    "dicke",
    "thickness",
    "diameter",
    "durchmesser",
]


def _are_int(values: list[Any]) -> bool:
    """
    Check if the column are int values.
    """
    return all(types.is_int(value) for value in values)


def _are_float(values: list[Any]) -> bool:
    """
    Check if the column are float values.
    """
    return all(types.is_float(value) for value in values)


def _are_bool(values: list[Any]) -> bool:
    """
    Check if the column is a boolean.
    """
    return all(types.is_bool(value) for value in values)


def _is_float_column(column: str) -> bool:
    """
    Check if the column name indicates a float value.
    """
    parts = column.split(" ")
    parts = [_clean_value(part) for part in parts if part]
    parts = [part.lower() for part in parts]
    return any(part in FLOAT_TYPES_PARTS for part in parts)


def _get_datatype(column: str, values: Iterable[Any]) -> DataType:
    """
    Combines the dataframes into one dataframe.
    """
    values = [val for val in values if val is not None and str(val) != str(nan)]
    if _are_int(values) and not _is_float_column(column):
        return DataType.INTEGER
    if _are_float(values):
        return DataType.FLOAT
    if _are_bool(values):
        return DataType.BOOLEAN
    return DataType.STRING


CLEAN_DATA_TYPE_VALUES = ["(", ")", "[", "]", "{", "}"]


def _clean_value(value: str) -> str:
    """
    Clean the value by removing unwanted characters.
    """
    for char in CLEAN_DATA_TYPE_VALUES:
        value = value.replace(char, "")
    return value.strip()


def _is_unit(column_parts: list[str], unit_values: list[str]) -> bool:
    """
    Check if the column is a meter.
    """
    for part in column_parts:
        if part.lower() not in unit_values:
            continue
        return True
    return False


def _is_kilometer(column_parts: list[str]) -> bool:
    """
    Check if the column is a meter.
    """
    return _is_unit(column_parts, ["km", "kilometer"])


def _is_meter(column_parts: list[str]) -> bool:
    """
    Check if the column is a meter.
    """
    return _is_unit(column_parts, ["m", "meter"])


def _is_centimeter(column_parts: list[str]) -> bool:
    """
    Check if the column is a meter.
    """
    return _is_unit(column_parts, ["cm", "centimeter"])


def _is_millimeter(column_parts: list[str]) -> bool:
    """
    Check if the column is a meter.
    """
    return _is_unit(column_parts, ["mm", "millimeter"])


def get_unit_from_name(column: str) -> UnitEnum:
    """
    Combines the dataframes into one dataframe.
    """
    parts = column.split(" ")
    parts = [_clean_value(part) for part in parts if part]
    if _is_kilometer(parts):
        return UnitEnum.KILOMETER
    if _is_meter(parts):
        return UnitEnum.METER
    if _is_centimeter(parts):
        return UnitEnum.CENTIMETER
    if _is_millimeter(parts):
        return UnitEnum.MILLIMETER
    return UnitEnum.NONE


def get_definition(name: str, values: Iterable[Any]) -> ParameterDefinition:
    """
    Creates a custom parameter definition.

    Parameters
    ----------
    name
        The name of the parameter.
    values
        All the values of the parameter.

    Returns
    -------
    ParameterDefinition
        The parameter definition.
    """
    return ParameterDefinition(
        name=name,
        datatype=_get_datatype(name, values),
        unit=get_unit_from_name(name),
        process=None,
    )
