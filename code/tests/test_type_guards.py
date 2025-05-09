"""
Unit Tests für die Type-Guards.
"""

import unittest

from ..common.models.element_models import (
    Foundation,
    Mast,
    Cantilever,
    Joch,
    Track,
    CurvedTrack,
    DrainagePipe,
    DrainageShaft,
)
from ..common.utils.type_guards import (
    is_foundation,
    is_mast,
    is_cantilever,
    is_joch,
    is_track,
    is_curved_track,
    is_drainage_pipe,
    is_drainage_shaft,
    has_clothoid_capability,
)
from ..common.models.base_models import InfrastructureElement
from ..common.enums.process_enums import ElementType, ProcessEnum


class TestTypeGuards(unittest.TestCase):
    """Tests für die Type-Guards."""

    def setUp(self):
        """Test-Setup mit Beispielelementen."""
        self.foundation = Foundation(name="TestFoundation")
        self.mast = Mast(name="TestMast")
        self.cantilever = Cantilever(name="TestCantilever")
        self.joch = Joch(name="TestJoch")
        self.track = Track(name="TestTrack")
        self.curved_track = CurvedTrack(name="TestCurvedTrack")
        self.drainage_pipe = DrainagePipe(name="TestDrainagePipe")
        self.drainage_shaft = DrainageShaft(name="TestDrainageShaft")

        # Element mit generischem Typ
        self.generic_foundation = InfrastructureElement(
            name="GenericFoundation", element_type=ElementType.FOUNDATION
        )

        # Element, das nicht dem Typ entspricht
        self.not_foundation = InfrastructureElement(
            name="NotFoundation", element_type=ElementType.MAST
        )

    def test_is_foundation(self):
        """Test: is_foundation Type-Guard."""
        # Spezifische Foundation-Klasse
        self.assertTrue(is_foundation(self.foundation))

        # Generisches Element mit Foundation-Typ
        self.assertTrue(is_foundation(self.generic_foundation))

        # Andere Elementtypen
        self.assertFalse(is_foundation(self.mast))
        self.assertFalse(is_foundation(self.not_foundation))

    def test_is_mast(self):
        """Test: is_mast Type-Guard."""
        self.assertTrue(is_mast(self.mast))

        # Generisches Element mit Mast-Typ
        generic_mast = InfrastructureElement(name="GenericMast", element_type=ElementType.MAST)
        self.assertTrue(is_mast(generic_mast))

        # Andere Elementtypen
        self.assertFalse(is_mast(self.foundation))

    def test_is_cantilever(self):
        """Test: is_cantilever Type-Guard."""
        self.assertTrue(is_cantilever(self.cantilever))
        self.assertFalse(is_cantilever(self.mast))

    def test_is_joch(self):
        """Test: is_joch Type-Guard."""
        self.assertTrue(is_joch(self.joch))
        self.assertFalse(is_joch(self.mast))

    def test_is_track(self):
        """Test: is_track Type-Guard."""
        self.assertTrue(is_track(self.track))
        self.assertTrue(is_track(self.curved_track))  # CurvedTrack ist auch ein Track
        self.assertFalse(is_track(self.foundation))

    def test_is_curved_track(self):
        """Test: is_curved_track Type-Guard."""
        self.assertTrue(is_curved_track(self.curved_track))
        self.assertFalse(is_curved_track(self.track))  # Track ist kein CurvedTrack

    def test_is_drainage_pipe(self):
        """Test: is_drainage_pipe Type-Guard."""
        self.assertTrue(is_drainage_pipe(self.drainage_pipe))
        self.assertFalse(is_drainage_pipe(self.drainage_shaft))

    def test_is_drainage_shaft(self):
        """Test: is_drainage_shaft Type-Guard."""
        self.assertTrue(is_drainage_shaft(self.drainage_shaft))
        self.assertFalse(is_drainage_shaft(self.drainage_pipe))

    def test_has_clothoid_capability(self):
        """Test: has_clothoid_capability Type-Guard."""
        # CurvedTrack hat Clothoid-Kapazität
        self.assertTrue(has_clothoid_capability(self.curved_track))

        # Normaler Track hat keine Clothoid-Kapazität
        self.assertFalse(has_clothoid_capability(self.track))

        # Dynamisch Clothoid-Kapazität hinzufügen
        self.track.set_param(ProcessEnum.CLOTHOID_PARAMETER, 300.0)
        self.track.set_param(ProcessEnum.START_RADIUS, 1000.0)
        self.track.set_param(ProcessEnum.END_RADIUS, 800.0)

        # Nach dem Hinzufügen der Parameter sollte has_clothoid_capability auch für normalen Track true sein
        self.assertTrue(has_clothoid_capability(self.track))

        # Für andere Typen sollte es immer false sein
        self.assertFalse(has_clothoid_capability(self.foundation))


if __name__ == "__main__":
    unittest.main()
