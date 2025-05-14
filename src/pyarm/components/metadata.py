"""
Metadata components for infrastructure elements and parameters.
This module defines components that can hold metadata information.
"""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Set, TypeVar

from pyarm.components.base import Component, ComponentType


class MetadataCategory(str, Enum):
    """Categories of metadata that can be attached to elements or parameters."""

    GENERAL = "general"  # General information
    TECHNICAL = "technical"  # Technical specifications
    ADMINISTRATIVE = "administrative"  # Administrative metadata
    SOURCE = "source"  # Information about data source
    TEMPORAL = "temporal"  # Time-related metadata
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
class BuildingPhase:
    """Represents a construction phase in a project."""

    id: str
    name: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BuildingPhase):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class MetadataRepository:
    """
    Central repository for metadata including building phases.
    Provides a unified interface for accessing different types of metadata.
    """

    _instance: ClassVar[Optional["MetadataRepository"]] = None

    @classmethod
    def get_instance(cls) -> "MetadataRepository":
        """Get or create the singleton instance of the repository."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the metadata repository with empty collections."""
        self._building_phases: dict[str, BuildingPhase] = {}
        self._ifc_entity_types: dict[str, str] = {}  # ID -> Description
        self._custom_metadata: dict[str, dict[str, Any]] = {}

    # BuildingPhase methods
    def add_building_phase(self, phase: BuildingPhase) -> None:
        """
        Add a building phase to the repository.

        Parameters
        ----------
        phase : BuildingPhase
            The building phase to add
        """
        self._building_phases[phase.id] = phase

    def get_building_phase(self, phase_id: str) -> Optional[BuildingPhase]:
        """
        Get a building phase by ID.

        Parameters
        ----------
        phase_id : str
            The ID of the building phase

        Returns
        -------
        Optional[BuildingPhase]
            The building phase or None if not found
        """
        return self._building_phases.get(phase_id)

    def get_all_building_phases(self) -> List[BuildingPhase]:
        """
        Get all building phases.

        Returns
        -------
        List[BuildingPhase]
            List of all building phases
        """
        return list(self._building_phases.values())

    def remove_building_phase(self, phase_id: str) -> bool:
        """
        Remove a building phase.

        Parameters
        ----------
        phase_id : str
            The ID of the building phase to remove

        Returns
        -------
        bool
            True if the phase was removed, False if it didn't exist
        """
        if phase_id in self._building_phases:
            del self._building_phases[phase_id]
            return True
        return False

    # IFC entity type methods
    def add_ifc_entity_type(self, type_id: str, description: str) -> None:
        """
        Add an IFC entity type.

        Parameters
        ----------
        type_id : str
            The ID of the IFC entity type
        description : str
            Description of the IFC entity type
        """
        self._ifc_entity_types[type_id] = description

    def get_ifc_entity_type_description(self, type_id: str) -> Optional[str]:
        """
        Get the description of an IFC entity type.

        Parameters
        ----------
        type_id : str
            The ID of the IFC entity type

        Returns
        -------
        Optional[str]
            The description or None if not found
        """
        return self._ifc_entity_types.get(type_id)

    def get_all_ifc_entity_types(self) -> Dict[str, str]:
        """
        Get all IFC entity types.

        Returns
        -------
        Dict[str, str]
            Dictionary mapping IFC entity type IDs to descriptions
        """
        return self._ifc_entity_types.copy()

    # Custom metadata methods
    def add_custom_metadata(self, category: str, key: str, value: Any) -> None:
        """
        Add a custom metadata entry.

        Parameters
        ----------
        category : str
            Category of the metadata
        key : str
            Unique key for the metadata
        value : Any
            Value of the metadata
        """
        if category not in self._custom_metadata:
            self._custom_metadata[category] = {}
        self._custom_metadata[category][key] = value

    def get_custom_metadata(self, category: str, key: str) -> Optional[Any]:
        """
        Get a custom metadata entry.

        Parameters
        ----------
        category : str
            Category of the metadata
        key : str
            Key of the metadata

        Returns
        -------
        Optional[Any]
            The value or None if not found
        """
        if category not in self._custom_metadata:
            return None
        return self._custom_metadata[category].get(key)

    def get_all_custom_metadata(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all custom metadata in a category or all categories.

        Parameters
        ----------
        category : Optional[str], optional
            Category to get metadata for, or None for all categories, by default None

        Returns
        -------
        Dict[str, Any]
            Dictionary of metadata
        """
        if category is None:
            return self._custom_metadata.copy()
        return self._custom_metadata.get(category, {}).copy()

    # Serialization methods
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the repository to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the repository
        """
        return {
            "building_phases": {id: asdict(phase) for id, phase in self._building_phases.items()},
            "ifc_entity_types": self._ifc_entity_types,
            "custom_metadata": self._custom_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataRepository":
        """
        Create a repository from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary representation of the repository

        Returns
        -------
        MetadataRepository
            New repository instance
        """
        repo = cls()

        # Load building phases
        for id, phase_data in data.get("building_phases", {}).items():
            repo._building_phases[id] = BuildingPhase(**phase_data)

        # Load IFC entity types
        repo._ifc_entity_types = data.get("ifc_entity_types", {})

        # Load custom metadata
        repo._custom_metadata = data.get("custom_metadata", {})

        return repo


class BuildingPhaseComponent(Component):
    """Component that references building phases in the metadata repository."""

    def __init__(self, name: str = "building_phases"):
        """
        Initialize a building phase component.

        Parameters
        ----------
        name : str, optional
            Name of the component, by default "building_phases"
        """
        super().__init__(name, ComponentType.BUILDING_PHASE)
        self.phase_ids: Set[str] = set()

    def add_phase_reference(self, phase_id: str) -> None:
        """
        Add a reference to a building phase.

        Parameters
        ----------
        phase_id : str
            ID of the building phase
        """
        self.phase_ids.add(phase_id)

    def remove_phase_reference(self, phase_id: str) -> bool:
        """
        Remove a reference to a building phase.

        Parameters
        ----------
        phase_id : str
            ID of the building phase

        Returns
        -------
        bool
            True if the reference was removed, False if it didn't exist
        """
        if phase_id in self.phase_ids:
            self.phase_ids.remove(phase_id)
            return True
        return False

    def get_phase_ids(self) -> Set[str]:
        """
        Get all building phase IDs.

        Returns
        -------
        Set[str]
            Set of building phase IDs
        """
        return self.phase_ids.copy()

    def get_phases(self) -> List[BuildingPhase]:
        """
        Get all building phases referenced by this component.

        Returns
        -------
        List[BuildingPhase]
            List of building phases
        """
        repo = MetadataRepository.get_instance()
        phases = []
        for phase_id in self.phase_ids:
            phase = repo.get_building_phase(phase_id)
            if phase is None:
                continue
            phases.append(phase)
        return phases

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the component to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the component
        """
        return {
            "name": self.name,
            "component_type": self.component_type.value,
            "phase_ids": list(self.phase_ids),
        }


class IfcConfigurationComponent(Component):
    """Component that contains IFC configuration information."""

    def __init__(self, name: str = "ifc_configuration"):
        """
        Initialize an IFC configuration component.

        Parameters
        ----------
        name : str, optional
            Name of the component, by default "ifc_configuration"
        """
        super().__init__(name, ComponentType.IFC_CONFIG)
        self.ifc_entity_type: Optional[str] = None
        self.ifc_global_id: Optional[str] = None
        self.ifc_predefined_type: Optional[str] = None
        self.ifc_object_type: Optional[str] = None
        self.ifc_element_class: Optional[str] = None
        self.representation_context: Optional[str] = None

    def set_ifc_entity_type(self, entity_type: str) -> None:
        """
        Set the IFC entity type.

        Parameters
        ----------
        entity_type : str
            IFC entity type (e.g., IfcBeam, IfcColumn)
        """
        self.ifc_entity_type = entity_type

    def set_ifc_global_id(self, global_id: str) -> None:
        """
        Set the IFC global ID.

        Parameters
        ----------
        global_id : str
            IFC global ID
        """
        self.ifc_global_id = global_id

    def set_ifc_predefined_type(self, predefined_type: str) -> None:
        """
        Set the IFC predefined type.

        Parameters
        ----------
        predefined_type : str
            IFC predefined type
        """
        self.ifc_predefined_type = predefined_type

    def set_ifc_object_type(self, object_type: str) -> None:
        """
        Set the IFC object type.

        Parameters
        ----------
        object_type : str
            IFC object type
        """
        self.ifc_object_type = object_type

    def set_ifc_element_class(self, element_class: str) -> None:
        """
        Set the IFC element class.

        Parameters
        ----------
        element_class : str
            IFC element class
        """
        self.ifc_element_class = element_class

    def set_representation_context(self, context: str) -> None:
        """
        Set the representation context.

        Parameters
        ----------
        context : str
            Representation context
        """
        self.representation_context = context

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the component to a dictionary for serialization.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the component
        """
        result = {"name": self.name, "component_type": self.component_type.value}

        if self.ifc_entity_type:
            result["ifc_entity_type"] = self.ifc_entity_type
        if self.ifc_global_id:
            result["ifc_global_id"] = self.ifc_global_id
        if self.ifc_predefined_type:
            result["ifc_predefined_type"] = self.ifc_predefined_type
        if self.ifc_object_type:
            result["ifc_object_type"] = self.ifc_object_type
        if self.ifc_element_class:
            result["ifc_element_class"] = self.ifc_element_class
        if self.representation_context:
            result["representation_context"] = self.representation_context

        return result
