"""
Unit Tests für die Element-Factory.
"""

import unittest
from uuid import uuid4

from ..common.enums.process_enums import ElementType, ProcessEnum, UnitEnum
from ..common.models.element_models import (
    CurvedTrack,
    Foundation,
    Mast,
    Track,
)
from ..common.utils.factory import create_element


class TestFactory(unittest.TestCase):
    """Tests für die Element-Factory."""

    def test_create_foundation(self):
        """Test: Erstellung eines Foundation-Elements."""
        element_uuid = uuid4()
        element_data = {
            "uuid": str(element_uuid),
            "name": "TestFoundation",
            "element_type": ElementType.FOUNDATION.value,
            "parameters": [
                {
                    "name": "X",
                    "value": 100.0,
                    "process": ProcessEnum.X_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y",
                    "value": 200.0,
                    "process": ProcessEnum.Y_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z",
                    "value": 300.0,
                    "process": ProcessEnum.Z_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Typ",
                    "value": "Typ A",
                    "process": ProcessEnum.FOUNDATION_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "Breite",
                    "value": 1.5,
                    "process": ProcessEnum.FOUNDATION_WIDTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Höhe",
                    "value": 1.0,
                    "process": ProcessEnum.FOUNDATION_HEIGHT.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Tiefe",
                    "value": 2.0,
                    "process": ProcessEnum.FOUNDATION_DEPTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Material",
                    "value": "Beton",
                    "process": ProcessEnum.MATERIAL.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Foundation)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestFoundation")
        self.assertEqual(element.element_type, ElementType.FOUNDATION)

        # Parameter prüfen
        self.assertEqual(element.east, 100.0)
        self.assertEqual(element.north, 200.0)
        self.assertEqual(element.altitude, 300.0)

        assert isinstance(element, Foundation)

        self.assertEqual(element.foundation_type, "Typ A")
        self.assertEqual(element.width, 1.5)
        self.assertEqual(element.height, 1.0)
        self.assertEqual(element.depth, 2.0)
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Beton")

    def test_create_mast(self):
        """Test: Erstellung eines Mast-Elements."""
        element_uuid = uuid4()
        element_data = {
            "uuid": str(element_uuid),
            "name": "TestMast",
            "element_type": ElementType.MAST.value,
            "parameters": [
                {
                    "name": "X",
                    "value": 100.0,
                    "process": ProcessEnum.X_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y",
                    "value": 200.0,
                    "process": ProcessEnum.Y_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z",
                    "value": 300.0,
                    "process": ProcessEnum.Z_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Typ",
                    "value": "Standard",
                    "process": ProcessEnum.MAST_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "Höhe",
                    "value": 15.0,
                    "process": ProcessEnum.MAST_HEIGHT.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Profil",
                    "value": "HEB 200",
                    "process": ProcessEnum.MAST_PROFILE_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "Material",
                    "value": "Stahl",
                    "process": ProcessEnum.MATERIAL.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "FoundationUUID",
                    "value": "foundation_12345",
                    "process": ProcessEnum.UUID.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Mast)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestMast")
        self.assertEqual(element.element_type, ElementType.MAST)

        # Parameter prüfen
        self.assertEqual(element.east, 100.0)
        self.assertEqual(element.north, 200.0)
        self.assertEqual(element.altitude, 300.0)
        assert isinstance(element, Mast)
        self.assertEqual(element.mast_type, "Standard")
        self.assertEqual(element.height, 15.0)
        self.assertEqual(element.profile_type, "HEB 200")
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Stahl")

    def test_create_track(self):
        """Test: Erstellung eines Track-Elements."""
        element_uuid = uuid4()
        element_data = {
            "uuid": str(element_uuid),
            "name": "TestTrack",
            "element_type": ElementType.TRACK.value,
            "parameters": [
                {
                    "name": "X",
                    "value": 100.0,
                    "process": ProcessEnum.X_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y",
                    "value": 200.0,
                    "process": ProcessEnum.Y_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z",
                    "value": 300.0,
                    "process": ProcessEnum.Z_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "X_Ende",
                    "value": 200.0,
                    "process": ProcessEnum.X_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y_Ende",
                    "value": 300.0,
                    "process": ProcessEnum.Y_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z_Ende",
                    "value": 310.0,
                    "process": ProcessEnum.Z_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Spurweite",
                    "value": 1.435,
                    "process": ProcessEnum.TRACK_GAUGE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Überhöhung",
                    "value": 100.0,
                    "process": ProcessEnum.TRACK_CANT.value,
                    "datatype": "float",
                    "unit": UnitEnum.MILLIMETER.value,
                },
                {
                    "name": "Material",
                    "value": "Stahl",
                    "process": ProcessEnum.MATERIAL.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "TrackType",
                    "value": "UIC60",
                    "process": ProcessEnum.TRACK_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Track)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestTrack")
        self.assertEqual(element.element_type, ElementType.TRACK)

        # Parameter prüfen
        self.assertEqual(element.east, 100.0)
        self.assertEqual(element.north, 200.0)
        self.assertEqual(element.altitude, 300.0)
        assert isinstance(element, Track)
        self.assertEqual(element.x_end, 200.0)
        self.assertEqual(element.y_end, 300.0)
        self.assertEqual(element.z_end, 310.0)
        self.assertEqual(element.gauge, 1.435)
        self.assertEqual(element.cant, 100.0)
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Stahl")
        self.assertEqual(element.track_type, "UIC60")

    def test_create_curved_track(self):
        """Test: Erstellung eines CurvedTrack-Elements."""
        element_uuid = uuid4()
        element_data = {
            "uuid": str(element_uuid),
            "name": "TestCurvedTrack",
            "element_type": ElementType.TRACK.value,
            "parameters": [
                # Basis-Parameter für Track
                {
                    "name": "X",
                    "value": 100.0,
                    "process": ProcessEnum.X_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y",
                    "value": 200.0,
                    "process": ProcessEnum.Y_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z",
                    "value": 300.0,
                    "process": ProcessEnum.Z_COORDINATE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "X_Ende",
                    "value": 200.0,
                    "process": ProcessEnum.X_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Y_Ende",
                    "value": 300.0,
                    "process": ProcessEnum.Y_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Z_Ende",
                    "value": 310.0,
                    "process": ProcessEnum.Z_COORDINATE_END.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Spurweite",
                    "value": 1.435,
                    "process": ProcessEnum.TRACK_GAUGE.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Überhöhung",
                    "value": 100.0,
                    "process": ProcessEnum.TRACK_CANT.value,
                    "datatype": "float",
                    "unit": UnitEnum.MILLIMETER.value,
                },
                {
                    "name": "Material",
                    "value": "Stahl",
                    "process": ProcessEnum.MATERIAL.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "TrackType",
                    "value": "UIC60",
                    "process": ProcessEnum.TRACK_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
                # Zusätzliche Parameter für CurvedTrack
                {
                    "name": "Klothoidenparameter",
                    "value": 300.0,
                    "process": ProcessEnum.CLOTHOID_PARAMETER.value,
                    "datatype": "float",
                    "unit": UnitEnum.NONE.value,
                },
                {
                    "name": "Startradius",
                    "value": "inf",
                    "process": ProcessEnum.START_RADIUS.value,
                    "datatype": "str",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Endradius",
                    "value": 800.0,
                    "process": ProcessEnum.END_RADIUS.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, CurvedTrack)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestCurvedTrack")
        self.assertEqual(element.element_type, ElementType.TRACK)

        # CurvedTrack-spezifische Parameter prüfen
        assert isinstance(element, CurvedTrack)
        self.assertEqual(element.clothoid_parameter, 300.0)
        self.assertEqual(element.end_radius, 800.0)

        # Der "inf"-String sollte in float('inf') umgewandelt werden
        self.assertEqual(element.start_radius, float("inf"))

    def test_create_with_invalid_data(self):
        """Test: Factory soll bei ungültigen Daten eine angemessene Behandlung durchführen."""
        # Fall 1: Fehlender element_type
        data_without_type = {"uuid": str(uuid4()), "name": "MissingType", "parameters": []}

        with self.assertRaises(ValueError):
            create_element(data_without_type)

        # Fall 2: Ungültiger element_type
        data_invalid_type = {
            "uuid": str(uuid4()),
            "name": "InvalidType",
            "element_type": "unknown_type",
            "parameters": [],
        }

        with self.assertRaises(ValueError):
            create_element(data_invalid_type)

        # Fall 3: Parameter-Konvertierungsfehler
        data_with_invalid_params = {
            "uuid": str(uuid4()),
            "name": "InvalidParams",
            "element_type": ElementType.FOUNDATION.value,
            "parameters": [
                {
                    "name": "Breite",
                    "value": "not_a_number",
                    "process": ProcessEnum.FOUNDATION_WIDTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                }
            ],
        }

        # Hier wird erwartet, dass kein Fehler geworfen wird, aber der Parameter ignoriert wird
        element = create_element(data_with_invalid_params)
        assert element is not None
        self.assertEqual(element.get_param(ProcessEnum.FOUNDATION_WIDTH), None)


if __name__ == "__main__":
    unittest.main()
