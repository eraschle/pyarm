# Typisierte Basisklasse für eine verbesserte Vererbungshierarchie
from typing import Any, TypeVar
from uuid import UUID, uuid4

from pyarm.models.base_models import InfrastructureElement
from pyarm.models.process_enums import ElementType
from pyarm.utils import helpers as hlp

T = TypeVar("T", bound=InfrastructureElement)


class ElementFactory:
    """Factory for creating specialized elements."""

    @staticmethod
    def create_from_data(
        data: dict[str, Any],
        element_class: type[T] | None = None,
    ) -> InfrastructureElement:
        """
        Creates an element from the given data.
        Uses the specified class or selects a suitable one based on element_type.

        Args:
            data: The element data
            element_class: Optional specific class to use

        Returns:
            The created element
        """
        # Extract base attributes
        name = hlp.extract_value(data, "name", "Unknown", str)
        uuid_value = hlp.extract_value(data, "uuid")
        uuid = UUID(uuid_value) if uuid_value else uuid4()

        # Element-Typ ermitteln
        element_type_value = hlp.extract_value(data, "element_type")
        if isinstance(element_type_value, str):
            try:
                element_type = ElementType(element_type_value)
            except ValueError:
                element_type = ElementType.UNDEFINED
        elif isinstance(
            element_type_value,
            ElementType,
        ):
            element_type = element_type_value
        else:
            element_type = ElementType.UNDEFINED

        # Parameter extrahieren
        parameters = []
        for param_data in data.get("parameters", []):
            parameters.append(hlp.create_parameter_from(param_data))

        # Element erstellen
        if element_class:
            # Verwende die angegebene Klasse
            element = element_class(
                name=name,
                uuid=uuid,
                element_type=element_type,
                parameters=parameters,
            )
        else:
            # Standardklasse verwenden
            element = InfrastructureElement(
                name=name,
                uuid=uuid,
                element_type=element_type,
                parameters=parameters,
            )

        return element
