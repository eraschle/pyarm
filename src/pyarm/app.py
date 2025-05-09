"""
Main application class for PyArm.
"""

import logging
from typing import Any

from pyarm.interfaces.plugin import PluginInterface

from pyarm.plugins import discover_plugins, get_plugin_settings

logger = logging.getLogger(__name__)


class Application:
    """
    Main application class for PyArm.
    Manages plugins and provides access to core functionality.
    """

    def __init__(self):
        """Initializes a new Application instance."""
        self.plugins: dict[str, PluginInterface] = {}
        self.plugin_classes = discover_plugins()

    def load_plugins(self, config: dict[str, dict[str, Any]] | None = None) -> None:
        """
        Loads and initializes all available plugins.

        Parameters
        ----------
        config: dict[str, dict[str, Any]] | None
            Configuration for plugins, where the key is the plugin name.
            If None, the configuration is loaded from the plugins.json file.
        """
        if config is None:
            config = {}

        for name, plugin_class in self.plugin_classes.items():
            try:
                plugin_instance = plugin_class()

                # Load configuration from passed parameter or from configuration file
                plugin_config = config.get(name, {})

                # If no configuration was passed, load from configuration file
                if not plugin_config:
                    plugin_config = get_plugin_settings(name)

                    # Debug output of loaded configuration
                    if plugin_config:
                        logger.debug(
                            f"Plugin configuration for {name} loaded from configuration file"
                        )

                if plugin_instance.initialize(plugin_config):
                    self.plugins[name] = plugin_instance
                    logger.info(
                        f"Plugin {plugin_instance.name} v{plugin_instance.version} initialized"
                    )
                else:
                    logger.warning(f"Plugin {name} could not be initialized")
            except Exception as e:
                logger.error(f"Error initializing plugin {name}: {e}")

    def get_plugin(self, name: str) -> PluginInterface | None:
        """
        Returns a plugin by its name.

        Parameters
        ----------
        name: str
            Name of the plugin

        Returns
        -------
        PluginInterface | None
            Plugin instance or None if the plugin was not found
        """
        return self.plugins.get(name)

    def get_plugins_for_element_type(self, element_type: str) -> list[PluginInterface]:
        """
        Returns all plugins that support a specific element type.

        Parameters
        ----------
        element_type: str
            Type of the element

        Returns
        -------
        list[PluginInterface]
            List of plugins that support the element type
        """
        return [
            plugin
            for plugin in self.plugins.values()
            if element_type in plugin.get_supported_element_types()
        ]

    def convert_element(
        self, data: dict[str, Any], element_type: str, plugin_name: str | None = None
    ) -> dict[str, Any] | None:
        """
        Converts data into an element using a specific plugin.

        Parameters
        ----------
        data: dict[str, Any]
            The data to be converted
        element_type: str
            Type of the element to be created
        plugin_name: str | None
            Optional name of the plugin to be used

        Returns
        -------
        dict[str, Any] | None
            Converted element or None if conversion is not possible
        """
        if plugin_name:
            # Use specific plugin
            plugin = self.get_plugin(plugin_name)
            if plugin and element_type in plugin.get_supported_element_types():
                return plugin.convert_element(data, element_type)
            return None
        else:
            # Use first plugin that supports the element type
            for plugin in self.get_plugins_for_element_type(element_type):
                result = plugin.convert_element(data, element_type)
                if result:
                    return result
            return None
