"""
Unit Tests für die Element-Factory.
"""

import unittest
from uuid import uuid4

from pyarm.components import Component, ComponentType
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.element_models import (
    CurvedTrack,
    Foundation,
    Mast,
    Track,
)
from pyarm.models.parameter import UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.utils import factory


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
                    "process": ProcessEnum.WIDTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Höhe",
                    "value": 1.0,
                    "process": ProcessEnum.HEIGHT.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
                {
                    "name": "Tiefe",
                    "value": 2.0,
                    "process": ProcessEnum.DEPTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = factory.create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Foundation)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestFoundation")
        self.assertEqual(element.element_type, ElementType.FOUNDATION)

        # Parameter prüfen
        assert element.position is not None
        self.assertEqual(element.position.x, 100.0)
        self.assertEqual(element.position.y, 200.0)
        self.assertEqual(element.position.z, 300.0)

        assert isinstance(element, Foundation)

        dimension = element.get_component(ComponentType.DIMENSION)
        assert isinstance(dimension, Component)
        self.assertIsNotNone(element.get_param(ProcessEnum.FOUNDATION_TYPE))
        self.assertEqual(dimension, 1.0)
        self.assertEqual(element.get_param(ProcessEnum.WIDTH), 1.5)

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
                    "process": ProcessEnum.HEIGHT.value,
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
                    "name": "FoundationUUID",
                    "value": "foundation_12345",
                    "process": ProcessEnum.UUID.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = factory.create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Mast)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestMast")
        self.assertEqual(element.element_type, ElementType.MAST)

        # Parameter prüfen
        assert element.position is not None
        self.assertEqual(element.position.x, 100.0)
        self.assertEqual(element.position.y, 200.0)
        self.assertEqual(element.position.z, 300.0)
        assert isinstance(element, Mast)
        self.assertEqual(element.get_param(ProcessEnum.MAST_TYPE), "Standard")
        self.assertEqual(element.get_param(ProcessEnum.HEIGHT), 15.0)
        self.assertEqual(element.get_param(ProcessEnum.MAST_PROFILE_TYPE), "HEB 200")

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
                    "name": "TrackType",
                    "value": "UIC60",
                    "process": ProcessEnum.TRACK_TYPE.value,
                    "datatype": "str",
                    "unit": UnitEnum.NONE.value,
                },
            ],
        }

        # Factory-Methode aufrufen
        element = factory.create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, Track)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestTrack")
        self.assertEqual(element.element_type, ElementType.TRACK)

        # Parameter prüfen
        assert element.location is not None
        self.assertEqual(element.location.x, 100.0)
        self.assertEqual(element.location.y, 200.0)
        self.assertEqual(element.location.z, 300.0)
        assert isinstance(element, Track)
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE_END), 200.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE_END), 300.0)
        self.assertEqual(element.get_param(ProcessEnum.Z_COORDINATE_END), 310.0)
        self.assertEqual(element.get_param(ProcessEnum.TRACK_GAUGE), 1.435)
        self.assertEqual(element.get_param(ProcessEnum.TRACK_CANT), 100.0)
        self.assertEqual(element.get_param(ProcessEnum.TRACK_TYPE), "UIC60")

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
                    "value": float("inf"),
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
        element = factory.create_element(element_data)

        # Typprüfung
        self.assertIsInstance(element, CurvedTrack)

        # Basisattribute prüfen
        self.assertEqual(str(element.uuid), str(element_uuid))
        self.assertEqual(element.name, "TestCurvedTrack")
        self.assertEqual(element.element_type, ElementType.TRACK)

        # CurvedTrack-spezifische Parameter prüfen
        assert isinstance(element, CurvedTrack)
        self.assertEqual(element.get_param(ProcessEnum.CLOTHOID_PARAMETER), 300.0)
        self.assertEqual(element.get_param(ProcessEnum.END_RADIUS), 800.0)

        # Der "inf"-String sollte in float('inf') umgewandelt werden
        self.assertEqual(element.get_param(ProcessEnum.START_RADIUS), float("inf"))

    def test_create_with_invalid_data(self):
        """Test: Factory soll bei ungültigen Daten eine angemessene Behandlung durchführen."""
        # Fall 2: Ungültiger element_type
        data_invalid_type = {
            "uuid": str(uuid4()),
            "name": "InvalidType",
            "element_type": "unknown_type",
            "parameters": [],
        }

        element = factory.create_element(data_invalid_type)
        assert element is not None
        element.element_type = ElementType.UNDEFINED

        # Fall 3: Parameter-Konvertierungsfehler
        data_with_invalid_params = {
            "uuid": str(uuid4()),
            "name": "InvalidParams",
            "element_type": ElementType.FOUNDATION.value,
            "parameters": [
                {
                    "name": "Breite",
                    "value": "not_a_number",
                    "process": ProcessEnum.WIDTH.value,
                    "datatype": "float",
                    "unit": UnitEnum.METER.value,
                }
            ],
        }

        # Hier wird erwartet, dass kein Fehler geworfen wird, aber der Parameter ignoriert wird
        element = factory.create_element(data_with_invalid_params)
        assert isinstance(element, InfrastructureElement)
        self.assertEqual(element.get_param(ProcessEnum.WIDTH), None)


if __name__ == "__main__":
    unittest.main()
