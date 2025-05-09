"""
Zentrale Definitionen von Enums für die Modellierung von Infrastrukturprojekten.
Diese Enums werden für die Zuordnung von Parametern zu Prozessanforderungen verwendet.
"""

from enum import Enum, auto


class ElementType(str, Enum):
    """Typen von Infrastrukturelementen"""

    UNDEFINED = "undefined"
    NONE = "no_element_type"
    FOUNDATION = "foundation"
    MAST = "mast"
    CANTILEVER = "cantilever"
    JOCH = "joch"
    TRACK = "track"
    SLEEPER = "sleeper"
    DRAINAGE_PIPE = "drainage_pipe"
    DRAINAGE_SHAFT = "drainage_shaft"
    BUILDING = "building"  # Neuer Elementtyp für FDK-Gebäudedaten


class ProcessEnum(str, Enum):
    """
    Zentrale Enum für die Prozessrelevanz von Parametern.
    Verwendet für die Zuordnung von Kundenspezifischen Daten zum kanonischen Modell.
    """

    # TODO Sollen Namen oder UUID Verwendet werden.
    # Wie können uns genellen Zugriff auf Paramter hilfreich sein
    # Allgemeine Identifikation
    UUID = "uuid"
    NAME = "name"
    ELEMENT_TYPE = "element_type"

    # Geometrische Grundlagen - Position
    X_COORDINATE = "x_coordinate"
    Y_COORDINATE = "y_coordinate"
    Z_COORDINATE = "z_coordinate"
    X_COORDINATE_END = "x_coordinate_end"
    Y_COORDINATE_END = "y_coordinate_end"
    Z_COORDINATE_END = "z_coordinate_end"

    # Ausrichtung
    AZIMUTH = "azimuth"
    ROTATION_X = "rotation_x"
    ROTATION_Y = "rotation_y"
    ROTATION_Z = "rotation_z"

    # Allgemeine Dimensionen
    WIDTH = "width"
    HEIGHT = "height"
    DEPTH = "depth"
    LENGTH = "length"
    DIAMETER = "diameter"

    # Material und Eigenschaften
    MATERIAL = "material"
    WEIGHT = "weight"

    # Fundament-spezifisch
    FOUNDATION_TYPE = "foundation_type"
    FOUNDATION_WIDTH = "foundation_width"
    FOUNDATION_HEIGHT = "foundation_height"
    FOUNDATION_DEPTH = "foundation_depth"

    # Mast-spezifisch
    MAST_TYPE = "mast_type"
    MAST_HEIGHT = "mast_height"
    MAST_PROFILE_TYPE = "mast_profile_type"

    # Ausleger-spezifisch
    CANTILEVER_TYPE = "cantilever_type"
    CANTILEVER_LENGTH = "cantilever_length"

    # Joch-spezifisch
    JOCH_TYPE = "joch_type"
    JOCH_SPAN = "joch_span"

    # Schienen-spezifisch
    TRACK_GAUGE = "track_gauge"
    TRACK_TYPE = "track_type"
    TRACK_CANT = "track_cant"

    # Kurvenparameter
    CLOTHOID_PARAMETER = "clothoid_parameter"
    START_RADIUS = "start_radius"
    END_RADIUS = "end_radius"

    # Schwellen-spezifisch
    SLEEPER_TYPE = "sleeper_type"
    SLEEPER_SPACING = "sleeper_spacing"

    # Entwässerung-spezifisch
    PIPE_DIAMETER = "pipe_diameter"
    PIPE_MATERIAL = "pipe_material"
    PIPE_SLOPE = "pipe_slope"
    SHAFT_DIAMETER = "shaft_diameter"
    SHAFT_MATERIAL = "shaft_material"
    SHAFT_DEPTH = "shaft_depth"
    SHAFT_COVER_TYPE = "shaft_cover_type"

    # Gebäude-spezifisch
    DESCRIPTION = "description"
    YEAR_BUILT = "year_built"
    RENOVATION_YEAR = "renovation_year"
    FLOORS = "floors"

    # Standort/Positionierung
    KILOMETER_POSITION = "kilometer_position"
    TRACK_REFERENCE = "track_reference"
    DISTANCE = "distance"
    START_KILOMETER = "start_kilometer"
    END_KILOMETER = "end_kilometer"
    RADIUS = "radius"

    # Spezifische Eigenschaften
    VOLUME = "volume"
    CAPACITY = "capacity"
    DRAINAGE_TYPE = "drainage_type"

    # IFC-Daten
    IFC_GLOBAL_ID = "ifc_global_id"
    IFC_TYPE = "ifc_type"
    IFC_MATERIAL = "ifc_material"
    IFC_CATEGORY = "ifc_category"

    # Bauphasen
    CONSTRUCTION_PHASE_ID = "construction_phase_id"
    CONSTRUCTION_PHASE_NAME = "construction_phase_name"
    CONSTRUCTION_PHASE_START = "construction_phase_start"
    CONSTRUCTION_PHASE_END = "construction_phase_end"


class UnitEnum(str, Enum):
    """Einheiten für Parameter"""

    METER = "m"
    CENTIMETER = "cm"
    MILLIMETER = "mm"
    DEGREE = "deg"
    RADIAN = "rad"
    KILOGRAM = "kg"
    TON = "t"
    PERCENT = "pct"
    PROMILLE = "‰"
    NEWTON = "N"
    KILONEWTON = "kN"
    CUBIC_METER = "m³"
    SQUARE_METER = "m²"
    KILOMETER = "km"
    NONE = ""


class ProcessRequirement(Enum):
    """Anforderungen verschiedener Prozesse an die Daten"""

    # Prozess 1: Einfache Visualisierung
    VISUALIZATION = auto()

    # Prozess 2: Detaillierte Berechnung
    CALCULATION = auto()
