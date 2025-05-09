"""
Unit Tests für die Basismodelle der Infrastrukturelemente.
"""

import unittest
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement, Parameter
from pyarm.models.parameter import UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.utils.helpers import DataType


class TestParameter(unittest.TestCase):
    """Tests für die Parameter-Klasse."""

    def test_create_parameter(self):
        """Test: Erstellung eines Parameters."""
        param = Parameter(
            name="TestParam",
            value=42.5,
            process=ProcessEnum.X_COORDINATE,
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
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
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        )

        # Parameter ohne Prozess
        param2 = Parameter(
            name="NoProcess",
            value="text",
            process=None,
            datatype=DataType.FLOAT,
            unit=UnitEnum.NONE,
        )

        self.assertEqual(str(param1), "TestParam: 42.5 m (X_COORDINATE)")
        self.assertEqual(str(param2), "NoProcess: text")


class TestInfrastructureElement(unittest.TestCase):
    """Tests für die InfrastructureElement-Klasse."""

    def test_create_element(self):
        """Test: Erstellung eines Elements mit Standardwerten."""
        element = InfrastructureElement(name="TestElement")

        self.assertEqual(element.name, "TestElement")
        self.assertIsInstance(element.uuid, UUID)
        self.assertEqual(element.element_type, ElementType.UNDEFINED)
        self.assertEqual(len(element.parameters), 3)  # UUID, Name, ElementType
        self.assertEqual(len(element.known_params), 3)

    def test_create_element_with_parameters(self):
        """Test: Erstellung eines Elements mit Parametern."""
        params = [
            Parameter(
                name="X",
                value=100.0,
                datatype=DataType.FLOAT,
                process=ProcessEnum.X_COORDINATE,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Y",
                value=200.0,
                datatype=DataType.FLOAT,
                process=ProcessEnum.Y_COORDINATE,
                unit=UnitEnum.METER,
            ),
        ]

        element = InfrastructureElement(
            name="ParamElement", element_type=ElementType.MAST, parameters=params
        )

        self.assertEqual(element.name, "ParamElement")
        self.assertEqual(element.element_type, ElementType.MAST)
        self.assertEqual(len(element.parameters), 5)  # 2 + UUID, Name, ElementType
        self.assertEqual(len(element.known_params), 5)

        # Prüfen der Parameter
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE), 100.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE), 200.0)

    def test_parameter_getter_setter(self):
        """Test: Getter und Setter für Parameter."""
        element = InfrastructureElement(name="GetterSetterTest")

        # Parameter abrufen
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE).value, 150.0)

        # Nicht existierender Parameter mit Standardwert
        self.assertIsNone(element.get_param(ProcessEnum.Y_COORDINATE))
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE), 0.0)
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE).value, 200.0)

    def test_property_access(self):
        """Test: Zugriff auf Properties."""
        element = InfrastructureElement(name="PropertyTest")

        # Properties lesen
        self.assertEqual(element.location.point.x, 100.0)
        self.assertEqual(element.location.point.y, 200.0)
        self.assertEqual(element.location.point.z, 300.0)
        self.assertEqual(element.location.point.rotation_x, 45.0)

        # Parameter-Zugriff über known_params prüfen
        self.assertEqual(element.get_param(ProcessEnum.X_COORDINATE).value, 100.0)
        self.assertEqual(element.get_param(ProcessEnum.Y_COORDINATE).value, 200.0)
        self.assertEqual(element.get_param(ProcessEnum.Z_COORDINATE).value, 300.0)
        self.assertEqual(element.get_param(ProcessEnum.ROTATION_X).value, 45.0)

    def test_to_dict(self):
        """Test: Konvertierung in ein Dictionary."""
        element = InfrastructureElement(name="DictTest")
        element_dict = element.to_dict()

        # Basis-Attribute prüfen
        self.assertEqual(element_dict["name"], "DictTest")
        self.assertEqual(element_dict["element_type"], ElementType.UNDEFINED.value)
        self.assertIsInstance(element_dict["uuid"], str)

        # Parameter prüfen
        parameters = element_dict["parameters"]
        self.assertEqual(len(parameters), 6)  # UUID, Name, ElementType, X, Y, Material

        # Parameter-Werte prüfen
        param_dict = {p["name"]: p for p in parameters}
        self.assertEqual(param_dict["UUID"]["value"], str(element.uuid))
        self.assertEqual(param_dict["Name"]["value"], "DictTest")
        self.assertEqual(float(param_dict["X_COORDINATE"]["value"]), 100.0)
        self.assertEqual(float(param_dict["Y_COORDINATE"]["value"]), 200.0)


if __name__ == "__main__":
    unittest.main()
