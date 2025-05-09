"""
Unit Tests für die spezialisierten Modellklassen der Infrastrukturelemente.
"""

import unittest
from uuid import uuid4, UUID

from ..common.models.element_models import Foundation, Mast, Cantilever, Joch, Track, CurvedTrack
from ..common.enums.process_enums import ProcessEnum, ElementType


class TestFoundation(unittest.TestCase):
    """Tests für die Foundation-Klasse."""

    def test_create_foundation(self):
        """Test: Erstellung eines Fundaments."""
        foundation = Foundation(name="TestFoundation")

        self.assertEqual(foundation.name, "TestFoundation")
        self.assertEqual(foundation.element_type, ElementType.FOUNDATION)
        self.assertIsInstance(foundation.uuid, UUID)

    def test_foundation_properties(self):
        """Test: Foundation-spezifische Properties."""
        foundation = Foundation(name="PropertyTest")

        # Properties setzen
        foundation.foundation_type = "Typ A"
        foundation.width = 1.5
        foundation.height = 1.0
        foundation.depth = 2.0

        # Geometrie-Koordinaten setzen
        foundation.east = 2600000.0
        foundation.north = 1200000.0
        foundation.altitude = 456.78

        # Properties prüfen
        self.assertEqual(foundation.foundation_type, "Typ A")
        self.assertEqual(foundation.width, 1.5)
        self.assertEqual(foundation.height, 1.0)
        self.assertEqual(foundation.depth, 2.0)
        self.assertEqual(foundation.east, 2600000.0)
        self.assertEqual(foundation.north, 1200000.0)
        self.assertEqual(foundation.altitude, 456.78)

        # Parameter-Zugriff prüfen
        self.assertEqual(foundation.get_param(ProcessEnum.FOUNDATION_TYPE), "Typ A")
        self.assertEqual(foundation.get_param(ProcessEnum.FOUNDATION_WIDTH), 1.5)
        self.assertEqual(foundation.get_param(ProcessEnum.FOUNDATION_HEIGHT), 1.0)
        self.assertEqual(foundation.get_param(ProcessEnum.FOUNDATION_DEPTH), 2.0)
        self.assertEqual(foundation.get_param(ProcessEnum.X_COORDINATE), 2600000.0)
        self.assertEqual(foundation.get_param(ProcessEnum.Y_COORDINATE), 1200000.0)
        self.assertEqual(foundation.get_param(ProcessEnum.Z_COORDINATE), 456.78)

    def test_validate_for_process(self):
        """Test: Validierung für einen Prozess mit Foundation-spezifischen Anforderungen."""
        foundation = Foundation(name="ValidationTest")
        foundation.east = 2600000.0
        foundation.north = 1200000.0
        foundation.altitude = 456.78

        # Foundation fehlt foundation_type für common
        missing_common = foundation.validate_for_process("common")
        self.assertIn(ProcessEnum.FOUNDATION_TYPE, missing_common)

        # Foundation fehlen spezifische geometry Parameter
        missing_geometry = foundation.validate_for_process("geometry")
        self.assertIn(ProcessEnum.FOUNDATION_WIDTH, missing_geometry)
        self.assertIn(ProcessEnum.FOUNDATION_DEPTH, missing_geometry)
        self.assertIn(ProcessEnum.FOUNDATION_HEIGHT, missing_geometry)

        # Parameter hinzufügen
        foundation.foundation_type = "Typ A"
        foundation.width = 1.5
        foundation.height = 1.0
        foundation.depth = 2.0
        foundation.set_param(ProcessEnum.MATERIAL, "Beton")

        # Erneute Validierung
        self.assertEqual(foundation.validate_for_process("common"), [])
        self.assertEqual(foundation.validate_for_process("geometry"), [])
        self.assertEqual(foundation.validate_for_process("calculation"), [])


