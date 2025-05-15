#!/usr/bin/env ipython


import logging
from typing import Any, TypeGuard

log = logging.getLogger(__name__)


def is_int(value: Any) -> TypeGuard[int]:
    """
    Check if the value is an integer.

    Parameters
    ----------
    value: str
        The value to be checked

    Returns
    -------
    bool
        True if the value is an integer, False otherwise
    """
    if value is None:
        return False
    if isinstance(value, int):
        return True
    if not isinstance(value, str):
        value = str(value)
    if isinstance(value, str):
        value = value.replace(",", ".").replace(".0", "")
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def is_float(value: Any) -> TypeGuard[float]:
    """
    Check if the value is a float.

    Parameters
    ----------
    value: str
        The value to be checked

    Returns
    -------
    bool
        True if the value is a float, False otherwise
    """
    if value is None:
        return False
    if isinstance(value, float):
        return True
    if not isinstance(value, str):
        value = str(value)
    if isinstance(value, str):
        value = value.replace(",", ".")
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


TRUE_VALUES = {"true", "1", "yes", "ja", "y", "on"}
FALSE_VALUES = {"false", "0", "no", "nein", "n", "off"}


def is_bool(value: Any) -> bool:
    """
    Check if the value is a boolean.

    Parameters
    ----------
    value: str
        The value to be checked

    Returns
    -------
    bool
        True if the value is a boolean, False otherwise
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if not isinstance(value, str):
        value = str(value)
    return value.lower() in TRUE_VALUES or value.lower() in FALSE_VALUES


def as_bool(value: Any) -> bool:
    """
    Convert a value to a boolean.

    Parameters
    ----------
    value: str
        The value to be converted

    Returns
    -------
    bool
        True if the value is a boolean, False otherwise
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        value = str(value)
    return value.lower() in TRUE_VALUES
