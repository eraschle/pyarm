"""
TypeGuard-Funktionen für die Typprüfung und -verfeinerung.
"""

from typing import Any, TypeGuard, TypeVar

from ..models.base_models import InfrastructureElement
from ..models.element_models import (
    Foundation,
    Mast,
    Cantilever,
    Joch,
    Track,
    CurvedTrack,
    Sleeper,
    DrainagePipe,
    DrainageShaft,
)
from ..interfaces.protocols import HasClothoid
from ..enums.process_enums import ElementType


# Typvariablen für generische TypeGuards
T = TypeVar("T")
ElementT = TypeVar("ElementT", bound=InfrastructureElement)


def is_infrastructure_element(obj: Any) -> TypeGuard[InfrastructureElement]:
    """
    Prüft, ob ein Objekt ein InfrastructureElement ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein InfrastructureElement ist
    """
    return isinstance(obj, InfrastructureElement)


def is_foundation(obj: Any) -> TypeGuard[Foundation]:
    """
    Prüft, ob ein Objekt ein Foundation ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Foundation ist
    """
    return isinstance(obj, Foundation) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.FOUNDATION
    )


def is_mast(obj: Any) -> TypeGuard[Mast]:
    """
    Prüft, ob ein Objekt ein Mast ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Mast ist
    """
    return isinstance(obj, Mast) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.MAST
    )


def is_cantilever(obj: Any) -> TypeGuard[Cantilever]:
    """
    Prüft, ob ein Objekt ein Cantilever ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Cantilever ist
    """
    return isinstance(obj, Cantilever) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.CANTILEVER
    )


def is_joch(obj: Any) -> TypeGuard[Joch]:
    """
    Prüft, ob ein Objekt ein Joch ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Joch ist
    """
    return isinstance(obj, Joch) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.JOCH
    )


def is_track(obj: Any) -> TypeGuard[Track]:
    """
    Prüft, ob ein Objekt ein Track ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Track ist
    """
    return isinstance(obj, Track) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.TRACK
    )


def is_curved_track(obj: Any) -> TypeGuard[CurvedTrack]:
    """
    Prüft, ob ein Objekt ein CurvedTrack ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein CurvedTrack ist
    """
    return isinstance(obj, CurvedTrack)


def is_sleeper(obj: Any) -> TypeGuard[Sleeper]:
    """
    Prüft, ob ein Objekt ein Sleeper ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein Sleeper ist
    """
    return isinstance(obj, Sleeper) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.SLEEPER
    )


def is_drainage_pipe(obj: Any) -> TypeGuard[DrainagePipe]:
    """
    Prüft, ob ein Objekt ein DrainagePipe ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein DrainagePipe ist
    """
    return isinstance(obj, DrainagePipe) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.DRAINAGE_PIPE
    )


def is_drainage_shaft(obj: Any) -> TypeGuard[DrainageShaft]:
    """
    Prüft, ob ein Objekt ein DrainageShaft ist.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt ein DrainageShaft ist
    """
    return isinstance(obj, DrainageShaft) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.DRAINAGE_SHAFT
    )


def has_clothoid_capability(obj: Any) -> TypeGuard[HasClothoid]:
    """
    Prüft, ob ein Objekt die Clothoid-Schnittstelle implementiert.

    Args:
        obj: Zu prüfendes Objekt

    Returns:
        True, wenn das Objekt die Clothoid-Schnittstelle implementiert
    """
    return (
        hasattr(obj, "clothoid_parameter")
        and hasattr(obj, "start_radius")
        and hasattr(obj, "end_radius")
    )


def is_list_of_type(items: list[Any], element_type: type[T]) -> TypeGuard[list[T]]:
    """
    Prüft, ob eine Liste nur Elemente eines bestimmten Typs enthält.

    Args:
        items: Zu prüfende Liste
        element_type: Zu prüfender Typ

    Returns:
        True, wenn die Liste nur Elemente des angegebenen Typs enthält
    """
    return all(isinstance(item, element_type) for item in items)


def ensure_type(obj: Any, expected_type: type[T]) -> T:
    """
    Stellt sicher, dass ein Objekt den erwarteten Typ hat.
    Wenn nicht, wird eine Ausnahme ausgelöst.

    Args:
        obj: Zu prüfendes Objekt
        expected_type: Erwarteter Typ

    Returns:
        Das Objekt als Instanz des erwarteten Typs

    Raises:
        TypeError: Wenn das Objekt nicht den erwarteten Typ hat
    """
    if not isinstance(obj, expected_type):
        raise TypeError(f"Expected {expected_type.__name__}, got {type(obj).__name__}")
    return obj
