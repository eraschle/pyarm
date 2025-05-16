"""
Defines a validation pipeline for processing data through multiple validators.
"""

from pyarm.interfaces.process import IProcessProtocol
from pyarm.interfaces.validator import IValidator
from pyarm.models.base_models import InfrastructureElement
from pyarm.validation.errors import ValidationResult


class ValidationPipeline:
    """
    A pipeline that manages different validators for different processes.
    """

    def __init__(self):
        self.process_validators: dict[str, list[IValidator]] = {}

    def register_process(self, process: IProcessProtocol) -> None:
        """
        Registers a process and its validators.

        Parameters
        ----------
        process: ProcessProtocol
            The process to register
        """
        process_name = process.get_process_name()
        validators = process.get_validators()

        if not validators:
            return

        if process_name not in self.process_validators:
            self.process_validators[process_name] = []

        self.process_validators[process_name].extend(validators)

    def validate_for_process(
        self, process: str, element: InfrastructureElement
    ) -> ValidationResult:
        """
        Runs all validators for a specific process on the provided data.

        Parameters
        ----------
        process_name: str
            Name of the process to validate for
        element_type: ElementType
            Type of element being validated
        data: Dict
            Data to validate

        Returns
        -------
        ValidationResult
            Result of the validation
        """
        validation_result = ValidationResult()

        if process not in self.process_validators:
            return validation_result

        for validator in self.process_validators[process]:
            if not validator.can_validate(element=element):
                continue
            result = validator.validate(element=element)
            validation_result.merge(result)

        return validation_result
