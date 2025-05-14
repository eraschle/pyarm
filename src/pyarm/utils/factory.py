"""
Factory methods for creating elements using the component system.
These factory methods are optimized to work with the new component-based design
and ensure that elements are correctly initialized with all necessary components.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from uuid import UUID, uuid4

from pyarm.components import (
    Dimension,
    ElementReference,
    LineLocation,
    PointLocation,
)
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.parameter import Parameter
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.utils import helpers as hlp

# Type variable for generic elements
T = TypeVar("T", bound=InfrastructureElement)


def determine_element_class(data: Dict[str, Any]) -> Type[Any]:
    """
    Determines the appropriate element class based on the element data.

    Parameters
    ----------
    data: Dict[str, Any]
        Dictionary with element data

    Returns
    -------
    Type[Any]
        Element class
    """
    # Runtime import to avoid circular imports
    from pyarm.models.element_models import (
        CurvedTrack,
        SewerPipe,
        SewerShaft,
        Foundation,
        Mast,
        Track,
    )

    # Determine element type using helper function
    element_type_value = hlp.extract_value(data, "element_type")

    if isinstance(element_type_value, str):
        element_type = hlp.resolve_element_type(element_type_value)
    elif isinstance(element_type_value, ElementType):
        element_type = element_type_value
    else:
        element_type = ElementType.UNDEFINED

    # Search parameter list for special properties
    parameters = data.get("parameters", [])

    # Check if it's a curve
    has_clothoid = any(p.get("process") == ProcessEnum.CLOTHOID_PARAMETER.value for p in parameters)

    # Check for start/end coordinates for linear elements
    has_end_coordinates = any(
        p.get("process")
        in [
            ProcessEnum.X_COORDINATE_END.value,
            ProcessEnum.Y_COORDINATE_END.value,
            ProcessEnum.Z_COORDINATE_END.value,
        ]
        for p in parameters
    )

    # Determine class based on element type and properties
    if element_type == ElementType.FOUNDATION:
        return Foundation
    elif element_type == ElementType.MAST:
        return Mast
    elif element_type == ElementType.TRACK:
        if has_clothoid:
            return CurvedTrack
        else:
            return Track
    elif element_type == ElementType.SEWER_PIPE:
        return SewerPipe
    elif element_type == ElementType.SEWER_SHAFT:
        return SewerShaft
    else:
        return InfrastructureElement


def create_element(data: dict[str, Any]) -> Any:
    """
    Creates an element based on the ElementType and element data
    and initializes the corresponding components.

    Parameters
    ----------
    data: dict[str, Any]
        Dictionary with element data

    Returns
    -------
    Any
        Created element with components
    """
    from pyarm.models.element_models import CurvedTrack, Mast, Track

    # Extract basic attributes using helper functions
    name = hlp.extract_value(data, "name", "Unknown", str)
    uuid_value = hlp.extract_value(data, "uuid")
    uuid = UUID(uuid_value) if uuid_value else uuid4()

    # Determine element type using helper functions
    element_type_value = hlp.extract_value(data, "element_type")
    if isinstance(element_type_value, str):
        element_type = hlp.resolve_element_type(element_type_value)
    elif isinstance(element_type_value, ElementType):
        element_type = element_type_value
    else:
        element_type = ElementType.UNDEFINED

    # Process parameters
    parameters = []
    for param_data in data.get("parameters", []):
        parameters.append(hlp.create_parameter_from(param_data))

    # Collect references
    references = {}
    for ref_key, ref_value in data.items():
        if ref_key.endswith("_uuid") and ref_value and ref_key != "uuid":
            if not isinstance(ref_value, UUID) and isinstance(ref_value, str):
                ref_value = UUID(ref_value)
            ref_type = ref_key.replace("_uuid", "")
            references[ref_type] = ref_value

    # Determine element class
    element_class = determine_element_class(data)

    # Create element
    element = element_class(
        name=name,
        uuid=uuid,
        element_type=element_type,
        parameters=parameters,
    )

    if isinstance(element, Mast) and "foundation" in references:
        foundation_uuid = references["foundation"]
        element.add_reference(Mast, foundation_uuid)

    if isinstance(element, (Track, CurvedTrack)) and "track" in references:
        track_uuid = references["track"]
        element.add_reference(type(element), track_uuid)

    # Add additional references
    for ref_type, ref_uuid in references.items():
        if ref_type not in ["uuid", "foundation", "track"]:
            element.add_reference(ref_type, ref_uuid)

    return element


def create_elements(element_data_list: list[dict[str, Any]]) -> list[Any]:
    """
    Creates multiple elements from a list of dictionaries
    and initializes all components.

    Parameters
    ----------
    element_data_list: list[dict[str, Any]]
        List of dictionaries with element data

    Returns
    -------
    list[Any]
        List of created elements with components
    """
    return [create_element(data) for data in element_data_list]


def create_component_based_element(
    name: str,
    element_type: ElementType,
    position: Optional[PointLocation] = None,
    line_location: Optional[LineLocation] = None,
    dimension: Optional[Dimension] = None,
    references: Optional[List[ElementReference]] = None,
    parameters: Optional[List[Parameter]] = None,
) -> Any:
    """
    Creates an element directly with components instead of parameters.
    This is the recommended way to create elements in the component system.

    Parameters
    ----------
    name: str
        Name of the element
    element_type: ElementType
        Type of the element
    position: Optional[PointLocation]
        Optional position component
    line_location: Optional[LineLocation]
        Optional line position component
    dimension: Optional[Dimension]
        Optional dimension component
    references: Optional[List[ElementReference]]
        Optional list of reference components
    parameters: Optional[List[Parameter]]
        Optional list of additional parameters

    Returns
    -------
    Any
        Created element with the specified components
    """
    # Runtime import to avoid circular imports
    from pyarm.models.element_models import (
        SewerPipe,
        SewerShaft,
        Foundation,
        Mast,
        Track,
    )

    # Choose element class based on type
    element_class = None
    if element_type == ElementType.FOUNDATION:
        element_class = Foundation
    elif element_type == ElementType.MAST:
        element_class = Mast
    elif element_type == ElementType.TRACK:
        element_class = Track
    elif element_type == ElementType.SEWER_PIPE:
        element_class = SewerPipe
    elif element_type == ElementType.SEWER_SHAFT:
        element_class = SewerShaft
    else:
        element_class = InfrastructureElement

    # Create element
    element = element_class(
        name=name,
        element_type=element_type,
        parameters=parameters or [],
    )

    # Add components
    if position:
        element.add_component(position)
    if line_location:
        element.add_component(line_location)
    if dimension:
        element.add_component(dimension)
    if references:
        for reference in references:
            element.add_component(reference)

    return element
