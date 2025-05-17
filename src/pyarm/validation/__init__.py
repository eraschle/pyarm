"""
Validation system for data converters in PyArm.

This package provides a validation framework for verifying data before
conversion to the canonical data model. It enables systematic
validation with meaningful error messages.
"""

from pyarm.interfaces.validator import IValidator
from pyarm.validation.errors import ValidationError, ValidationResult, ValidationWarning
from pyarm.validation.pipeline import ValidationPipeline
from pyarm.validation.schema import Constraint, ConstraintType, SchemaDefinition
from pyarm.validation.schema_loader import load_schema_from_json, load_schemas_from_directory
from pyarm.validation.validators import GenericValidator

__all__ = [
    "ValidationError",
    "ValidationWarning",
    "ValidationResult",
    "IValidator",
    "SchemaDefinition",
    "Constraint",
    "ConstraintType",
    "GenericValidator",
    "ValidationPipeline",
    "load_schema_from_json",
    "load_schemas_from_directory",
]
