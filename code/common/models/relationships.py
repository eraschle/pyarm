from enum import StrEnum
from dataclasses import dataclass, field
from uuid import UUID

from code.common.models.infrastructure import InfrastructureElement


@dataclass
class Relationship:
    """
    Repräsentiert eine Beziehung zwischen zwei Infrastrukturelementen.
    """

    from_uuid: UUID
    to_uuid: UUID
    relationship_type: (
        str  # Optional: Typ der Beziehung (z. B. "connected_to", "supports", etc.)
    )

    def __post_init__(self):
        """Validierung der Beziehung."""
        if not self.from_uuid or not self.to_uuid:
            raise ValueError("Both 'from_uuid' and 'to_uuid' must be provided.")


@dataclass
class OneToOneRelationship:
    """
    Repräsentiert eine Beziehung zwischen zwei Standorten.
    """

    from_gguid: UUID
    from_element: InfrastructureElement

    to_gguid: UUID
    to_element: InfrastructureElement

    guid: UUID | str | None = None


@dataclass
class OneToManyRelationship:
    """
    Repräsentiert eine Beziehung zwischen einem Standort und mehreren Infrastrukturelementen.
    """


@dataclass
class FromToManyRelationship:
    """
    Repräsentiert eine Beziehung zwischen einem Standort und mehreren Infrastrukturelementen.
    """

    to_gguids: list[UUID]
    to_elements: list[InfrastructureElement]

    guid: UUID | str | None = None


@dataclass
class ToManyToManyRelationship:
    from_gguid: UUID
    from_element: InfrastructureElement

    to_gguids: list[UUID]
    to_elements: list[InfrastructureElement]

    guid: UUID | str | None = None
