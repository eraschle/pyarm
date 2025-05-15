"""
Modul zur Verwaltung von Element-Verknüpfungen während der Importphase.

Ermöglicht das Verknüpfen von Elementen basierend auf beliebigen Parametern,
nicht nur auf UUIDs. Die Verknüpfung erfolgt während der Importphase und
nicht erst nachträglich.
"""

import logging
from typing import Dict, List, Optional, Protocol, Set, Type
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class ILinkDefinition(Protocol):
    source_type: Type[InfrastructureElement]
    target_type: Type[InfrastructureElement]
    source_uuid_param: Optional[ProcessEnum] = ProcessEnum.UUID
    target_uuid_param: Optional[ProcessEnum] = ProcessEnum.UUID
    bidirectional: bool


class LinkDefinition(ILinkDefinition):
    """
    Definition of a link between two elements.
    Specifies which parameters should be used for the link.
    """

    def __init__(
        self,
        source_type: Type[InfrastructureElement],
        target_type: Type[InfrastructureElement],
        source_param_name: str,
        target_param_name: str,
        source_uuid_param: ProcessEnum = ProcessEnum.UUID,
        target_uuid_param: ProcessEnum = ProcessEnum.UUID,
        bidirectional: bool = True,
        try_link_with_coordinate: bool = False,
        offset_coordinate: Optional[float] = None,
    ):
        """
        Initializes a new link definition.

        Parameters
        ----------
        source_type: Type[InfrastructureElement]
            Source element type (e.g. Foundation)
        target_type: Type[InfrastructureElement]
            Target element type (e.g. Mast)
        source_param_name: str
            Parameter name in the source element that corresponds to the target parameter
            (z.B. "MastID" oder "MastReference")
        target_param_name: str
            Parameter name in the target element that corresponds to the source parameter
            (z.B. "ID" oder "UUID")
        source_uuid_param: ProcessEnum
            Parameter name in the source element that corresponds to the UUID
            (default: ProcessEnum.UUID)
        target_uuid_param: ProcessEnum
            Parameter name in the target element that corresponds to the UUID
            (default: ProcessEnum.UUID)
        bidirectional: bool
            If the link should be bidirectional
            (default: True)
        try_link_with_coordinate: bool
            If the link should be attempted using coordinates
            (default: False)
        offset_coordinate: Optional[float]
            Offset for the coordinate link
            (default: None)
        """
        self.source_type = source_type
        self.target_type = target_type
        self.source_param_name = source_param_name
        self.target_param_name = target_param_name
        self.source_uuid_param = source_uuid_param
        self.target_uuid_param = target_uuid_param
        self.bidirectional = bidirectional
        self.try_link_with_coordinate = try_link_with_coordinate
        self.offset_coordinate = offset_coordinate

    def __repr__(self) -> str:
        return (
            f"LinkDefinition({self.source_type.__name__} -> {self.target_type.__name__}, "
            f"{self.source_param_name} -> {self.target_param_name})"
        )


