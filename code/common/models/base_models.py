"""
Basismodelle für die Infrastrukturelemente.
Dieses Modul definiert die grundlegende Struktur der Datenmodelle,
die in allen Prozessen verwendet werden.
"""

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Type, TypeVar, cast
from uuid import UUID, uuid4

from ..enums.process_enums import ProcessEnum, ElementType, UnitEnum
from .components import (
    Component, 
    ComponentType, 
    CoordinateLocation, 
    LineLocation, 
    Dimension, 
    MaterialProperties, 
    ElementReference,
    ComponentFactory
)


@dataclass
class Parameter:
    """
    Repräsentiert einen einzelnen Parameter eines Infrastrukturelements.
    """

    name: str  # Originaler Name aus der Datenquelle
    value: Any  # Wert des Parameters
    process: Optional[ProcessEnum] = None  # Zuordnung zum Prozess-Enum
    datatype: str = "str"  # Datentyp als String
    unit: UnitEnum = UnitEnum.NONE  # Einheit des Parameters

    def __str__(self) -> str:
        """String-Repräsentation des Parameters."""
        unit_str = f" {self.unit.value}" if self.unit != UnitEnum.NONE else ""
        process_str = f" ({self.process})" if self.process else ""
        return f"{self.name}: {self.value}{unit_str}{process_str}"


