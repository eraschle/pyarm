from typing import Any, Dict, List, Optional, Protocol

from pyarm.components.metadata import ProjectPhase


class IMetadataRepository(Protocol):
    """
    Central repository for metadata including building phases.
    Provides a unified interface for accessing different types of metadata.
    """

    def add_project_phase(self, phase: ProjectPhase) -> None:
        """
        Add a project phase to the repository.

        Parameters
        ----------
        phase : BuildingPhase
            The project phase to add
        """
        ...

    def get_project_phase(self, phase_id: str) -> Optional[ProjectPhase]:
        """
        Get a building phase by ID.

        Parameters
        ----------
        phase_id : str
            The ID of the project phase

        Returns
        -------
        Optional[BuildingPhase]
            The project phase or None if not found
        """
        ...

    def get_all_project_phases(self) -> List[ProjectPhase]:
        """
        Get all project phases.

        Returns
        -------
        List[BuildingPhase]
            List of all project phases
        """
        ...

    def remove_project_phase(self, phase_id: str) -> bool:
        """
        Remove a building phase.

        Parameters
        ----------
        phase_id : str
            The ID of the project phase to remove

        Returns
        -------
        bool
            True if the phase was removed, False if it didn't exist
        """
        ...

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
        ...

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
        ...

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
        ...