class ElementLinker:
    """
    Verwaltet die Verknüpfung von Elementen während der Importphase.
    Ermöglicht das Verknüpfen von Elementen basierend auf beliebigen Parametern,
    nicht nur auf UUIDs.
    """

    def __init__(self):
        """Initialisiert einen neuen ElementLinker."""
        self.link_definitions: List[LinkDefinition] = []

        # Element-Cache für den schnellen Zugriff nach Typ und Attributwert
        # Format: {ElementTypName: {AttributName:AttributWert: [Elemente]}}
        self.element_cache: Dict[str, Dict[str, List[InfrastructureElement]]] = {}

        # Coordinate-Cache für den schnellen Zugriff auf Koordinaten
        # Format: {Tuple: [Elemente]}
        self.coordinate_cache: Dict[tuple, List[InfrastructureElement]] = {}

        # UUID-zu-Element-Cache für den direkten Zugriff über UUIDs
        # Format: {UUID-String: Element}
        self.uuid_cache: Dict[str, InfrastructureElement] = {}

        # Verfolgung bereits verarbeiteter Elemente
        self.processed_elements: Set[UUID] = set()

        # Statistiken
        self.links_created = 0

    def register_link_definition(self, link_definition: LinkDefinition) -> None:
        """
        Registriert eine neue Link-Definition.

        Parameters
        ----------
        link_definition: LinkDefinition
            Die zu registrierende Link-Definition
        """
        self.link_definitions.append(link_definition)

        # Initialisiere den Cache für die Quell- und Zieltypen, falls nicht vorhanden
        source_type_name = link_definition.source_type.__name__
        target_type_name = link_definition.target_type.__name__

        if source_type_name not in self.element_cache:
            self.element_cache[source_type_name] = {}
        if target_type_name not in self.element_cache:
            self.element_cache[target_type_name] = {}

    def register_element(self, element: InfrastructureElement) -> None:
        """
        Registriert ein Element im Cache für spätere Verknüpfungen.

        Parameters
        ----------
        element: InfrastructureElement
            Das zu registrierende Element
        """
        element_type = type(element).__name__
        if element_type not in self.element_cache:
            self.element_cache[element_type] = {}

        # Speichere das Element im UUID-Cache
        self.uuid_cache[str(element.uuid)] = element

        # Speichere das Element unter all seinen relevanten Parametern
        for param in element.parameters:
            cache_key_with_point = f"{param.name}:{param.value}"
            if cache_key_with_point not in self.element_cache[element_type]:
                self.element_cache[element_type][cache_key_with_point] = []
            self.element_cache[element_type][cache_key_with_point].append(element)

    def process_element_links(self, element: InfrastructureElement) -> None:
        """
        Verarbeitet alle Link-Definitionen für ein Element und stellt die Verknüpfungen her.

        Parameters
        ----------
        element: InfrastructureElement
            Das zu verarbeitende Element
        """
        if element.uuid in self.processed_elements:
            return

        element_type = type(element).__name__

        # Für jede Link-Definition, die auf diesen Elementtyp als Quelle passt
        for link_def in self.link_definitions:
            if link_def.source_type.__name__ != element_type:
                continue

            # Suche nach dem Parameter im Element
            source_param_value = None
            for param in element.parameters:
                if param.name == link_def.source_param_name:
                    source_param_value = str(param.value)
                    break

            if not source_param_value:
                continue

            # Suche nach dem Ziel-Element im Cache
            target_type = link_def.target_type.__name__
            target_elements = []

            # Erst versuchen, über den Parameter-Namen und -Wert zu suchen
            target_key = f"{link_def.target_param_name}:{source_param_value}"
            if target_type in self.element_cache and target_key in self.element_cache[target_type]:
                target_elements = self.element_cache[target_type][target_key]

            # Erstelle Referenzen zu allen gefundenen Ziel-Elementen
            for target_element in target_elements:
                self._create_reference(element, target_element, link_def)

        self.processed_elements.add(element.uuid)

    def _create_reference(
        self,
        source: InfrastructureElement,
        target: InfrastructureElement,
        link_def: ILinkDefinition,
    ) -> None:
        """
        Erstellt eine Referenz zwischen zwei Elementen.

        Parameters
        ----------
        source: InfrastructureElement
            Das Quell-Element
        target: InfrastructureElement
            Das Ziel-Element
        link_def: LinkDefinition
            Die Link-Definition, die für diese Verknüpfung verwendet wird
        """
        try:
            # Erstelle Referenz von Quelle zu Ziel
            source.add_reference(
                reference_type=type(target),
                referenced_uuid=target.uuid,
                bidirectional=link_def.bidirectional,
            )

            source_uuid_param = link_def.source_uuid_param or ProcessEnum.UUID
            # Erstelle Parameter für die UUID-Referenz, falls nicht vorhanden
            if not source.has_param(source_uuid_param):
                raise ValueError(
                    f"Parameter '{source_uuid_param}' in element "
                    f"{type(source).__name__}({source.name}) does not exist"
                )

            # Erfolgreiche Verknüpfung protokollieren
            self.links_created += 1
            log.debug(
                f"Referenz erstellt: {type(source).__name__}({source.name}) -> "
                f"{type(target).__name__}({target.name})"
            )

        except Exception as e:
            log.error(
                f"Fehler beim Erstellen der Referenz: {type(source).__name__}({source.name}) -> "
                f"{type(target).__name__}({target.name}): {e}"
            )

    def finalize_links(self) -> int:
        """
        Schließt den Verknüpfungsprozess ab und gibt die Anzahl erstellter Links zurück.

        Returns
        -------
        int
            Anzahl der erstellten Verknüpfungen
        """
        log.info(f"Verknüpfungsprozess abgeschlossen: {self.links_created} Links erstellt")
        log.info(f"{len(self.processed_elements)} Elemente verarbeitet")

        return self.links_created

    def clear_caches(self) -> None:
        """Leert alle Caches, um Speicher freizugeben."""
        self.element_cache.clear()
        self.uuid_cache.clear()
        self.processed_elements.clear()
        self.links_created = 0
