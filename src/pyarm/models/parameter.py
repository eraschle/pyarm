"""
Base models for infrastructure elements.
This module defines the fundamental structure of data models
that are used in all processes.
"""

import logging
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pyarm.components import Component, ComponentType
from pyarm.interfaces.component import IComponentModel
from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class UnitCategory(str, Enum):
    """Categories for units of measurement"""

    LENGTH = "length"
    AREA = "area"
    VOLUME = "volume"
    MASS = "mass"
    FORCE = "force"
    ANGLE = "angle"
    RATIO = "ratio"
    TIME = "time"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    VELOCITY = "velocity"
    UNKNOWN = "unknown"


class UnitEnum(str, Enum):
    """Units for parameters, organized by measurement type"""

    # Length units
    METER = "m"
    CENTIMETER = "cm"
    MILLIMETER = "mm"
    KILOMETER = "km"

    # Area units
    SQUARE_METER = "m²"
    SQUARE_CENTIMETER = "cm²"
    SQUARE_MILLIMETER = "mm²"
    SQUARE_KILOMETER = "km²"
    HECTARE = "ha"

    # Volume units
    CUBIC_METER = "m³"
    CUBIC_CENTIMETER = "cm³"
    CUBIC_MILLIMETER = "mm³"
    LITER = "L"
    MILLILITER = "mL"

    # Mass units
    KILOGRAM = "kg"
    GRAM = "g"
    MILLIGRAM = "mg"
    TON = "t"

    # Force units
    NEWTON = "N"
    KILONEWTON = "kN"
    MEGANEWTON = "MN"

    # Angle units
    DEGREE = "deg"
    RADIAN = "rad"
    GRAD = "grad"

    # Ratio units
    PERCENT = "pct"
    PROMILLE = "‰"
    RATIO = ":"

    # Time units
    SECOND = "s"
    MINUTE = "min"
    HOUR = "h"
    DAY = "d"

    # Temperature units
    CELSIUS = "°C"
    KELVIN = "K"

    # Pressure units
    PASCAL = "Pa"
    KILOPASCAL = "kPa"
    MEGAPASCAL = "MPa"
    BAR = "bar"

    # Velocity units
    METER_PER_SECOND = "m/s"
    KILOMETER_PER_HOUR = "km/h"

    # No unit
    NONE = ""


