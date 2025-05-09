"""
Base models for infrastructure elements.
This module defines the fundamental structure of data models
that are used in all processes.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class UnitEnum(str, Enum):
    """Units for parameters"""

    METER = "m"
    CENTIMETER = "cm"
    MILLIMETER = "mm"
    DEGREE = "deg"
    RADIAN = "rad"
    KILOGRAM = "kg"
    TON = "t"
    PERCENT = "pct"
    PROMILLE = "‰"
    NEWTON = "N"
    KILONEWTON = "kN"
    CUBIC_METER = "m³"
    SQUARE_METER = "m²"
    KILOMETER = "km"
    NONE = ""


class DataType(str, Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"


@dataclass
class Parameter:
    """
    Represents a single parameter of an infrastructure element.
    """

    name: str  # Original name from the data source
    value: Any  # Value of the parameter
    datatype: DataType
    process: ProcessEnum | None = field(default=None)
    unit: UnitEnum = field(default=UnitEnum.NONE)

    def __str__(self) -> str:
        """
        String representation of the parameter.

        Returns
        -------
        str
            Formatted string representation of the parameter
        """
        data_str = f" {self.datatype.value}"
        unit_str = f" {self.unit.value}" if self.unit != UnitEnum.NONE else ""
        process_str = f" ({self.process.value.upper()})" if self.process else ""
        return f"{self.name}[{data_str}]: {self.value}{unit_str}{process_str}"