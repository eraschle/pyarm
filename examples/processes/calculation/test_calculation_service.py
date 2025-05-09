"""
Unit Tests für den CalculationService.
"""

import unittest
from uuid import uuid4

from pyarm.models.element_models import (
    Cantilever,
    CurvedTrack,
    Foundation,
    Joch,
    Mast,
    Track,
)
from pyarm.models.parameter import UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum

from .calculation_service import CalculationElement, CalculationService


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


class TestCalculationElement(unittest.TestCase):
    """Tests für die CalculationElement-Klasse."""

    def test_create_calculation_element(self):
        """Test: Erstellung eines Berechnungselements."""
        element_uuid = uuid4()
        calc_elem = CalculationElement(element_uuid, "TestElement", "foundation")

        self.assertEqual(calc_elem.uuid, str(element_uuid))
        self.assertEqual(calc_elem.name, "TestElement")
        self.assertEqual(calc_elem.element_type, "foundation")
        self.assertEqual(calc_elem.properties, {})
        self.assertEqual(calc_elem.calculation_data, {})
        self.assertEqual(calc_elem.dependencies, [])

    def test_add_property(self):
        """Test: Hinzufügen einer Eigenschaft."""
        calc_elem = CalculationElement(uuid4(), "TestElement", "foundation")

        calc_elem.add_property("material", "Beton")
        calc_elem.add_property("dimensions", {"width": 1.5, "height": 1.0, "depth": 2.0})

        self.assertEqual(calc_elem.properties["material"], "Beton")
        self.assertEqual(calc_elem.properties["dimensions"]["width"], 1.5)

    def test_add_calculation_data(self):
        """Test: Hinzufügen von Berechnungsdaten."""
        calc_elem = CalculationElement(uuid4(), "TestElement", "foundation")

        calc_elem.add_calculation_data("volume", 3.0)
        calc_elem.add_calculation_data("weight", 7500.0)

        self.assertEqual(calc_elem.calculation_data["volume"], 3.0)
        self.assertEqual(calc_elem.calculation_data["weight"], 7500.0)

    def test_add_dependency(self):
        """Test: Hinzufügen einer Abhängigkeit."""
        calc_elem = CalculationElement(uuid4(), "TestElement", "mast")
        dependency_id = str(uuid4())

        calc_elem.add_dependency(dependency_id)

        self.assertIn(dependency_id, calc_elem.dependencies)

        # Hinzufügen der gleichen Abhängigkeit sollte keine Duplikate erzeugen
        calc_elem.add_dependency(dependency_id)
        self.assertEqual(len(calc_elem.dependencies), 1)

    def test_to_dict(self):
        """Test: Konvertierung in ein Dictionary."""
        element_uuid = uuid4()
        calc_elem = CalculationElement(element_uuid, "TestElement", "foundation")

        calc_elem.add_property("material", "Beton")
        calc_elem.add_calculation_data("volume", 3.0)
        dependency_id = str(uuid4())
        calc_elem.add_dependency(dependency_id)

        result = calc_elem.to_dict()

        self.assertEqual(result["uuid"], str(element_uuid))
        self.assertEqual(result["name"], "TestElement")
        self.assertEqual(result["element_type"], "foundation")
        self.assertEqual(result["properties"]["material"], "Beton")
        self.assertEqual(result["calculation_data"]["volume"], 3.0)
        self.assertEqual(result["dependencies"], [dependency_id])


