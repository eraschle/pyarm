"""
Validation system for data converters in PyArm.

This package provides a validation framework for verifying data before
conversion to the canonical data model. It enables systematic
validation with meaningful error messages.
"""

from pyarm.validation.errors import ValidationError, ValidationWarning, ValidationResult
from pyarm.validation.interfaces import IValidator, IValidationService
from pyarm.validation.schema import SchemaDefinition, Constraint, ConstraintType
from pyarm.validation.validators import GenericValidator, ElementValidator
from pyarm.validation.service import ValidationService

__all__ = [
    "ValidationError",
    "ValidationWarning",
    "ValidationResult",
    "IValidator",
    "IValidationService",
    "SchemaDefinition",
    "Constraint",
    "ConstraintType",
    "GenericValidator",
    "ElementValidator",
    "ValidationService",
]