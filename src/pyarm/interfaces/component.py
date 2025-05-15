from typing import Protocol

from pyarm.components.base import Component, ComponentType


class IComponentModel(Protocol):
    def add_component(self, component: Component) -> None:
        """
        Adds a component or replaces an existing one with the same name.

        Parameters
        ----------
        component: Component
            The component to add
        """
        ...

    def get_component(self, component_name: str) -> Component | None:
        """
        Returns a component by its name.

        Parameters
        ----------
        component_name: str
            Name of the component

        Returns
        -------
        Optional[Component]
            The component or None if it doesn't exist
        """
        ...

    def get_components_by_type(self, component_type: ComponentType) -> list[Component]:
        """
        Returns all components of a specific type.

        Parameters
        ----------
        component_type: ComponentType
            Type of the components

        Returns
        -------
        list[Component]
            List of components of the specified type
        """
        ...

    def remove_component(self, component_name: str) -> bool:
        """
        Removes a component by its name.

        Parameters
        ----------
        component_name: str
            Name of the component

        Returns
        -------
        bool
            True if the component was removed, False if it didn't exist
        """
        ...
