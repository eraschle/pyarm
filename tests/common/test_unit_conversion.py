"""
Tests for unit conversion functionality in pyarm.
"""

import sys
import unittest
from math import pi
from pathlib import Path

# Add src to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pyarm.models import units
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ProcessEnum


class TestUnitConversion(unittest.TestCase):
    """Test cases for unit conversion functions."""

    def test_get_unit_category(self):
        """Test that unit categories are correctly identified."""
        # Test length units
        self.assertEqual(units.get_unit_category(UnitEnum.METER), "length")
        self.assertEqual(units.get_unit_category(UnitEnum.CENTIMETER), "length")

        # Test area units
        self.assertEqual(units.get_unit_category(UnitEnum.SQUARE_METER), "area")
        self.assertEqual(units.get_unit_category(UnitEnum.HECTARE), "area")

        # Test volume units
        self.assertEqual(units.get_unit_category(UnitEnum.CUBIC_METER), "volume")
        self.assertEqual(units.get_unit_category(UnitEnum.LITER), "volume")

        # Test unknown unit
        self.assertEqual(units.get_unit_category(UnitEnum.NONE), "unknown")

    def test_length_conversion(self):
        """Test conversion between length units."""
        # Test meter to centimeter
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.METER, UnitEnum.CENTIMETER), 100)

        # Test centimeter to meter
        self.assertAlmostEqual(units.convert_unit(100, UnitEnum.CENTIMETER, UnitEnum.METER), 1)

        # Test meter to millimeter
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.METER, UnitEnum.MILLIMETER), 1000)

        # Test kilometer to meter
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.KILOMETER, UnitEnum.METER), 1000)

    def test_area_conversion(self):
        """Test conversion between area units."""
        # Test square meter to square centimeter
        self.assertAlmostEqual(
            units.convert_unit(1, UnitEnum.SQUARE_METER, UnitEnum.SQUARE_CENTIMETER), 10000
        )

        # Test hectare to square meter
        self.assertAlmostEqual(
            units.convert_unit(1, UnitEnum.HECTARE, UnitEnum.SQUARE_METER), 10000
        )

    def test_volume_conversion(self):
        """Test conversion between volume units."""
        # Test cubic meter to liter
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.CUBIC_METER, UnitEnum.LITER), 1000)

        # Test liter to milliliter
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.LITER, UnitEnum.MILLILITER), 1000)

    def test_mass_conversion(self):
        """Test conversion between mass units."""
        # Test kilogram to gram
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.KILOGRAM, UnitEnum.GRAM), 1000)

        # Test ton to kilogram
        self.assertAlmostEqual(units.convert_unit(1, UnitEnum.TON, UnitEnum.KILOGRAM), 1000)

    def test_angle_conversion(self):
        """Test conversion between angle units."""
        # Test degree to radian
        self.assertAlmostEqual(units.convert_unit(180, UnitEnum.DEGREE, UnitEnum.RADIAN), pi)

        # Test radian to degree
        self.assertAlmostEqual(units.convert_unit(pi, UnitEnum.RADIAN, UnitEnum.DEGREE), 180)

        # Test grad to degree
        self.assertAlmostEqual(units.convert_unit(100, UnitEnum.GRAD, UnitEnum.DEGREE), 90)

    def test_temperature_conversion(self):
        """Test conversion between temperature units."""
        # Test celsius to kelvin
        self.assertAlmostEqual(units.convert_unit(0, UnitEnum.CELSIUS, UnitEnum.KELVIN), 273.15)

        # Test kelvin to celsius
        self.assertAlmostEqual(units.convert_unit(273.15, UnitEnum.KELVIN, UnitEnum.CELSIUS), 0)

    def test_cross_category_conversion_fails(self):
        """Test that conversion between different unit categories fails."""
        with self.assertRaises(ValueError):
            units.convert_unit(1, UnitEnum.METER, UnitEnum.KILOGRAM)

        with self.assertRaises(ValueError):
            units.convert_unit(1, UnitEnum.DEGREE, UnitEnum.SECOND)

    def test_parameter_unit_conversion(self):
        """Test conversion of a Parameter's unit."""
        # Create a parameter with meters
        param = Parameter(
            name="Length",
            value=1.0,
            datatype=DataType.FLOAT,
            process=ProcessEnum.LENGTH,
            unit=UnitEnum.METER,
        )

        # Convert to centimeters
        converted = units.convert_parameter_unit(param, UnitEnum.CENTIMETER)

        # Check results
        self.assertEqual(converted.name, "Length")
        self.assertAlmostEqual(converted.value, 100.0)
        self.assertEqual(converted.unit, UnitEnum.CENTIMETER)
        self.assertEqual(converted.process, ProcessEnum.LENGTH)

        # Original should be unchanged
        self.assertEqual(param.value, 1.0)
        self.assertEqual(param.unit, UnitEnum.METER)

    def test_convert_parameter_list(self):
        """Test conversion of a list of Parameters."""
        # Create parameters with different units
        params = [
            Parameter(
                name="Length",
                value=1.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Width",
                value=10.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.CENTIMETER,
            ),
            Parameter(
                name="Height",
                value=1000.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.MILLIMETER,
            ),
            Parameter(
                name="Name",
                value="Test",
                datatype=DataType.STRING,
                unit=UnitEnum.NONE,
            ),
        ]

        # Define conversion map
        unit_map = {UnitEnum.METER: UnitEnum.CENTIMETER, UnitEnum.MILLIMETER: UnitEnum.CENTIMETER}

        # Convert units
        converted = units.convert_parameter_list_units(params, unit_map)

        # Check results
        self.assertEqual(len(converted), 4)

        # Length: 1m -> 100cm
        self.assertEqual(converted[0].name, "Length")
        self.assertAlmostEqual(converted[0].value, 100.0)
        self.assertEqual(converted[0].unit, UnitEnum.CENTIMETER)

        # Width: Already in cm, should be unchanged
        self.assertEqual(converted[1].name, "Width")
        self.assertAlmostEqual(converted[1].value, 10.0)
        self.assertEqual(converted[1].unit, UnitEnum.CENTIMETER)

        # Height: 1000mm -> 100cm
        self.assertEqual(converted[2].name, "Height")
        self.assertAlmostEqual(converted[2].value, 100.0)
        self.assertEqual(converted[2].unit, UnitEnum.CENTIMETER)

        # Name: Not a numeric value, should be unchanged
        self.assertEqual(converted[3].name, "Name")
        self.assertEqual(converted[3].value, "Test")
        self.assertEqual(converted[3].unit, UnitEnum.NONE)

    def test_standardize_units(self):
        """Test standardization of units in a parameter list."""
        params = [
            Parameter(
                name="Length",
                value=100.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.CENTIMETER,
            ),
            Parameter(
                name="Area",
                value=10000.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.SQUARE_CENTIMETER,
            ),
            Parameter(
                name="Volume",
                value=1.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.LITER,
            ),
            Parameter(
                name="Temperature",
                value=20.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.CELSIUS,
            ),
            Parameter(
                name="Pressure",
                value=2.0,
                datatype=DataType.FLOAT,
                unit=UnitEnum.BAR,
            ),
        ]

        # Standardize units
        standardized = units.standardize_units(params)

        # Check results
        self.assertEqual(len(standardized), 5)

        # Length: 100cm -> 1m
        self.assertEqual(standardized[0].name, "Length")
        self.assertAlmostEqual(standardized[0].value, 1.0)
        self.assertEqual(standardized[0].unit, UnitEnum.METER)

        # Area: 10000cm² -> 1m²
        self.assertEqual(standardized[1].name, "Area")
        self.assertAlmostEqual(standardized[1].value, 1.0)
        self.assertEqual(standardized[1].unit, UnitEnum.SQUARE_METER)

        # Volume: 1L -> 0.001m³
        self.assertEqual(standardized[2].name, "Volume")
        self.assertAlmostEqual(standardized[2].value, 0.001)
        self.assertEqual(standardized[2].unit, UnitEnum.CUBIC_METER)

        # Temperature: 20°C -> 293.15K
        self.assertEqual(standardized[3].name, "Temperature")
        self.assertAlmostEqual(standardized[3].value, 293.15)
        self.assertEqual(standardized[3].unit, UnitEnum.KELVIN)

        # Pressure: 2bar -> 200000Pa
        self.assertEqual(standardized[4].name, "Pressure")
        self.assertAlmostEqual(standardized[4].value, 200000.0)
        self.assertEqual(standardized[4].unit, UnitEnum.PASCAL)

    def test_parameter_convert_to_method(self):
        """Test the convert_to method on Parameter class."""
        # Create a parameter with meters
        param = Parameter(
            name="Length",
            value=1.0,
            datatype=DataType.FLOAT,
            process=ProcessEnum.LENGTH,
            unit=UnitEnum.METER,
        )

        # Use the convert_to method
        converted = param.convert_to(UnitEnum.CENTIMETER)

        # Check results
        self.assertEqual(converted.name, "Length")
        self.assertAlmostEqual(converted.value, 100.0)
        self.assertEqual(converted.unit, UnitEnum.CENTIMETER)
        self.assertEqual(converted.process, ProcessEnum.LENGTH)

        # Original should be unchanged
        self.assertEqual(param.value, 1.0)
        self.assertEqual(param.unit, UnitEnum.METER)

    def test_parameter_with_standard_unit_method(self):
        """Test the with_standard_unit method on Parameter class."""
        # Create a parameter with non-standard unit
        param = Parameter(
            name="Length",
            value=100.0,
            datatype=DataType.FLOAT,
            process=ProcessEnum.LENGTH,
            unit=UnitEnum.CENTIMETER,
        )

        # Use the with_standard_unit method
        standardized = param.with_standard_unit()

        # Check results
        self.assertEqual(standardized.name, "Length")
        self.assertAlmostEqual(standardized.value, 1.0)
        self.assertEqual(standardized.unit, UnitEnum.METER)
        self.assertEqual(standardized.process, ProcessEnum.LENGTH)

        # Original should be unchanged
        self.assertEqual(param.value, 100.0)
        self.assertEqual(param.unit, UnitEnum.CENTIMETER)

    def test_parameter_factory_unit_conversion(self):
        """Test unit conversion in ParameterFactory."""
        from pyarm.factories.parameter import ParameterDefinition, ParameterFactory

        # Set up a custom parameter definition with centimeters
        custom_def = ParameterDefinition(
            process=None, name="Width", datatype=DataType.FLOAT, unit=UnitEnum.CENTIMETER
        )
        ParameterFactory.add_custom_definitions({"Width": custom_def})

        # Create a parameter with custom unit but standard process enum
        param = ParameterFactory.create(
            name="Width",
            process_enum=ProcessEnum.WIDTH,  # By default, this would use meters
            value=10.0,  # This value is interpreted in meters because ProcessEnum.WIDTH uses meters
        )

        # Check that the parameter uses centimeters (from custom definition)
        # but has the process enum WIDTH
        self.assertEqual(param.name, "Width")
        self.assertEqual(param.process, ProcessEnum.WIDTH)
        self.assertEqual(param.unit, UnitEnum.CENTIMETER)

        # Value is automatically converted from meters to centimeters
        # 10 meters = 1000 centimeters
        self.assertAlmostEqual(param.value, 1000)

        # Test a scenario with direct parameter creation (no unit conversion)
        from pyarm.models.parameter import Parameter

        # Create a parameter directly
        direct_param = Parameter(
            name="Direct",
            value=20.0,
            datatype=DataType.FLOAT,
            process=ProcessEnum.WIDTH,  # WIDTH typically uses meters
            unit=UnitEnum.CENTIMETER,  # But we explicitly use cm
        )

        # This should create a parameter with centimeters without conversion
        self.assertEqual(direct_param.name, "Direct")
        self.assertEqual(direct_param.unit, UnitEnum.CENTIMETER)
        self.assertAlmostEqual(direct_param.value, 20.0)  # Value stays as given

        # Now convert it to meters using the new conversion method
        meters_param = direct_param.convert_to(UnitEnum.METER)
        self.assertEqual(meters_param.unit, UnitEnum.METER)
        self.assertAlmostEqual(meters_param.value, 0.2)  # 20 cm = 0.2 m

        # Clean up
        ParameterFactory._custom_params.pop("Width", None)


if __name__ == "__main__":
    unittest.main()