class DataType(str, Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    UUID = "uuid"


class Parameter(IComponentModel):
    """
    Represents a single parameter of an infrastructure element.
    Now with support for components, enabling metadata and other extensions.
    """

    def __init__(
        self,
        name: str,
        value: Any,
        datatype: DataType,
        process: ProcessEnum | None = None,
        unit: UnitEnum = UnitEnum.NONE,
        components: Dict[str, Component] | None = None,
    ):
        self.name = name
        self.value = value
        self.datatype = datatype
        self.process = process
        self._unit = unit
        self._update_unit(unit)
        self.components = components or {}

    @property
    def has_value(self) -> bool:
        """
        Check if the parameter has a value.

        Returns
        -------
        bool
            True if the parameter has a value, False otherwise
        """
        if self.value is None:
            return False
        return len(str(self.value).strip()) > 0

    def as_int(self) -> int:
        """
        Convert the parameter value to an integer.

        Returns
        -------
        Optional[int]
            The integer value of the parameter, or None if conversion is not possible
        """
        if self.datatype != DataType.INTEGER:
            raise ValueError(f"Cannot convert {self.datatype} to int")
        return int(self.value)

    def can_as_int(self) -> bool:
        """
        Check if the parameter can be converted to an integer.

        Returns
        -------
        bool
            True if the parameter can be converted, False otherwise
        """
        try:
            self.as_int()
            return True
        except (ValueError, TypeError):
            return False

    def as_float(self) -> float:
        """
        Convert the parameter value to an integer.

        Returns
        -------
        Optional[int]
            The integer value of the parameter, or None if conversion is not possible
        """
        if self.datatype not in (DataType.INTEGER, DataType.FLOAT):
            raise ValueError(f"Cannot convert {self.datatype} to float")
        return float(self.value)

    def can_as_float(self) -> bool:
        """
        Check if the parameter can be converted to a float.

        Returns
        -------
        bool
            True if the parameter can be converted, False otherwise
        """
        try:
            self.as_float()
            return True
        except (ValueError, TypeError):
            return False

    def as_bool(self) -> bool:
        """
        Convert the parameter value to a boolean.

        Returns
        -------
        Optional[int]
            The integer value of the parameter, or None if conversion is not possible
        """
        if self.datatype != DataType.BOOLEAN:
            raise ValueError(f"Cannot convert {self.datatype} to bool")
        return bool(self.value)

    def can_as_bool(self) -> bool:
        """
        Check if the parameter can be converted to a boolean.

        Returns
        -------
        bool
            True if the parameter can be converted, False otherwise
        """
        try:
            self.as_bool()
            return True
        except (ValueError, TypeError):
            return False

    def as_str(self) -> str:
        """
        Convert the parameter value to a string.

        Returns
        -------
        Optional[int]
            The integer value of the parameter, or None if conversion is not possible
        """
        if self.value is None:
            return ""
        return str(self.value)

    def as_uuid(self) -> UUID:
        """
        Convert the parameter value to a UUID.

        Returns
        -------
        Optional[int]
            The integer value of the parameter, or None if conversion is not possible
        """
        if self.datatype != DataType.UUID:
            raise ValueError(f"Cannot convert {self.datatype} to UUID")
        return UUID(str(self.value))

    def can_as_uuid(self) -> bool:
        """
        Check if the parameter can be converted to a UUID.

        Returns
        -------
        bool
            True if the parameter can be converted, False otherwise
        """
        try:
            self.as_uuid()
            return True
        except (ValueError, TypeError):
            return False

    @property
    def unit(self) -> UnitEnum:
        """
        Get the unit of the parameter.

        Returns
        -------
        UnitEnum
            The unit of the parameter
        """
        return self._unit

    @unit.setter
    def unit(self, unit: UnitEnum) -> None:
        """
        Set the unit of the parameter.

        Parameters
        ----------
        value : UnitEnum
            The unit to set
        """
        self._update_unit(unit)
        self._unit = unit

    def _update_unit(self, unit: UnitEnum) -> None:
        if unit != UnitEnum.NONE:
            self.datatype = DataType.FLOAT
        if unit == self._unit:
            return

        from pyarm.models import units

        self.value = units.convert_unit(self.value, self.unit, unit)

    def add_component(self, component: Component) -> None:
        self.components[component.name] = component

    def get_component(self, component_name: str) -> Optional[Component]:
        return self.components.get(component_name)

    def get_components_by_type(self, component_type: ComponentType) -> List[Component]:
        return [comp for comp in self.components.values() if comp.component_type == component_type]

    def remove_component(self, component_name: str) -> bool:
        if component_name in self.components:
            del self.components[component_name]
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the parameter to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the parameter
        """
        value = self.value
        if isinstance(value, time):
            # Convert datetime to ISO format
            value = value.isoformat()
        elif isinstance(value, date):
            # Convert datetime to ISO format
            value = value.isoformat()
        elif isinstance(value, datetime):
            # Convert datetime to ISO format
            value = value.isoformat()
        if str(value).lower() == "nan":
            value = None
        result = {
            "name": self.name,
            "value": value,
            "datatype": self.datatype.value,
        }

        if self.unit != UnitEnum.NONE:
            result["unit"] = self.unit.value

        if self.process:
            result["process"] = self.process.value

        if self.components:
            result["components"] = {name: comp.to_dict() for name, comp in self.components.items()}

        return result

    def convert_to(self, target_unit: UnitEnum) -> "Parameter":
        """
        Convert this parameter to a different unit.

        This method creates a new Parameter instance with the converted value and unit.
        It does not modify the current instance.

        Parameters
        ----------
        target_unit : UnitEnum
            The target unit for conversion

        Returns
        -------
        Parameter
            A new Parameter with the converted value and unit

        Raises
        ------
        ValueError
            If the conversion is not supported or the parameter is not numeric
        """
        from pyarm.models import units

        return units.convert_parameter_unit(self, target_unit)

    def with_standard_unit(self) -> "Parameter":
        """
        Convert this parameter to the standard SI unit for its unit category.

        Returns
        -------
        Parameter
            A new Parameter with the standard unit for its category

        Raises
        ------
        ValueError
            If the conversion is not supported or the parameter is not numeric
        """
        from pyarm.models import units

        category_to_standard = {
            "length": UnitEnum.METER,
            "area": UnitEnum.SQUARE_METER,
            "volume": UnitEnum.CUBIC_METER,
            "mass": UnitEnum.KILOGRAM,
            "force": UnitEnum.NEWTON,
            "angle": UnitEnum.RADIAN,
            "ratio": UnitEnum.NONE,
            "time": UnitEnum.SECOND,
            "temperature": UnitEnum.KELVIN,
            "pressure": UnitEnum.PASCAL,
            "velocity": UnitEnum.METER_PER_SECOND,
        }

        category = units.get_unit_category(self.unit)
        standard_unit = category_to_standard.get(category)
        if category == UnitCategory.UNKNOWN or self.unit == standard_unit:
            return self

        return self.convert_to(category_to_standard[category])

    def __str__(self) -> str:
        data_str = f" {self.datatype.value}"
        unit_str = f" {self.unit.value}" if self.unit != UnitEnum.NONE else ""
        process_str = f" ({self.process.value.upper()})" if self.process else ""
        components_str = f" +{len(self.components)} components" if self.components else ""
        return f"{self.name}[{data_str}]: {self.value}{unit_str}{process_str}{components_str}"
