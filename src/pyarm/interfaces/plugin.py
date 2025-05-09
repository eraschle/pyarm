"""
Defines the plugin interface for the PyArm system.
All plugins must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class PluginInterface(ABC):
    """
    Base interface for all plugins.
    Each plugin must implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initializes the plugin with the specified configuration.

        Parameters
        ----------
        config: Dict[str, Any]
            Configuration parameters for the plugin

        Returns
        -------
        bool
            True if initialization was successful, otherwise False
        """
        pass

    @abstractmethod
    def get_supported_element_types(self) -> List[str]:
        """
        Returns the element types supported by this plugin.

        Returns
        -------
        List[str]
            List of supported element types
        """
        pass

    @abstractmethod
    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Converts data into an element of the specified type.

        Parameters
        ----------
        data: Dict[str, Any]
            The data to be converted
        element_type: str
            Type of the element to be created

        Returns
        -------
        Optional[Dict[str, Any]]
            Converted element or None if conversion is not possible
        """
        pass
