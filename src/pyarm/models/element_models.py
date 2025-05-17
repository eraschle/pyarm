"""
Specialized models for different types of infrastructure elements.
These models build upon the base class InfrastructureElement and add
element-specific functionality.
"""

import logging
from dataclasses import dataclass

from pyarm.components.dimension import Dimension, RectangularDimension, RoundDimension
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType

log = logging.getLogger(__name__)


@dataclass
class Foundation[TDimension: Dimension](InfrastructureElement[TDimension]):
    """Foundation element."""

    element_type: ElementType = ElementType.FOUNDATION


@dataclass
class Mast[TDimension: Dimension](InfrastructureElement[TDimension]):
    """Mast element with optional reference to foundation."""

    element_type: ElementType = ElementType.MAST


@dataclass
class Cantilever[TDimension: Dimension](InfrastructureElement[TDimension]):
    """Cantilever element with reference to mast."""

    element_type: ElementType = ElementType.CANTILEVER


@dataclass
class Joch(InfrastructureElement[RectangularDimension]):
    """Yoke element with references to two masts."""

    element_type: ElementType = ElementType.JOCH


@dataclass
class Track[TDimension: Dimension](InfrastructureElement[TDimension]):
    """Track element."""

    element_type: ElementType = ElementType.TRACK


@dataclass
class CurvedTrack[TDimension: Dimension](Track[TDimension]):
    """Curved track element with clothoid parameters."""

    element_type: ElementType = ElementType.TRACK


@dataclass
class Sleeper(InfrastructureElement[RectangularDimension]):
    """Sleeper element with reference to track."""

    element_type: ElementType = ElementType.SLEEPER


@dataclass
class SewerPipe(InfrastructureElement[RoundDimension]):
    """Drainage pipe element."""

    element_type: ElementType = ElementType.SEWER_PIPE


@dataclass
class SewerShaft(InfrastructureElement[RoundDimension]):
    """Drainage shaft element."""

    element_type: ElementType = ElementType.SEWER_SHAFT


@dataclass
class CableShaft[TDimension: Dimension](InfrastructureElement[TDimension]):
    """Cable shaft element."""

    element_type: ElementType = ElementType.CABLE_SHAFT
