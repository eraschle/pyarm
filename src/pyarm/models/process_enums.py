"""
Central definitions of enums for modeling infrastructure projects.
These enums are used for mapping parameters to process requirements.
"""

from enum import Enum, auto


class ElementType(str, Enum):
    """Types of infrastructure elements"""

    UNDEFINED = "undefined"
    FOUNDATION = "foundation"
    MAST = "mast"
    CANTILEVER = "cantilever"  # Cantilever
    JOCH = "joch"
    TRACK = "track"
    SLEEPER = "sleeper"
    DRAINAGE_PIPE = "drainage_pipe"
    DRAINAGE_SHAFT = "drainage_shaft"
    BUILDING = "building"


class ProcessEnum(str, Enum):
    """
    Central enum for process relevance of parameters.
    Used for mapping client-specific data to the canonical model.
    """

    UUID = "uuid"
    NAME = "name"
    ELEMENT_TYPE = "element_type"

    # Geometric fundamentals - Position
    X_COORDINATE = "x_coordinate"
    Y_COORDINATE = "y_coordinate"
    Z_COORDINATE = "z_coordinate"
    X_COORDINATE_END = "x_coordinate_end"
    Y_COORDINATE_END = "y_coordinate_end"
    Z_COORDINATE_END = "z_coordinate_end"

    # Orientation
    AZIMUTH = "azimuth"
    ROTATION_X = "rotation_x"
    ROTATION_Y = "rotation_y"
    ROTATION_Z = "rotation_z"

    # General dimensions
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH = "depth"
    LENGTH = "length"
    DIAMETER = "diameter"

    # Foundation-specific
    FOUNDATION_TYPE = "foundation_type"

    # Mast-specific
    MAST_TYPE = "mast_type"
    MAST_PROFILE_TYPE = "mast_profile_type"

    # Cantilever-specific
    CANTILEVER_TYPE = "cantilever_type"

    # Joch-specific
    JOCH_TYPE = "joch_type"
    JOCH_SPAN = "joch_span"

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
    PIPE_SLOPE = "pipe_slope"
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
    RADIUS = "radius"

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