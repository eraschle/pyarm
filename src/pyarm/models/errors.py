import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement


class PyArmError(Exception):
    """Base class for all exceptions raised by the PyArm library."""

    @abc.abstractmethod
    def get_message(self) -> str:
        pass

    def __str__(self) -> str:
        return self.get_message()


class PyArmComponentError(PyArmError):
    """Exception raised when Element has no location."""

    def __init__(self, element: "InfrastructureElement", component: str):
        self.element = element
        self.component = component

    def get_message(self) -> str:
        name = self.element.name
        uuid = self.element.uuid
        cmp_name = self.component
        return f"Element {name} [UUID: {uuid}] has no component '{cmp_name}'."


class PyArmReferenceError(PyArmError):
    """Exception raised when Element has no location."""

    def __init__(self, message: str):
        self.message = message

    def get_message(self) -> str:
        return self.message


class PyArmParameterError(PyArmError):
    """Exception raised when Element has no location."""

    def __init__(self, element: "InfrastructureElement", process_param: str):
        self.element = element
        self.proc_param = process_param

    def get_message(self) -> str:
        name = self.element.name
        uuid = self.element.uuid
        param_name = self.proc_param
        return f"Element {name} [UUID: {uuid}] has no known parameter '{param_name}'."
