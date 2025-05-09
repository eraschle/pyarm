# """
# Unit Tests für die spezialisierten Modellklassen der Infrastrukturelemente.
# """

# import unittest
# from uuid import UUID, uuid4

# from pyarm.models.element_models import (
#     Cantilever,
#     CurvedTrack,
#     Foundation,
#     Joch,
#     Mast,
#     Track,
# )
# from pyarm.models.parameter import DataType, UnitEnum
# from pyarm.models.process_enums import ElementType, ProcessEnum


# class TestFoundation(unittest.TestCase):
#     """Tests für die Foundation-Klasse."""

#     def test_create_foundation(self):
#         """Test: Erstellung eines Fundaments."""
#         foundation = Foundation(name="TestFoundation")

#         self.assertEqual(foundation.name, "TestFoundation")
#         self.assertEqual(foundation.element_type, ElementType.FOUNDATION)
#         self.assertIsInstance(foundation.uuid, UUID)

#     def test_foundation_properties(self):
#         """Test: Foundation-spezifische Properties mit dem Komponenten-System."""
#         foundation = Foundation(name="PropertyTest")

#         # Properties setzen via set_param
#         foundation.add_param(
#             name="Fundament-Typ",
#             process=ProcessEnum.FOUNDATION_TYPE,
#             value="Typ A",
#             datatype=DataType.STRING,
#         )
#         foundation.set_param(ProcessEnum.WIDTH, 1.5, UnitEnum.METER)
#         foundation.set_param(ProcessEnum.HEIGHT, 1.0, UnitEnum.METER)
#         foundation.set_param(ProcessEnum.DEPTH, 2.0, UnitEnum.METER)

#         # Geometrie-Koordinaten setzen
#         foundation.set_param(ProcessEnum.X_COORDINATE, 2600000.0, UnitEnum.METER)
#         foundation.set_param(ProcessEnum.Y_COORDINATE, 1200000.0, UnitEnum.METER)
#         foundation.set_param(ProcessEnum.Z_COORDINATE, 456.78, UnitEnum.METER)

#         # Properties über Parameter prüfen
#         self.assertEqual(foundation.get_param(ProcessEnum.FOUNDATION_TYPE).value, "Typ A")
#         self.assertEqual(foundation.get_param(ProcessEnum.WIDTH).value, 1.5)
#         self.assertEqual(foundation.get_param(ProcessEnum.HEIGHT).value, 1.0)
#         self.assertEqual(foundation.get_param(ProcessEnum.DEPTH).value, 2.0)
#         self.assertEqual(foundation.get_param(ProcessEnum.X_COORDINATE).value, 2600000.0)
#         self.assertEqual(foundation.get_param(ProcessEnum.Y_COORDINATE).value, 1200000.0)
#         self.assertEqual(foundation.get_param(ProcessEnum.Z_COORDINATE).value, 456.78)

#         # Komponenten-Zugriff prüfen
#         assert foundation.dimension is not None, "Dimensionen-Komponente fehlt"
#         self.assertEqual(foundation.dimension.width, 1.5)
#         self.assertEqual(foundation.dimension.height, 1.0)
#         self.assertEqual(foundation.dimension.depth, 2.0)

#         self.assertIsNotNone(foundation.location, "Positions-Komponente fehlt")
#         self.assertEqual(foundation.location.point.x, 2600000.0)
#         self.assertEqual(foundation.location.point.y, 1200000.0)
#         self.assertEqual(foundation.location.point.z, 456.78)


# class TestMast(unittest.TestCase):
#     """Tests für die Mast-Klasse."""

#     def test_create_mast(self):
#         """Test: Erstellung eines Masts."""
#         mast = Mast(name="TestMast")

#         self.assertEqual(mast.name, "TestMast")
#         self.assertEqual(mast.element_type, ElementType.MAST)
#         self.assertIsNone(mast.foundation_uuid)

#     def test_create_mast_with_foundation_ref(self):
#         """Test: Erstellung eines Masts mit Fundament-Referenz."""
#         foundation_uuid = uuid4()
#         mast = Mast(name="MastWithFoundation", foundation_uuid=foundation_uuid)

#         self.assertEqual(mast.foundation_uuid, foundation_uuid)
#         self.assertEqual(mast.get_param(ProcessEnum.UUID).value, str(foundation_uuid))

#     def test_mast_properties(self):
#         """Test: Mast-spezifische Properties über das Komponenten-System."""
#         mast = Mast(name="PropertyTest")

#         # Properties setzen via set_param
#         mast.set_param(ProcessEnum.MAST_TYPE, "Standard")
#         mast.set_param(ProcessEnum.HEIGHT, 15.0, UnitEnum.METER)
#         mast.set_param(ProcessEnum.MAST_PROFILE_TYPE, "HEB 200")
#         mast.set_param(ProcessEnum.DIAMETER, 0.3, UnitEnum.METER)