class TestCalculationService(unittest.TestCase):
    """Tests für den CalculationService."""

    def setUp(self):
        """Test-Setup: Repository und Service initialisieren und mit Beispielelementen füllen."""
        # Mock-Repository erstellen
        self.repository = MockRepository()

        # Service mit dem Mock-Repository initialisieren
        self.service = CalculationService(self.repository)

        # Beispielelemente erstellen

        # Foundation
        self.foundation = Foundation(name="TestFoundation")
        self.foundation.set_point(east=100.0, north=200.0, altitude=300.0)
        self.foundation.set_param(ProcessEnum.FOUNDATION_TYPE, "Typ A")
        self.foundation.set_param(ProcessEnum.FOUNDATION_WIDTH, 1.5, UnitEnum.METER)
        self.foundation.set_param(ProcessEnum.FOUNDATION_HEIGHT, 1.0, UnitEnum.METER)
        self.foundation.set_param(ProcessEnum.FOUNDATION_DEPTH, 2.0, UnitEnum.METER)
        self.foundation.set_param(ProcessEnum.MATERIAL, "Beton")

        # Mast
        self.mast = Mast(name="TestMast")
        self.mast.set_point(east=100.0, north=200.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.MAST_HEIGHT, 15.0, UnitEnum.METER)
        self.mast.set_param(ProcessEnum.MAST_TYPE, "DP20")
        self.mast.set_param(ProcessEnum.MAST_PROFILE_TYPE, "HEB 200")
        self.mast.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Ausleger an Mast
        self.cantilever = Cantilever(name="TestCantilever")
        self.cantilever.set_point(east=100.0, north=200.0, altitude=305.0)
        self.cantilever.set_param(ProcessEnum.CANTILEVER_TYPE, "Einfach")
        self.cantilever.set_param(ProcessEnum.CANTILEVER_LENGTH, 3.5, UnitEnum.METER)
        self.cantilever.mast_uuid = self.mast.uuid
        self.cantilever.set_param(ProcessEnum.MATERIAL, "Aluminium")

        # Gleis
        self.track = Track(name="TestTrack")
        self.track.set_point(east=100.0, north=200.0, altitude=300.0)
        self.track.set_param(ProcessEnum.X_COORDINATE_END, 200.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.Y_COORDINATE_END, 300.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.Z_COORDINATE_END, 310.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
        self.track.set_param(ProcessEnum.TRACK_GAUGE, 1.435)
        self.track.set_param(ProcessEnum.TRACK_CANT, 100.0)
        self.track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Kurvengleis mit Clothoid
        self.curved_track = CurvedTrack(name="TestCurvedTrack")
        self.curved_track.set_point(east=200.0, north=300.0, altitude=300.0)
        self.curved_track.set_param(ProcessEnum.X_COORDINATE_END, 300.0, UnitEnum.METER)
        self.curved_track.set_param(ProcessEnum.Y_COORDINATE_END, 400.0, UnitEnum.METER)
        self.curved_track.set_param(ProcessEnum.Z_COORDINATE_END, 310.0, UnitEnum.METER)
        self.curved_track.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
        self.curved_track.set_param(ProcessEnum.TRACK_GAUGE, 1.435)
        self.curved_track.set_param(ProcessEnum.TRACK_CANT, 120.0)
        self.curved_track.set_param(ProcessEnum.CLOTHOID_PARAMETER, 300.0)
        self.curved_track.set_param(ProcessEnum.START_RADIUS, float("inf"))
        self.curved_track.set_param(ProcessEnum.END_RADIUS, 800.0, UnitEnum.METER)
        self.curved_track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Joch zwischen zwei Masten
        self.mast2 = Mast(name="TestMast2")
        self.mast2.set_point(east=120.0, north=200.0, altitude=300.0)
        self.mast2.set_param(ProcessEnum.MAST_HEIGHT, 15.0, UnitEnum.METER)
        self.mast2.set_param(ProcessEnum.MAST_TYPE, "DP20")
        self.mast2.set_param(ProcessEnum.MATERIAL, "Stahl")

        self.joch = Joch(name="TestJoch")
        self.joch.set_point(east=100.0, north=200.0, altitude=315.0)
        self.joch.set_param(ProcessEnum.X_COORDINATE_END, 120.0, UnitEnum.METER)
        self.joch.set_param(ProcessEnum.Y_COORDINATE_END, 200.0, UnitEnum.METER)
        self.joch.set_param(ProcessEnum.Z_COORDINATE_END, 315.0, UnitEnum.METER)
        self.joch.set_param(ProcessEnum.JOCH_TYPE, "Standard")
        self.joch.set_param(ProcessEnum.JOCH_SPAN, 20.0, UnitEnum.METER)
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
        """Test: Abrufen eines Elements für die Berechnung."""
        # Foundation abrufen
        calc_element = self.service.get_element(self.foundation.uuid)

        # Prüfen, ob das Element korrekt abgerufen und vorbereitet wurde
        assert calc_element is not None

        self.assertEqual(calc_element.uuid, str(self.foundation.uuid))
        self.assertEqual(calc_element.name, "TestFoundation")
        self.assertEqual(calc_element.element_type, ElementType.FOUNDATION.value)

        # Eigenschaften prüfen
        assert calc_element.properties is not None

        self.assertEqual(calc_element.properties["material"], "Beton")
        self.assertEqual(calc_element.properties["position"]["x"], 100.0)
        self.assertEqual(calc_element.properties["position"]["y"], 200.0)
        self.assertEqual(calc_element.properties["position"]["z"], 300.0)
        self.assertEqual(calc_element.properties["foundation_type"], "Typ A")
        self.assertEqual(calc_element.properties["dimensions"]["width"], 1.5)
        self.assertEqual(calc_element.properties["dimensions"]["height"], 1.0)
        self.assertEqual(calc_element.properties["dimensions"]["depth"], 2.0)

        # Berechnungsdaten prüfen
        self.assertEqual(calc_element.calculation_data["volume"], 1.5 * 1.0 * 2.0)
        self.assertEqual(calc_element.calculation_data["weight"], 1.5 * 1.0 * 2.0 * 2500)
        self.assertEqual(
            calc_element.calculation_data["bottom_pressure"],
            (1.5 * 1.0 * 2.0 * 2500) / (1.5 * 2.0),
        )

    def test_get_elements_by_type(self):
        """Test: Abrufen von Elementen eines bestimmten Typs."""
        # Alle Tracks abrufen
        tracks = self.service.get_elements_by_type(ElementType.TRACK)

        # Prüfen, ob die richtige Anzahl von Elementen abgerufen wurde
        self.assertEqual(len(tracks), 2)  # 1 Track + 1 CurvedTrack

        # Track-spezifische Eigenschaften und Berechnungsdaten prüfen
        for track in tracks:
            if track.name == "TestTrack":
                self.assertEqual(track.properties["track_type"], "UIC60")
                self.assertEqual(track.properties["gauge"], 1.435)
                self.assertEqual(track.properties["cant"], 100.0)

                # Länge sollte berechnet sein
                expected_length = ((200.0 - 100.0) ** 2 + (300.0 - 200.0) ** 2) ** 0.5
                self.assertAlmostEqual(track.calculation_data["length"], expected_length)

                # Gewicht sollte basierend auf der Länge berechnet sein
                self.assertAlmostEqual(track.calculation_data["weight"], expected_length * 60.0)

            elif track.name == "TestCurvedTrack":
                self.assertTrue(track.properties["is_curved"])
                self.assertEqual(track.properties["clothoid_parameter"], 300.0)
                self.assertEqual(track.properties["end_radius"], 800.0)

                # Clothoid-Länge sollte berechnet sein
                expected_clothoid_length = 300.0**2 / 800.0
                self.assertAlmostEqual(
                    track.calculation_data["clothoid_length"], expected_clothoid_length
                )

    def test_calculate_track_forces(self):
        """Test: Berechnung von Kräften auf einem Gleis."""
        # Parameter für die Berechnung
        speed = 20.0  # m/s (72 km/h)
        load = 10.0  # kN/m

        # Kräfte auf geradem Gleis berechnen
        track_forces = self.service.calculate_track_forces(self.track.uuid, speed, load)

        # Länge des Gleises berechnen
        track_length = ((200.0 - 100.0) ** 2 + (300.0 - 200.0) ** 2) ** 0.5

        # Ergebnis prüfen
        self.assertEqual(track_forces["is_curved"], False)
        self.assertEqual(track_forces["radius"], "inf")
        self.assertAlmostEqual(track_forces["length"], track_length)
        self.assertAlmostEqual(track_forces["vertical_force"], load * track_length)
        self.assertAlmostEqual(
            track_forces["lateral_force"], 0.0
        )  # Keine Querkraft auf gerader Strecke

        # Kräfte auf Kurvengleis berechnen
        curved_track_forces = self.service.calculate_track_forces(
            self.curved_track.uuid, speed, load
        )

        # Ergebnis prüfen
        self.assertEqual(curved_track_forces["is_curved"], True)
        self.assertEqual(curved_track_forces["radius"], 800.0)

        # Querkraft sollte ungleich Null sein in einer Kurve
        self.assertNotEqual(curved_track_forces["lateral_force"], 0.0)

        # Für Kurvengleis: Berechnung der Querkraft prüfen
        # Zentrifugalkraft ohne Überhöhung
        expected_centrifugal_force = load * speed**2 / 800.0

        # Reduktion durch Überhöhung (120mm)
        cant_effect = load * 9.81 * (120.0 / 1000.0) / 1.435
        expected_lateral_force = expected_centrifugal_force - cant_effect

        self.assertAlmostEqual(
            curved_track_forces["lateral_force"], expected_lateral_force, places=3
        )

    def test_calculate_structure_load(self):
        """Test: Berechnung der Strukturlast."""
        # Last für ein Fundament berechnen
        foundation_load = self.service.calculate_structure_load(self.foundation.uuid)

        # Fundament-spezifische Last prüfen
        self.assertIn("load_case", foundation_load)
        self.assertIn("self_weight", foundation_load["load_case"])
        self.assertIn("soil_pressure", foundation_load["load_case"])
        self.assertIn("max_allowed_pressure", foundation_load["load_case"])

        expected_weight = 1.5 * 1.0 * 2.0 * 2500
        expected_pressure = expected_weight / (1.5 * 2.0)

        self.assertAlmostEqual(foundation_load["load_case"]["self_weight"], expected_weight)
        self.assertAlmostEqual(foundation_load["load_case"]["soil_pressure"], expected_pressure)

        # Last für einen Mast mit Ausleger berechnen
        mast_load = self.service.calculate_structure_load(self.mast.uuid)

        # Mast-spezifische Last prüfen
        self.assertIn("load_case", mast_load)
        self.assertIn("self_weight", mast_load["load_case"])
        self.assertIn("cantilever_weight", mast_load["load_case"])
        self.assertIn("total_weight", mast_load["load_case"])
        self.assertIn("foundation_moment", mast_load["load_case"])

        # Gewicht des Mastes (basierend auf Typ und Höhe)
        expected_mast_weight = 15.0 * 45.0  # DP20 Mast, 15m hoch, 45 kg/m
        # Gewicht des Auslegers (aus dem Service)
        cantilever_weight = 3.5 * 20.0  # 3.5m lang, 20 kg/m

        self.assertAlmostEqual(mast_load["load_case"]["self_weight"], expected_mast_weight)
        self.assertAlmostEqual(mast_load["load_case"]["cantilever_weight"], cantilever_weight)
        self.assertAlmostEqual(
            mast_load["load_case"]["total_weight"],
            expected_mast_weight + cantilever_weight,
        )

        # Moment an der Mastbasis
        expected_moment = (expected_mast_weight + cantilever_weight) * 15.0 / 2.0
        self.assertAlmostEqual(mast_load["load_case"]["foundation_moment"], expected_moment)

        # Abhängigkeiten prüfen
        self.assertEqual(len(mast_load["dependencies"]), 1)
        self.assertEqual(mast_load["dependencies"][0]["name"], "TestCantilever")


if __name__ == "__main__":
    unittest.main()
