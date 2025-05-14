"""
Integration des Validierungssystems in das Plugin-System.

Dieses Modul bietet Klassen und Funktionen für die Integration des
Validierungssystems in das Plugin-System, einschließlich eines
Wrapper-Plugins für die Validierung.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from pyarm.interfaces.plugin import PluginInterface
from pyarm.validation.errors import ValidationResult
from pyarm.validation.interfaces import IValidationService

log = logging.getLogger(__name__)


class ValidatedPlugin(PluginInterface):
    """
    Wrapper-Klasse für Plugins, die Validierung vor der Konvertierung durchführt.
    """

    def __init__(self, plugin: PluginInterface, validation_service: IValidationService):
        """
        Initialisiert das ValidatedPlugin.

        Parameters
        ----------
        plugin : PluginInterface
            Das zu umhüllende Plugin
        validation_service : IValidationService
            Der zu verwendende ValidationService
        """
        self._plugin = plugin
        self._validation_service = validation_service
        self._validation_enabled = True

        # Konfigurationsoptionen für die Validierung
        self._validation_config = {
            "strict_mode": False,  # Bei True werden Elemente mit Fehlern abgelehnt
            "ignore_warnings": True,  # Bei True werden Warnungen ignoriert
            "log_level": "WARNING",  # Logging-Level für Validierungsfehler
        }

    @property
    def name(self) -> str:
        """Name des Plugins."""
        return f"{self._plugin.name} [Validiert]"

    @property
    def version(self) -> str:
        """Version des Plugins."""
        return self._plugin.version

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialisiert das Plugin mit der Konfiguration.

        Parameters
        ----------
        config : Dict[str, Any]
            Die Konfiguration

        Returns
        -------
        bool
            True bei erfolgreicher Initialisierung
        """
        # Validierungskonfiguration extrahieren
        validation_config = config.pop("validation", {})

        # Validierungskonfiguration aktualisieren
        self._validation_config.update(validation_config)

        # Validierung aktivieren/deaktivieren
        self._validation_enabled = validation_config.get("enabled", True)

        # Logging-Level einstellen
        log_level_name = self._validation_config.get("log_level", "WARNING")
        log_level = getattr(logging, log_level_name, logging.WARNING)
        log.setLevel(log_level)

        # Plugin initialisieren
        return self._plugin.initialize(config)

    def get_supported_element_types(self) -> List[str]:
        """
        Gibt die unterstützten Elementtypen zurück.

        Returns
        -------
        List[str]
            Die unterstützten Elementtypen
        """
        return self._plugin.get_supported_element_types()

    def pre_validate(self, data: Dict[str, Any], element_type: str) -> ValidationResult:
        """
        Führt eine Validierung vor der Konvertierung durch.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu validierenden Daten
        element_type : str
            Der Elementtyp

        Returns
        -------
        ValidationResult
            Das Validierungsergebnis
        """
        if not self._validation_enabled:
            # Dummy-Ergebnis zurückgeben, wenn Validierung deaktiviert ist
            return ValidationResult()

        if not data:
            log.warning(f"Leere Daten für Elementtyp {element_type}")
            return ValidationResult()

        # Element-Sammlung oder einzelnes Element?
        element_data = data.get("data", [])
        project_id = data.get("project_id", "unknown")

        if not element_data:
            log.warning(f"Keine Daten für Elementtyp {element_type} in Projekt {project_id}")
            return ValidationResult()

        # Sammlung von Elementen validieren
        results = self._validation_service.validate_collection(element_data, element_type)

        # Validierungsbericht erstellen
        report = self._validation_service.create_validation_report(element_type, results)
        log.info(
            f"Validierungsbericht für {element_type}: {json.dumps(report['summary'], indent=2)}"
        )

        # Gesamtergebnis berechnen
        combined_result = ValidationResult()
        for result in results:
            combined_result.merge(result)

        return combined_result

    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Konvertiert Daten in ein Element des angegebenen Typs,
        mit Validierung vor der Konvertierung.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu konvertierenden Daten
        element_type : str
            Der Elementtyp

        Returns
        -------
        Optional[Dict[str, Any]]
            Konvertiertes Element oder None, wenn Konvertierung nicht möglich
        """
        if self._validation_enabled:
            # Validieren vor der Konvertierung
            validation_result = self.pre_validate(data, element_type)

            # Im Strict-Modus: Bei Fehlern abbrechen
            if self._validation_config.get("strict_mode", False) and not validation_result.is_valid:
                log.error(
                    f"Validierung fehlgeschlagen für Elementtyp {element_type}: {validation_result}"
                )
                return None

        # Originales Plugin zur Konvertierung verwenden
        converted = self._plugin.convert_element(data, element_type)

        if converted and self._validation_enabled:
            # Anzahl der erfolgreich konvertierten Elemente
            element_count = len(converted.get("elements", []))
            log.info(f"{element_count} Elemente vom Typ {element_type} erfolgreich konvertiert")

        return converted


class ValidationPluginWrapper:
    """
    Factory-Klasse zum Erstellen von validierten Plugin-Wrappern.
    """

    @staticmethod
    def wrap_plugin(
        plugin: PluginInterface, validation_service: IValidationService
    ) -> 'ValidatedPlugin':
        """
        Umhüllt ein Plugin mit einem ValidatedPlugin.

        Parameters
        ----------
        plugin : PluginInterface
            Das zu umhüllende Plugin
        validation_service : IValidationService
            Der zu verwendende ValidationService

        Returns
        -------
        ValidatedPlugin
            Das umhüllte Plugin
        """
        validated_plugin = ValidatedPlugin(plugin, validation_service)
        log.info(f"Plugin {plugin.name} mit Validierung umhüllt")
        return validated_plugin