#         # Geometrie-Koordinaten setzen
#         mast.set_param(ProcessEnum.X_COORDINATE, 2600000.0, UnitEnum.METER)
#         mast.set_param(ProcessEnum.Y_COORDINATE, 1200000.0, UnitEnum.METER)
#         mast.set_param(ProcessEnum.Z_COORDINATE, 456.78, UnitEnum.METER)

#         # Properties über Parameter prüfen
#         self.assertEqual(mast.get_param(ProcessEnum.MAST_TYPE).value, "Standard")
#         self.assertEqual(mast.get_param(ProcessEnum.HEIGHT).value, 15.0)
#         self.assertEqual(mast.get_param(ProcessEnum.MAST_PROFILE_TYPE).value, "HEB 200")
#         self.assertEqual(mast.get_param(ProcessEnum.X_COORDINATE).value, 2600000.0)

#         # Komponenten-Zugriff prüfen
#         assert mast.dimension is not None, "Dimensionen-Komponente fehlt"
#         self.assertEqual(mast.dimension.height, 15.0)
#         self.assertEqual(mast.dimension.diameter, 0.3)

#         self.assertIsNotNone(mast.location, "Positions-Komponente fehlt")
#         self.assertEqual(mast.location.point.x, 2600000.0)
#         self.assertEqual(mast.location.point.y, 1200000.0)
#         self.assertEqual(mast.location.point.z, 456.78)


# class TestTrack(unittest.TestCase):
#     """Tests für die Track-Klasse."""

#     def test_create_track(self):
#         """Test: Erstellung einer Schiene."""
#         track = Track(name="TestTrack")

#         self.assertEqual(track.name, "TestTrack")
#         self.assertEqual(track.element_type, ElementType.TRACK)

#     def test_track_properties(self):
#         """Test: Track-spezifische Properties über das Komponenten-System."""
#         track = Track(name="PropertyTest")

#         # Properties setzen via set_param
#         track.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
#         track.set_param(ProcessEnum.TRACK_GAUGE, 1.435, UnitEnum.METER)
#         track.set_param(ProcessEnum.TRACK_CANT, 100.0, UnitEnum.MILLIMETER)

#         # Start- und End-Koordinaten setzen
#         track.add_param(
#             ProcessEnum.X_COORDINATE, 2600000.0, datatype=DataType.FLOAT, unit=UnitEnum.METER
#         )
#         track.set_param(ProcessEnum.Y_COORDINATE, 1200000.0, UnitEnum.METER)
#         track.set_param(ProcessEnum.Z_COORDINATE, 456.78, UnitEnum.METER)
#         track.set_param(ProcessEnum.X_COORDINATE_END, 2600100.0, UnitEnum.METER)
#         track.set_param(ProcessEnum.Y_COORDINATE_END, 1200100.0, UnitEnum.METER)
#         track.set_param(ProcessEnum.Z_COORDINATE_END, 457.0, UnitEnum.METER)

#         # Parameter-Zugriff prüfen
#         self.assertEqual(track.get_param(ProcessEnum.TRACK_TYPE).value, "UIC60")
#         self.assertEqual(track.get_param(ProcessEnum.TRACK_GAUGE).value, 1.435)
#         self.assertEqual(track.get_param(ProcessEnum.TRACK_CANT).value, 100.0)

#         # Komponenten-Zugriff prüfen
#         # TODO: Ist TRACK_GAUGE eine Dimension?
#         # assert track.dimension is not None, "Dimensionen-Komponente fehlt"
#         # self.assertEqual(track.dimension.has_width, 1.435)
#         # self.assertEqual(track.dimension.width, 1.435)

#         self.assertIsNotNone(track.location, "LineLocation-Komponente fehlt")
#         self.assertEqual(track.location.point.x, 2600000.0)
#         self.assertEqual(track.location.point.y, 1200000.0)
#         self.assertEqual(track.location.point.z, 456.78)
#         self.assertEqual(track.location.end_point.x, 2600100.0)
#         self.assertEqual(track.location.end_point.y, 1200100.0)
#         self.assertEqual(track.location.end_point.z, 457.0)

#         # Länge über Zugangsmethode prüfen
#         assert track.dimension.length is not None, "Längen-Komponente fehlt"
#         self.assertAlmostEqual(track.dimension.length, 141.42, places=2)


# class TestCurvedTrack(unittest.TestCase):
#     """Tests für die CurvedTrack-Klasse."""

#     def test_create_curved_track(self):
#         """Test: Erstellung einer gekrümmten Schiene."""
#         curved_track = CurvedTrack(name="TestCurvedTrack")

