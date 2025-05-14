"""
Basic tests for the validation system.

This module contains tests for the basic validation functionality.
"""

import pytest
from typing import Dict, Any

from pyarm.validation.errors import ErrorSeverity, ValidationError, ValidationResult
from pyarm.validation.service import ValidationService
from pyarm.validation.interfaces import IValidator


class SimpleTestValidator(IValidator):
    """
    A simple validator for testing purposes.
    """
    
    @property
    def supported_element_types(self):
        return ["foundation", "mast"]
    
    def can_validate(self, element_type: str) -> bool:
        return element_type in self.supported_element_types
    
    def validate(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        result = ValidationResult()
        
        # Basic structure check
        if not isinstance(data, dict):
            result.add_error(
                ValidationError(
                    message="Data must be a dictionary",
                    context={"data_type": type(data).__name__},
                    severity=ErrorSeverity.CRITICAL,
                    element_type=element_type,
                )
            )
            return result
        
        # Required fields check
        required_fields = ["id", "name"]
        for field in required_fields:
            if field not in data:
                result.add_error(
                    ValidationError(
                        message=f"Required field '{field}' is missing",
                        context={"field": field},
                        severity=ErrorSeverity.ERROR,
                        element_type=element_type,
                        parameter_name=field
                    )
                )
        
        # Type check
        if "id" in data and not isinstance(data["id"], str):
            result.add_error(
                ValidationError(
                    message="Field 'id' must be a string",
                    context={"field_type": type(data["id"]).__name__},
                    severity=ErrorSeverity.ERROR,
                    element_type=element_type,
                    parameter_name="id"
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
        self.service = ValidationService()
        self.service.register_validator(self.validator)
    
    def test_validator_handles_non_dict_data(self):
        """
        Test: The validator correctly handles non-dictionary data.
        """
        # GIVEN different types of invalid data
        invalid_data_types = ["string", 123, None, [], True]
        
        # WHEN validating with each type
        for data in invalid_data_types:
            result = self.validator.validate(data, "foundation")
            
            # THEN critical errors are reported
            assert not result.is_valid
            assert len(result.errors) == 1
            assert result.errors[0].message == "Data must be a dictionary"
            assert result.errors[0].severity == ErrorSeverity.CRITICAL
    
    def test_validator_checks_required_fields(self):
        """
        Test: The validator checks for required fields.
        """
        # GIVEN data with missing required fields
        data1 = {}
        data2 = {"id": "test"}
        data3 = {"name": "Test Name"}
        data4 = {"id": "test", "name": "Test Name"}
        
        # WHEN validating each dataset
        result1 = self.validator.validate(data1, "foundation")
        result2 = self.validator.validate(data2, "foundation")
        result3 = self.validator.validate(data3, "foundation")
        result4 = self.validator.validate(data4, "foundation")
        
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
        data1 = {"id": 123, "name": "Test Name"}
        data2 = {"id": "test", "name": "Test Name"}
        
        # WHEN validating each dataset
        result1 = self.validator.validate(data1, "foundation")
        result2 = self.validator.validate(data2, "foundation")
        
        # THEN appropriate errors are reported
        assert not result1.is_valid
        assert len(result1.errors) == 1
        assert result1.errors[0].message == "Field 'id' must be a string"
        assert result1.errors[0].severity == ErrorSeverity.ERROR
        assert result1.errors[0].parameter_name == "id"
        
        assert result2.is_valid  # All fields have correct types
        assert len(result2.errors) == 0
    
    def test_validation_service_aggregates_results(self):
        """
        Test: The validation service aggregates results from multiple validators.
        """
        # GIVEN a collection of elements to validate (all dictionary objects)
        collection = [
            {"id": "1", "name": "Element 1"},
            {"id": 2, "name": "Element 2"},
            {"name": "Element 3"}
        ]
        
        # WHEN validating the collection
        results = self.service.validate_collection(collection, "foundation")
        
        # THEN each element is validated
        assert len(results) == 3
        
        # AND results are accurate for each element
        assert results[0].is_valid  # First element is valid
        assert not results[1].is_valid  # Second has wrong ID type
        assert not results[2].is_valid  # Third is missing ID
        
        # AND error counts match expectations
        valid_count = sum(1 for result in results if result.is_valid)
        assert valid_count == 1
        
        error_count = sum(len(result.errors) for result in results)
        assert error_count == 2  # 1 type error, 1 missing field
    
    def test_validation_report_creation(self):
        """
        Test: The validation service can create meaningful reports.
        """
        # GIVEN a collection of elements with various issues
        collection = [
            {"id": "1", "name": "Element 1"},  # Valid
            {"id": 2, "name": "Element 2"},    # Invalid ID type
            {"id": 3},                      # Missing name
            {"name": "Element 4"}           # Missing ID
        ]
        
        # WHEN creating a validation report
        results = self.service.validate_collection(collection, "foundation")
        report = self.service.create_validation_report("foundation", results)
        
        # THEN the report contains a meaningful summary
        assert "summary" in report
        assert report["summary"]["total_elements"] == 4
        assert report["summary"]["valid_elements"] == 1
        assert report["summary"]["invalid_elements"] == 3
        
        # AND error types are categorized
        assert "error_types" in report
        error_messages = [error["message"] for error in report["error_types"]]
        assert "Field 'id' must be a string" in error_messages
        assert "Required field 'name' is missing" in error_messages