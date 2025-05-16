"""
Error definitions for the validation system.

This module defines various error types that can occur during validation
as well as a class for storing validation results.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional


class ErrorSeverity(Enum):
    """Severity level of a validation error."""

    CRITICAL = auto()  # Critical error that prevents conversion
    ERROR = auto()  # Severe error that may lead to data loss
    WARNING = auto()  # Warning, conversion can continue
    INFO = auto()  # Informational message


class ValidationError:
    """Represents a validation error with context information."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        parameter_name: Optional[str] = None,
        element_type: Optional[str] = None,
        element_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.severity = severity
        self.parameter_name = parameter_name
        self.element_type = element_type
        self.element_id = element_id
        self.context = context or {}

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


class ValidationWarning(ValidationError):
    """Represents a validation warning."""

    def __init__(
        self,
        message: str,
        parameter_name: Optional[str] = None,
        element_type: Optional[str] = None,
        element_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            severity=ErrorSeverity.WARNING,
            parameter_name=parameter_name,
            element_type=element_type,
            element_id=element_id,
            context=context,
        )


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
        
    def has_errors(self, min_severity: ErrorSeverity = ErrorSeverity.ERROR) -> bool:
        """
        Prüft, ob Fehler mit mindestens dem angegebenen Schweregrad vorhanden sind.

        Parameters
        ----------
        min_severity : ErrorSeverity, optional
            Minimaler Schweregrad, standardmäßig ErrorSeverity.ERROR

        Returns
        -------
        bool
            True, wenn Fehler vorhanden sind, sonst False
        """
        for error in self.errors:
            if error.severity.value <= min_severity.value:  # Niedrigere Werte = höhere Schwere
                return True
        return False

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
