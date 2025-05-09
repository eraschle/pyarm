"""
Unit Tests für den VisualizationProcess.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pyarm.models.element_models import CurvedTrack, Foundation, Mast, Track
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.repository.json_repository import JsonElementRepository

from .process1_visualization import VisualizationProcess


class TestVisualizationProcess(unittest.TestCase):
    """Tests für den VisualizationProcess."""

    def setUp(self):
        """Test-Setup: Temporäre Verzeichnisse für Repository und Output erstellen."""
        # Temporäre Verzeichnisse erstellen
        self.repo_dir = tempfile.TemporaryDirectory()
        self.output_dir = tempfile.TemporaryDirectory()

        # Repository mit Beispieldaten erstellen
        self.repository = JsonElementRepository(self.repo_dir.name)

        # Beispielelemente erstellen und speichern

        # Foundation
        self.foundation = Foundation(name="TestFoundation")
        self.foundation.set_point(east=100.0, north=200.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.FOUNDATION_TYPE, "Typ A")
        self.mast.set_param(ProcessEnum.FOUNDATION_WIDTH, 1.5)
        self.mast.set_param(ProcessEnum.FOUNDATION_HEIGHT, 1.0)
        self.mast.set_param(ProcessEnum.FOUNDATION_DEPTH, 2.0)
        self.foundation.set_param(ProcessEnum.MATERIAL, "Beton")

        # Mast
        self.mast = Mast(name="TestMast")
        self.mast.set_point(east=100.0, north=200.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.MAST_TYPE, "Standard")
        self.mast.set_param(ProcessEnum.MAST_HEIGHT, 15.0)
        self.mast.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Gleis
        self.track = Track(name="TestTrack")
        self.track.set_point(east=100.0, north=200.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.MAST_HEIGHT, 15.0)
        self.mast.set_param(ProcessEnum.X_COORDINATE_END, 200.0)
        self.mast.set_param(ProcessEnum.Y_COORDINATE_END, 300.0)
        self.mast.set_param(ProcessEnum.Z_COORDINATE_END, 310.0)
        self.mast.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
        self.mast.set_param(ProcessEnum.TRACK_GAUGE, 1.435)
        self.track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Kurvengleis
        self.curved_track = CurvedTrack(name="TestCurvedTrack")
        self.curved_track.set_point(east=200.0, north=300.0, altitude=300.0)
        self.mast.set_param(ProcessEnum.X_COORDINATE_END, 300.0)
        self.mast.set_param(ProcessEnum.Y_COORDINATE_END, 400.0)
        self.mast.set_param(ProcessEnum.Z_COORDINATE_END, 310.0)
        self.mast.set_param(ProcessEnum.CLOTHOID_PARAMETER, 300.0)
        self.mast.set_param(ProcessEnum.START_RADIUS, float("inf"))
        self.mast.set_param(ProcessEnum.END_RADIUS, 800.0)
        self.curved_track.set_param(ProcessEnum.MATERIAL, "Stahl")

        # Elemente zum Repository hinzufügen
        self.repository.save_all([self.foundation, self.mast, self.track, self.curved_track])

        # Prozess initialisieren
        self.process = VisualizationProcess(self.repo_dir.name, self.output_dir.name)

    def tearDown(self):
        """Test-Teardown: Temporäre Verzeichnisse entfernen."""
        self.repo_dir.cleanup()
        self.output_dir.cleanup()

    def test_run(self):
        """Test: Ausführung des gesamten Visualisierungsprozesses."""
        # Prozess ausführen
        self.process.run()

        # Prüfen, ob Ausgabedateien erzeugt wurden
        expected_files = [
            "foundation_visualization.json",
            "mast_visualization.json",
            "track_visualization.json",
            "visualization_overview.json",
        ]

        for filename in expected_files:
            file_path = os.path.join(self.output_dir.name, filename)
            self.assertTrue(os.path.exists(file_path), f"Datei {filename} wurde nicht erstellt")

        # Inhalt der Übersichtsdatei prüfen
        overview_path = os.path.join(self.output_dir.name, "visualization_overview.json")
        with open(overview_path, "r") as f:
            overview = json.load(f)

        self.assertIn("element_counts", overview)
        self.assertIn("total_elements", overview)
        self.assertEqual(overview["total_elements"], 4)

        # Elementanzahlen prüfen
        self.assertEqual(overview["element_counts"]["foundation"], 1)
        self.assertEqual(overview["element_counts"]["mast"], 1)
        self.assertEqual(overview["element_counts"]["track"], 2)  # Track + CurvedTrack

    def test_process_element(self):
        """Test: Verarbeitung eines einzelnen Elements."""
        # Ein Element verarbeiten
        result = self.process.process_element(str(self.foundation.uuid))

        # Prüfen, ob die Ausgabedatei erstellt wurde
        file_path = os.path.join(
            self.output_dir.name, f"element_{self.foundation.uuid}_visualization.json"
        )
        self.assertTrue(os.path.exists(file_path))

        # Inhalt des Ergebnisses prüfen
        self.assertEqual(result["name"], "TestFoundation")
        self.assertEqual(result["type"], ElementType.FOUNDATION.value)
        self.assertEqual(result["foundation_type"], "Typ A")

        # Prüfen, ob das Ergebnis korrekt in die Datei geschrieben wurde
        with open(file_path, "r") as f:
            file_content = json.load(f)

        self.assertEqual(file_content, result)

    def test_process_elements_by_type(self):
        """Test: Verarbeitung aller Elemente eines bestimmten Typs."""
        # Alle Elemente vom Typ TRACK verarbeiten
        results = self.process.process_elements_by_type(ElementType.TRACK)

        # Prüfen, ob die Ausgabedatei erstellt wurde
        file_path = os.path.join(self.output_dir.name, "track_visualization.json")
        self.assertTrue(os.path.exists(file_path))

        # Prüfen, ob die richtige Anzahl von Elementen verarbeitet wurde
        self.assertEqual(len(results), 2)  # Track + CurvedTrack

        # Prüfen, ob die Ergebnisse korrekt in die Datei geschrieben wurden
        with open(file_path, "r") as f:
            file_content = json.load(f)

        self.assertEqual(len(file_content), 2)

        # Prüfen, ob beide Tracks enthalten sind
        track_ids = [track["id"] for track in file_content]
        self.assertIn(str(self.track.uuid), track_ids)
        self.assertIn(str(self.curved_track.uuid), track_ids)

    def test_calculate_clothoid_points(self):
        """Test: Berechnung von Punkten entlang einer Klothoide."""
        # Klothoidenpunkte berechnen
        points = self.process.calculate_clothoid_points(
            str(self.curved_track.uuid), 0.0, 100.0, 10.0
        )

        # Prüfen, ob die Ausgabedatei erstellt wurde
        file_path = os.path.join(
            self.output_dir.name, f"element_{self.curved_track.uuid}_clothoid.json"
        )
        self.assertTrue(os.path.exists(file_path))

        # Prüfen, ob die richtige Anzahl von Punkten berechnet wurde
        self.assertEqual(len(points), 11)  # 0, 10, 20, ..., 100

        # Prüfen, ob die Punkte korrekt in die Datei geschrieben wurden
        with open(file_path, "r") as f:
            file_content = json.load(f)

        self.assertEqual(len(file_content), 11)

        # Format der Punkte prüfen
        for point in file_content:
            self.assertEqual(len(point), 3)  # [x, y, z]
            self.assertIsInstance(point[0], (int, float))
            self.assertIsInstance(point[1], (int, float))
            self.assertIsInstance(point[2], (int, float))

    def test_error_handling(self):
        """Test: Fehlerbehandlung bei nicht existierenden Elementen."""
        # Nicht existierendes Element verarbeiten
        with self.assertRaises(ValueError):
            self.process.process_element("non_existent_id")

    @patch("builtins.print")
    def test_output_messages(self, mock_print):
        """Test: Ausgabe von Nachrichten während der Verarbeitung."""
        # Prozess ausführen
        self.process.run()

        # Prüfen, ob Start- und Ende-Nachrichten ausgegeben wurden
        mock_print.assert_any_call("Starte Visualisierungsprozess...")

        # Die letzte Nachricht sollte die Zusammenfassung sein
        mock_print.assert_any_call(
            f"Visualisierungsprozess abgeschlossen. Übersicht gespeichert: {Path(self.output_dir.name) / 'visualization_overview.json'}"
        )


if __name__ == "__main__":
    unittest.main()
