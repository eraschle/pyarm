"""
Modul zur Verwaltung von Element-Verknüpfungen während der Importphase.

Ermöglicht das Verknüpfen von Elementen basierend auf beliebigen Parametern,
nicht nur auf UUIDs. Die Verknüpfung erfolgt während der Importphase und
nicht erst nachträglich.
"""

import logging
from typing import Dict, List, Optional, Set, Type
from uuid import UUID

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class LinkDefinition:
    """
    Definition einer Verknüpfung zwischen zwei Elementtypen.
    Spezifiziert, welche Parameter zur Verknüpfung verwendet werden sollen.
    """

    def __init__(
        self,
        source_type: Type[InfrastructureElement],
        target_type: Type[InfrastructureElement],
        source_param_name: str,
        target_param_name: str,
        source_uuid_param: Optional[ProcessEnum] = None,
        target_uuid_param: Optional[ProcessEnum] = ProcessEnum.UUID,
        bidirectional: bool = True,
    ):
        """
        Initialisiert eine neue Link-Definition.

        Parameters
        ----------
        source_type: Type[InfrastructureElement]
            Der Quell-Elementtyp (z.B. Foundation)
        target_type: Type[InfrastructureElement]
            Der Ziel-Elementtyp (z.B. Mast)
        source_param_name: str
            Name des Parameters im Quell-Element, der auf das Ziel-Element verweist
            (z.B. "MastID" oder "MastReference")
        target_param_name: str
            Name des Parameters im Ziel-Element, der dem in source_param_name entspricht
            (z.B. "ID" oder "UUID")
        source_uuid_param: Optional[ProcessEnum]
            Prozess-Enum für die UUID-Referenz im Quell-Element
            (z.B. ProcessEnum.FOUNDATION_TO_MAST_UUID)
        target_uuid_param: Optional[ProcessEnum]
            Prozess-Enum für die UUID des Ziel-Elements
            (z.B. ProcessEnum.UUID)
        bidirectional: bool
            Ob die Verknüpfung bidirektional sein soll (Standard: True)
        """
        self.source_type = source_type
        self.target_type = target_type
        self.source_param_name = source_param_name
        self.target_param_name = target_param_name
        self.source_uuid_param = source_uuid_param
        self.target_uuid_param = target_uuid_param
        self.bidirectional = bidirectional

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

    def register_link_definitions_for_project(self, project_id: str) -> None:
        """
        Registriert Link-Definitionen basierend auf der Projekt-ID.
        Nutze diese Methode, um projektspezifische Verknüpfungen zu definieren.

        Parameters
        ----------
        project_id: str
            ID des Projekts
        """
        # Diese Methode würde von konkretren Implementierungen überschrieben
        log.warning(f"Keine spezifischen Link-Definitionen für Projekt {project_id} gefunden")

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
            param_value = str(param.value)
            param_name = param.name

            # Speichere unter der Kombination aus Parametername und -wert
            cache_key_with_name = f"{param_name}:{param_value}"
            if cache_key_with_name not in self.element_cache[element_type]:
                self.element_cache[element_type][cache_key_with_name] = []
            self.element_cache[element_type][cache_key_with_name].append(element)

            # Zusätzlich: Speichere das Element auch nur unter dem Parameterwert
            # (für den Fall, dass wir den Namen nicht kennen)
            if param_value not in self.element_cache[element_type]:
                self.element_cache[element_type][param_value] = []
            self.element_cache[element_type][param_value].append(element)

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

            # Alternativ nur nach dem Wert suchen, falls noch nichts gefunden wurde
            elif (
                target_type in self.element_cache
                and source_param_value in self.element_cache[target_type]
            ):
                target_elements = self.element_cache[target_type][source_param_value]

            # Erstelle Referenzen zu allen gefundenen Ziel-Elementen
            for target_element in target_elements:
                self._create_reference(element, target_element, link_def)

        self.processed_elements.add(element.uuid)

    def _create_reference(
        self, source: InfrastructureElement, target: InfrastructureElement, link_def: LinkDefinition
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

            # Bei bidirektionalen Referenzen: Speichere die UUID im passenden Parameter
            if link_def.source_uuid_param:
                from pyarm.models.parameter import DataType, Parameter, UnitEnum

                # Erstelle Parameter für die UUID-Referenz, falls nicht vorhanden
                if not source.has_param(link_def.source_uuid_param):
                    param = Parameter(
                        name=link_def.source_param_name,
                        value=target.uuid,
                        process=link_def.source_uuid_param,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    )
                    source.parameters.append(param)
                    source.known_params[link_def.source_uuid_param] = param

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
