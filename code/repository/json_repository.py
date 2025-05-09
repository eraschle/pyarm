"""
JSON-basiertes Repository für Infrastrukturelemente.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from ..common.enums.process_enums import ElementType
from ..common.models.base_models import InfrastructureElement
from ..common.utils.factory import create_element


class JsonElementRepository:
    """
    Repository für die Speicherung von Infrastrukturelementen in JSON-Dateien.
    """

    def __init__(self, repository_path: str):
        """
        Initialisiert das Repository.

        Args:
            repository_path: Pfad zum Repository-Verzeichnis
        """
        self.repository_path = Path(repository_path)
        self.ensure_directory_exists()

        # In-Memory-Cache für bessere Performance
        self._elements_cache: Dict[str, InfrastructureElement] = {}
        self._cache_loaded = False

    def ensure_directory_exists(self) -> None:
        """
        Stellt sicher, dass das Repository-Verzeichnis existiert.
        """
        os.makedirs(self.repository_path, exist_ok=True)

    def _load_cache(self) -> None:
        """
        Lädt alle Elemente in den Cache.
        """
        if self._cache_loaded:
            return

        self._elements_cache.clear()

        # Alle JSON-Dateien im Repository-Verzeichnis laden
        for file_path in self.repository_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    elements_data = json.load(f)

                if isinstance(elements_data, list):
                    for element_data in elements_data:
                        element = create_element(element_data)
                        uuid_str = str(element.uuid)
                        self._elements_cache[uuid_str] = element
                elif isinstance(elements_data, dict):
                    element = create_element(elements_data)
                    uuid_str = str(element.uuid)
                    self._elements_cache[uuid_str] = element
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        self._cache_loaded = True

    def _save_cache(self) -> None:
        """
        Speichert den Cache in Dateien.
        """
        # Elemente nach Typ gruppieren
        elements_by_type: Dict[ElementType, List[InfrastructureElement]] = {}
        for element in self._elements_cache.values():
            if element.element_type not in elements_by_type:
                elements_by_type[element.element_type] = []
            elements_by_type[element.element_type].append(element)

        # Für jeden Typ eine Datei erstellen
        for element_type, elements in elements_by_type.items():
            file_path = self.repository_path / f"{element_type.value}.json"
            elements_data = [element.to_dict() for element in elements]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(elements_data, f, indent=2)

    def get_all(self) -> List[InfrastructureElement]:
        """
        Ruft alle Elemente ab.

        Returns:
            Liste aller Elemente
        """
        self._load_cache()
        return list(self._elements_cache.values())

    def get_by_id(self, uuid: Union[UUID, str]) -> Optional[InfrastructureElement]:
        """
        Ruft ein Element anhand seiner UUID ab.

        Args:
            uuid: UUID des Elements

        Returns:
            Das gefundene Element oder None
        """
        self._load_cache()
        uuid_str = str(uuid)
        return self._elements_cache.get(uuid_str)

    def get_by_type(self, element_type: ElementType) -> List[InfrastructureElement]:
        """
        Ruft Elemente eines bestimmten Typs ab.

        Args:
            element_type: Typ der abzurufenden Elemente

        Returns:
            Liste der gefundenen Elemente
        """
        self._load_cache()
        return [
            element
            for element in self._elements_cache.values()
            if element.element_type == element_type
        ]

    def save(self, element: InfrastructureElement) -> None:
        """
        Speichert ein Element.

        Args:
            element: Zu speicherndes Element
        """
        self._load_cache()
        uuid_str = str(element.uuid)
        self._elements_cache[uuid_str] = element
        self._save_cache()

    def save_all(self, elements: List[InfrastructureElement]) -> None:
        """
        Speichert mehrere Elemente.

        Args:
            elements: Zu speichernde Elemente
        """
        self._load_cache()
        for element in elements:
            uuid_str = str(element.uuid)
            self._elements_cache[uuid_str] = element
        self._save_cache()

    def delete(self, uuid: Union[UUID, str]) -> None:
        """
        Löscht ein Element.

        Args:
            uuid: UUID des zu löschenden Elements
        """
        self._load_cache()
        uuid_str = str(uuid)
        if uuid_str in self._elements_cache:
            del self._elements_cache[uuid_str]
            self._save_cache()

    def clear(self) -> None:
        """
        Löscht alle Elemente.
        """
        self._elements_cache.clear()
        self._cache_loaded = True
        self._save_cache()

        # Alle JSON-Dateien im Repository-Verzeichnis löschen
        for file_path in self.repository_path.glob("*.json"):
            os.remove(file_path)

    def backup(self) -> str:
        """
        Erstellt ein Backup des Repositories.

        Returns:
            Pfad zum Backup-Verzeichnis
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.repository_path.parent / f"backup_{timestamp}"
        os.makedirs(backup_path, exist_ok=True)

        # Alle Dateien kopieren
        for file_path in self.repository_path.glob("*.json"):
            backup_file = backup_path / file_path.name
            with (
                open(file_path, "r", encoding="utf-8") as src,
                open(backup_file, "w", encoding="utf-8") as dst,
            ):
                dst.write(src.read())

        return str(backup_path)
