"""
Unit Tests für die Enum-Definitionen.
"""

import unittest

from pyarm.models.parameter import UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum


class TestProcessEnum(unittest.TestCase):
    """Tests für die ProcessEnum-Klasse."""

    def test_process_enum_values(self):
        """Test: ProcessEnum-Werte sind korrekt definiert."""
        # Basisparameter vorhanden
        self.assertEqual(ProcessEnum.UUID.value, "uuid")
        self.assertEqual(ProcessEnum.NAME.value, "name")
        self.assertEqual(ProcessEnum.ELEMENT_TYPE.value, "element_type")

        # Koordinaten-Parameter
        self.assertEqual(ProcessEnum.X_COORDINATE.value, "x_coordinate")
        self.assertEqual(ProcessEnum.Y_COORDINATE.value, "y_coordinate")
        self.assertEqual(ProcessEnum.Z_COORDINATE.value, "z_coordinate")
        self.assertEqual(ProcessEnum.X_COORDINATE_END.value, "x_coordinate_end")
        self.assertEqual(ProcessEnum.Y_COORDINATE_END.value, "y_coordinate_end")
        self.assertEqual(ProcessEnum.Z_COORDINATE_END.value, "z_coordinate_end")

        # Foundation-Parameter
        self.assertEqual(ProcessEnum.FOUNDATION_TYPE.value, "foundation_type")
        self.assertEqual(ProcessEnum.WIDTH.value, "foundation_width")
        self.assertEqual(ProcessEnum.DEPTH.value, "foundation_depth")
        self.assertEqual(ProcessEnum.HEIGHT.value, "foundation_height")

        # Allgemeine Parameter
        self.assertEqual(ProcessEnum.WIDTH.value, "width")
        self.assertEqual(ProcessEnum.HEIGHT.value, "height")
        self.assertEqual(ProcessEnum.LENGTH.value, "length")


class TestElementType(unittest.TestCase):
    """Tests für die ElementType-Klasse."""

    def test_element_type_values(self):
        """Test: ElementType-Werte sind korrekt definiert."""
        self.assertEqual(ElementType.FOUNDATION.value, "foundation")
        self.assertEqual(ElementType.MAST.value, "mast")
        self.assertEqual(ElementType.CANTILEVER.value, "cantilever")
        self.assertEqual(ElementType.JOCH.value, "joch")
        self.assertEqual(ElementType.TRACK.value, "track")
        self.assertEqual(ElementType.SLEEPER.value, "sleeper")
        self.assertEqual(ElementType.DRAINAGE_PIPE.value, "drainage_pipe")
        self.assertEqual(ElementType.DRAINAGE_SHAFT.value, "drainage_shaft")


class TestUnitEnum(unittest.TestCase):
    """Tests für die UnitEnum-Klasse."""

    def test_unit_enum_values(self):
        """Test: UnitEnum-Werte sind korrekt definiert."""
        self.assertEqual(UnitEnum.NONE.value, "")
        self.assertEqual(UnitEnum.METER.value, "m")
        self.assertEqual(UnitEnum.MILLIMETER.value, "mm")
        self.assertEqual(UnitEnum.DEGREE.value, "°")
        self.assertEqual(UnitEnum.PROMILLE.value, "‰")
        self.assertEqual(UnitEnum.NEWTON.value, "N")
        self.assertEqual(UnitEnum.KILONEWTON.value, "kN")


if __name__ == "__main__":
    unittest.main()
