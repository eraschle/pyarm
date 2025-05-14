"""
Integration tests for the validation system.

This module contains tests for the integration between validation and the plugin system.
"""

import pytest
from typing import Dict, Any, List, Optional

from pyarm.interfaces.plugin import PluginInterface
from pyarm.validation.errors import ValidationResult
from pyarm.validation.interfaces import IValidationService, IValidator
from pyarm.validation.plugin_integration import ValidatedPlugin, ValidationPluginWrapper
from pyarm.validation.service import ValidationService


class MockPlugin(PluginInterface):
    """
    Mock plugin for testing validation integration.
    """
    
    def __init__(self, plugin_name="MockPlugin", plugin_version="1.0.0"):
        self._name = plugin_name
        self._version = plugin_version
        self.initialized = False
        self.convert_called = False
        self.last_data = None
        self.last_element_type = None
        self.should_fail = False
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def version(self) -> str:
        return self._version
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self.initialized = True
        self.config = config
        return True
    
    def get_supported_element_types(self) -> List[str]:
        return ["foundation", "mast"]
    
    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        self.convert_called = True
        self.last_data = data
        self.last_element_type = element_type
        
        if self.should_fail:
            return None
            
        return {
            "elements": [
                {"id": "test", "name": "Test Element", "type": element_type}
            ]
        }


class MockValidator(IValidator):
    """
    Mock validator for testing validation integration.
    """
    
    def __init__(self, should_fail=False):
        self.validate_called = False
        self.last_data = None
        self.last_element_type = None
        self.should_fail = should_fail
    
    @property
    def supported_element_types(self):
        return ["foundation", "mast"]
    
    def can_validate(self, element_type: str) -> bool:
        return element_type in self.supported_element_types
    
    def validate(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        self.validate_called = True
        self.last_data = data
        self.last_element_type = element_type
        
        result = ValidationResult()
        if self.should_fail:
            from pyarm.validation.errors import ValidationError, ErrorSeverity
            result.add_error(
                ValidationError(
                    message="Validation failed",
                    severity=ErrorSeverity.ERROR,
                    element_type=element_type
                )
            )
        return result


class MockValidationService(IValidationService):
    """
    Mock validation service for testing validation integration.
    """
    
    def __init__(self, should_fail=False):
        self.validators = []
        self.validate_called = False
        self.last_data = None
        self.last_element_type = None
        self.should_fail = should_fail
    
    def register_validator(self, validator: IValidator) -> None:
        self.validators.append(validator)
    
    def validate_element(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        self.validate_called = True
        self.last_data = data
        self.last_element_type = element_type
        
        result = ValidationResult()
        if self.should_fail:
            from pyarm.validation.errors import ValidationError, ErrorSeverity
            result.add_error(
                ValidationError(
                    message="Validation failed",
                    severity=ErrorSeverity.ERROR,
                    element_type=element_type
                )
            )
        return result
    
    def validate_collection(self, data: List[Dict[str, Any]], element_type: str) -> List[ValidationResult]:
        return [self.validate_element(item, element_type) for item in data]
    
    def create_validation_report(self, element_type: str, results: List[ValidationResult]) -> Dict[str, Any]:
        return {
            "element_type": element_type,
            "summary": {
                "total_elements": len(results),
                "valid_elements": sum(1 for r in results if r.is_valid),
                "invalid_elements": sum(1 for r in results if not r.is_valid),
            }
        }


class TestValidationPluginIntegration:
    """
    Tests for the integration between validation and the plugin system.
    """
    
    def setup_method(self):
        """
        Set up a test environment.
        """
        self.plugin = MockPlugin()
        self.validation_service = MockValidationService()
    
    def test_validated_plugin_initialization(self):
        """
        Test: ValidatedPlugin initialization passes through to the wrapped plugin.
        """
        # GIVEN a plugin and validation service
        plugin = self.plugin
        validation_service = self.validation_service
        
        # WHEN wrapping the plugin
        validated_plugin = ValidatedPlugin(plugin, validation_service)
        
        # THEN the ValidatedPlugin has the expected properties
        assert validated_plugin.name == "MockPlugin [Validiert]"
        assert validated_plugin.version == plugin.version
        
        # AND when initializing with a configuration
        config = {"test": "value", "validation": {"strict_mode": True}}
        result = validated_plugin.initialize(config)
        
        # THEN the initialization is passed through to the plugin
        assert result is True
        assert plugin.initialized is True
        
        # AND the validation config is extracted
        assert "validation" not in plugin.config
        assert plugin.config["test"] == "value"
    
    def test_validated_plugin_element_conversion_with_validation(self):
        """
        Test: ValidatedPlugin validates data before conversion.
        """
        # GIVEN a plugin wrapped with validation
        validated_plugin = ValidatedPlugin(self.plugin, self.validation_service)
        validated_plugin.initialize({"validation": {"enabled": True}})
        
        # WHEN converting an element
        data = {"data": [{"id": "test", "name": "Test Element"}], "project_id": "project1"}
        result = validated_plugin.convert_element(data, "foundation")
        
        # THEN validation is performed
        assert self.validation_service.validate_called is True
        assert self.validation_service.last_element_type == "foundation"
        
        # AND the plugin's convert_element is called
        assert self.plugin.convert_called is True
        assert self.plugin.last_data == data
        assert self.plugin.last_element_type == "foundation"
        
        # AND the result is returned
        assert result is not None
        assert "elements" in result
    
    def test_validated_plugin_with_disabled_validation(self):
        """
        Test: ValidatedPlugin skips validation when disabled.
        """
        # GIVEN a plugin with validation disabled
        validated_plugin = ValidatedPlugin(self.plugin, self.validation_service)
        validated_plugin.initialize({"validation": {"enabled": False}})
        
        # WHEN converting an element
        data = {"data": [{"id": "test", "name": "Test Element"}], "project_id": "project1"}
        result = validated_plugin.convert_element(data, "foundation")
        
        # THEN validation is not performed
        assert self.validation_service.validate_called is False
        
        # BUT the plugin's convert_element is still called
        assert self.plugin.convert_called is True
        assert result is not None
    
    def test_validated_plugin_with_strict_mode(self):
        """
        Test: ValidatedPlugin in strict mode rejects invalid data.
        """
        # GIVEN a plugin with validation in strict mode
        validation_service = MockValidationService(should_fail=True)
        validated_plugin = ValidatedPlugin(self.plugin, validation_service)
        validated_plugin.initialize({"validation": {"enabled": True, "strict_mode": True}})
        
        # WHEN converting an element that fails validation
        data = {"data": [{"id": "invalid", "name": "Invalid Element"}], "project_id": "project1"}
        result = validated_plugin.convert_element(data, "foundation")
        
        # THEN the conversion is rejected
        assert result is None
        
        # AND validation was performed
        assert validation_service.validate_called is True
        
        # BUT the plugin's convert_element is not called
        assert self.plugin.convert_called is False
    
    def test_validation_plugin_wrapper(self):
        """
        Test: ValidationPluginWrapper creates wrapped plugins.
        """
        # GIVEN a plugin and validation service
        plugin = self.plugin
        validation_service = self.validation_service
        
        # WHEN wrapping the plugin
        validated_plugin = ValidationPluginWrapper.wrap_plugin(plugin, validation_service)
        
        # THEN a ValidatedPlugin is returned
        assert isinstance(validated_plugin, ValidatedPlugin)
        assert validated_plugin.name == "MockPlugin [Validiert]"