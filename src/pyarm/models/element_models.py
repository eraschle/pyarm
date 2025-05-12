"""
Specialized models for different types of infrastructure elements.
These models build upon the base class InfrastructureElement and add
element-specific functionality.
"""

import logging
from dataclasses import dataclass
from typing import Type

from pyarm.components.dimension import RectangularDimension
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.errors import PyArmReferenceError
from pyarm.models.parameter import Parameter
from pyarm.models.process_enums import ElementType, ProcessEnum

log = logging.getLogger(__name__)


def get_reference_to_type(process_enum: ProcessEnum) -> str | None:
    """Get a list of process enums that are used for referencing."""
    parts = process_enum.value.split("_")
    to_index = parts.index("TO") if "TO" in parts else -1
    if to_index == -1:
        log.warning(f"{process_enum.value} seems not to be a reference. Does not contain 'TO'.")
        return None
    return "_".join(parts[to_index + 1 :])


def get_reference_to_element_type(proc_enum: ProcessEnum) -> Type[InfrastructureElement] | None:
    """Get a list of process enums that are used for referencing."""
    element_type_name = get_reference_to_type(proc_enum)
    if not element_type_name:
        return None
    element_type_name = "".join([part.capitalize() for part in element_type_name.split("_")])
    for clazz in InfrastructureElement.__subclasses__():
        if clazz.__name__ != element_type_name:
            continue
        return clazz
    sub_classes = [cls.__name__ for cls in InfrastructureElement.__subclasses__()]
    type_name = element_type_name
    proc_name = proc_enum.value
    log.warning(f"{type_name} [{proc_name}] not found in InfrastructureElement: {sub_classes}")
    message = f"Could not find element type {element_type_name} for process enum: {proc_enum}"
    raise PyArmReferenceError(message=message)


def get_reference_process_enums(element_type: Type["InfrastructureElement"]) -> list[ProcessEnum]:
    """Get a list of process enums that are used for referencing."""
    references_to = []
    element_type_name = f"{element_type.__name__.upper()}_TO_"
    for proc_enum in ProcessEnum:
        if not proc_enum.value.startswith(element_type_name):
            continue
        references_to.append(proc_enum)
    return references_to


def add_references_to(reference_params: list[Parameter], element: InfrastructureElement):
    """Get a list of process enums that are used for referencing."""
    for param in reference_params:
        if not param.has_value or param.process is None:
            continue
        reference_type = get_reference_to_element_type(param.process)
        if reference_type is None:
            log.warning(f"Could not find reference type for process enum: {param.process}")
            continue
        element.add_reference(reference_type=reference_type, referenced_uuid=param.value)


def add_references_to_other_elements(element: InfrastructureElement):
    """Get a list of process enums that are used for referencing."""
    element_type = type(element)
    for proc_enum in get_reference_process_enums(element_type):
        if not element.has_param(process_enum=proc_enum):
            continue
        params = element.get_reference_params(process_enum=proc_enum)
        add_references_to(reference_params=params, element=element)


@dataclass
class Foundation(InfrastructureElement[RectangularDimension]):
    """Foundation element."""

    element_type: ElementType = ElementType.FOUNDATION

    def __post_init__(self):
        super().__post_init__()
        add_references_to_other_elements(self)


@dataclass
class Mast(InfrastructureElement):
    """Mast element with optional reference to foundation."""

    element_type: ElementType = ElementType.MAST

    def __post_init__(self):
        super().__post_init__()
        add_references_to_other_elements(self)


@dataclass
class Cantilever(InfrastructureElement):
    """Cantilever element with reference to mast."""

    element_type: ElementType = ElementType.CANTILEVER

    def __post_init__(self):
        super().__post_init__()
        add_references_to_other_elements(self)


@dataclass
class Joch(InfrastructureElement):
    """Yoke element with references to two masts."""

    element_type: ElementType = ElementType.JOCH

    def __post_init__(self):
        super().__post_init__()
        add_references_to_other_elements(self)


@dataclass
class Track(InfrastructureElement):
    """Track element."""

    element_type: ElementType = ElementType.TRACK

    def __post_init__(self):
        super().__post_init__()


@dataclass
class CurvedTrack(Track):
    """Curved track element with clothoid parameters."""

    element_type: ElementType = ElementType.TRACK

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Sleeper(InfrastructureElement):
    """Sleeper element with reference to track."""

    element_type: ElementType = ElementType.SLEEPER

    def __post_init__(self):
        super().__post_init__()


@dataclass
class DrainagePipe(InfrastructureElement):
    """Drainage pipe element."""

    element_type: ElementType = ElementType.SEWER_SHAFT

    def __post_init__(self):
        super().__post_init__()


@dataclass
class DrainageShaft(InfrastructureElement):
    """Drainage shaft element."""

    element_type: ElementType = ElementType.SEWER_SHAFT

    def __post_init__(self):
        super().__post_init__()
