"""
Error definitions for the validation system.

This module defines various error types that can occur during validation
as well as a class for storing validation results.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class ErrorSeverity(Enum):
    """Severity level of a validation error."""

    CRITICAL = auto()  # Critical error that prevents conversion
    ERROR = auto()  # Severe error that may lead to data loss
    WARNING = auto()  # Warning, conversion can continue


@dataclass
class ValidationError:
    """Represents a validation error with context information."""

    message: str
    context: Dict[str, Any]  # Context-specific information (e.g., parameter name, value)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    element_type: Optional[str] = None
    element_id: Optional[str] = None
    parameter_name: Optional[str] = None

    def __str__(self) -> str:
        """Returns a formatted error message."""
        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        element_info = ""
        if self.element_type:
            element_info += f"[Type: {self.element_type}]"
        if self.element_id:
            element_info += f"[ID: {self.element_id}]"
        if self.parameter_name:
            element_info += f"[Parameter: {self.parameter_name}]"

        return f"{self.severity.name}: {self.message} {element_info} {{{context_str}}}"


@dataclass
class ValidationWarning(ValidationError):
    """Represents a validation warning."""

    severity: ErrorSeverity = ErrorSeverity.WARNING


@dataclass
class ValidationResult:
    """Contains the result of a validation with errors and warnings."""

    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)

    def add_error(self, error: ValidationError) -> None:
        """Adds an error and sets is_valid to False
        if it is a critical error."""
        self.errors.append(error)
        if error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.ERROR]:
            self.is_valid = False

    def add_warning(self, warning: ValidationWarning) -> None:
        """Adds a warning."""
        self.warnings.append(warning)

    def merge(self, other: "ValidationResult") -> None:
        """Merges two validation results."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def __str__(self) -> str:
        """Returns a summary of the validation result."""
        result = f"Validation {'successful' if self.is_valid else 'failed'}\n"
        if self.errors:
            result += f"Errors ({len(self.errors)}):\n"
            for error in self.errors:
                result += f"  - {error}\n"
        if self.warnings:
            result += f"Warnings ({len(self.warnings)}):\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"
        return result