class TestMast(unittest.TestCase):
    """Tests für die Mast-Klasse."""

    def test_create_mast(self):
        """Test: Erstellung eines Masts."""
        mast = Mast(name="TestMast")

        self.assertEqual(mast.name, "TestMast")
        self.assertEqual(mast.element_type, ElementType.MAST)
        self.assertIsNone(mast.foundation_uuid)

    def test_create_mast_with_foundation_ref(self):
        """Test: Erstellung eines Masts mit Fundament-Referenz."""
        foundation_uuid = uuid4()
        mast = Mast(name="MastWithFoundation", foundation_uuid=foundation_uuid)

        self.assertEqual(mast.foundation_uuid, foundation_uuid)
        self.assertEqual(
            mast.get_param(ProcessEnum.UUID, default="FoundationUUID"),
            f"foundation_{foundation_uuid}",
        )

    def test_mast_properties(self):
        """Test: Mast-spezifische Properties."""
        mast = Mast(name="PropertyTest")

        # Properties setzen
        mast.mast_type = "Standard"
        mast.height = 15.0
        mast.profile_type = "HEB 200"

        # Geometrie-Koordinaten setzen
        mast.east = 2600000.0
        mast.north = 1200000.0
        mast.altitude = 456.78

        # Properties prüfen
        self.assertEqual(mast.mast_type, "Standard")
        self.assertEqual(mast.height, 15.0)
        self.assertEqual(mast.profile_type, "HEB 200")
        self.assertEqual(mast.east, 2600000.0)
        self.assertEqual(mast.north, 1200000.0)
        self.assertEqual(mast.altitude, 456.78)

        # Parameter-Zugriff prüfen
        self.assertEqual(mast.get_param(ProcessEnum.MAST_TYPE), "Standard")
        self.assertEqual(mast.get_param(ProcessEnum.MAST_HEIGHT), 15.0)
        self.assertEqual(mast.get_param(ProcessEnum.MAST_PROFILE_TYPE), "HEB 200")


class TestTrack(unittest.TestCase):
    """Tests für die Track-Klasse."""

    def test_create_track(self):
        """Test: Erstellung einer Schiene."""
        track = Track(name="TestTrack")

        self.assertEqual(track.name, "TestTrack")
        self.assertEqual(track.element_type, ElementType.TRACK)

    def test_track_properties(self):
        """Test: Track-spezifische Properties."""
        track = Track(name="PropertyTest")

        # Properties setzen
        track.track_type = "UIC60"
        track.gauge = 1.435
        track.cant = 100.0

        # Start- und Endkoordinaten setzen
        track.east = 2600000.0
        track.north = 1200000.0
        track.altitude = 456.78
        track.x_end = 2600100.0
        track.y_end = 1200100.0
        track.z_end = 457.0

        # Properties prüfen
        self.assertEqual(track.track_type, "UIC60")
        self.assertEqual(track.gauge, 1.435)
        self.assertEqual(track.cant, 100.0)
        self.assertEqual(track.east, 2600000.0)
        self.assertEqual(track.north, 1200000.0)
        self.assertEqual(track.altitude, 456.78)
        self.assertEqual(track.x_end, 2600100.0)
        self.assertEqual(track.y_end, 1200100.0)
        self.assertEqual(track.z_end, 457.0)

        # Parameter-Zugriff prüfen
        self.assertEqual(track.get_param(ProcessEnum.TRACK_TYPE), "UIC60")
        self.assertEqual(track.get_param(ProcessEnum.TRACK_GAUGE), 1.435)
        self.assertEqual(track.get_param(ProcessEnum.TRACK_CANT), 100.0)
        self.assertEqual(track.get_param(ProcessEnum.X_COORDINATE_END), 2600100.0)
        self.assertEqual(track.get_param(ProcessEnum.Y_COORDINATE_END), 1200100.0)
        self.assertEqual(track.get_param(ProcessEnum.Z_COORDINATE_END), 457.0)


class TestCurvedTrack(unittest.TestCase):
    """Tests für die CurvedTrack-Klasse."""

    def test_create_curved_track(self):
        """Test: Erstellung einer gekrümmten Schiene."""
        curved_track = CurvedTrack(name="TestCurvedTrack")

        self.assertEqual(curved_track.name, "TestCurvedTrack")
        self.assertEqual(curved_track.element_type, ElementType.TRACK)

    def test_curved_track_properties(self):
        """Test: CurvedTrack-spezifische Properties."""
        curved_track = CurvedTrack(name="PropertyTest")

        # Basis-Track-Properties setzen
        curved_track.track_type = "UIC60"
        curved_track.gauge = 1.435

        # Kurven-spezifische Properties setzen
        curved_track.clothoid_parameter = 300.0
        curved_track.start_radius = 1000.0
        curved_track.end_radius = 800.0

        # Start- und Endkoordinaten setzen
        curved_track.east = 2600000.0
        curved_track.north = 1200000.0
        curved_track.altitude = 456.78
        curved_track.x_end = 2600100.0
        curved_track.y_end = 1200100.0
        curved_track.z_end = 457.0

        # Properties prüfen
        self.assertEqual(curved_track.track_type, "UIC60")
        self.assertEqual(curved_track.gauge, 1.435)
        self.assertEqual(curved_track.clothoid_parameter, 300.0)
        self.assertEqual(curved_track.start_radius, 1000.0)
        self.assertEqual(curved_track.end_radius, 800.0)

        # Parameter-Zugriff prüfen
        self.assertEqual(curved_track.get_param(ProcessEnum.CLOTHOID_PARAMETER), 300.0)
        self.assertEqual(curved_track.get_param(ProcessEnum.START_RADIUS), 1000.0)
        self.assertEqual(curved_track.get_param(ProcessEnum.END_RADIUS), 800.0)


