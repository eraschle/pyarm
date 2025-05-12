"""
Base models for infrastructure elements.
This module defines the basic structure of the data models
that are used in all processes.
"""

import abc
import logging
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    ClassVar,
    Optional,
    Type,
    cast,
)
from uuid import UUID, uuid4

from pyarm.components import (
    Component,
    ComponentFactory,
    ComponentType,
    Dimension,
    ElementReference,
    LineLocation,
    Location,
)
from pyarm.components.location import PointLocation
from pyarm.models.errors import PyArmComponentError, PyArmParameterError
from pyarm.models.parameter import (
    DataType,
    Parameter,
    UnitEnum,
)
from pyarm.models.process_enums import (
    ElementType,
    ProcessEnum,
)

# Import at the end of the file to avoid circular imports

log = logging.getLogger(__name__)


@dataclass
class InfrastructureElement[TDimension: Dimension](abc.ABC):
    """
    Base class for all infrastructure elements.
    Uses the flexible parameter model with process enums and components.
    """

    # Class attribute: Required parameters for different processes
    required_params: ClassVar[dict[str, set[ProcessEnum]]] = {
        "common": {
            ProcessEnum.UUID,
            ProcessEnum.NAME,
            ProcessEnum.ELEMENT_TYPE,
        },
        "geometry": {
            ProcessEnum.X_COORDINATE,
            ProcessEnum.Y_COORDINATE,
            ProcessEnum.Z_COORDINATE,
        },
        "visualization": {ProcessEnum.ELEMENT_TYPE},
        "calculation": {
            ProcessEnum.ELEMENT_TYPE,
        },
    }

    # Basic attributes
    name: str
    element_type: ElementType
    uuid: UUID = field(default_factory=uuid4)

    # Parameter storage
    parameters: list[Parameter] = field(default_factory=list)
    known_params: dict[ProcessEnum, Any] = field(
        default_factory=dict,
        repr=False,
    )

    # Component storage
    components: dict[str, "Component"] = field(
        default_factory=dict,
        repr=False,
    )

    def __post_init__(self):
        """
        After initialization: Analyze parameters and categorize in known_params.
        Also create standard components.
        """

        # Add standard parameters if they are missing
        if ProcessEnum.UUID not in self.known_params:
            self.parameters.append(
                Parameter(
                    name="UUID",
                    value=str(self.uuid),
                    process=ProcessEnum.UUID,
                    datatype=DataType.STRING,
                    unit=UnitEnum.NONE,
                )
            )

        if ProcessEnum.NAME not in self.known_params:
            self.parameters.append(
                Parameter(
                    name="Name",
                    value=self.name,
                    process=ProcessEnum.NAME,
                    datatype=DataType.STRING,
                    unit=UnitEnum.NONE,
                )
            )

        if ProcessEnum.ELEMENT_TYPE not in self.known_params:
            self.parameters.append(
                Parameter(
                    name="ElementType",
                    value=self.element_type.value,
                    process=ProcessEnum.ELEMENT_TYPE,
                    datatype=DataType.STRING,
                    unit=UnitEnum.NONE,
                )
            )

        self._update_known_params()
        # Create standard components
        self._initialize_components()

    def _update_known_params(self):
        self.known_params.clear()
        for param in self.parameters:
            if not isinstance(param.process, ProcessEnum):
                continue
            self.known_params[param.process] = param.value

    def _initialize_components(self):
        """Initializes the standard components based on the parameters."""
        component = ComponentFactory.create_location(self)
        self.components[component.name] = component

        component = ComponentFactory.create_dimension(self)
        self.components[component.name] = component

    def has_param(self, process_enum: ProcessEnum) -> bool:
        """
        Check if the parameter exists in the known parameters.

        Parameters
        ----------
        process_enum: ProcessEnum
            The ProcessEnum of the parameter to check

        Returns
        -------
        bool
            True if the parameter exists, False otherwise
        """
        return process_enum in self.known_params

    def get_param(self, process_enum: ProcessEnum) -> Parameter:
        """
        Return the parameter based on the process enum.

        Parameters
        ----------
        process_enum: ProcessEnum
            The ProcessEnum of the parameter to get

        Returns
        -------
        Parameter
            The Parameter or None if it does not exist
        """
        param = self.known_params.get(process_enum)
        if param is None:
            raise PyArmParameterError(self, process_enum)
        return param

    def get_reference_params(self, process_enum: ProcessEnum) -> list[Parameter]:
        """
        Returns zero, one or more parameters with the given process enum.

        Parameters
        ----------
        process_enum: ProcessEnum
            The ProcessEnum of the parameter to get

        Returns
        -------
        list[Parameter]
            List of Parameters with the given process enum
        """
        references = []
        for param in self.parameters:
            if param.process != process_enum:
                continue
            references.append(param)
        return references

    def get_component(self, component_name: str) -> Optional[Component]:
        """
        Returns a component by its name.

        Parameters
        ----------
        component_name: str
            Name of the component

        Returns
        -------
        Optional[Component]
            The component or None if it doesn't exist
        """
        return self.components.get(component_name)

    def get_components_by_type(self, component_type: ComponentType) -> list[Component]:
        """
        Returns all components of a specific type.

        Parameters
        ----------
        component_type: ComponentType
            Type of the components

        Returns
        -------
        list[Component]
            List of components of the specified type
        """
        return [comp for comp in self.components.values() if comp.component_type == component_type]

    def add_component(self, component: Component) -> None:
        """
        Adds a component or replaces an existing one with the same name.

        Parameters
        ----------
        component: Component
            The component to add
        """
        self.components[component.name] = component

    def remove_component(self, component_name: str) -> bool:
        """
        Removes a component by its name.

        Parameters
        ----------
        component_name: str
            Name of the component

        Returns
        -------
        bool
            True if the component was removed, False if it didn't exist
        """
        if component_name in self.components:
            del self.components[component_name]
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the element into a dictionary for serialization.

        Returns
        -------
        dict[str, Any]
            Dictionary with all attributes and parameters
        """
        result = {
            "name": self.name,
            "uuid": str(self.uuid),
            "element_type": self.element_type.value,
            "parameters": [],
        }

        # Add parameters
        for param in self.parameters:
            param_dict = {
                "name": param.name,
                "value": param.value,
                "datatype": param.datatype,
                "unit": param.unit.value,
            }

            if param.process:
                param_dict["process"] = param.process.value

            result["parameters"].append(param_dict)

        return result

    @property
    def location(self) -> Location:
        """Linear position of the element."""
        components = self.get_components_by_type(ComponentType.LOCATION)
        for comp in components:
            if not isinstance(comp, (PointLocation, LineLocation)):
                continue
            return comp
        raise PyArmComponentError(self, ComponentType.LOCATION)

    @property
    def dimension(self) -> TDimension:
        """Dimensions of the element."""
        components = self.get_components_by_type(ComponentType.DIMENSION)
        for comp in components:
            if not isinstance(comp, (PointLocation, LineLocation)):
                continue
            return cast(TDimension, comp)
        raise PyArmComponentError(self, ComponentType.DIMENSION)

    def does_reference_exist(self, reference: ElementReference) -> bool:
        return reference.name in self.components

    def update_reference_with(self, reference: ElementReference) -> None:
        """
        Adds the reference to the element if it doesn't exist.
        If it exists, it updates the reference with the new value.

        Parameters
        ----------
        reference: ElementReference
            The reference to add or update
        """
        if self.does_reference_exist(reference):
            return
        self.add_component(reference)

    def add_reference(
        self,
        reference_type: Type["InfrastructureElement"],
        referenced_uuid: UUID,
        bidirectional: bool = False,
    ) -> None:
        """
        Adds a reference to another element.
        If bidirectional is True, this only declares the intent;
        the RelationshipManager is responsible for creating the reverse link.

        Parameters
        ----------
        reference_type: Type["InfrastructureElement"]
            The class type of the referenced element (e.g., Foundation, Mast).
        referenced_uuid: UUID
            UUID of the referenced element
        bidirectional : bool, optional
            If True, indicates this reference is part of a bidirectional link.
            Defaults to False.
        """
        reference = ComponentFactory.create_reference(
            reference_type, referenced_uuid, bidirectional
        )
        self.add_component(reference)

    def get_references(self, reference_type: Optional[str] = None) -> list[ElementReference]:
        """
        Returns all references or only references of a specific type.

        Parameters
        ----------
        reference_type: Optional[str]
            Optional type of references

        Returns
        -------
        list[ElementReference]
            List of references
        """
        references = self.get_components_by_type(ComponentType.REFERENCE)
        references = [ref for ref in references if isinstance(ref, ElementReference)]
        if reference_type:
            references = [ref for ref in references if ref.reference_type == reference_type]
        return references

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InfrastructureElement):
            return False
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)
