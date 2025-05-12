"""
Central definitions of enums for modeling infrastructure projects.
These enums are used for mapping parameters to process requirements.
"""

from enum import Enum


class ElementType(str, Enum):
    """Types of infrastructure elements"""

    UNDEFINED = "undefined"
    FOUNDATION = "foundation"
    MAST = "mast"
    CANTILEVER = "cantilever"  # Cantilever
    JOCH = "joch"
    TRACK = "track"
    SLEEPER = "sleeper"
    SEWER_PIPE = "sewer_pipe"
    SEWER_SHAFT = "sewer_shaft"
    BUILDING = "building"


class ProcessEnum(str, Enum):
    """
    Central enum for process relevance of parameters.
    Used for mapping client-specific data to the canonical model.
    """

    UUID = "uuid"
    NAME = "name"
    ELEMENT_TYPE = "element_type"

    # Geometric - Position
    # Point or Startpoint
    X_COORDINATE = "x"
    Y_COORDINATE = "y"
    Z_COORDINATE = "z"
    X_ROTATION = "x_rotation"
    Y_ROTATION = "y_rotation"
    Z_ROTATION = "z_rotation"

    # Endpoint
    X_COORDINATE_END = "x"
    Y_COORDINATE_END = "y"
    Z_COORDINATE_END = "z"
    X_ROTATION_END = "x_rotation"
    Y_ROTATION_END = "y_rotation"
    Z_ROTATION_END = "z_rotation"

    # General dimensions
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH = "depth"
    LENGTH = "length"
    DIAMETER = "diameter"
    SLOPE = "slope"
    RADIUS = "radius"

    # Foundation-specific
    FOUNDATION_TYPE = "foundation_type"
    FOUNDATION_TO_MAST_UUID = "foundation_to_mast_uuid"

    # Mast-specific
    MAST_TYPE = "mast_type"
    MAST_PROFILE_TYPE = "mast_profile_type"
    MAST_TO_FOUNDATION_UUID = "mast_to_foundation_uuid"
    MAST_TO_CANTILEVER_UUID = "mast_to_cantilever_uuid"
    MAST_TO_JOCH_UUID = "mast_to_joch_uuid"

    # Cantilever-specific
    CANTILEVER_TYPE = "cantilever_type"
    CANTILEVER_TO_MAST_UUID = "cantilever_to_mast_uuid"

    # Joch-specific
    JOCH_TYPE = "joch_type"
    JOCH_SPAN = "joch_span"
    JOCH_TO_MAST_UUID = "joch_to_mast_uuid"

    # Track-specific
    TRACK_GAUGE = "track_gauge"
    TRACK_TYPE = "track_type"
    TRACK_CANT = "track_cant"

    # Curve parameters
    CLOTHOID_PARAMETER = "clothoid_parameter"
    START_RADIUS = "start_radius"
    END_RADIUS = "end_radius"

    # Sleeper-specific
    SLEEPER_TYPE = "sleeper_type"
    SLEEPER_SPACING = "sleeper_spacing"

    # Drainage-specific
    PIPE_MATERIAL = "pipe_material"
    SHAFT_MANHOLE_DIAMETER = "manhole_diameter"
    SHAFT_COVER_TYPE = "shaft_cover_type"

    # Building-specific
    DESCRIPTION = "description"
    YEAR_BUILT = "year_built"
    RENOVATION_YEAR = "renovation_year"
    FLOORS = "floors"

    # Location/Positioning
    KILOMETER_POSITION = "kilometer_position"
    TRACK_REFERENCE = "track_reference"
    DISTANCE = "distance"
    START_KILOMETER = "start_kilometer"
    END_KILOMETER = "end_kilometer"

    # Specific properties
    VOLUME = "volume"
    CAPACITY = "capacity"
    DRAINAGE_TYPE = "drainage_type"

    # IFC data
    IFC_GLOBAL_ID = "ifc_global_id"
    IFC_TYPE = "ifc_type"
    IFC_MATERIAL = "ifc_material"
    IFC_CATEGORY = "ifc_category"

    # Construction phases
    CONSTRUCTION_PHASE_ID = "construction_phase_id"
    CONSTRUCTION_PHASE_NAME = "construction_phase_name"
    CONSTRUCTION_PHASE_START = "construction_phase_start"
    CONSTRUCTION_PHASE_END = "construction_phase_end"
