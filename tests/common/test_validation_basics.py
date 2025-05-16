"""
Basic tests for the validation system.

This module contains tests for the basic validation functionality.
"""

import pytest
from typing import Dict, Any

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.parameter import DataType
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.errors import ErrorSeverity, ValidationError, ValidationResult
from pyarm.interfaces.validator import IValidator
from pyarm.validation.pipeline import ValidationPipeline


class SimpleTestValidator(IValidator):
    """
    A simple validator for testing purposes.
    """

    @property
    def supported_element_types(self):
        return [ElementType.FOUNDATION, ElementType.MAST]

    def can_validate(self, element_type: ElementType) -> bool:
        return element_type in self.supported_element_types

    def validate(self, element: InfrastructureElement) -> ValidationResult:
        result = ValidationResult()
        if element.element_type not in self.supported_element_types:
            result.add_error(
                ValidationError(
                    message="Unsupported element type",
                    context={"element_type": element.element_type},
                    severity=ErrorSeverity.ERROR,
                    element_type=element.element_type,
                )
            )
            return result

        # Basic structure check
        if not isinstance(element, InfrastructureElement):
            result.add_error(
                ValidationError(
                    message="Data must be a dictionary",
                    context={"data_type": type(element).__name__},
                    severity=ErrorSeverity.CRITICAL,
                    element_type=element.element_type,
                )
            )
            return result

        # Required fields check
        required_fields = [ProcessEnum.X_COORDINATE, ProcessEnum.Y_COORDINATE]
        for field in required_fields:
            if element.has_param(field):
                continue
            result.add_error(
                ValidationError(
                    message=f"Required field '{field}' is missing",
                    context={"field": field},
                    severity=ErrorSeverity.ERROR,
                    element_type=element.element_type,
                    parameter_name=field,
                )
            )

        # Type check
        parameter = element.get_param(ProcessEnum.WIDTH)
        if parameter.is_float():
            result.add_error(
                ValidationError(
                    message=f"Field '{ProcessEnum.WIDTH}' must be a float.",
                    context={"data_type": DataType.FLOAT},
                    severity=ErrorSeverity.ERROR,
                    element_type=element.element_type,
                    parameter_name=ProcessEnum.WIDTH,
                )
            )

        return result


class TestValidationBasics:
    """
    Tests for basic validation functionality.
    """

    def setup_method(self):
        """
        Set up a test environment.
        """
        self.validator = SimpleTestValidator()

    def test_validator_checks_required_fields(self):
        """
        Test: The validator checks for required fields.
        """
        # GIVEN data with missing required fields
        elem1 = {}
        elem2 = {"id": "test"}
        elem3 = {"name": "Test Name"}
        elem4 = {"id": "test", "name": "Test Name"}

        # WHEN validating each dataset
        result1 = self.validator.validate(elem1)
        result2 = self.validator.validate(elem2)
        result3 = self.validator.validate(elem3)
        result4 = self.validator.validate(elem4)

        # THEN appropriate errors are reported
        assert not result1.is_valid
        assert len(result1.errors) == 2  # Both 'id' and 'name' missing
        assert any(e.message == "Required field 'id' is missing" for e in result1.errors)
        assert any(e.message == "Required field 'name' is missing" for e in result1.errors)

        assert not result2.is_valid
        assert len(result2.errors) == 1  # Only 'name' missing
        assert result2.errors[0].message == "Required field 'name' is missing"

        assert not result3.is_valid
        assert len(result3.errors) == 1  # Only 'id' missing
        assert result3.errors[0].message == "Required field 'id' is missing"

        assert result4.is_valid  # All required fields present
        assert len(result4.errors) == 0

    def test_validator_checks_field_types(self):
        """
        Test: The validator checks field types.
        """
        # GIVEN data with incorrect field types
        elem1 = {"id": 123, "name": "Test Name"}
        elem2 = {"id": "test", "name": "Test Name"}

        # WHEN validating each dataset
        result1 = self.validator.validate(elem1)
        result2 = self.validator.validate(elem2)

        # THEN appropriate errors are reported
        assert not result1.is_valid
        assert len(result1.errors) == 1
        assert result1.errors[0].message == "Field 'id' must be a string"
        assert result1.errors[0].severity == ErrorSeverity.ERROR
        assert result1.errors[0].parameter_name == "id"

        assert result2.is_valid  # All fields have correct types
        assert len(result2.errors) == 0
