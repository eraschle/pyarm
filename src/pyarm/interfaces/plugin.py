"""
Defines the plugin interface for the PyArm system.
All plugins must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pyarm.interfaces.process import IProcessProtocol
from pyarm.interfaces.validator import IValidator
from pyarm.linking.element_linker import ElementLinker
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType


@dataclass
class ConversionResult:
    """
    Class representing the result of a conversion process for an element type.
    """

    elements: List[InfrastructureElement]
    element_type: ElementType
    plugin_name: str
    validation: Dict[str, Any] = field(default_factory=dict)


class PluginInterface(ABC, IProcessProtocol):
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
    def get_supported_element_types(self) -> List[ElementType]:
        """
        Returns the element types supported by this plugin.

        Returns
        -------
        List[ElementType]
            List of supported element types as ElementType enum values
        """
        pass

    @abstractmethod
    def load_data_from_directory(self, directory_path: Union[str, Path]) -> None:
        """
        Loads all relevant data from the specified directory and stores it internally in the plugin.
        The plugin is responsible for finding and reading all necessary files.

        Parameters
        ----------
        directory_path: Union[str, Path]
            Path to the directory containing the files
        """
        pass

    @abstractmethod
    def convert_element(self, element_type: ElementType) -> Optional[ConversionResult]:
        """
        Converts internally stored data into elements of the specified type.

        Parameters
        ----------
        element_type: ElementType
            Type of the elements to be created

        Returns
        -------
        Optional[ConversionResult]
            Conversion result containing the created elements and their type
        """
        pass

    @abstractmethod
    def define_element_links(self, linker_manager: ElementLinker) -> None:
        """
        Defines element links using the provided linker manager.
        This method should be called after all elements have been converted.

        Parameters
        ----------
        linker_manager: Any
            The linker manager to use for defining element links
        """
        pass

    def get_process_name(self) -> str:
        """
        Returns the name of the process.
        By default, returns the plugin name.

        Returns
        -------
        str
            Name of the process
        """
        return self.name

    def get_validators(self) -> List[IValidator]:
        """
        Returns the validators used by this plugin.
        Default implementation returns an empty list.
        Override this method to provide custom validators.

        Returns
        -------
        List[IValidator]
            A list of validators for this plugin
        """
        return []
