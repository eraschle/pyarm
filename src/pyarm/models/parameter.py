"""
Base models for infrastructure elements.
This module defines the fundamental structure of data models
that are used in all processes.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pyarm.components import Component, ComponentType
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
    Now with support for components, enabling metadata and other extensions.
    """

    name: str  # Original name from the data source
    value: Any  # Value of the parameter
    datatype: DataType
    process: ProcessEnum | None = field(default=None)
    unit: UnitEnum = field(default=UnitEnum.NONE)
    
    # Component storage for parameters
    components: Dict[str, Component] = field(default_factory=dict, repr=False)

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

    def add_component(self, component: Component) -> None:
        """
        Add a component to the parameter.
        
        Parameters
        ----------
        component : Component
            The component to add
        """
        self.components[component.name] = component
    
    def get_component(self, component_name: str) -> Optional[Component]:
        """
        Get a component by name.
        
        Parameters
        ----------
        component_name : str
            Name of the component
            
        Returns
        -------
        Optional[Component]
            The component or None if not found
        """
        return self.components.get(component_name)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[Component]:
        """
        Get all components of a specific type.
        
        Parameters
        ----------
        component_type : ComponentType
            Type of the components
            
        Returns
        -------
        List[Component]
            List of components of the specified type
        """
        return [comp for comp in self.components.values() if comp.component_type == component_type]
    
    def remove_component(self, component_name: str) -> bool:
        """
        Remove a component by name.
        
        Parameters
        ----------
        component_name : str
            Name of the component
            
        Returns
        -------
        bool
            True if the component was removed, False if it didn't exist
        """
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
        result = {
            "name": self.name,
            "value": self.value,
            "datatype": self.datatype.value,
            "unit": self.unit.value
        }
        
        if self.process:
            result["process"] = self.process.value
        
        if self.components:
            result["components"] = {
                name: comp.to_dict() if hasattr(comp, "to_dict") else {"name": comp.name}
                for name, comp in self.components.items()
            }
        
        return result

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
        components_str = f" +{len(self.components)} components" if self.components else ""
        return f"{self.name}[{data_str}]: {self.value}{unit_str}{process_str}{components_str}"