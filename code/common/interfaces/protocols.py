"""
Protokolle (Interfaces) für die verschiedenen Komponenten des Systems.
"""

from typing import Any, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from ..enums.process_enums import ElementType, ProcessEnum
from ..models.base_models import InfrastructureElement

# Typvariablen für generische Protokolle
T = TypeVar("T", covariant=True)
TElement = TypeVar("TElement", bound=InfrastructureElement)


# Reader-Protokolle
@runtime_checkable
class IDataReader(Protocol):
    """
    Protokoll für Komponenten, die Daten aus einer Quelle lesen können.
    Verschiedene Datenquellen implementieren dieses Protokoll.
    """

    @property
    def name(self) -> str:
        """Name des Lesers"""
        ...

    @property
    def version(self) -> str:
        """Version des Lesers"""
        ...

    @property
    def supported_formats(self) -> list[str]:
        """Liste der unterstützten Dateiformate"""
        ...

    def can_handle(self, file_path: str) -> bool:
        """
        Prüft, ob dieser Reader die angegebene Datei verarbeiten kann.

        Args:
            file_path: Pfad zur Datei

        Returns:
            True, wenn dieser Reader die Datei verarbeiten kann
        """
        ...

    def read_data(self, file_path: str) -> dict[str, Any]:
        """
        Liest Daten aus der angegebenen Datei.

        Args:
            file_path: Pfad zur Datei

        Returns:
            Dictionary mit den gelesenen Daten
        """
        ...


# Converter-Protokolle
@runtime_checkable
class IDataConverter(Protocol[T]):
    """
    Protokoll für Komponenten, die Daten in ein anderes Format konvertieren können.
    """

    @property
    def name(self) -> str:
        """Name des Konverters"""
        ...

    @property
    def version(self) -> str:
        """Version des Konverters"""
        ...

    @property
    def supported_types(self) -> list[str]:
        """Liste der unterstützten Datentypen"""
        ...

    def can_convert(self, data: dict[str, Any]) -> bool:
        """
        Prüft, ob dieser Konverter die angegebenen Daten konvertieren kann.

        Args:
            data: Zu konvertierende Daten

        Returns:
            True, wenn dieser Konverter die Daten konvertieren kann
        """
        ...

    def convert(self, data: dict[str, Any]) -> T:
        """
        Konvertiert die angegebenen Daten.

        Args:
            data: Zu konvertierende Daten

        Returns:
            Konvertierte Daten
        """
        ...


# Repository-Protokolle
@runtime_checkable
class IElementRepository(Protocol):
    """
    Protokoll für Komponenten, die Elemente speichern und abrufen können.
    """

    def get_all(self) -> list[InfrastructureElement]:
        """
        Ruft alle Elemente ab.

        Returns:
            Liste aller Elemente
        """
        ...

    def get_by_id(self, uuid: UUID | str) -> InfrastructureElement | None:
        """
        Ruft ein Element anhand seiner UUID ab.

        Args:
            uuid: UUID des Elements

        Returns:
            Das gefundene Element oder None
        """
        ...

    def get_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        """
        Ruft Elemente eines bestimmten Typs ab.

        Args:
            element_type: Typ der abzurufenden Elemente

        Returns:
            Liste der gefundenen Elemente
        """
        ...

    def save(self, element: InfrastructureElement) -> None:
        """
        Speichert ein Element.

        Args:
            element: Zu speicherndes Element
        """
        ...

    def save_all(self, elements: list[InfrastructureElement]) -> None:
        """
        Speichert mehrere Elemente.

        Args:
            elements: Zu speichernde Elemente
        """
        ...

    def delete(self, uuid: UUID | str) -> None:
        """
        Löscht ein Element.

        Args:
            uuid: UUID des zu löschenden Elements
        """
        ...


# Service-Protokolle
@runtime_checkable
class IElementService(Protocol):
    """
    Protokoll für Komponenten, die Geschäftslogik für Elemente implementieren.
    """

    def get_element(self, uuid: UUID | str) -> InfrastructureElement | None:
        """
        Ruft ein Element ab.

        Args:
            uuid: UUID des Elements

        Returns:
            Das gefundene Element oder None
        """
        ...

    def get_elements_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        """
        Ruft Elemente eines bestimmten Typs ab.

        Args:
            element_type: Typ der abzurufenden Elemente

        Returns:
            Liste der gefundenen Elemente
        """
        ...

    def create_element(self, element_data: dict[str, Any]) -> InfrastructureElement:
        """
        Erstellt ein neues Element.

        Args:
            element_data: Daten für das neue Element

        Returns:
            Das erstellte Element
        """
        ...

    def update_element(
        self, uuid: UUID | str, element_data: dict[str, Any]
    ) -> InfrastructureElement | None:
        """
        Aktualisiert ein Element.

        Args:
            uuid: UUID des zu aktualisierenden Elements
            element_data: Neue Daten für das Element

        Returns:
            Das aktualisierte Element oder None
        """
        ...

    def delete_element(self, uuid: UUID | str) -> bool:
        """
        Löscht ein Element.

        Args:
            uuid: UUID des zu löschenden Elements

        Returns:
            True, wenn das Element gelöscht wurde
        """
        ...


@runtime_checkable
class InfraElement(Protocol):
    name: str
    uuid: UUID
    element_type: ElementType


# Kapazitäts-Protokolle (für spezifische Funktionalitäten)
@runtime_checkable
class HasClothoid(Protocol):
    """
    Protokoll für Elemente, die Klothoiden-Funktionalität haben.
    Wird für funktionale Klassifikation statt Vererbung verwendet.
    """

    @property
    def clothoid_parameter(self) -> float | None:
        """Klothoidenparameter"""
        ...

    @property
    def start_radius(self) -> float | None:
        """Startradius"""
        ...

    @property
    def end_radius(self) -> float | None:
        """Endradius"""
        ...

    def get_param(self, process_enum: ProcessEnum, default: Any = None) -> Any:
        """
        Gibt den Wert eines Parameters basierend auf dem Prozess-Enum zurück.

        Args:
            process_enum: Das ProcessEnum des gesuchten Parameters
            default: Standardwert, falls der Parameter nicht gefunden wird

        Returns:
            Der Wert des Parameters oder der Standardwert
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Konvertiert das Element in ein Dictionary zur Serialisierung.

        Returns:
            Dictionary mit allen Attributen und Parametern
        """
        ...
