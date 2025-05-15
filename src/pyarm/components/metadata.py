"""
Metadata components for infrastructure elements and parameters.
This module defines components that can hold metadata information.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set, TypeVar

from pyarm.components.base import Component, ComponentType


class MetadataCategory(str, Enum):
    """Categories of metadata that can be attached to elements or parameters."""

    GENERAL = "general"  # General information
    SOURCE = "source"  # Information about data source
    SPATIAL = "spatial"  # Location and spatial context metadata
    PROCESS = "process"  # Process-specific metadata
    CUSTOM = "custom"  # Custom metadata category


T = TypeVar("T")


@dataclass
class MetadataEntry[T]:
    """A single metadata entry with typed value and optional description."""

    value: T
    description: str | None = None
    source: Optional[str] = None

    def __str__(self) -> str:
        desc = f" ({self.description})" if self.description else ""
        source = f" [from: {self.source}]" if self.source else ""
        return f"{self.value}{desc}{source}"


@dataclass
class ProjectPhase:
    """Represents a construction phase in a project."""

    phase_id: str
    name: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProjectPhase):
            return False
        return self.phase_id == other.phase_id

    def __hash__(self) -> int:
        return hash(self.phase_id)


class ProjectPhaseComponent(Component):
    """Component that references building phases in the metadata repository."""

    def __init__(self, name: str = "phases"):
        super().__init__(name, ComponentType.PROJECT_PHASE)
        self.phase_ids: Set[str] = set()

    def add_phase(self, phase_id: str) -> None:
        """
        Add a reference to a project phase.

        Parameters
        ----------
        phase_id : str
            ID of the project phase
        """
        self.phase_ids.add(phase_id)

    def remove_phase(self, phase_id: str) -> bool:
        """
        Remove a reference to a project phase.

        Parameters
        ----------
        phase_id : str
            ID of the project phase

        Returns
        -------
        bool
            True if the reference was removed, False if it didn't exist
        """
        if phase_id in self.phase_ids:
            self.phase_ids.remove(phase_id)
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the component to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the component
        """
        result = super().to_dict()
        result["phase_ids"] = list(self.phase_ids)
        return result


class IfcConfigComponent(Component):
    """Component that contains IFC configuration information."""

    def __init__(self, name: str = "ifc_config"):
        super().__init__(name, ComponentType.IFC_CONFIG)
        self.ifc_entity_type: Optional[str] = None
        self.ifc_object_type: Optional[str] = None
        self.ifc_element_class: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the component to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the component
        """
        result = super().to_dict()
        if self.ifc_entity_type:
            result["ifc_entity_type"] = self.ifc_entity_type
        if self.ifc_object_type:
            result["ifc_object_type"] = self.ifc_object_type
        if self.ifc_element_class:
            result["ifc_element_class"] = self.ifc_element_class

        return result
