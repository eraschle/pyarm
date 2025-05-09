"""
Specialized models for different types of infrastructure elements.
These models build upon the base class InfrastructureElement and add
element-specific functionality.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType
from pyarm.utils import coordinate as cs


@dataclass
class LinearElement(InfrastructureElement):
    """
    Base class for all linear elements (tracks, pipes, etc.).
    """

    def __post_init__(self):
        super().__post_init__()

    @property
    def length(self) -> Optional[float]:
        """Length of the element."""
        if self.dimension.has_length:
            return self.dimension.length
        return cs.calculate_length(*self.location.as_tuple())


@dataclass
class Foundation(InfrastructureElement):
    """Foundation element."""

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.FOUNDATION
        super().__post_init__()


@dataclass
class Mast(InfrastructureElement):
    """Mast element with optional reference to foundation."""

    foundation_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.MAST
        super().__post_init__()

        # Add reference to foundation if available
        if self.foundation_uuid:
            self.add_reference("foundation", self.foundation_uuid)


@dataclass
class Cantilever(InfrastructureElement):
    """Cantilever element with reference to mast."""

    mast_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.CANTILEVER
        super().__post_init__()

        # Add reference to mast if available
        if self.mast_uuid:
            self.add_reference("mast", self.mast_uuid)


@dataclass
class Joch(InfrastructureElement):
    """Yoke element with references to two masts."""

    mast_uuid_1: Optional[UUID] = None
    mast_uuid_2: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.JOCH
        super().__post_init__()

        # Add references to masts if available
        if self.mast_uuid_1:
            self.add_reference("mast", self.mast_uuid_1)
        if self.mast_uuid_2:
            self.add_reference("mast", self.mast_uuid_2)


@dataclass
class Track(InfrastructureElement):
    """Track element."""

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.TRACK
        super().__post_init__()


@dataclass
class CurvedTrack(Track):
    """Curved track element with clothoid parameters."""

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Sleeper(InfrastructureElement):
    """Sleeper element with reference to track."""

    track_uuid: Optional[UUID] = None

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.SLEEPER
        super().__post_init__()

        # Add reference to track if available
        if self.track_uuid:
            self.add_reference("track", self.track_uuid)


@dataclass
class DrainagePipe(LinearElement):
    """Drainage pipe element."""

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.DRAINAGE_PIPE
        super().__post_init__()


@dataclass
class DrainageShaft(InfrastructureElement):
    """Drainage shaft element."""

    def __post_init__(self):
        if self.element_type == ElementType.UNDEFINED:
            self.element_type = ElementType.DRAINAGE_SHAFT
        super().__post_init__()