class TestJoch(unittest.TestCase):
    """Tests für die Joch-Klasse."""

    def test_create_joch(self):
        """Test: Erstellung eines Jochs."""
        joch = Joch(name="TestJoch")

        self.assertEqual(joch.name, "TestJoch")
        self.assertEqual(joch.element_type, ElementType.JOCH)
        self.assertIsNone(joch.mast_uuid_1)
        self.assertIsNone(joch.mast_uuid_2)

    def test_create_joch_with_mast_refs(self):
        """Test: Erstellung eines Jochs mit Mast-Referenzen."""
        mast_uuid_1 = uuid4()
        mast_uuid_2 = uuid4()
        joch = Joch(name="JochWithMasts", mast_uuid_1=mast_uuid_1, mast_uuid_2=mast_uuid_2)

        self.assertEqual(joch.mast_uuid_1, mast_uuid_1)
        self.assertEqual(joch.mast_uuid_2, mast_uuid_2)
        self.assertEqual(
            joch.get_param(ProcessEnum.UUID, default="Mast1UUID"), f"mast1_{mast_uuid_1}"
        )
        self.assertEqual(
            joch.get_param(ProcessEnum.UUID, default="Mast2UUID"), f"mast2_{mast_uuid_2}"
        )

    def test_joch_properties(self):
        """Test: Joch-spezifische Properties."""
        joch = Joch(name="PropertyTest")

        # Properties setzen
        joch.joch_type = "Standard"
        joch.span = 15.0

        # Start- und Endkoordinaten setzen
        joch.east = 2600000.0
        joch.north = 1200000.0
        joch.altitude = 456.78
        joch.x_end = 2600015.0
        joch.y_end = 1200000.0
        joch.z_end = 456.78

        # Properties prüfen
        self.assertEqual(joch.joch_type, "Standard")
        self.assertEqual(joch.span, 15.0)
        self.assertEqual(joch.east, 2600000.0)
        self.assertEqual(joch.north, 1200000.0)
        self.assertEqual(joch.altitude, 456.78)
        self.assertEqual(joch.x_end, 2600015.0)
        self.assertEqual(joch.y_end, 1200000.0)
        self.assertEqual(joch.z_end, 456.78)

        # Parameter-Zugriff prüfen
        self.assertEqual(joch.get_param(ProcessEnum.JOCH_TYPE), "Standard")
        self.assertEqual(joch.get_param(ProcessEnum.JOCH_SPAN), 15.0)


class TestCantilever(unittest.TestCase):
    """Tests für die Cantilever-Klasse."""

    def test_create_cantilever(self):
        """Test: Erstellung eines Auslegers."""
        cantilever = Cantilever(name="TestCantilever")

        self.assertEqual(cantilever.name, "TestCantilever")
        self.assertEqual(cantilever.element_type, ElementType.CANTILEVER)
        self.assertIsNone(cantilever.mast_uuid)

    def test_create_cantilever_with_mast_ref(self):
        """Test: Erstellung eines Auslegers mit Mast-Referenz."""
        mast_uuid = uuid4()
        cantilever = Cantilever(name="CantileverWithMast", mast_uuid=mast_uuid)

        self.assertEqual(cantilever.mast_uuid, mast_uuid)
        self.assertEqual(
            cantilever.get_param(ProcessEnum.UUID, default="MastUUID"), f"mast_{mast_uuid}"
        )

    def test_cantilever_properties(self):
        """Test: Cantilever-spezifische Properties."""
        cantilever = Cantilever(name="PropertyTest")

        # Properties setzen
        cantilever.cantilever_type = "Einfach"
        cantilever.length = 3.5

        # Geometrie-Koordinaten setzen
        cantilever.east = 2600000.0
        cantilever.north = 1200000.0
        cantilever.altitude = 463.0  # Höher als der Mast-Fuß

        # Properties prüfen
        self.assertEqual(cantilever.cantilever_type, "Einfach")
        self.assertEqual(cantilever.length, 3.5)
        self.assertEqual(cantilever.east, 2600000.0)
        self.assertEqual(cantilever.north, 1200000.0)
        self.assertEqual(cantilever.altitude, 463.0)

        # Parameter-Zugriff prüfen
        self.assertEqual(cantilever.get_param(ProcessEnum.CANTILEVER_TYPE), "Einfach")
        self.assertEqual(cantilever.get_param(ProcessEnum.CANTILEVER_LENGTH), 3.5)


if __name__ == "__main__":
    unittest.main()
