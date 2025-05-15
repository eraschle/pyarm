"""
Beispiel für die Integration des ElementLinkers in einem Client-Plugin.
"""

import logging
from typing import Any, Dict, List, Optional

from pyarm.interfaces.plugin import PluginInterface
from pyarm.linking.element_linker import ElementLinker, LinkDefinition
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.element_models import Foundation, Mast
from pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class ClientPlugin(PluginInterface):
    """
    Beispiel-Plugin mit ElementLinker-Integration.
    """

    def __init__(self):
        """Initialisiert das Plugin."""
        self._element_linker = None
        self._elements_by_type = {}

    @property
    def name(self) -> str:
        return "Client Plugin mit ElementLinker"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin mit der Konfiguration."""
        log.info(f"Initialisiere {self.name} v{self.version}")
        log.debug(f"Konfiguration: {config}")

        try:
            # ElementLinker erstellen
            self._element_linker = ElementLinker()

            # Projekt-ID aus der Konfiguration auslesen
            project_id = config.get("project_id", "default")

            # Link-Definitionen für das Projekt registrieren
            self._configure_link_definitions(project_id, config)

            log.info(f"ElementLinker für Projekt {project_id} initialisiert")
            return True

        except Exception as e:
            log.error(f"Fehler bei der Initialisierung des ElementLinkers: {e}")
            return False

    def _configure_link_definitions(self, project_id: str, config: Dict[str, Any]) -> None:
        """
        Konfiguriert die Link-Definitionen basierend auf dem Projekt.

        Parameters
        ----------
        project_id : str
            ID des Projekts
        config : Dict[str, Any]
            Plugin-Konfiguration
        """
        if project_id == "project1":
            # Für Projekt 1: Fundament -> Mast über "MastID" -> "ID"
            self._element_linker.register_link_definition(
                LinkDefinition(
                    source_type=Foundation,
                    target_type=Mast,
                    source_param_name="MastID",
                    target_param_name="ID",
                    source_uuid_param=ProcessEnum.FOUNDATION_TO_MAST_UUID,
                    target_uuid_param=ProcessEnum.UUID,
                    bidirectional=True,
                )
            )

            # Gegenrichtung: Mast -> Fundament über "FundamentID" -> "ID"
            self._element_linker.register_link_definition(
                LinkDefinition(
                    source_type=Mast,
                    target_type=Foundation,
                    source_param_name="FundamentID",
                    target_param_name="ID",
                    source_uuid_param=ProcessEnum.MAST_TO_FOUNDATION_UUID,
                    target_uuid_param=ProcessEnum.UUID,
                    bidirectional=True,
                )
            )

        elif project_id == "project2":
            # Für Projekt 2: Fundament -> Mast über "MastReference" -> "UUID"
            self._element_linker.register_link_definition(
                LinkDefinition(
                    source_type=Foundation,
                    target_type=Mast,
                    source_param_name="MastReference",
                    target_param_name="UUID",
                    source_uuid_param=ProcessEnum.FOUNDATION_TO_MAST_UUID,
                    target_uuid_param=ProcessEnum.UUID,
                    bidirectional=True,
                )
            )

            # Gegenrichtung: Mast -> Fundament über "FoundationReference" -> "UUID"
            self._element_linker.register_link_definition(
                LinkDefinition(
                    source_type=Mast,
                    target_type=Foundation,
                    source_param_name="FoundationReference",
                    target_param_name="UUID",
                    source_uuid_param=ProcessEnum.MAST_TO_FOUNDATION_UUID,
                    target_uuid_param=ProcessEnum.UUID,
                    bidirectional=True,
                )
            )

        else:
            # Benutzerdefinierte Konfiguration aus config lesen
            link_configs = config.get("element_links", {})
            if link_configs:
                self._configure_from_link_configs(link_configs)
            else:
                log.warning(f"Keine Link-Definitionen für Projekt {project_id} gefunden")

    def _configure_from_link_configs(self, link_configs: Dict[str, Any]) -> None:
        """
        Konfiguriert die Link-Definitionen basierend auf einer JSON-Konfiguration.

        Parameters
        ----------
        link_configs : Dict[str, Any]
            JSON-Konfiguration für Links
        """
        # Mapping von Elementtyp-Strings zu tatsächlichen Klassen
        type_map = {
            "foundation": Foundation,
            "mast": Mast,
            # Weitere Elementtypen hier hinzufügen
        }

        # Mapping von Process-Enum-Strings zu tatsächlichen Enums
        process_enum_map = {
            "uuid": ProcessEnum.UUID,
            "foundation_to_mast_uuid": ProcessEnum.FOUNDATION_TO_MAST_UUID,
            "mast_to_foundation_uuid": ProcessEnum.MAST_TO_FOUNDATION_UUID,
            # Weitere ProcessEnums hier hinzufügen
        }

        for link_name, link_def in link_configs.items():
            try:
                # Elementtypen aus der Konfiguration extrahieren
                source_type_str = link_def.get("source_type")
                target_type_str = link_def.get("target_type")

                # Parameter-Namen aus der Konfiguration extrahieren
                source_param = link_def.get("source_param")
                target_param = link_def.get("target_param")

                # UUID-Parameter (optional)
                source_uuid_param_str = link_def.get("source_uuid_param")
                target_uuid_param_str = link_def.get("target_uuid_param", "uuid")

                # Bidirektionalität (optional)
                bidirectional = link_def.get("bidirectional", True)

                # Typen und Enums konvertieren
                source_type = type_map.get(source_type_str.lower())
                target_type = type_map.get(target_type_str.lower())

                source_uuid_param = None
                if source_uuid_param_str:
                    source_uuid_param = process_enum_map.get(source_uuid_param_str.lower())

                target_uuid_param = process_enum_map.get(target_uuid_param_str.lower())

                # Prüfen, ob alle erforderlichen Werte vorhanden sind
                if not all([source_type, target_type, source_param, target_param]):
                    log.warning(f"Unvollständige Link-Definition: {link_name}")
                    continue

                # LinkDefinition erstellen und registrieren
                self._element_linker.register_link_definition(
                    LinkDefinition(
                        source_type=source_type,
                        target_type=target_type,
                        source_param_name=source_param,
                        target_param_name=target_param,
                        source_uuid_param=source_uuid_param,
                        target_uuid_param=target_uuid_param,
                        bidirectional=bidirectional,
                    )
                )

                log.info(f"Link-Definition registriert: {link_name}")

            except Exception as e:
                log.error(f"Fehler bei der Konfiguration der Link-Definition {link_name}: {e}")

    def get_supported_element_types(self) -> List[str]:
        """Gibt die unterstützten Elementtypen zurück."""
        return ["foundation", "mast", "joch", "track"]

    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Konvertiert Daten in ein Element des angegebenen Typs.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu konvertierenden Daten
        element_type : str
            Der Elementtyp

        Returns
        -------
        Optional[Dict[str, Any]]
            Konvertiertes Element oder None bei Fehler
        """
        if element_type not in self.get_supported_element_types():
            log.warning(f"Elementtyp {element_type} wird nicht unterstützt")
            return None

        # Element-Daten und Projekt-ID extrahieren
        element_data = data.get("data", [])
        project_id = data.get("project_id", "unknown")

        if not element_data:
            log.warning(f"Keine Daten für Elementtyp {element_type} vorhanden")
            return None

        # Konvertierungsmethode basierend auf Elementtyp und Projekt auswählen
        converter_method = None
        if project_id in ["project1", "project2"]:
            converter_method = getattr(self, f"_convert_{element_type}_{project_id}", None)

        if converter_method is None:
            converter_method = getattr(self, f"_convert_{element_type}", None)

        if converter_method is None:
            log.warning(f"Keine Konvertierungsmethode für {element_type} in Projekt {project_id}")
            return None

        # Elemente konvertieren
        converted_elements = converter_method(element_data, project_id)

        if not converted_elements:
            log.warning(f"Konvertierung für {element_type} ergab keine Elemente")
            return None

        # Speichere die konvertierten Elemente für die Verknüpfung
        if element_type not in self._elements_by_type:
            self._elements_by_type[element_type] = []
        self._elements_by_type[element_type].extend(converted_elements)

        # Elemente im ElementLinker registrieren
        if self._element_linker:
            for element in converted_elements:
                self._element_linker.register_element(element)

            # Verknüpfungen für die neuen Elemente verarbeiten
            for element in converted_elements:
                self._element_linker.process_element_links(element)

            # Nach dem letzten Elementtyp alle Verknüpfungen finalisieren
            if element_type == self.get_supported_element_types()[-1]:
                links_created = self._element_linker.finalize_links()
                log.info(f"Insgesamt {links_created} Verknüpfungen erstellt")

        # Elemente für die Serialisierung vorbereiten
        serialized_elements = [element.to_dict() for element in converted_elements]

        return {
            "element_type": element_type,
            "project_id": project_id,
            "elements": serialized_elements,
            "converted_by": self.name,
        }

    # Beispiel für Konvertierungsmethoden (müssten in einer echten Implementierung ausgefüllt werden)
    def _convert_foundation_project1(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten aus Projekt 1."""
        # Implementierung hier...
        return []

    def _convert_mast_project1(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten aus Projekt 1."""
        # Implementierung hier...
        return []

    def _convert_foundation_project2(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten aus Projekt 2."""
        # Implementierung hier...
        return []

    def _convert_mast_project2(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten aus Projekt 2."""
        # Implementierung hier...
        return []
