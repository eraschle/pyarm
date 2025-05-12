"""
Protocols (Interfaces) for the various components of the system.
"""

from typing import Any, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType, ProcessEnum

# Type variables for generic protocols
T = TypeVar("T", covariant=True)
TElement = TypeVar("TElement", bound=InfrastructureElement)


class DfaDataReader:
    @property
    def name(self) -> str:
        return "DFA Data Reader"

    @property
    def version(self) -> str:
        return "1.0"

    @property
    def supported_formats(self) -> list[str]:
        return ["AbwasserHaltung", "Abwasser_Schacht"]

    def can_handle(self, file_path: str) -> bool:
        pass

    def read_data(self, file_path: str) -> dict[str, Any]:
        return pd.read_excel(file_path, engine="openpyxl", sheet_name=None)


@runtime_checkable
class IDataConverter(Protocol[T]):
    @property
    def name(self) -> str:
        pass

    @property
    def version(self) -> str:
        pass

    @property
    def supported_types(self) -> list[str]:
        pass

    def can_convert(self, data: dict[str, Any]) -> bool:
        pass

    def convert(self, data: dict[str, Any]) -> T:
        pass


class IElementRepository(Protocol):
    def get_all(self) -> list[InfrastructureElement]:
        pass

    def get_by_id(self, uuid: UUID | str) -> InfrastructureElement | None:
        pass

    def get_by_type(self, element_type: ElementType) -> list[InfrastructureElement]:
        pass

    def save(self, element: InfrastructureElement) -> None:
        pass

    def save_all(self, elements: list[InfrastructureElement]) -> None:
        pass

    def delete(self, uuid: UUID | str) -> None:
        pass


class InfraElement(Protocol):
    name: str
    uuid: UUID
    element_type: ElementType


class HasClothoid(Protocol):
    @property
    def clothoid_parameter(self) -> float | None:
        pass

    @property
    def start_radius(self) -> float | None:
        pass

    @property
    def end_radius(self) -> float | None:
        pass

    def get_param(self, process_enum: ProcessEnum, default: Any = None) -> Any:
        pass

    def to_dict(self) -> dict[str, Any]:
        pass
