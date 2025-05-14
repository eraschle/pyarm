"""
Factory für die Erstellung von Parameter-Instanzen.
Bietet eine standardisierte, konfigurierbare Möglichkeit zur Parametererstellung.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pyarm.components.metadata import BuildingPhaseComponent
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ProcessEnum


@dataclass
class ParameterDefinition:
    """
    Definition eines Parameters mit allen Konfigurationsoptionen.
    Wird verwendet, um Parameter standardisiert zu erstellen.
    """

    process: ProcessEnum
    name: Optional[str] = None  # Falls None, wird process.value verwendet
    datatype: DataType = DataType.STRING
    unit: UnitEnum = UnitEnum.NONE
    validation: Optional[Dict[str, Any]] = None  # Optional: Validierungsregeln
    component_definitions: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Komponenten-Definitionen

    def get_name(self) -> str:
        """
        Gibt den Namen des Parameters zurück.
        Fällt auf process.value zurück, wenn nicht explizit gesetzt.

        Returns
        -------
        str
            Der Name des Parameters
        """
        return self.name if self.name else self.process.value

    def create_parameter(self, value: Any) -> Parameter:
        """
        Erstellt einen Parameter basierend auf dieser Definition.

        Parameters
        ----------
        value : Any
            Der Wert des Parameters

        Returns
        -------
        Parameter
            Der erstellte Parameter
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
    """Factory für die standardisierte Erstellung von Parametern."""

    # Standarddefinitionen für häufig verwendete Parameter
    _standard_params: Dict[ProcessEnum, ParameterDefinition] = {
        # Koordinaten
        ProcessEnum.X_COORDINATE: ParameterDefinition(
            process=ProcessEnum.X_COORDINATE, name="X", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.Y_COORDINATE: ParameterDefinition(
            process=ProcessEnum.Y_COORDINATE, name="Y", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.Z_COORDINATE: ParameterDefinition(
            process=ProcessEnum.Z_COORDINATE, name="Z", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        # Dimensionen
        ProcessEnum.HEIGHT: ParameterDefinition(
            process=ProcessEnum.HEIGHT, name="Höhe", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.WIDTH: ParameterDefinition(
            process=ProcessEnum.WIDTH, name="Breite", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.DEPTH: ParameterDefinition(
            process=ProcessEnum.DEPTH, name="Tiefe", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.LENGTH: ParameterDefinition(
            process=ProcessEnum.LENGTH, name="Länge", datatype=DataType.FLOAT, unit=UnitEnum.METER
        ),
        ProcessEnum.DIAMETER: ParameterDefinition(
            process=ProcessEnum.DIAMETER,
            name="Durchmesser",
            datatype=DataType.FLOAT,
            unit=UnitEnum.METER,
        ),
        # Elementspezifische Parameter
        ProcessEnum.MAST_TYPE: ParameterDefinition(
            process=ProcessEnum.MAST_TYPE, name="Masttyp", datatype=DataType.STRING
        ),
        ProcessEnum.FOUNDATION_TYPE: ParameterDefinition(
            process=ProcessEnum.FOUNDATION_TYPE, name="Fundamenttyp", datatype=DataType.STRING
        ),
        ProcessEnum.TRACK_TYPE: ParameterDefinition(
            process=ProcessEnum.TRACK_TYPE, name="Gleistyp", datatype=DataType.STRING
        ),
        # IFC-bezogene Parameter
        ProcessEnum.IFC_GLOBAL_ID: ParameterDefinition(
            process=ProcessEnum.IFC_GLOBAL_ID, name="IFC Global ID", datatype=DataType.STRING
        ),
        ProcessEnum.IFC_TYPE: ParameterDefinition(
            process=ProcessEnum.IFC_TYPE, name="IFC Typ", datatype=DataType.STRING
        ),
    }

    @classmethod
    def create_parameter(
        cls, process_enum: ProcessEnum, value: Any, definition: Optional[ParameterDefinition] = None
    ) -> Parameter:
        """
        Erstellt einen Parameter basierend auf einer ProcessEnum und einem Wert.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum des Parameters
        value : Any
            Wert des Parameters
        definition : Optional[ParameterDefinition], optional
            Benutzerdefinierte Definition, by default None

        Returns
        -------
        Parameter
            Der erstellte Parameter
        """
        if definition:
            # Definierte ProcessEnum überschreiben
            if definition.process != process_enum:
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
    def _get_parameter_definition(cls, process_enum: ProcessEnum) -> ParameterDefinition:
        """
        Holt die passende ParameterDefinition mit Fallback auf generische Definition.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum des Parameters

        Returns
        -------
        ParameterDefinition
            Die passende ParameterDefinition
        """
        if process_enum in cls._standard_params:
            return cls._standard_params[process_enum]
        # Standarddefinition zurückgeben, wenn nichts passendes gefunden wurde
        return ParameterDefinition(process=process_enum)

    @staticmethod
    def _add_component_to_parameter(param: Parameter, component_def: Dict[str, Any]) -> None:
        """
        Fügt eine Komponente zum Parameter basierend auf der Definition hinzu.

        Parameters
        ----------
        param : Parameter
            Der Parameter, dem die Komponente hinzugefügt werden soll
        component_def : Dict[str, Any]
            Definition der Komponente
        """
        comp_type = component_def.get("type")
        if comp_type == "building_phase":
            phase_comp = BuildingPhaseComponent()
            for phase_id in component_def.get("phase_ids", []):
                phase_comp.add_phase_reference(phase_id)
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
        Erstellt einen Koordinaten-Parameter.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum des Parameters (sollte eine der Koordinaten-Enums sein)
        value : float
            Koordinatenwert
        name : Optional[str], optional
            Benutzerdefinierter Name, by default None
        unit : UnitEnum, optional
            Einheit, by default UnitEnum.METER

        Returns
        -------
        Parameter
            Der erstellte Koordinaten-Parameter
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
        Erstellt einen Dimensions-Parameter.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum des Parameters (sollte eine der Dimensions-Enums sein)
        value : float
            Dimensionswert
        name : Optional[str], optional
            Benutzerdefinierter Name, by default None
        unit : UnitEnum, optional
            Einheit, by default UnitEnum.METER

        Returns
        -------
        Parameter
            Der erstellte Dimensions-Parameter
        """
        definition = ParameterDefinition(
            process=process_enum, name=name, datatype=DataType.FLOAT, unit=unit
        )
        return definition.create_parameter(value)

    @classmethod
    def create_type_parameter(
        cls, process_enum: ProcessEnum, value: str, name: Optional[str] = None
    ) -> Parameter:
        """
        Erstellt einen Typ-Parameter.

        Parameters
        ----------
        process_enum : ProcessEnum
            ProcessEnum des Parameters
        value : str
            Typwert
        name : Optional[str], optional
            Benutzerdefinierter Name, by default None

        Returns
        -------
        Parameter
            Der erstellte Typ-Parameter
        """
        definition = ParameterDefinition(process=process_enum, name=name, datatype=DataType.STRING)
        return definition.create_parameter(value)

    @classmethod
    def add_standard_definitions(cls, definitions: Dict[ProcessEnum, ParameterDefinition]) -> None:
        """
        Fügt benutzerdefinierte Standarddefinitionen hinzu oder aktualisiert bestehende.

        Parameters
        ----------
        definitions : Dict[ProcessEnum, ParameterDefinition]
            Zu ergänzende/aktualisierende Definitionen
        """
        cls._standard_params.update(definitions)
