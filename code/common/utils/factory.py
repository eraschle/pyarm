"""
Fabrikmethoden für die Erstellung von Elementen.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast
from uuid import UUID

from ..enums.process_enums import ElementType, ProcessEnum, UnitEnum
from ..models.base_models import InfrastructureElement, Parameter
from ..models.element_models import (
    CurvedTrack,
    DrainagePipe,
    DrainageShaft,
    Foundation,
    InfrastructureElementBase,
    LinearElement, 
    Mast,
    PipeElement,
    Track,
)


# Typvariable für generische Elemente
T = TypeVar("T", bound=InfrastructureElement)


def create_parameter(param_data: Dict[str, Any]) -> Parameter:
    """
    Erstellt ein Parameter-Objekt aus einem Dictionary.

    Args:
        param_data: Dictionary mit Parameterdaten

    Returns:
        Parameter-Objekt
    """
    name = param_data.get("name", "")
    value = param_data.get("value")
    datatype = param_data.get("datatype", "str")
    unit = UnitEnum(param_data.get("unit", "")) if param_data.get("unit") else UnitEnum.NONE

    # Prozess-Enum aus String oder direkt
    process = None
    process_value = param_data.get("process")
    if process_value:
        if isinstance(process_value, str):
            try:
                process = ProcessEnum(process_value)
            except ValueError:
                pass
        elif isinstance(process_value, ProcessEnum):
            process = process_value

    return Parameter(name=name, value=value, process=process, datatype=datatype, unit=unit)


def determine_element_class(element_data: Dict[str, Any]) -> Type[InfrastructureElement]:
    """
    Bestimmt die passende Element-Klasse basierend auf den Elementdaten.

    Args:
        element_data: Dictionary mit Elementdaten

    Returns:
        Element-Klasse
    """
    # Element-Typ ermitteln
    element_type_value = element_data.get("element_type")
    if element_type_value and isinstance(element_type_value, str):
        try:
            element_type = ElementType(element_type_value)
        except ValueError:
            element_type = ElementType.NONE
    elif element_type_value and isinstance(element_type_value, ElementType):
        element_type = element_type_value
    else:
        element_type = ElementType.NONE
        
    # Parameter-Liste durchsuchen für spezielle Eigenschaften
    parameters = element_data.get("parameters", [])
    
    # Prüfen, ob es sich um eine Kurve handelt
    has_clothoid = any(
        p.get("process") == ProcessEnum.CLOTHOID_PARAMETER.value for p in parameters
    )
    
    # Prüfen auf Start/End-Koordinaten für lineare Elemente
    has_end_coordinates = any(
        p.get("process") in [ProcessEnum.X_COORDINATE_END.value, 
                            ProcessEnum.Y_COORDINATE_END.value, 
                            ProcessEnum.Z_COORDINATE_END.value] for p in parameters
    )
    
    # Klasse basierend auf Elementtyp und Eigenschaften bestimmen
    if element_type == ElementType.FOUNDATION:
        return Foundation
    elif element_type == ElementType.MAST:
        return Mast
    elif element_type == ElementType.TRACK:
        if has_clothoid:
            return CurvedTrack
        else:
            return Track
    elif element_type == ElementType.DRAINAGE_PIPE:
        return DrainagePipe
    elif element_type == ElementType.DRAINAGE_SHAFT:
        return DrainageShaft
    elif has_end_coordinates:
        # Generisches lineares Element
        return LinearElement
    else:
        # Fallback auf generisches Element
        return InfrastructureElementBase


def create_element(element_data: Dict[str, Any]) -> InfrastructureElement:
    """
    Erstellt ein Element basierend auf dem ElementType und den Elementdaten.

    Args:
        element_data: Dictionary mit Elementdaten

    Returns:
        Erstelltes Element
    """
    # Grundlegende Attribute extrahieren
    name = element_data.get("name", "Unknown")
    uuid_value = element_data.get("uuid")
    uuid = UUID(uuid_value) if uuid_value else None

    # Element-Typ ermitteln
    element_type_value = element_data.get("element_type")
    if element_type_value and isinstance(element_type_value, str):
        try:
            element_type = ElementType(element_type_value)
        except ValueError:
            element_type = ElementType.NONE
    elif element_type_value and isinstance(element_type_value, ElementType):
        element_type = element_type_value
    else:
        element_type = ElementType.NONE

    # Parameter verarbeiten
    parameters = []
    for param_data in element_data.get("parameters", []):
        parameters.append(create_parameter(param_data))

    # Spezifische Attribute für bestimmte Elementtypen
    foundation_uuid = element_data.get("foundation_uuid")
    if foundation_uuid and not isinstance(foundation_uuid, UUID) and isinstance(foundation_uuid, str):
        foundation_uuid = UUID(foundation_uuid)

    references = {}
    # Spezifische Referenzen sammeln
    for ref_key, ref_value in element_data.items():
        if ref_key.endswith("_uuid") and ref_value and ref_key != "uuid":
            if not isinstance(ref_value, UUID) and isinstance(ref_value, str):
                ref_value = UUID(ref_value)
            ref_type = ref_key.replace("_uuid", "")
            references[ref_type] = ref_value

    # Element-Klasse bestimmen
    element_class = determine_element_class(element_data)

    # UUID sicherstellen
    if uuid is None:
        raise ValueError("UUID is required to create an element.")
        
    # Element mit passender Klasse erstellen
    if element_class == Foundation:
        element = Foundation(
            name=name,
            uuid=uuid,
            element_type=ElementType.FOUNDATION,
            parameters=parameters,
            references=references
        )
    elif element_class == Mast:
        element = Mast(
            name=name,
            uuid=uuid,
            element_type=ElementType.MAST,
            parameters=parameters,
            foundation_uuid=foundation_uuid,
            references=references
        )
    elif element_class == Track:
        element = Track(
            name=name,
            uuid=uuid,
            element_type=ElementType.TRACK,
            parameters=parameters,
            references=references
        )
    elif element_class == CurvedTrack:
        element = CurvedTrack(
            name=name,
            uuid=uuid,
            element_type=ElementType.TRACK,
            parameters=parameters,
            references=references
        )
    elif element_class == DrainagePipe:
        element = DrainagePipe(
            name=name,
            uuid=uuid,
            element_type=ElementType.DRAINAGE_PIPE,
            parameters=parameters,
            references=references
        )
    elif element_class == DrainageShaft:
        element = DrainageShaft(
            name=name,
            uuid=uuid,
            element_type=ElementType.DRAINAGE_SHAFT,
            parameters=parameters,
            references=references
        )
    elif element_class == LinearElement or has_linear_properties(element_data):
        element = LinearElement(
            name=name,
            uuid=uuid,
            element_type=element_type,
            parameters=parameters,
            references=references
        )
    else:
        # Fallback auf generisches Element
        element = InfrastructureElementBase(
            name=name,
            uuid=uuid,
            element_type=element_type,
            parameters=parameters,
            references=references
        )

    return element


def has_linear_properties(element_data: Dict[str, Any]) -> bool:
    """
    Prüft, ob die Elementdaten lineare Eigenschaften haben.

    Args:
        element_data: Dictionary mit Elementdaten

    Returns:
        True, wenn das Element lineare Eigenschaften hat
    """
    parameters = element_data.get("parameters", [])
    return any(
        p.get("process") in [
            ProcessEnum.X_COORDINATE_END.value,
            ProcessEnum.Y_COORDINATE_END.value,
            ProcessEnum.Z_COORDINATE_END.value
        ] for p in parameters
    )


def create_typed_element(element_data: Dict[str, Any], element_class: Type[T]) -> T:
    """
    Erstellt ein Element eines spezifischen Typs.

    Args:
        element_data: Dictionary mit Elementdaten
        element_class: Klasse des zu erstellenden Elements

    Returns:
        Erstelltes Element des angegebenen Typs

    Raises:
        TypeError: Wenn das erstellte Element nicht den erwarteten Typ hat
    """
    element = create_element(element_data)
    if not isinstance(element, element_class):
        # Versuchen, ein Element des gewünschten Typs zu erstellen
        custom_element = convert_to_class(element, element_class)
        if custom_element:
            return custom_element
        raise TypeError(f"Created element is not of type {element_class.__name__}")
    return cast(T, element)


def convert_to_class(element: InfrastructureElement, target_class: Type[T]) -> Optional[T]:
    """
    Konvertiert ein Element in eine andere Klasse.

    Args:
        element: Zu konvertierendes Element
        target_class: Zielklasse

    Returns:
        Konvertiertes Element oder None, wenn Konvertierung nicht möglich
    """
    try:
        # Hier könnte eine komplexere Logik implementiert werden, um unterschiedliche
        # Elementtypen ineinander zu konvertieren. Für jetzt verwenden wir einen einfachen Ansatz.
        return target_class(
            name=element.name,
            uuid=element.uuid,
            element_type=element.element_type,
            parameters=element.parameters,
            # Referenzen hinzufügen, wenn das Zielelement sie unterstützt
            references={} if hasattr(target_class, "references") else {}
        )
    except Exception:
        return None


def create_elements(element_data_list: List[Dict[str, Any]]) -> List[InfrastructureElement]:
    """
    Erstellt mehrere Elemente aus einer Liste von Dictionaries.

    Args:
        element_data_list: Liste von Dictionaries mit Elementdaten

    Returns:
        Liste der erstellten Elemente
    """
    return [create_element(data) for data in element_data_list]


def create_element_from_parameters(
    name: str,
    element_type: ElementType,
    parameters: List[Parameter],
    uuid: Optional[UUID] = None,
    references: Optional[Dict[str, UUID]] = None
) -> InfrastructureElement:
    """
    Erstellt ein Element aus einer Liste von Parametern.

    Args:
        name: Name des Elements
        element_type: Typ des Elements
        parameters: Liste von Parametern
        uuid: Optional UUID des Elements
        references: Optionales Dictionary mit Referenzen

    Returns:
        Erstelltes Element
    """
    # Element-Daten erstellen
    element_data = {
        "name": name,
        "element_type": element_type.value,
        "parameters": [
            {
                "name": param.name,
                "value": param.value,
                "process": param.process.value if param.process else None,
                "datatype": param.datatype,
                "unit": param.unit.value
            }
            for param in parameters
        ]
    }
    
    if uuid:
        element_data["uuid"] = str(uuid)
        
    if references:
        for ref_type, ref_uuid in references.items():
            element_data[f"{ref_type}_uuid"] = str(ref_uuid)
    
    return create_element(element_data)