"""
Factory für die Erstellung von Parameter-Instanzen.
Bietet eine standardisierte, konfigurierbare Möglichkeit zur Parametererstellung.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pyarm.components.metadata import ProjectPhaseComponent
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


@dataclass
class ParameterDefinition:
    """
    Definition eines Parameters mit allen Konfigurationsoptionen.
    Wird verwendet, um Parameter standardisiert zu erstellen.
    """

    process: Optional[ProcessEnum]
    name: Optional[str] = None  # Falls None, wird process.value verwendet
    datatype: DataType = DataType.STRING
    unit: UnitEnum = UnitEnum.NONE
    validation: Optional[Dict[str, Any]] = None  # Optional: Validierungsregeln
    component_definitions: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        if self.process is None and self.name is None:
            raise ValueError("Either process or name must be provided.")
        if self.unit != UnitEnum.NONE and self.datatype != DataType.FLOAT:
            self.datatype = DataType.FLOAT

    def get_name(self) -> str:
        """
        Returns the name of the parameter.
        If no name is provided, the process value is used.

        Returns
        -------
        str
            Name of the parameter
        """
        if self.process is None:
            return self.name  # pyright: ignore[reportReturnType]
        return self.name if self.name else self.process.value

    def create_parameter(self, value: Any) -> Parameter:
        """
        Creates a Parameter instance based on the definition.

        Parameters
        ----------
        value : Any
            Value of the parameter

        Returns
        -------
        Parameter
            The created parameter instance
        """
        param = Parameter(
            name=self.get_name(),
            value=value,
            datatype=self.datatype,
            process=self.process,
            unit=self.unit,
        )

        # Komponenten hinzufügen, falls definiert
        for comp_def in self.component_definitions:
            ParameterFactory._add_component_to_parameter(param, comp_def)

        return param


class ParameterFactory:
    """Factory to create parameters with standard definitions."""

    # Standarddefinitionen für häufig verwendete Parameter
    _standard_params: Dict[ProcessEnum, ParameterDefinition] = {
        ProcessEnum.NAME: ParameterDefinition(
            process=ProcessEnum.NAME,
            name="Name",
            datatype=DataType.STRING,
        ),
        ProcessEnum.ELEMENT_TYPE: ParameterDefinition(
            process=ProcessEnum.ELEMENT_TYPE,
            name="Element-Typ",
            datatype=DataType.STRING,
        ),
        ProcessEnum.UUID: ParameterDefinition(
            process=ProcessEnum.UUID,
            name="UUID",
            datatype=DataType.STRING,
        ),
        ProcessEnum.DOMAIN: ParameterDefinition(
            process=ProcessEnum.DOMAIN,
            name="Fachbereich",
            datatype=DataType.STRING,
        ),
        ProcessEnum.X_COORDINATE: ParameterDefinition(
            process=ProcessEnum.X_COORDINATE,
            name="East",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.Y_COORDINATE: ParameterDefinition(
            process=ProcessEnum.Y_COORDINATE,
            name="North",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.Z_COORDINATE: ParameterDefinition(
            process=ProcessEnum.Z_COORDINATE,
            name="Altitude",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.X_COORDINATE_END: ParameterDefinition(
            process=ProcessEnum.X_COORDINATE_END,
            name="East End",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.Y_COORDINATE_END: ParameterDefinition(
            process=ProcessEnum.Y_COORDINATE_END,
            name="North End",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.Z_COORDINATE_END: ParameterDefinition(
            process=ProcessEnum.Z_COORDINATE_END,
            name="Altitude End",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.LENGTH: ParameterDefinition(
            process=ProcessEnum.LENGTH,
            name="Länge",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.WIDTH: ParameterDefinition(
            process=ProcessEnum.WIDTH,
            name="Breite",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.HEIGHT: ParameterDefinition(
            process=ProcessEnum.HEIGHT,
            name="Höhe",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.DEPTH: ParameterDefinition(
            process=ProcessEnum.DEPTH,
            name="Tiefe",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.DIAMETER: ParameterDefinition(
            process=ProcessEnum.DIAMETER,
            name="Durchmesser",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.RADIUS: ParameterDefinition(
            process=ProcessEnum.RADIUS,
            name="Radius",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.SHAFT_MANHOLE_DIAMETER: ParameterDefinition(
            process=ProcessEnum.SHAFT_MANHOLE_DIAMETER,
            name="Deckel Durchmesser",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        ProcessEnum.ANGLE: ParameterDefinition(
            process=ProcessEnum.ANGLE,
            name="Winkel",
            datatype=DataType.FLOAT,
            unit=UnitEnum.DEGREE,
        ),
    }
    _custom_params: Dict[str, ParameterDefinition] = {}

    @classmethod
    def create_custom(cls, name: str, value: Any) -> Parameter:
        """
        Creates a custom parameter based on the provided definition.

        Parameters
        ----------
        name : str
            Name of the parameter
        value : Any
            Value of the parameter
        definition : Optional[ParameterDefinition], optional
            Definition of the parameter, by default None

        Returns
        -------
        Parameter
            The created custom parameter
        """
        if name not in cls._custom_params:
            raise ValueError(f"Custom parameter '{name}' not found.")
        definition = cls._custom_params[name]
        return definition.create_parameter(value)

    @classmethod
    def create_parameter(
        cls, process_enum: ProcessEnum, value: Any, definition: Optional[ParameterDefinition] = None
    ) -> Parameter:
        """
        Creates a Parameter based on a ProcessEnum and a value

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum of the parameter
        value : Any
            Value of the parameter
        definition : Optional[ParameterDefinition], optional
            Definition of the parameter, by default None
            If provided, it will be used instead of the standard definition

        Returns
        -------
        Parameter
            The created parameter
        """
        if definition:
            # Definierte ProcessEnum überschreiben
            if definition.process != process_enum:
                log.warning(
                    f"ProcessEnum in definition ({definition.process}) "
                    f"does not match provided one ({process_enum})."
                )
                definition = ParameterDefinition(
                    process=process_enum,
                    name=definition.name,
                    datatype=definition.datatype,
                    unit=definition.unit,
                    validation=definition.validation,
                    component_definitions=definition.component_definitions,
                )
            return definition.create_parameter(value)

        # Standard-Definition verwenden oder generische erstellen
        definition = cls._get_parameter_definition(process_enum)
        return definition.create_parameter(value)

    @classmethod
    def create(
        cls,
        name: str,
        process_enum: Optional[ProcessEnum],
        value: Any,
    ) -> Parameter:
        custom_param = cls.create_custom(name, value)
        if process_enum is None:
            return custom_param
        parameter = ParameterFactory.create_parameter(process_enum, value)
        parameter.name = name

        # Handle different units between custom parameter and standard parameter
        if custom_param.unit != UnitEnum.NONE and custom_param.unit != parameter.unit:
            parameter.unit = custom_param.unit
            parameter.datatype = custom_param.datatype
        return parameter

    @classmethod
    def _get_parameter_definition(cls, process_enum: ProcessEnum) -> ParameterDefinition:
        """
        Returns the appropriate ParameterDefinition for a given ProcessEnum.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum of the parameter

        Returns
        -------
        ParameterDefinition
            The corresponding ParameterDefinition
        """
        if process_enum in cls._standard_params:
            return cls._standard_params[process_enum]
        # Standarddefinition zurückgeben, wenn nichts passendes gefunden wurde
        return ParameterDefinition(process=process_enum)

    @staticmethod
    def _add_component_to_parameter(param: Parameter, component_def: Dict[str, Any]) -> None:
        """
        Adds a component to a parameter based on its definition.

        Parameters
        ----------
        param : Parameter
            The parameter to which the component will be added
        component_def : Dict[str, Any]
            Definition of the component to be added
        """
        comp_type = component_def.get("type")
        if comp_type == "building_phase":
            phase_comp = ProjectPhaseComponent()
            for phase_id in component_def.get("phase_ids", []):
                phase_comp.add_phase(phase_id)
            param.add_component(phase_comp)
        # Weitere Komponententypen hier hinzufügen...

    # Vordefinierte Parametererstellungsmethoden

    @classmethod
    def create_coordinate_parameter(
        cls,
        process_enum: ProcessEnum,
        value: float,
        name: Optional[str] = None,
        unit: UnitEnum = UnitEnum.METER,
    ) -> Parameter:
        """
        Creates a coordinate parameter.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum of the parameter (should be one of the coordinate enums)
        value : float
            Coordinate value
        name : Optional[str], optional
            Custom name, by default None
        unit : UnitEnum, optional
            Unit, by default UnitEnum.METER

        Returns
        -------
        Parameter
            The created coordinate parameter
        """
        definition = ParameterDefinition(
            process=process_enum, name=name, datatype=DataType.FLOAT, unit=unit
        )
        return definition.create_parameter(value)

    @classmethod
    def create_dimension_parameter(
        cls,
        process_enum: ProcessEnum,
        value: float,
        name: Optional[str] = None,
        unit: UnitEnum = UnitEnum.METER,
    ) -> Parameter:
        """
        Creates a dimension parameter.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum of the parameter (should be one of the dimension enums)
        value : float
            Dimension value
        name : Optional[str], optional
            Custom name, by default None
        unit : UnitEnum, optional
            Unit, by default UnitEnum.METER

        Returns
        -------
        Parameter
            The created dimension parameter
        """
        definition = ParameterDefinition(
            process=process_enum, name=name, datatype=DataType.FLOAT, unit=unit
        )
        return definition.create_parameter(value)

    @classmethod
    def add_standard_definitions(cls, definitions: Dict[ProcessEnum, ParameterDefinition]) -> None:
        """
        Adds or updates standard parameter definitions.

        Parameters
        ----------
        definitions : Dict[ProcessEnum, ParameterDefinition]
            Dictionary of ProcessEnum to ParameterDefinition
            to be added or updated in the standard definitions
        """
        cls._standard_params.update(definitions)

    @classmethod
    def add_custom_definitions(cls, definitions: Dict[str, ParameterDefinition]) -> None:
        """
        Adds or updates standard parameter definitions.

        Parameters
        ----------
        definitions : Dict[ProcessEnum, ParameterDefinition]
            Dictionary of ProcessEnum to ParameterDefinition
            to be added or updated in the standard definitions
        """
        for definition in definitions.values():
            if definition.unit == UnitEnum.NONE or definition.datatype == DataType.FLOAT:
                continue
            definition.datatype = DataType.FLOAT
            log.info(
                f"Custom parameter '{definition.name}' has unit {definition.unit} "
                f"and will be set to datatype FLOAT."
            )
        cls._custom_params.update(definitions)
