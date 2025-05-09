"""
Unit Tests für die Basismodelle der Infrastrukturelemente.
"""

import unittest
from uuid import UUID

from ..common.models.base_models import Parameter, InfrastructureElement
from ..common.enums.process_enums import ProcessEnum, ElementType, UnitEnum


class TestParameter(unittest.TestCase):
    """Tests für die Parameter-Klasse."""
    
    def test_create_parameter(self):
        """Test: Erstellung eines Parameters."""
        param = Parameter(
            name="TestParam",
            value=42.5,
            process=ProcessEnum.X_COORDINATE,
            datatype="float",
            unit=UnitEnum.METER
        )
        
        self.assertEqual(param.name, "TestParam")
        self.assertEqual(param.value, 42.5)
        self.assertEqual(param.process, ProcessEnum.X_COORDINATE)
        self.assertEqual(param.datatype, "float")
        self.assertEqual(param.unit, UnitEnum.METER)
    
    def test_parameter_string_representation(self):
        """Test: String-Repräsentation eines Parameters."""
        # Parameter mit allen Attributen
        param1 = Parameter(
            name="TestParam",
            value=42.5,
            process=ProcessEnum.X_COORDINATE,
            datatype="float",
            unit=UnitEnum.METER
        )
        
        # Parameter ohne Prozess
        param2 = Parameter(
            name="NoProcess",
            value="text",
            process=None,
            datatype="str",
            unit=UnitEnum.NONE
        )
        
        # Parameter ohne Einheit
        param3 = Parameter(
            name="NoUnit",
            value=True,
            process=ProcessEnum.MATERIAL,
            datatype="bool"
        )
        
        self.assertEqual(str(param1), "TestParam: 42.5 m (X_COORDINATE)")
        self.assertEqual(str(param2), "NoProcess: text")
        self.assertEqual(str(param3), "NoUnit: True (MATERIAL)")


class TestInfrastructureElement(unittest.TestCase):
    """Tests für die InfrastructureElement-Klasse."""
    
    def test_create_element(self):
        """Test: Erstellung eines Elements mit Standardwerten."""
        element = InfrastructureElement(name="TestElement")
        
        self.assertEqual(element.name, "TestElement")
        self.assertIsInstance(element.uuid, UUID)
        self.assertEqual(element.element_type, ElementType.FOUNDATION)
        self.assertEqual(len(element.parameters), 3)  # UUID, Name, ElementType
        self.assertEqual(len(element.known_params), 3)
    
    def test_create_element_with_parameters(self):
        """Test: Erstellung eines Elements mit Parametern."""
        params = [
            Parameter(name="X", value=100.0, process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
            Parameter(name="Y", value=200.0, process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
            Parameter(name="Material", value="Beton", process=ProcessEnum.MATERIAL)
        ]
        
        element = InfrastructureElement(
            name="ParamElement",
            element_type=ElementType.MAST,
            parameters=params
        )
        
        self.assertEqual(element.name, "ParamElement")
        self.assertEqual(element.element_type, ElementType.MAST)
        self.assertEqual(len(element.parameters), 6)  # 3 + UUID, Name, ElementType
        self.assertEqual(len(element.known_params), 6)
        
        # Prüfen der Parameter
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 100.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE), 200.0)
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Beton")
    
    def test_parameter_getter_setter(self):
        """Test: Getter und Setter für Parameter."""
        element = InfrastructureElement(name="GetterSetterTest")
        
        # Parameter setzen
        element.set_param(ProcessEnum.X_COORDINATE, 150.0, UnitEnum.METER)
        element.set_param(ProcessEnum.MATERIAL, "Stahl")
        
        # Parameter abrufen
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 150.0)
        self.assertEqual(element.get_param(ProcessEnum.MATERIAL), "Stahl")
        
        # Nicht existierender Parameter mit Standardwert
        self.assertIsNone(element.get_param(ProcessEnum.Y_COORDINATE))
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE, 0.0), 0.0)
        
        # Parameter überschreiben
        element.set_param(ProcessEnum.X_COORDINATE, 200.0, UnitEnum.METER)
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 200.0)
    
    def test_property_access(self):
        """Test: Zugriff auf Properties."""
        element = InfrastructureElement(name="PropertyTest")
        
        # Properties setzen
        element.east = 100.0
        element.north = 200.0
        element.altitude = 300.0
        element.azimuth = 45.0
        
        # Properties lesen
        self.assertEqual(element.east, 100.0)
        self.assertEqual(element.north, 200.0)
        self.assertEqual(element.altitude, 300.0)
        self.assertEqual(element.azimuth, 45.0)
        
        # Parameter-Zugriff über known_params prüfen
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 100.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE), 200.0)
        self.assertEqual(element.get_param(ProcessEnum.Z_COORDINATE), 300.0)
        self.assertEqual(element.get_param(ProcessEnum.AZIMUTH), 45.0)
    
    def test_validate_for_process(self):
        """Test: Validierung für einen Prozess."""
        element = InfrastructureElement(name="ValidationTest")
        
        # Element hat bereits die common Parameter
        self.assertEqual(element.validate_for_process("common"), [])
        
        # Element fehlen geometry Parameter
        missing_geometry = element.validate_for_process("geometry")
        self.assertIn(ProcessEnum.X_COORDINATE, missing_geometry)
        self.assertIn(ProcessEnum.Y_COORDINATE, missing_geometry)
        self.assertIn(ProcessEnum.Z_COORDINATE, missing_geometry)
        
        # Hinzufügen der fehlenden Parameter
        element.east = 100.0
        element.north = 200.0
        element.altitude = 300.0
        
        # Erneute Validierung
        self.assertEqual(element.validate_for_process("geometry"), [])
        
        # Fehlender Parameter für calculation
        missing_calculation = element.validate_for_process("calculation")
        self.assertIn(ProcessEnum.MATERIAL, missing_calculation)
        
        # Hinzufügen des fehlenden Parameters
        element.set_param(ProcessEnum.MATERIAL, "Beton")
        
        # Erneute Validierung
        self.assertEqual(element.validate_for_process("calculation"), [])
        
        # Test mit ungültigem Prozessnamen
        with self.assertRaises(ValueError):
            element.validate_for_process("unknown_process")
    
    def test_to_dict(self):
        """Test: Konvertierung in ein Dictionary."""
        element = InfrastructureElement(name="DictTest")
        element.east = 100.0
        element.north = 200.0
        element.set_param(ProcessEnum.MATERIAL, "Beton")
        
        element_dict = element.to_dict()
        
        # Basis-Attribute prüfen
        self.assertEqual(element_dict["name"], "DictTest")
        self.assertEqual(element_dict["element_type"], ElementType.FOUNDATION.value)
        self.assertIsInstance(element_dict["uuid"], str)
        
        # Parameter prüfen
        parameters = element_dict["parameters"]
        self.assertEqual(len(parameters), 6)  # UUID, Name, ElementType, X, Y, Material
        
        # Parameter-Werte prüfen
        param_dict = {p["name"]: p for p in parameters}
        self.assertEqual(param_dict["UUID"]["value"], str(element.uuid))
        self.assertEqual(param_dict["Name"]["value"], "DictTest")
        self.assertEqual(float(param_dict["X"]["value"]), 100.0)
        self.assertEqual(float(param_dict["Y"]["value"]), 200.0)
        self.assertEqual(param_dict["Material"]["value"], "Beton")


if __name__ == "__main__":
    unittest.main()