@dataclass
class InfrastructureElement:
    """
    Basisklasse für alle Infrastrukturelemente.
    Verwendet das flexible Parameter-Modell mit Prozess-Enums und Komponenten.
    """

    # Grundlegende Attribute
    name: str
    uuid: UUID = field(default_factory=uuid4)
    element_type: ElementType = field(default=ElementType.NONE)

    # Parameter-Speicherung
    parameters: List[Parameter] = field(default_factory=list)
    known_params: Dict[ProcessEnum, Any] = field(default_factory=dict, repr=False)
    
    # Komponenten-Speicherung
    components: Dict[str, Component] = field(default_factory=dict, repr=False)

    # Klassenattribut: Erforderliche Parameter für verschiedene Prozesse
    required_params: ClassVar[Dict[str, set[ProcessEnum]]] = {
        "common": {ProcessEnum.UUID, ProcessEnum.NAME, ProcessEnum.ELEMENT_TYPE},
        "geometry": {
            ProcessEnum.X_COORDINATE,
            ProcessEnum.Y_COORDINATE,
            ProcessEnum.Z_COORDINATE,
        },
        "visualization": {ProcessEnum.ELEMENT_TYPE},
        "calculation": {ProcessEnum.ELEMENT_TYPE, ProcessEnum.MATERIAL},
    }

    def __post_init__(self):
        """
        Nach Initialisierung: Parameter analysieren und in known_params einordnen.
        Außerdem Standardkomponenten erstellen.
        """
        for param in self.parameters:
            if isinstance(param.process, ProcessEnum):
                self.known_params[param.process] = param.value

        # Standard-Parameter hinzufügen, wenn sie fehlen
        if ProcessEnum.UUID not in self.known_params:
            self.known_params[ProcessEnum.UUID] = str(self.uuid)
            self.parameters.append(
                Parameter(
                    name="UUID",
                    value=str(self.uuid),
                    process=ProcessEnum.UUID,
                    datatype="str",
                )
            )

        if ProcessEnum.NAME not in self.known_params:
            self.known_params[ProcessEnum.NAME] = self.name
            self.parameters.append(
                Parameter(
                    name="Name",
                    value=self.name,
                    process=ProcessEnum.NAME,
                    datatype="str",
                )
            )

        if ProcessEnum.ELEMENT_TYPE not in self.known_params:
            self.known_params[ProcessEnum.ELEMENT_TYPE] = self.element_type.value
            self.parameters.append(
                Parameter(
                    name="ElementType",
                    value=self.element_type.value,
                    process=ProcessEnum.ELEMENT_TYPE,
                    datatype="str",
                )
            )
            
        # Standardkomponenten erstellen
        self._initialize_components()

    def _initialize_components(self):
        """Initialisiert die Standardkomponenten basierend auf den Parametern."""
        # Position
        location = ComponentFactory.create_location_from_params(self.known_params)
        if location:
            self.components[location.name] = location
            
        # Linienposition für Elemente mit Start- und Endpunkt
        line_location = ComponentFactory.create_line_location_from_params(self.known_params)
        if line_location:
            self.components[line_location.name] = line_location
            
        # Dimensionen je nach Elementtyp
        if self.element_type == ElementType.FOUNDATION:
            dimension = ComponentFactory.create_foundation_dimension(self.known_params)
            if dimension:
                self.components[dimension.name] = dimension
        elif self.element_type == ElementType.MAST:
            dimension = ComponentFactory.create_mast_dimension(self.known_params)
            if dimension:
                self.components[dimension.name] = dimension
        elif self.element_type == ElementType.DRAINAGE_PIPE:
            dimension = ComponentFactory.create_pipe_dimension(self.known_params)
            if dimension:
                self.components[dimension.name] = dimension
        elif self.element_type == ElementType.DRAINAGE_SHAFT:
            dimension = ComponentFactory.create_shaft_dimension(self.known_params)
            if dimension:
                self.components[dimension.name] = dimension
        elif self.element_type == ElementType.TRACK:
            dimension = ComponentFactory.create_track_dimension(self.known_params)
            if dimension:
                self.components[dimension.name] = dimension
                
        # Material
        material = ComponentFactory.create_material_from_params(self.known_params)
        if material:
            self.components[material.name] = material
            
    def get_param(self, process_enum: ProcessEnum, default: Any = None) -> Any:
        """
        Gibt den Wert eines Parameters basierend auf dem Prozess-Enum zurück.

        Args:
            process_enum: Das ProcessEnum des gesuchten Parameters
            default: Standardwert, falls der Parameter nicht gefunden wird

        Returns:
            Der Wert des Parameters oder der Standardwert
        """
        return self.known_params.get(process_enum, default)

    def set_param(
        self,
        process_enum: ProcessEnum,
        value: Any,
        unit: UnitEnum = UnitEnum.NONE,
        name: Optional[str] = None,
    ) -> None:
        """
        Setzt einen Parameter basierend auf dem Prozess-Enum.

        Args:
            process_enum: Das ProcessEnum des zu setzenden Parameters
            value: Der neue Wert des Parameters
            unit: Die Einheit des Parameters
            name: Optionaler Name für den Parameter, falls neu
        """
        # Wert im Dictionary aktualisieren
        self.known_params[process_enum] = value

        # Parameter in der Liste aktualisieren oder neu anlegen
        param_name = name or process_enum.value
        data_type = type(value).__name__

        # Existierenden Parameter suchen
        existing_param = next(
            (p for p in self.parameters if p.process == process_enum), None
        )

        if existing_param:
            # Existierenden Parameter aktualisieren
            existing_param.value = value
            existing_param.datatype = data_type
            existing_param.unit = unit
        else:
            # Neuen Parameter anlegen
            new_param = Parameter(
                name=param_name,
                value=value,
                process=process_enum,
                datatype=data_type,
                unit=unit,
            )
            self.parameters.append(new_param)
            
        # Betroffene Komponenten aktualisieren
        self._update_components_for_param(process_enum)
            
    def _update_components_for_param(self, process_enum: ProcessEnum):
        """Aktualisiert die Komponenten basierend auf einer Parameteränderung."""
        # Position aktualisieren
        if process_enum in (ProcessEnum.X_COORDINATE, ProcessEnum.Y_COORDINATE, ProcessEnum.Z_COORDINATE):
            if "main_location" in self.components:
                # Existierende Komponente aktualisieren
                location = cast(CoordinateLocation, self.components["main_location"])
                if process_enum == ProcessEnum.X_COORDINATE:
                    location.x = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Y_COORDINATE:
                    location.y = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Z_COORDINATE:
                    location.z = self.get_param(process_enum)
            else:
                # Neue Komponente erstellen
                location = ComponentFactory.create_location_from_params(self.known_params)
                if location:
                    self.components[location.name] = location
                    
        # Linienposition aktualisieren
        if process_enum in (
            ProcessEnum.X_COORDINATE, ProcessEnum.Y_COORDINATE, ProcessEnum.Z_COORDINATE,
            ProcessEnum.X_COORDINATE_END, ProcessEnum.Y_COORDINATE_END, ProcessEnum.Z_COORDINATE_END
        ):
            if "line_location" in self.components:
                # Existierende Komponente aktualisieren
                line_location = cast(LineLocation, self.components["line_location"])
                if process_enum == ProcessEnum.X_COORDINATE:
                    line_location.start.x = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Y_COORDINATE:
                    line_location.start.y = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Z_COORDINATE:
                    line_location.start.z = self.get_param(process_enum)
                elif process_enum == ProcessEnum.X_COORDINATE_END:
                    line_location.end.x = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Y_COORDINATE_END:
                    line_location.end.y = self.get_param(process_enum)
                elif process_enum == ProcessEnum.Z_COORDINATE_END:
                    line_location.end.z = self.get_param(process_enum)
            else:
                # Neue Komponente erstellen
                line_location = ComponentFactory.create_line_location_from_params(self.known_params)
                if line_location:
                    self.components[line_location.name] = line_location
                    
        # Dimensionen und weitere Parameter nach Bedarf aktualisieren...
        # Hier würde je nach Elementtyp die richtige Dimension aktualisiert werden

    def get_component(self, component_name: str) -> Optional[Component]:
        """
        Gibt eine Komponente anhand ihres Namens zurück.

        Args:
            component_name: Name der Komponente

        Returns:
            Die Komponente oder None, wenn sie nicht existiert
        """
        return self.components.get(component_name)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[Component]:
        """
        Gibt alle Komponenten eines bestimmten Typs zurück.

        Args:
            component_type: Typ der Komponenten

        Returns:
            Liste der Komponenten des angegebenen Typs
        """
        return [comp for comp in self.components.values() if comp.component_type == component_type]
    
    def add_component(self, component: Component) -> None:
        """
        Fügt eine Komponente hinzu oder ersetzt eine existierende mit dem gleichen Namen.

        Args:
            component: Die hinzuzufügende Komponente
        """
        self.components[component.name] = component
    
    def remove_component(self, component_name: str) -> bool:
        """
        Entfernt eine Komponente anhand ihres Namens.

        Args:
            component_name: Name der Komponente

        Returns:
            True, wenn die Komponente entfernt wurde, False, wenn sie nicht existierte
        """
        if component_name in self.components:
            del self.components[component_name]
            return True
        return False

    def validate_for_process(self, process_name: str) -> List[ProcessEnum]:
        """
        Prüft, ob alle erforderlichen Parameter für einen Prozess vorhanden sind.

        Args:
            process_name: Name des Prozesses ("common", "geometry", "visualization", "calculation")

        Returns:
            Liste fehlender Parameter
        """
        if process_name not in self.required_params:
            raise ValueError(f"Unknown process: {process_name}")

        required = self.required_params[process_name]
        missing = [param for param in required if param not in self.known_params]
        return missing

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Element in ein Dictionary zur Serialisierung.

        Returns:
            Dictionary mit allen Attributen und Parametern
        """
        result = {
            "name": self.name,
            "uuid": str(self.uuid),
            "element_type": self.element_type.value,
            "parameters": [],
        }

        # Parameter hinzufügen
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

    # Häufig verwendete Properties für Basiskoordinaten
    @property
    def position(self) -> Optional[CoordinateLocation]:
        """Position des Elements im Raum."""
        location_components = self.get_components_by_type(ComponentType.LOCATION)
        for comp in location_components:
            if isinstance(comp, CoordinateLocation) and comp.name == "main_location":
                return comp
        return None
    
    @property
    def location(self) -> Optional[LineLocation]:
        """Linienförmige Position des Elements."""
        location_components = self.get_components_by_type(ComponentType.LOCATION)
        for comp in location_components:
            if isinstance(comp, LineLocation):
                return comp
        return None
    
    @property
    def dimensions(self) -> Optional[Dimension]:
        """Abmessungen des Elements."""
        dimension_components = self.get_components_by_type(ComponentType.DIMENSION)
        if dimension_components:
            return cast(Dimension, dimension_components[0])
        return None
    
    @property
    def material(self) -> Optional[MaterialProperties]:
        """Materialeigenschaften des Elements."""
        material_components = self.get_components_by_type(ComponentType.MATERIAL)
        if material_components:
            return cast(MaterialProperties, material_components[0])
        return None

    # Rückwärtskompatibilität für die bisherigen Eigenschaften
    @property
    def east(self) -> Optional[float]:
        """X-Koordinate des Elements (rückwärtskompatibel)."""
        if self.position:
            return self.position.x
        return self.get_param(ProcessEnum.X_COORDINATE)

    @east.setter
    def east(self, value: float) -> None:
        """X-Koordinate setzen (rückwärtskompatibel)."""
        self.set_param(ProcessEnum.X_COORDINATE, value, UnitEnum.METER)

    @property
    def north(self) -> Optional[float]:
        """Y-Koordinate des Elements (rückwärtskompatibel)."""
        if self.position:
            return self.position.y
        return self.get_param(ProcessEnum.Y_COORDINATE)

    @north.setter
    def north(self, value: float) -> None:
        """Y-Koordinate setzen (rückwärtskompatibel)."""
        self.set_param(ProcessEnum.Y_COORDINATE, value, UnitEnum.METER)

    @property
    def altitude(self) -> Optional[float]:
        """Z-Koordinate des Elements (rückwärtskompatibel)."""
        if self.position:
            return self.position.z
        return self.get_param(ProcessEnum.Z_COORDINATE)

    @altitude.setter
    def altitude(self, value: float) -> None:
        """Z-Koordinate setzen (rückwärtskompatibel)."""
        self.set_param(ProcessEnum.Z_COORDINATE, value, UnitEnum.METER)

    @property
    def azimuth(self) -> Optional[float]:
        """Azimut des Elements (rückwärtskompatibel)."""
        return self.get_param(ProcessEnum.AZIMUTH)

    @azimuth.setter
    def azimuth(self, value: float) -> None:
        """Azimut setzen (rückwärtskompatibel)."""
        self.set_param(ProcessEnum.AZIMUTH, value, UnitEnum.DEGREE)


# Typisierte Basisklasse für eine verbesserte Vererbungshierarchie
T = TypeVar('T', bound=InfrastructureElement)


class ElementFactory:
    """Factory für die Erstellung von spezialisierten Elementen."""
    
    @staticmethod
    def create_from_data(
        data: Dict[str, Any],
        element_class: Optional[Type[T]] = None
    ) -> InfrastructureElement:
        """
        Erstellt ein Element aus den angegebenen Daten.
        Verwendet die angegebene Klasse oder wählt eine passende basierend auf element_type.
        
        Args:
            data: Die Elementdaten
            element_class: Optional eine spezifische Klasse zu verwenden
            
        Returns:
            Das erstellte Element
        """
        # Basisattribute extrahieren
        name = data.get("name", "Unbekannt")
        uuid_value = data.get("uuid")
        uuid = UUID(uuid_value) if uuid_value else uuid4()
        
        # Element-Typ ermitteln
        element_type_value = data.get("element_type")
        if isinstance(element_type_value, str):
            try:
                element_type = ElementType(element_type_value)
            except ValueError:
                element_type = ElementType.NONE
        elif isinstance(element_type_value, ElementType):
            element_type = element_type_value
        else:
            element_type = ElementType.NONE
            
        # Parameter extrahieren
        parameters = []
        for param_data in data.get("parameters", []):
            param_name = param_data.get("name", "")
            param_value = param_data.get("value")
            datatype = param_data.get("datatype", "str")
            
            # Einheit konvertieren
            unit_value = param_data.get("unit", "")
            unit = UnitEnum.NONE
            if unit_value:
                try:
                    unit = UnitEnum(unit_value)
                except ValueError:
                    pass
                
            # Process-Enum ermitteln
            process_value = param_data.get("process")
            process = None
            if process_value:
                try:
                    process = ProcessEnum(process_value)
                except ValueError:
                    pass
                    
            # Parameter erstellen
            parameters.append(
                Parameter(
                    name=param_name,
                    value=param_value,
                    process=process,
                    datatype=datatype,
                    unit=unit
                )
            )
            
        # Element erstellen
        if element_class:
            # Verwende die angegebene Klasse
            element = element_class(
                name=name,
                uuid=uuid,
                element_type=element_type,
                parameters=parameters
            )
        else:
            # Standardklasse verwenden
            element = InfrastructureElement(
                name=name,
                uuid=uuid,
                element_type=element_type,
                parameters=parameters
            )
            
        return element