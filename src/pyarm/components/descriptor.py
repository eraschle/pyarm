import abc
import logging
from typing import TYPE_CHECKING, Any

from pyarm.models.process_enums import ProcessEnum

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement
    from pyarm.models.parameter import Parameter

log = logging.getLogger(__name__)


class AComponentDescriptor:
    def __init__(self, element_attr: str) -> None:
        self.element_attr = element_attr

    def _get_element(self, instance: Any) -> "InfrastructureElement":
        from pyarm.models.base_models import InfrastructureElement

        element = getattr(instance, self.element_attr, None)
        if not isinstance(element, InfrastructureElement):
            log.error(f"{self.element_attr} must be an InfrastructureElement, got {type(element)}")
            raise TypeError(f"{self.element_attr} must return an InfrastructureElement")
        return element

    def _get_parameter(self, instance: Any) -> "Parameter":
        element = self._get_element(instance)
        process_enum = self._get_process_enum(instance)
        if process_enum not in element.known_params:
            log.error(
                f"Parameter {process_enum} from {self.element_attr} not found in {element.name}"
            )
            raise AttributeError(f"Parameter {process_enum} not found in {element.name}")
        return element.get_param(process_enum)

    def __get__(self, instance: Any, owner: Any) -> float:
        log.debug(f"Getting parameter value for {self.element_attr} in {instance} of {owner}")
        param = self._get_parameter(instance)
        return param.value

    def __set__(self, instance: Any, value: float) -> None:
        param = self._get_parameter(instance)
        param.value = value

    @abc.abstractmethod
    def _get_process_enum(self, instance: Any) -> ProcessEnum:
        pass


class ParameterDescriptor(AComponentDescriptor):
    def __init__(self, param: ProcessEnum, element_attr: str = "element") -> None:
        super().__init__(element_attr)
        self.param = param

    def _get_process_enum(self, instance: Any) -> ProcessEnum:
        log.debug(f"Getting process enum for {self.element_attr} in {instance}")
        return self.param