#         self.assertEqual(curved_track.name, "TestCurvedTrack")
#         self.assertEqual(curved_track.element_type, ElementType.TRACK)

#     def test_curved_track_properties(self):
#         """Test: CurvedTrack-spezifische Properties über das Komponenten-System."""
#         curved_track = CurvedTrack(name="PropertyTest")

#         # Basis-Track-Properties setzen via set_param
#         curved_track.set_param(ProcessEnum.TRACK_TYPE, "UIC60")
#         curved_track.set_param(ProcessEnum.TRACK_GAUGE, 1.435, UnitEnum.METER)

#         # Spezifische Kurven-Properties setzen
#         curved_track.set_param(ProcessEnum.CLOTHOID_PARAMETER, 150.0)
#         curved_track.set_param(ProcessEnum.START_RADIUS, 1000.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.END_RADIUS, 800.0, UnitEnum.METER)

#         # Geometrie-Koordinaten setzen
#         curved_track.set_param(ProcessEnum.X_COORDINATE, 2600000.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Y_COORDINATE, 1200000.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Z_COORDINATE, 456.78, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.X_COORDINATE_END, 2600100.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Y_COORDINATE_END, 1200100.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Z_COORDINATE_END, 457.0, UnitEnum.METER)

#         # Parameter-Zugriff prüfen
#         self.assertEqual(curved_track.get_param(ProcessEnum.TRACK_TYPE).value, "UIC60")
#         self.assertEqual(curved_track.get_param(ProcessEnum.CLOTHOID_PARAMETER).value, 150.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.START_RADIUS).value, 1000.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.END_RADIUS).value, 800.0)

#         # Komponenten-Zugriff prüfen
#         # self.assertIsNotNone(curved_track.location, "LineLocation-Komponente fehlt")
#         # self.assertTrue(curved_track.dimension.has_width)
#         # self.assertEqual(curved_track.dimension.width, 1.435)

#         self.assertIsNotNone(curved_track.location, "LineLocation-Komponente fehlt")
#         self.assertEqual(curved_track.location.point.x, 2600000.0)
#         self.assertEqual(curved_track.location.end_point.x, 2600100.0)
#         curved_track.set_param(ProcessEnum.TRACK_GAUGE, 1.435)

#         # Kurven-spezifische Properties setzen via set_param
#         curved_track.set_param(ProcessEnum.CLOTHOID_PARAMETER, 300.0)
#         curved_track.set_param(ProcessEnum.START_RADIUS, 1000.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.END_RADIUS, 800.0, UnitEnum.METER)

#         # Start-Koordinaten setzen via set_point
#         curved_track.set_point(east=2600000.0, north=1200000.0, altitude=456.78)
#         curved_track.set_param(ProcessEnum.X_COORDINATE_END, 2600100.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Y_COORDINATE_END, 1200100.0, UnitEnum.METER)
#         curved_track.set_param(ProcessEnum.Z_COORDINATE_END, 457.0, UnitEnum.METER)

#         # Properties prüfen
#         self.assertEqual(curved_track.get_param(ProcessEnum.TRACK_TYPE).value, "UIC60")
#         self.assertEqual(curved_track.get_param(ProcessEnum.TRACK_GAUGE).value, 1.435)
#         self.assertEqual(curved_track.get_param(ProcessEnum.CLOTHOID_PARAMETER).value, 300.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.START_RADIUS).value, 1000.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.END_RADIUS).value, 800.0)

#         # Parameter-Zugriff prüfen
#         self.assertEqual(curved_track.get_param(ProcessEnum.CLOTHOID_PARAMETER).value, 300.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.START_RADIUS).value, 1000.0)
#         self.assertEqual(curved_track.get_param(ProcessEnum.END_RADIUS).value, 800.0)


# class TestJoch(unittest.TestCase):
#     """Tests für die Joch-Klasse."""

#     def test_create_joch(self):
#         """Test: Erstellung eines Jochs."""
#         joch = Joch(name="TestJoch")

#         self.assertEqual(joch.name, "TestJoch")
#         self.assertEqual(joch.element_type, ElementType.JOCH)
#         self.assertIsNone(joch.mast_uuid_1)
#         self.assertIsNone(joch.mast_uuid_2)

#     def test_create_joch_with_mast_refs(self):
#         """Test: Erstellung eines Jochs mit Mast-Referenzen."""
#         mast_uuid_1 = uuid4()
#         mast_uuid_2 = uuid4()
#         joch = Joch(name="JochWithMasts", mast_uuid_1=mast_uuid_1, mast_uuid_2=mast_uuid_2)

