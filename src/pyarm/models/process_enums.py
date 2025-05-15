"""
Central definitions of enums for modeling infrastructure projects.
These enums are used for mapping parameters to process requirements.
"""

from enum import StrEnum


class ElementType(StrEnum):
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
    CABLE_SHAFT = "cable_shaft"


class ProcessEnum(StrEnum):
    """
    Central enum for process relevance of parameters.
    Used for mapping client-specific data to the canonical model.
    """

    UUID = "uuid"
    NAME = "name"
    ELEMENT_TYPE = "element_type"
    DOMAIN = "domain"

    # Geometric - Position
    # Point or Startpoint
    X_COORDINATE = "x_coordinate"
    Y_COORDINATE = "y_coordinate"
    Z_COORDINATE = "z_coordinate"
    X_ROTATION = "x_rotation"
    Y_ROTATION = "y_rotation"
    Z_ROTATION = "z_rotation"

    # Endpoint
    X_COORDINATE_END = "x_coordinate_end"
    Y_COORDINATE_END = "y_coordinate_end"
    Z_COORDINATE_END = "z_coordinate_end"
    X_ROTATION_END = "x_rotation"
    Y_ROTATION_END = "y_rotation"
    Z_ROTATION_END = "z_rotation"

    # General dimensions
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH = "depth"
    LENGTH = "length"
    DIAMETER = "diameter"
    RADIUS = "radius"
    ANGLE = "angle"
    SLOPE = "slope"

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

    # Sewer-specific
    SHAFT_MANHOLE_DIAMETER = "manhole_diameter"
    SHAFT_COVER_TYPE = "shaft_cover_type"
    SEWER_TYPE = "sewer_type"

    # Location/Positioning
    KILOMETER_POSITION = "kilometer_position"
    TRACK_REFERENCE = "track_reference"
    DISTANCE = "distance"
    START_KILOMETER = "start_kilometer"
    END_KILOMETER = "end_kilometer"

    # IFC data
    IFC_GLOBAL_ID = "ifc_global_id"
    IFC_TYPE = "ifc_type"

    # Construction phases
    CONSTRUCTION_PHASE_ID = "construction_phase_id"
    CONSTRUCTION_PHASE_NAME = "construction_phase_name"
    CONSTRUCTION_PHASE_START = "construction_phase_start"
    CONSTRUCTION_PHASE_END = "construction_phase_end"
