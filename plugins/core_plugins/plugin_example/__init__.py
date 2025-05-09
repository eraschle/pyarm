"""
Beispiel-Plugin für PyArm.
Dieses Plugin zeigt, wie ein Plugin für PyArm implementiert werden kann.
"""

from typing import Any, Dict, List, Optional

from pyarm.interfaces.plugin import PluginInterface


class ExamplePlugin(PluginInterface):
    """
    Beispiel-Plugin für PyArm.
    """

    @property
    def name(self) -> str:
        return "Example Plugin"

    @property
    def version(self) -> str:
        return "0.1.0"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialisiert das Plugin mit der angegebenen Konfiguration.

        Args:
            config: Konfigurationsparameter für das Plugin

        Returns:
            True wenn die Initialisierung erfolgreich war, sonst False
        """
        print(f"Beispiel-Plugin initialisiert mit Konfiguration: {config}")
        return True

    def get_supported_element_types(self) -> List[str]:
        """
        Gibt die unterstützten Element-Typen zurück.

        Returns:
            Liste der unterstützten Element-Typen
        """
        return ["example", "foundation", "mast"]

    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Konvertiert Daten in ein Element des angegebenen Typs.

        Args:
            data: Die zu konvertierenden Daten
            element_type: Typ des zu erstellenden Elements

        Returns:
            Konvertiertes Element oder None, wenn die Konvertierung nicht möglich ist
        """
        if element_type not in self.get_supported_element_types():
            return None

        # Einfache Konvertierung, die die Daten nur kopiert und einen Typ hinzufügt
        result = data.copy()
        result["element_type"] = element_type
        result["converted_by"] = self.name
        return result
