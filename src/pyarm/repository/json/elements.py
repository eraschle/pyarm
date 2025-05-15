"""
JSON-based repository for infrastructure elements.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType
from pyarm.repository.elements import IElementRepository
from pyarm.utils import factory


class JsonElementRepository(IElementRepository):
    """
    Repository for storing infrastructure elements in JSON files.
    """

    def __init__(self, repository_path: str):
        """
        Initializes the repository.

        Parameters
        ----------
        repository_path: str
            Path to the repository directory
        """
        self.repository_path = Path(repository_path)
        self.ensure_directory_exists()

        # In-memory cache for better performance
        self._elements_cache: dict[str, InfrastructureElement] = {}
        self._cache_loaded = False

    def ensure_directory_exists(self) -> None:
        """
        Ensures that the repository directory exists.
        """
        os.makedirs(self.repository_path, exist_ok=True)

    def _load_cache(self) -> None:
        """
        Loads all elements into the cache.
        """
        if self._cache_loaded:
            return

        self._elements_cache.clear()

        # Load all JSON files in the repository directory
        for file_path in self.repository_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    elements_data = json.load(f)

                if isinstance(elements_data, list):
                    for element_data in elements_data:
                        element = factory.create_element(element_data)
                        uuid_str = str(element.uuid)
                        self._elements_cache[uuid_str] = element
                elif isinstance(elements_data, dict):
                    element = factory.create_element(elements_data)
                    uuid_str = str(element.uuid)
                    self._elements_cache[uuid_str] = element
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        self._cache_loaded = True

    def _save_cache(self) -> None:
        """
        Saves the cache to files.
        """
        # Group elements by type
        elements_by_type: dict[ElementType, list[InfrastructureElement]] = {}
        for element in self._elements_cache.values():
            if element.element_type not in elements_by_type:
                elements_by_type[element.element_type] = []
            elements_by_type[element.element_type].append(element)

        # Create a file for each type
        for element_type, elements in elements_by_type.items():
            file_path = self.repository_path / f"{element_type.value}.json"
            elements_data = [element.to_dict() for element in elements]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(elements_data, f, indent=2)

    def get_all(self) -> list[InfrastructureElement]:
        self._load_cache()
        return list(self._elements_cache.values())

    def get_by_id(self, uuid: Union[UUID, str]) -> Optional[InfrastructureElement]:
        self._load_cache()
        uuid_str = str(uuid)
        return self._elements_cache.get(uuid_str)

    def get_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        self._load_cache()
        return [
            element
            for element in self._elements_cache.values()
            if element.element_type == element_type
        ]

    def save(self, element: InfrastructureElement) -> None:
        self._load_cache()
        uuid_str = str(element.uuid)
        self._elements_cache[uuid_str] = element
        self._save_cache()

    def save_all(self, elements: list[InfrastructureElement]) -> None:
        self._load_cache()
        for element in elements:
            uuid_str = str(element.uuid)
            self._elements_cache[uuid_str] = element
        self._save_cache()

    def delete(self, uuid: Union[UUID, str]) -> None:
        self._load_cache()
        uuid_str = str(uuid)
        if uuid_str in self._elements_cache:
            del self._elements_cache[uuid_str]
            self._save_cache()

    def clear(self) -> None:
        self._elements_cache.clear()
        self._cache_loaded = True
        self._save_cache()

        # Delete all JSON files in the repository directory
        for file_path in self.repository_path.glob("*.json"):
            os.remove(file_path)

    def backup(self) -> str:
        """
        Creates a backup of the repository.

        Returns
        -------
        str
            Path to the backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.repository_path.parent / f"backup_{timestamp}"
        os.makedirs(backup_path, exist_ok=True)

        # Copy all files
        for file_path in self.repository_path.glob("*.json"):
            backup_file = backup_path / file_path.name
            with (
                open(file_path, "r", encoding="utf-8") as src,
                open(backup_file, "w", encoding="utf-8") as dst,
            ):
                dst.write(src.read())

        return str(backup_path)