#         self.assertEqual(joch.mast_uuid_1, mast_uuid_1)
#         self.assertEqual(joch.mast_uuid_2, mast_uuid_2)
#         self.assertEqual(
#             joch.get_param(ProcessEnum.UUID, default="Mast1UUID"),
#             f"mast1_{mast_uuid_1}",
#         )
#         self.assertEqual(
#             joch.get_param(ProcessEnum.UUID, default="Mast2UUID"),
#             f"mast2_{mast_uuid_2}",
#         )

#     def test_joch_properties(self):
#         """Test: Joch-spezifische Properties."""
#         joch = Joch(name="PropertyTest")

#         # Properties setzen via set_param
#         joch.set_param(ProcessEnum.JOCH_TYPE, "Standard")
#         joch.set_param(ProcessEnum.JOCH_SPAN, 15.0, UnitEnum.METER)

#         # Start-Koordinaten setzen via set_point
#         joch.set_point(east=2600000.0, north=1200000.0, altitude=456.78)
#         joch.set_param(ProcessEnum.X_COORDINATE_END, 2600015.0, UnitEnum.METER)
#         joch.set_param(ProcessEnum.Y_COORDINATE_END, 1200000.0, UnitEnum.METER)
#         joch.set_param(ProcessEnum.Z_COORDINATE_END, 456.78, UnitEnum.METER)

#         # Properties prüfen
#         self.assertEqual(joch.get_param(ProcessEnum.JOCH_TYPE).value, "Standard")
#         self.assertEqual(joch.get_param(ProcessEnum.JOCH_SPAN).value, 15.0)
#         self.assertEqual(joch.get_param(ProcessEnum.X_COORDINATE).value, 2600000.0)
#         self.assertEqual(joch.get_param(ProcessEnum.Y_COORDINATE).value, 1200000.0)
#         self.assertEqual(joch.get_param(ProcessEnum.Z_COORDINATE).value, 456.78)
#         self.assertEqual(joch.get_param(ProcessEnum.X_COORDINATE_END).value, 2600015.0)
#         self.assertEqual(joch.get_param(ProcessEnum.Y_COORDINATE_END).value, 1200000.0)
#         self.assertEqual(joch.get_param(ProcessEnum.Z_COORDINATE_END).value, 456.78)

#         # Parameter-Zugriff prüfen
#         self.assertEqual(joch.get_param(ProcessEnum.JOCH_TYPE).value, "Standard")
#         self.assertEqual(joch.get_param(ProcessEnum.JOCH_SPAN).value, 15.0)


# class TestCantilever(unittest.TestCase):
#     """Tests für die Cantilever-Klasse."""

#     def test_create_cantilever(self):
#         """Test: Erstellung eines Auslegers."""
#         cantilever = Cantilever(name="TestCantilever")

#         self.assertEqual(cantilever.name, "TestCantilever")
#         self.assertEqual(cantilever.element_type, ElementType.CANTILEVER)
#         self.assertIsNone(cantilever.mast_uuid)

#     def test_create_cantilever_with_mast_ref(self):
#         """Test: Erstellung eines Auslegers mit Mast-Referenz."""
#         mast_uuid = uuid4()
#         cantilever = Cantilever(name="CantileverWithMast", mast_uuid=mast_uuid)

#         self.assertEqual(cantilever.mast_uuid, mast_uuid)
#         self.assertEqual(
#             cantilever.get_param(ProcessEnum.UUID, default="MastUUID").value,
#             f"mast_{mast_uuid}",
#         )

#     def test_cantilever_properties(self):
#         """Test: Cantilever-spezifische Properties."""
#         cantilever = Cantilever(name="PropertyTest")

#         # Properties setzen via set_param
#         cantilever.set_param(ProcessEnum.CANTILEVER_TYPE, "Einfach")
#         cantilever.set_param(ProcessEnum.LENGTH, 3.5, UnitEnum.METER)

#         # Geometrie-Koordinaten setzen via set_point
#         cantilever.set_point(
#             east=2600000.0, north=1200000.0, altitude=463.0
#         )  # Höher als der Mast-Fuß

#         # Properties prüfen
#         self.assertEqual(cantilever.get_param(ProcessEnum.CANTILEVER_TYPE).value, "Einfach")
#         self.assertEqual(cantilever.get_param(ProcessEnum.LENGTH).value, 3.5)
#         self.assertEqual(cantilever.get_param(ProcessEnum.X_COORDINATE).value, 2600000.0)
#         self.assertEqual(cantilever.get_param(ProcessEnum.Y_COORDINATE).value, 1200000.0)
#         self.assertEqual(cantilever.get_param(ProcessEnum.Z_COORDINATE).value, 463.0)

#         # Parameter-Zugriff prüfen
#         self.assertEqual(cantilever.get_param(ProcessEnum.CANTILEVER_TYPE).value, "Einfach")
#         self.assertEqual(cantilever.get_param(ProcessEnum.LENGTH).value, 3.5)


# if __name__ == "__main__":
#     unittest.main()
