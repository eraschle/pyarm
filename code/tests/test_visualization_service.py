"""
Unit Tests für den VisualizationService.
"""

import unittest

from ..common.enums.process_enums import ElementType, ProcessEnum
from ..common.models.element_models import Cantilever, CurvedTrack, Foundation, Joch, Mast, Track
from ..services.visualization_service import VisualizationService


class MockRepository:
    """Mock-Klasse für das Repository zum Testen des Services."""

    def __init__(self):
        self.elements = {}

    def add_element(self, element):
        """Fügt ein Element zum Mock-Repository hinzu."""
        self.elements[str(element.uuid)] = element

    def get_by_id(self, uuid):
        """Ruft ein Element anhand seiner ID ab."""
        return self.elements.get(str(uuid))

    def get_by_type(self, element_type):
        """Ruft Elemente eines bestimmten Typs ab."""
        return [elem for elem in self.elements.values() if elem.element_type == element_type]

    def get_all(self):
        """Ruft alle Elemente ab."""
        return list(self.elements.values())


class TestVisualizationService(unittest.TestCase):
    """Tests für den VisualizationService."""

    def setUp(self):
        """Test-Setup: Repository und Service initialisieren und mit Beispielelementen füllen."""
        # Mock-Repository erstellen
        self.repository = MockRepository()

        # Service mit dem Mock-Repository initialisieren
        self.service = VisualizationService(self.repository)

        # Beispielelemente erstellen

        # Foundation
        self.foundation = Foundation(name="TestFoundation")
        self.foundation.east = 100.0
        self.foundation.north = 200.0
        self.foundation.altitude = 300.0
        self.foundation.foundation_type = "Typ A"
        self.foundation.width = 1.5
        self.foundation.height = 1.0
        self.foundation.depth = 2.0
        self.foundation.set_param(ProcessEnum.MATERIAL, "Beton")

        # Mast
        self.mast = Mast(name="TestMast")
        self.mast.east = 100.0
        self.mast.north = 200.0
        self.mast.altitude = 300.0
        self.mast.height = 15.0
        self.mast.mast_type = "Standard"
        self.mast.profile_type = "HEB 200"
        self.mast.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Ausleger an Mast
        self.cantilever = Cantilever(name="TestCantilever")
        self.cantilever.east = 100.0
        self.cantilever.north = 200.0
        self.cantilever.altitude = 305.0  # 5m über dem Mastsockel
        self.cantilever.cantilever_type = "Einfach"
        self.cantilever.length = 3.5
        self.cantilever.mast_uuid = self.mast.uuid
        self.cantilever.set_param(ProcessEnum.MATERIAL, "Aluminium")

        # Gleis
        self.track = Track(name="TestTrack")
        self.track.east = 100.0
        self.track.north = 200.0
        self.track.altitude = 300.0
        self.track.x_end = 200.0
        self.track.y_end = 300.0
        self.track.z_end = 310.0
        self.track.track_type = "UIC60"
        self.track.gauge = 1.435
        self.track.cant = 100.0  # 100mm Überhöhung
        self.track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Kurvengleis mit Clothoid
        self.curved_track = CurvedTrack(name="TestCurvedTrack")
        self.curved_track.east = 200.0
        self.curved_track.north = 300.0
        self.curved_track.altitude = 300.0
        self.curved_track.x_end = 300.0
        self.curved_track.y_end = 400.0
        self.curved_track.z_end = 310.0
        self.curved_track.track_type = "UIC60"
        self.curved_track.gauge = 1.435
        self.curved_track.cant = 120.0  # 120mm Überhöhung
        self.curved_track.clothoid_parameter = 300.0
        self.curved_track.start_radius = float("inf")  # Gerade
        self.curved_track.end_radius = 800.0  # Kreisbogen mit R=800m
        self.curved_track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Joch zwischen zwei Masten
        self.mast2 = Mast(name="TestMast2")
        self.mast2.east = 120.0
        self.mast2.north = 200.0
        self.mast2.altitude = 300.0
        self.mast2.height = 15.0
        self.mast2.mast_type = "DP20"
        self.mast2.set_param(ProcessEnum.MATERIAL, "Stahl")

        self.joch = Joch(name="TestJoch")
        self.joch.east = 100.0
        self.joch.north = 200.0
        self.joch.altitude = 315.0  # 15m über dem Boden (Masthöhe)
        self.joch.x_end = 120.0
        self.joch.y_end = 200.0
        self.joch.z_end = 315.0
        self.joch.joch_type = "Standard"
        self.joch.span = 20.0
        self.joch.mast_uuid_1 = self.mast.uuid
        self.joch.mast_uuid_2 = self.mast2.uuid
        self.joch.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Elemente zum Repository hinzufügen
        self.repository.add_element(self.foundation)
        self.repository.add_element(self.mast)
        self.repository.add_element(self.cantilever)
        self.repository.add_element(self.track)
        self.repository.add_element(self.curved_track)
        self.repository.add_element(self.mast2)
        self.repository.add_element(self.joch)

    def test_get_element(self):
        """Test: Abrufen eines Elements für die Visualisierung."""
        # Foundation abrufen
        vis_element = self.service.get_element(self.foundation.uuid)
        assert vis_element is not None

        # Prüfen, ob das Element korrekt abgerufen und vorbereitet wurde
        self.assertIsNotNone(vis_element)
        self.assertEqual(vis_element["id"], str(self.foundation.uuid))
        self.assertEqual(vis_element["name"], "TestFoundation")
        self.assertEqual(vis_element["type"], ElementType.FOUNDATION.value)

        # Position prüfen
        self.assertEqual(vis_element["position"]["x"], 100.0)
        self.assertEqual(vis_element["position"]["y"], 200.0)
        self.assertEqual(vis_element["position"]["z"], 300.0)

        # Foundation-spezifische Attribute prüfen
        self.assertEqual(vis_element["foundation_type"], "Typ A")
        self.assertEqual(vis_element["dimensions"]["width"], 1.5)
        self.assertEqual(vis_element["dimensions"]["height"], 1.0)
        self.assertEqual(vis_element["dimensions"]["depth"], 2.0)

    def test_get_elements_by_type(self):
        """Test: Abrufen von Elementen eines bestimmten Typs für die Visualisierung."""
        # Alle Tracks abrufen
        vis_tracks = self.service.get_elements_by_type(ElementType.TRACK)

        # Prüfen, ob die richtige Anzahl von Elementen abgerufen wurde
        self.assertEqual(len(vis_tracks), 2)  # 1 Track + 1 CurvedTrack

        # Track-spezifische Attribute prüfen
        track_ids = {track["id"] for track in vis_tracks}
        self.assertIn(str(self.track.uuid), track_ids)
        self.assertIn(str(self.curved_track.uuid), track_ids)

        # Details eines bestimmten Tracks prüfen
        curved_track_vis = next(t for t in vis_tracks if t["id"] == str(self.curved_track.uuid))
        self.assertEqual(curved_track_vis["track_type"], "UIC60")
        self.assertEqual(curved_track_vis["gauge"], 1.435)
        self.assertEqual(curved_track_vis["cant"], 120.0)
        self.assertTrue(curved_track_vis["is_curved"])
        self.assertEqual(curved_track_vis["clothoid_parameter"], 300.0)
        self.assertEqual(curved_track_vis["start_radius"], "inf")
        self.assertEqual(curved_track_vis["end_radius"], 800.0)

    def test_get_all_elements(self):
        """Test: Abrufen aller Elemente für die Visualisierung."""
        # Alle Elemente abrufen
        vis_elements = self.service.get_all_elements()

        # Prüfen, ob die richtige Anzahl von Elementen abgerufen wurde
        self.assertEqual(len(vis_elements), 7)

        # Prüfen, ob alle Elementtypen vorhanden sind
        element_types = {element["type"] for element in vis_elements}
        self.assertIn(ElementType.FOUNDATION.value, element_types)
        self.assertIn(ElementType.MAST.value, element_types)
        self.assertIn(ElementType.CANTILEVER.value, element_types)
        self.assertIn(ElementType.TRACK.value, element_types)
        self.assertIn(ElementType.JOCH.value, element_types)

    def test_element_position(self):
        """Test: Extraktion der Positionsdaten eines Elements."""
        # Einfaches Element mit Basispositionen
        foundation_pos = self.service._get_element_position(self.foundation)
        self.assertEqual(foundation_pos["x"], 100.0)
        self.assertEqual(foundation_pos["y"], 200.0)
        self.assertEqual(foundation_pos["z"], 300.0)
        self.assertNotIn("x2", foundation_pos)  # Kein Endpunkt

        # Element mit Start- und Endpunkt
        track_pos = self.service._get_element_position(self.track)
        self.assertEqual(track_pos["x"], 100.0)
        self.assertEqual(track_pos["y"], 200.0)
        self.assertEqual(track_pos["z"], 300.0)
        self.assertEqual(track_pos["x2"], 200.0)
        self.assertEqual(track_pos["y2"], 300.0)
        self.assertEqual(track_pos["z2"], 310.0)

        # Element mit Azimut
        element_with_azimuth = Foundation(name="AzimuthTest")
        element_with_azimuth.east = 100.0
        element_with_azimuth.north = 200.0
        element_with_azimuth.altitude = 300.0
        element_with_azimuth.set_param(ProcessEnum.AZIMUTH, 45.0)

        azimuth_pos = self.service._get_element_position(element_with_azimuth)
        self.assertEqual(azimuth_pos["azimuth"], 45.0)

    def test_joch_visualization(self):
        """Test: Visualisierungsdaten für ein Joch."""
        vis_joch = self.service.get_element(self.joch.uuid)
        assert vis_joch is not None
        # Joch-spezifische Attribute prüfen
        self.assertEqual(vis_joch["joch_type"], "Standard")
        self.assertEqual(vis_joch["span"], 20.0)
        self.assertEqual(vis_joch["mast_id_1"], str(self.mast.uuid))
        self.assertEqual(vis_joch["mast_id_2"], str(self.mast2.uuid))

        # Position prüfen
        self.assertEqual(vis_joch["position"]["x"], 100.0)
        self.assertEqual(vis_joch["position"]["y"], 200.0)
        self.assertEqual(vis_joch["position"]["z"], 315.0)
        self.assertEqual(vis_joch["position"]["x2"], 120.0)
        self.assertEqual(vis_joch["position"]["y2"], 200.0)
        self.assertEqual(vis_joch["position"]["z2"], 315.0)

    def test_mast_visualization(self):
        """Test: Visualisierungsdaten für einen Mast."""
        vis_mast = self.service.get_element(self.mast.uuid)
        assert vis_mast is not None

        # Mast-spezifische Attribute prüfen
        self.assertEqual(vis_mast["mast_type"], "Standard")
        self.assertEqual(vis_mast["height"], 15.0)

        # Da Mast keine Foundation-UUID hat, sollte kein foundation_id-Attribut vorhanden sein
        self.assertNotIn("foundation_id", vis_mast)

        # Mast mit Foundation-Referenz erstellen
        mast_with_foundation = Mast(name="MastWithFoundation")
        mast_with_foundation.east = 100.0
        mast_with_foundation.north = 200.0
        mast_with_foundation.altitude = 300.0
        mast_with_foundation.foundation_uuid = self.foundation.uuid

        self.repository.add_element(mast_with_foundation)

        # Visualisierungsdaten für Mast mit Foundation-Referenz abrufen
        vis_mast_with_foundation = self.service.get_element(mast_with_foundation.uuid)
        assert vis_mast_with_foundation is not None

        # Foundation-Referenz prüfen
        self.assertIn("foundation_id", vis_mast_with_foundation)
        self.assertEqual(vis_mast_with_foundation["foundation_id"], str(self.foundation.uuid))

    def test_calculate_clothoid_points(self):
        """Test: Berechnung von Punkten entlang einer Klothoide."""
        # Testparameter
        start_station = 0.0
        end_station = 100.0
        step = 10.0

        # Punkte berechnen
        points = self.service.calculate_clothoid_points(
            self.curved_track.uuid, start_station, end_station, step
        )

        # Prüfen, ob die richtige Anzahl von Punkten berechnet wurde
        self.assertEqual(len(points), 11)  # 0, 10, 20, ..., 100

        # Einige Punkte prüfen
        first_point = points[0]
        last_point = points[-1]

        # Erster Punkt sollte der Startpunkt des Gleises sein
        assert first_point is not None
        track = self.curved_track
        assert track is not None
        assert track.east is not None
        assert track is not None
        assert track.north is not None
        assert track is not None
        assert track.altitude is not None

        self.assertAlmostEqual(first_point[0], track.east)
        self.assertAlmostEqual(first_point[1], track.north)
        self.assertAlmostEqual(first_point[2], track.altitude)
        assert track is not None and track.altitude is not None
        assert track.x_end is not None
        assert track.y_end is not None

        # Letzter Punkt sollte der Endpunkt des Gleises sein oder nahe dran
        # (Da dies eine lineare Approximation ist, nicht exakt die Klothoide)
        track_length = ((track.x_end - track.east) ** 2 + (track.y_end - track.north) ** 2) ** 0.5

        assert last_point is not None
        # Wenn end_station gleich der Track-Länge ist, sollte der letzte Punkt der Endpunkt sein
        if abs(end_station - track_length) < 0.001:
            self.assertAlmostEqual(last_point[0], track.x_end, places=1)
            self.assertAlmostEqual(last_point[1], track.y_end, places=1)
            self.assertAlmostEqual(last_point[2], track.y_end, places=1)


if __name__ == "__main__":
    unittest.main()
