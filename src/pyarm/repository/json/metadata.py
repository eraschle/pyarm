from dataclasses import asdict
from typing import Any, Dict, List, Optional

from pyarm.components.metadata import ProjectPhase
from pyarm.repository.metadata import IMetadataRepository


class MetadataRepository(IMetadataRepository):
    """
    Central repository for metadata including building phases.
    Provides a unified interface for accessing different types of metadata.
    """

    def __init__(self):
        """Initialize the metadata repository with empty collections."""
        self._project_phases: dict[str, ProjectPhase] = {}
        self._ifc_entity_types: dict[str, str] = {}  # ID -> Description
        self._custom_metadata: dict[str, dict[str, Any]] = {}

    # BuildingPhase methods
    def add_project_phase(self, phase: ProjectPhase) -> None:
        self._project_phases[phase.phase_id] = phase

    def get_project_phase(self, phase_id: str) -> Optional[ProjectPhase]:
        return self._project_phases.get(phase_id)

    def get_all_project_phases(self) -> List[ProjectPhase]:
        return list(self._project_phases.values())

    def remove_project_phase(self, phase_id: str) -> bool:
        if phase_id in self._project_phases:
            del self._project_phases[phase_id]
            return True
        return False

    # Custom metadata methods
    def add_custom_metadata(self, category: str, key: str, value: Any) -> None:
        if category not in self._custom_metadata:
            self._custom_metadata[category] = {}
        self._custom_metadata[category][key] = value

    def get_custom_metadata(self, category: str, key: str) -> Optional[Any]:
        if category not in self._custom_metadata:
            return None
        return self._custom_metadata[category].get(key)

    def get_all_custom_metadata(self, category: Optional[str] = None) -> Dict[str, Any]:
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
            "phases": {id: asdict(phase) for id, phase in self._project_phases.items()},
            "ifc_config": self._ifc_entity_types,
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
        for id, phase_data in data.get("phases", {}).items():
            repo._project_phases[id] = ProjectPhase(**phase_data)

        # Load IFC entity types
        repo._ifc_entity_types = data.get("ifc_config", {})

        # Load custom metadata
        repo._custom_metadata = data.get("custom_metadata", {})

        return repo
