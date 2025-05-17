"""
Plugin management module for PyArm.
This module handles the discovery and management of plugins.
"""

import importlib
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from pyarm.interfaces.plugin import PluginInterface

logger = logging.getLogger(__name__)


def discover_plugins() -> dict[str, type[PluginInterface]]:
    """
    Discovers all available plugins in the defined plugin directories.

    Returns
    -------
    dict[str, type[PluginInterface]]
        Dictionary with plugin names as keys and plugin classes as values
    """
    plugins = {}

    # Search in custom plugin directories
    custom_plugin_paths = _get_custom_plugin_paths()
    for path in custom_plugin_paths:
        custom_plugins = _discover_plugins_in(path)
        plugins.update(custom_plugins)

    # Search for installed plugins (via entry_points)
    installed_plugins = _discover_installed_plugins()
    plugins.update(installed_plugins)

    # Check for disabled plugins
    disabled_plugins = _get_disabled_plugins()
    for plugin_name in disabled_plugins:
        if plugin_name in plugins:
            logger.info(f"Plugin {plugin_name} is disabled and will not be loaded")
            del plugins[plugin_name]

    return plugins


def _get_plugin_type(module: ModuleType) -> type[PluginInterface] | None:
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if not isinstance(attr, type) or attr is PluginInterface:
            continue
        if not issubclass(attr, PluginInterface):
            continue
        return attr
    return None


def _discover_plugins_in(directory: str) -> dict[str, type[PluginInterface]]:
    """
    Discovers plugins in a specific directory.

    Parameters
    ----------
    directory: str
        The directory to search

    Returns
    -------
    dict[str, type[PluginInterface]]
        Dictionary with plugin names and plugin classes
    """
    discovered_plugins = {}
    plugin_dir = Path(directory)

    if not plugin_dir.exists() or not plugin_dir.is_dir():
        logger.warning(f"Plugin directory {directory} does not exist or is not a directory")
        return discovered_plugins

    # Consider all subdirectories as potential plugins
    for item in plugin_dir.iterdir():
        if not item.is_dir() or not (item / "__init__.py").exists():
            continue
        plugin_name = item.name
        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(plugin_name, str(item / "__init__.py"))
            if spec is None or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            # Search for plugin class
            plugin_type = _get_plugin_type(module)
            if plugin_type is None:
                continue
            plugin_instance = plugin_type()
            discovered_plugins[plugin_instance.name] = plugin_type
            logger.info(
                f"Plugin {plugin_instance.name} v{plugin_instance.version} loaded from {directory}"
            )
            break
        except Exception as e:
            logger.warning(f"Error loading plugin {plugin_name} from {directory}: {e}")

    return discovered_plugins


def _discover_installed_plugins() -> dict[str, type[PluginInterface]]:
    """
    Discovers plugins installed via entry_points.

    Returns:
        Dictionary with plugin names and plugin classes
    """
    discovered_plugins = {}

    try:
        import importlib.metadata

        for entry_point in importlib.metadata.entry_points(group="pyarm.plugins"):
            try:
                plugin_class = entry_point.load()
                if (
                    issubclass(plugin_class, PluginInterface)
                    and plugin_class is not PluginInterface
                ):
                    plugin_instance = plugin_class()
                    discovered_plugins[plugin_instance.name] = plugin_class
                    logger.info(
                        f"Installed plugin {plugin_instance.name} "
                        f"v{plugin_instance.version} loaded"
                    )
            except (ImportError, AttributeError) as e:
                logger.warning(
                    f"Error loading installed plugin {entry_point.name}: {e}"
                )
    except ImportError:
        logger.warning(
            "importlib.metadata not available, cannot detect installed plugins"
        )

    return discovered_plugins


def get_plugin_settings(plugin_name: str) -> dict[str, Any]:
    """
    Reads the settings for a specific plugin from the configuration.

    Args:
        plugin_name: Name of the plugin

    Returns:
        Dictionary with plugin settings
    """
    config = _get_plugin_config()
    return config.get("plugin_settings", {}).get(plugin_name, {})


def _get_custom_plugin_paths() -> list[str]:
    """
    Determines custom plugin directories from environment variables
    and configuration file.

    Returns:
        List of directory paths
    """
    paths = []

    # Environment variable for plugin paths
    env_paths = os.environ.get("PYARM_PLUGIN_PATHS", "")
    if env_paths:
        paths.extend(env_paths.split(os.pathsep))

    # Read configuration file
    config_paths = _get_config_plugin_paths()
    if config_paths:
        paths.extend(config_paths)

    # Default directories for development if no configuration is present
    if not config_paths:
        dev_paths = [
            os.path.join(os.getcwd(), "plugins"),
            os.path.join(os.getcwd(), "client_plugins"),
        ]

        # Only add paths if they exist
        for path in dev_paths:
            if os.path.exists(path) and os.path.isdir(path):
                paths.append(path)

    return paths


def _get_config_plugin_paths() -> list[str]:
    """
    Reads plugin paths from the configuration file.

    Returns:
        List of plugin paths
    """
    config = _get_plugin_config()

    paths = []

    # Internal plugin paths
    for entry in config.get("plugin_paths", []):
        if entry.get("enabled", True):
            path = os.path.abspath(os.path.join(os.getcwd(), entry["path"]))
            if os.path.exists(path) and os.path.isdir(path):
                paths.append(path)

    # External plugin paths
    for entry in config.get("external_plugin_paths", []):
        if entry.get("enabled", True):
            path = os.path.abspath(entry["path"])
            if os.path.exists(path) and os.path.isdir(path):
                paths.append(path)

    return paths


def _get_disabled_plugins() -> list[str]:
    """
    Reads the list of disabled plugins from the configuration.

    Returns:
        List of names of disabled plugins
    """
    config = _get_plugin_config()
    return config.get("disabled_plugins", [])


def _get_plugin_config() -> dict[str, Any]:
    """
    Reads the plugin configuration file.

    Returns:
        Plugin configuration as a dictionary
    """
    config_files = [
        os.path.join(os.getcwd(), "config", "plugins.json"),
        os.path.join(os.path.expanduser("~"), ".pyarm", "plugins.json"),
    ]

    # Custom configuration path from environment variable
    config_env = os.environ.get("PYARM_CONFIG")
    if config_env:
        config_files.insert(0, config_env)

    # Search for the first available configuration file
    for config_file in config_files:
        if not os.path.exists(config_file):
            continue
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            logger.info(f"Plugin configuration loaded from {config_file}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error reading plugin configuration from {config_file}: {e}")

    # Empty configuration if none was found
    return {}
