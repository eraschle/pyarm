"""
TypeGuard functions for type checking and refinement.
"""

from typing import Any, TypeGuard, TypeVar

from pyarm.interfaces.element import HasClothoid
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.element_models import (
    Cantilever,
    CurvedTrack,
    Foundation,
    Joch,
    Mast,
    SewerPipe,
    SewerShaft,
    Sleeper,
    Track,
)
from pyarm.models.process_enums import ElementType

# Type variables for generic TypeGuards
T = TypeVar("T")
ElementT = TypeVar("ElementT", bound=InfrastructureElement)


def is_infrastructure_element(obj: Any) -> TypeGuard[InfrastructureElement]:
    """
    Checks if an object is an InfrastructureElement.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[InfrastructureElement]
        True if the object is an InfrastructureElement
    """
    return isinstance(obj, InfrastructureElement)


def is_foundation(obj: Any) -> TypeGuard[Foundation]:
    """
    Checks if an object is a Foundation.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Foundation]
        True if the object is a Foundation
    """
    return isinstance(obj, Foundation) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.FOUNDATION
    )


def is_mast(obj: Any) -> TypeGuard[Mast]:
    """
    Checks if an object is a Mast.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Mast]
        True if the object is a Mast
    """
    return isinstance(obj, Mast) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.MAST
    )


def is_cantilever(obj: Any) -> TypeGuard[Cantilever]:
    """
    Checks if an object is a Cantilever.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Cantilever]
        True if the object is a Cantilever
    """
    return isinstance(obj, Cantilever) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.CANTILEVER
    )


def is_joch(obj: Any) -> TypeGuard[Joch]:
    """
    Checks if an object is a Joch.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Joch]
        True if the object is a Joch
    """
    return isinstance(obj, Joch) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.JOCH
    )


def is_track(obj: Any) -> TypeGuard[Track]:
    """
    Checks if an object is a Track.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Track]
        True if the object is a Track
    """
    return isinstance(obj, Track) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.TRACK
    )


def is_curved_track(obj: Any) -> TypeGuard[CurvedTrack]:
    """
    Checks if an object is a CurvedTrack.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[CurvedTrack]
        True if the object is a CurvedTrack
    """
    return isinstance(obj, CurvedTrack)


def is_sleeper(obj: Any) -> TypeGuard[Sleeper]:
    """
    Checks if an object is a Sleeper.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[Sleeper]
        True if the object is a Sleeper
    """
    return isinstance(obj, Sleeper) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.SLEEPER
    )


def is_drainage_pipe(obj: Any) -> TypeGuard[SewerPipe]:
    """
    Checks if an object is a DrainagePipe.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[DrainagePipe]
        True if the object is a DrainagePipe
    """
    return isinstance(obj, SewerPipe) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.SEWER_SHAFT
    )


def is_drainage_shaft(obj: Any) -> TypeGuard[SewerShaft]:
    """
    Checks if an object is a DrainageShaft.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[DrainageShaft]
        True if the object is a DrainageShaft
    """
    return isinstance(obj, SewerShaft) or (
        isinstance(obj, InfrastructureElement) and obj.element_type == ElementType.SEWER_SHAFT
    )


def has_clothoid_capability(obj: Any) -> TypeGuard[HasClothoid]:
    """
    Checks if an object implements the Clothoid interface.

    Parameters
    ----------
    obj: Any
        Object to check

    Returns
    -------
    TypeGuard[HasClothoid]
        True if the object implements the Clothoid interface
    """
    return (
        hasattr(obj, "clothoid_parameter")
        and hasattr(obj, "start_radius")
        and hasattr(obj, "end_radius")
    )


def is_list_of_type(items: list[Any], element_type: type[T]) -> TypeGuard[list[T]]:
    """
    Checks if a list contains only elements of a specific type.

    Parameters
    ----------
    items: list[Any]
        List to check
    element_type: type[T]
        Type to check for

    Returns
    -------
    TypeGuard[list[T]]
        True if the list contains only elements of the specified type
    """
    return all(isinstance(item, element_type) for item in items)


def is_dict_of_type(items: dict[str, Any], element_type: type[T]) -> TypeGuard[dict[str, T]]:
    """
    Checks if a dictionary contains only values of a specific type.

    Parameters
    ----------
    items: dict[str, Any]
        Dictionary to check
    element_type: type[T]
        Type to check for

    Returns
    -------
    TypeGuard[dict[str, T]]
        True if the dictionary contains only values of the specified type
    """
    return all(isinstance(item, element_type) for item in items.values())


def ensure_type(obj: Any, expected_type: type[T]) -> T:
    """
    Ensures that an object has the expected type.
    If not, an exception is raised.

    Parameters
    ----------
    obj: Any
        Object to check
    expected_type: type[T]
        Expected type

    Returns
    -------
    T
        The object as an instance of the expected type

    Raises
    ------
    TypeError
        If the object does not have the expected type
    """
    if not isinstance(obj, expected_type):
        raise TypeError(f"Expected {expected_type.__name__}, got {type(obj).__name__}")
    return obj
