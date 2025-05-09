"""
Unit Tests für das JsonElementRepository.
"""

import json
import os
import tempfile
import unittest

from pyarm.models.element_models import Foundation, Mast, Track
from pyarm.models.parameter import UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.repository.json_repository import JsonElementRepository


class TestJsonElementRepository(unittest.TestCase):
    """Tests für die JsonElementRepository-Klasse."""

    def setUp(self):
        """Test-Setup mit temporärem Verzeichnis für Repository-Dateien."""
        # Temporäres Verzeichnis für Repository-Dateien erstellen
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_dir = self.temp_dir.name

        # Repository initialisieren
        self.repository = JsonElementRepository(self.repo_dir)

        # Beispielelemente erstellen
        self.foundation1 = Foundation(name="Foundation1")
        self.foundation1.set_point(east=100.0, north=200.0, altitude=300.0)
        self.foundation1.set_param(ProcessEnum.FOUNDATION_TYPE, "Typ A")
        self.foundation1.set_param(ProcessEnum.WIDTH, 1.5, UnitEnum.METER)
        self.foundation1.set_param(ProcessEnum.HEIGHT, 1.0, UnitEnum.METER)
        self.foundation1.set_param(ProcessEnum.DEPTH, 2.0, UnitEnum.METER)
        self.foundation1.set_param(ProcessEnum.MATERIAL, "Beton")

        self.foundation2 = Foundation(name="Foundation2")
        self.foundation2.set_point(east=110.0, north=210.0, altitude=310.0)
        self.foundation2.set_param(ProcessEnum.FOUNDATION_TYPE, "Typ B")
        self.foundation2.set_param(ProcessEnum.WIDTH, 2.0, UnitEnum.METER)
        self.foundation2.set_param(ProcessEnum.HEIGHT, 1.2, UnitEnum.METER)
        self.foundation2.set_param(ProcessEnum.DEPTH, 2.5, UnitEnum.METER)
        self.foundation2.set_param(ProcessEnum.MATERIAL, "Beton")

        self.mast = Mast(name="Mast1")
        self.mast.set_point(east=100.0, north=200.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.HEIGHT, 15.0, UnitEnum.METER)
        self.mast.set_param(ProcessEnum.MAST_TYPE, "Standard")
        self.mast.set_param(ProcessEnum.MAST_PROFILE_TYPE, "HEB 200")
        self.mast.set_param(ProcessEnum.MATERIAL, "Stahl")

        self.track = Track(name="Track1")
        self.track.set_point(east=100.0, north=200.0, altitude=300.0)
        self.track.set_param(ProcessEnum.X_COORDINATE_END, 150.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.Y_COORDINATE_END, 250.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.Z_COORDINATE_END, 310.0, UnitEnum.METER)
        self.track.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
        self.track.set_param(ProcessEnum.TRACK_GAUGE, 1.435)
        self.track.set_param(ProcessEnum.MATERIAL, "Stahl")

    def tearDown(self):
        """Test-Teardown: Temporäres Verzeichnis entfernen."""
        self.temp_dir.cleanup()

    def test_save_and_get_by_id(self):
        """Test: Speichern und Abrufen eines Elements anhand seiner ID."""
        # Element speichern
        self.repository.save(self.foundation1)

        # Element abrufen
        element = self.repository.get_by_id(self.foundation1.uuid)
        assert element is not None

        # Prüfen, ob das Element korrekt abgerufen wurde
        self.assertIsNotNone(element)
        self.assertEqual(element.name, "Foundation1")
        self.assertEqual(element.element_type, ElementType.FOUNDATION)
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 100.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE), 200.0)
        self.assertEqual(element.get_param(ProcessEnum.Z_COORDINATE), 300.0)
        self.assertEqual(element.get_param(ProcessEnum.FOUNDATION_TYPE), "Typ A")
        self.assertEqual(element.get_param(ProcessEnum.WIDTH), 1.5)
        self.assertEqual(element.get_param(ProcessEnum.HEIGHT), 1.0)
        self.assertEqual(element.get_param(ProcessEnum.DEPTH), 2.0)
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Beton")

    def test_save_all_and_get_all(self):
        """Test: Speichern und Abrufen mehrerer Elemente."""
        # Elemente speichern
        elements = [self.foundation1, self.foundation2, self.mast, self.track]
        self.repository.save_all(elements)

        # Alle Elemente abrufen
        all_elements = self.repository.get_all()

        # Prüfen, ob alle Elemente korrekt abgerufen wurden
        self.assertEqual(len(all_elements), 4)

        # UUIDs sammeln
        uuids = {str(element.uuid): element for element in all_elements}

        # Prüfen, ob alle gespeicherten Elemente enthalten sind
        self.assertIn(str(self.foundation1.uuid), uuids)
        self.assertIn(str(self.foundation2.uuid), uuids)
        self.assertIn(str(self.mast.uuid), uuids)
        self.assertIn(str(self.track.uuid), uuids)

        # Prüfen eines spezifischen Elements
        mast_element = uuids[str(self.mast.uuid)]
        self.assertEqual(mast_element.name, "Mast1")
        self.assertEqual(mast_element.element_type, ElementType.MAST)
        self.assertEqual(mast_element.get_param(ProcessEnum.HEIGHT), 15.0)

    def test_get_by_type(self):
        """Test: Abrufen von Elementen nach Typ."""
        # Elemente speichern
        elements = [self.foundation1, self.foundation2, self.mast, self.track]
        self.repository.save_all(elements)

        # Elemente nach Typ abrufen
        foundations = self.repository.get_by_type(ElementType.FOUNDATION)
        masts = self.repository.get_by_type(ElementType.MAST)
        tracks = self.repository.get_by_type(ElementType.TRACK)

        # Prüfen, ob die Elemente korrekt nach Typ gefiltert wurden
        self.assertEqual(len(foundations), 2)
        self.assertEqual(len(masts), 1)
        self.assertEqual(len(tracks), 1)

        # Inhalt der nach Typ gefilterten Elemente prüfen
        foundation_names = {element.name for element in foundations}
        self.assertIn("Foundation1", foundation_names)
        self.assertIn("Foundation2", foundation_names)

        self.assertEqual(masts[0].name, "Mast1")
        self.assertEqual(tracks[0].name, "Track1")

    def test_delete(self):
        """Test: Löschen eines Elements."""
        # Elemente speichern
        elements = [self.foundation1, self.foundation2, self.mast, self.track]
        self.repository.save_all(elements)

        # Anzahl der Elemente vor dem Löschen prüfen
        self.assertEqual(len(self.repository.get_all()), 4)

        # Ein Element löschen
        self.repository.delete(self.mast.uuid)

        # Anzahl der Elemente nach dem Löschen prüfen
        self.assertEqual(len(self.repository.get_all()), 3)

        # Prüfen, ob das gelöschte Element nicht mehr abrufbar ist
        self.assertIsNone(self.repository.get_by_id(self.mast.uuid))

        # Prüfen, ob die anderen Elemente noch abrufbar sind
        self.assertIsNotNone(self.repository.get_by_id(self.foundation1.uuid))
        self.assertIsNotNone(self.repository.get_by_id(self.foundation2.uuid))
        self.assertIsNotNone(self.repository.get_by_id(self.track.uuid))

    def test_file_structure(self):
        """Test: Dateistruktur und -format des Repositories."""
        # Elemente speichern
        elements = [self.foundation1, self.foundation2, self.mast, self.track]
        self.repository.save_all(elements)

        # Prüfen, ob für jeden Elementtyp eine JSON-Datei erstellt wurde
        foundation_file = os.path.join(self.repo_dir, f"{ElementType.FOUNDATION.value}.json")
        mast_file = os.path.join(self.repo_dir, f"{ElementType.MAST.value}.json")
        track_file = os.path.join(self.repo_dir, f"{ElementType.TRACK.value}.json")

        self.assertTrue(os.path.exists(foundation_file))
        self.assertTrue(os.path.exists(mast_file))
        self.assertTrue(os.path.exists(track_file))

        # Inhalt der Foundation-Datei prüfen
        with open(foundation_file, "r") as f:
            foundation_data = json.load(f)

        self.assertEqual(len(foundation_data), 2)  # Zwei Foundation-Elemente

        # UUIDs der Foundations prüfen
        foundation_uuids = {item.get("uuid") for item in foundation_data}
        self.assertIn(str(self.foundation1.uuid), foundation_uuids)
        self.assertIn(str(self.foundation2.uuid), foundation_uuids)

        # Inhalt eines Elements prüfen
        foundation1_data = next(
            item for item in foundation_data if item.get("uuid") == str(self.foundation1.uuid)
        )
        self.assertEqual(foundation1_data.get("name"), "Foundation1")
        self.assertEqual(foundation1_data.get("element_type"), ElementType.FOUNDATION.value)

        # Parameter-Liste prüfen
        params = {param.get("name"): param for param in foundation1_data.get("parameters", [])}

        # Überprüfen einiger wichtiger Parameter
        self.assertIn("X", params)
        self.assertEqual(float(params["X"].get("value")), 100.0)
        self.assertEqual(params["X"].get("unit"), UnitEnum.METER.value)

        self.assertIn("FOUNDATION_TYPE", params)
        self.assertEqual(params["FOUNDATION_TYPE"].get("value"), "Typ A")


if __name__ == "__main__":
    unittest.main()
