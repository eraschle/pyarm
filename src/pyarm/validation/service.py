"""
Validierungsservice für das Validierungssystem.

Dieser Service koordiniert die Validierung von Elementen über verschiedene
Validatoren hinweg und bietet eine zentrale Schnittstelle für die Validierung.
"""

import logging
from typing import Any, Dict, List

from pyarm.validation.errors import ErrorSeverity, ValidationResult, ValidationWarning
from pyarm.validation.interfaces import IValidationService, IValidator

log = logging.getLogger(__name__)


class ValidationService(IValidationService):
    """
    Service zur Koordination von Validatoren und zur Durchführung von Validierungen.
    """

    def __init__(self):
        """Initialisiert den ValidationService."""
        self._validators: List[IValidator] = []

    def register_validator(self, validator: IValidator) -> None:
        """
        Registriert einen Validator beim Service.

        Parameters
        ----------
        validator : IValidator
            Der zu registrierende Validator
        """
        self._validators.append(validator)
        supported_types = ", ".join([str(t) for t in validator.supported_element_types])
        log.info(f"Validator für Elementtypen [{supported_types}] registriert")

    def get_validators_for_type(self, element_type: str) -> List[IValidator]:
        """
        Findet alle Validatoren, die den angegebenen Elementtyp validieren können.

        Parameters
        ----------
        element_type : str
            Der Elementtyp

        Returns
        -------
        List[IValidator]
            Liste von Validatoren, die den Elementtyp validieren können
        """
        return [v for v in self._validators if v.can_validate(element_type)]

    def validate_element(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        """
        Validiert ein einzelnes Element.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu validierenden Elementdaten
        element_type : str
            Der Elementtyp

        Returns
        -------
        ValidationResult
            Das Ergebnis der Validierung
        """
        result = ValidationResult()

        # Validatoren für diesen Elementtyp suchen
        validators = self.get_validators_for_type(element_type)

        if not validators:
            result.add_warning(
                ValidationWarning(
                    message=f"Keine Validatoren für Elementtyp {element_type} gefunden",
                    context={"element_type": element_type},
                )
            )
            return result

        # Alle Validatoren ausführen und Ergebnisse zusammenführen
        for validator in validators:
            validator_result = validator.validate(data, element_type)
            result.merge(validator_result)

        return result

    def validate_collection(
        self, data: List[Dict[str, Any]], element_type: str
    ) -> List[ValidationResult]:
        """
        Validiert eine Sammlung von Elementen.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            Die zu validierenden Elemente
        element_type : str
            Der Elementtyp

        Returns
        -------
        List[ValidationResult]
            Die Validierungsergebnisse für jedes Element
        """
        results = []

        for i, element_data in enumerate(data):
            # Element-ID für Logging extrahieren
            element_id = element_data.get("id", element_data.get("uuid", f"Element-{i + 1}"))
            log.debug(f"Validiere {element_type} {element_id}")

            # Element validieren
            result = self.validate_element(element_data, element_type)
            results.append(result)

            # Schwerwiegende Fehler loggen
            for error in result.errors:
                if error.severity == ErrorSeverity.CRITICAL:
                    log.error(f"Kritischer Validierungsfehler: {error}")
                elif error.severity == ErrorSeverity.ERROR:
                    log.warning(f"Validierungsfehler: {error}")

            # Warnungen loggen
            for warning in result.warnings:
                log.info(f"Validierungswarnung: {warning}")

        # Zusammenfassung loggen
        valid_count = sum(1 for result in results if result.is_valid)
        log.info(
            f"Validierungsergebnis: {valid_count} von "
            f"{len(results)} {element_type}-Elementen valide"
        )

        return results

    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Erstellt eine Zusammenfassung der Validierungsergebnisse.

        Parameters
        ----------
        results : List[ValidationResult]
            Die Validierungsergebnisse

        Returns
        -------
        Dict[str, Any]
            Zusammenfassung der Validierungsergebnisse
        """
        total = len(results)
        valid = sum(1 for result in results if result.is_valid)
        invalid = total - valid

        # Fehler nach Schweregrad zählen
        error_counts = {
            ErrorSeverity.CRITICAL.name: 0,
            ErrorSeverity.ERROR.name: 0,
            ErrorSeverity.WARNING.name: 0,
        }

        for result in results:
            for error in result.errors:
                error_counts[error.severity.name] += 1
            for warning in result.warnings:
                error_counts[warning.severity.name] += 1

        return {
            "total_elements": total,
            "valid_elements": valid,
            "invalid_elements": invalid,
            "validation_rate": valid / total if total > 0 else 0,
            "error_counts": error_counts,
        }

    def create_validation_report(
        self, element_type: str, results: List[ValidationResult]
    ) -> Dict[str, Any]:
        """
        Erstellt einen detaillierten Validierungsbericht.

        Parameters
        ----------
        element_type : str
            Der Elementtyp
        results : List[ValidationResult]
            Die Validierungsergebnisse

        Returns
        -------
        Dict[str, Any]
            Detaillierter Validierungsbericht
        """
        summary = self.get_validation_summary(results)

        # Aggregierte Fehlertypen
        error_types = {}

        for i, result in enumerate(results):
            for error in result.errors:
                error_message = error.message
                if error_message not in error_types:
                    error_types[error_message] = {
                        "count": 0,
                        "severity": error.severity.name,
                        "examples": [],
                    }

                error_info = error_types[error_message]
                error_info["count"] += 1

                # Beispiel-Kontext hinzufügen (maximal 5 Beispiele)
                if len(error_info["examples"]) < 5:
                    example = {
                        "element_index": i,
                        "element_type": error.element_type,
                        "element_id": error.element_id,
                        "parameter": error.parameter_name,
                        "context": error.context,
                    }
                    error_info["examples"].append(example)

        # Nach Häufigkeit sortierte Fehlertypen
        sorted_error_types = sorted(
            [{"message": msg, **info} for msg, info in error_types.items()],
            key=lambda x: x["count"],
            reverse=True,
        )

        return {
            "element_type": element_type,
            "summary": summary,
            "error_types": sorted_error_types,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
