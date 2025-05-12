from typing import TYPE_CHECKING, Type
from uuid import UUID

from pyarm.components.base import Component, ComponentType

if TYPE_CHECKING:
    from pyarm.models.base_models import InfrastructureElement


class ElementReference(Component):
    """Komponente für die Referenz zu einem anderen Element."""

    def __init__(
        self,
        name: str,
        referenced_uuid: UUID,
        reference_type: Type["InfrastructureElement"],
        bidirectional: bool = False,
        component_type: ComponentType = ComponentType.REFERENCE,
    ):
        """
        Initialisiert eine ElementReference-Komponente.

        Args:
            referenced_uuid: UUID des referenzierten Elements
            reference_type: Typ der Referenz (z.B. "foundation", "mast")
            name: Name der Komponente
            bidirectional: Ob die Referenz bidirektional ist
            component_type: Typ der Komponente (sollte REFERENCE sein)
        """
        super().__init__(name=name, component_type=component_type)
        self.referenced_uuid = referenced_uuid
        self.reference_type = reference_type
        self.bidirectional = bidirectional

    def __str__(self) -> str:
        return f"{self.reference_type}: {self.referenced_uuid}"
