"""
Manages relationships and links between infrastructure elements and other entities.
"""

import logging

from pyarm.components.factory import ComponentFactory
from pyarm.models.base_models import InfrastructureElement

log = logging.getLogger(__name__)


class RelationshipManager:
    """
    Manages and establishes relationships between elements stored in a repository.
    This includes bidirectional references between InfrastructureElements and can be
    extended for other types of links (e.g., to metadata).
    """

    def __init__(self):
        self._relationships = {}

    def _add_element_references_to_target(self, element: InfrastructureElement) -> None:
        for ref_component in element.get_references():
            if not ref_component.bidirectional:
                continue

            backlink = ComponentFactory.create_reference(
                referenced_uuid=element.uuid,
                reference_type=type(element),
                bidirectional=True,
            )
            target_uuid = ref_component.referenced_uuid
            if target_uuid not in self._relationships:
                self._relationships[target_uuid] = {}
            if target_uuid in self._relationships:
                if "instance" in self._relationships[target_uuid]:
                    target_instance = self._relationships[target_uuid]["instance"]
                    # Target element already exists. Update with the new reference.
                    target_instance.update_reference_with(backlink)
                elif "references" not in self._relationships[target_uuid]:
                    # Be sure to initialize the references dictionary
                    self._relationships[target_uuid]["references"] = {}
            target_references = self._relationships[target_uuid]["references"]
            if element.uuid in target_references:
                continue
            # Add the backlink reference to the target element's references
            target_references[element.uuid] = backlink

    def _add_element_reference_to_current(self, element: InfrastructureElement) -> None:
        if element.uuid not in self._relationships:
            # Register the element if it is not already registered, do it now!
            self._relationships[element.uuid] = {"instance": element, "references": {}}
            return
        if element.uuid in self._relationships:
            # Either some references already exist or the element itself is already registered
            if "instance" not in self._relationships[element.uuid]:
                # The element is not registered yet. Register it now.
                self._relationships[element.uuid]["instance"] = element
        for reference in self._relationships[element.uuid]["references"].values():
            if not reference.bidirectional:
                continue
            # Update reference in the current element
            element.update_reference_with(reference)

    def establish_bidirectional_ref_for(self, element: InfrastructureElement) -> None:
        """Establishes bidirectional references for a given element.

        It first establishes bidirectional references for the element itself,
        and then for all the elements it references.

        Parameters
        ----------
        element : InfrastructureElement
            The infrastructure element for which to establish bidirectional references.
        """
        if not isinstance(element, InfrastructureElement):
            log.debug(
                f"Item {getattr(element, 'uuid', element)} in subset "
                "is not an InfrastructureElement. Skipping."
            )
            return
        self._add_element_references_to_target(element)
        self._add_element_reference_to_current(element)

    def establish_bidirectional_ref_for_subset(self, elements: list[InfrastructureElement]) -> None:
        """
        Establishes bidirectional references for a given subset of elements.

        This method iterates through the provided list of elements. For each
        element in the subset that has a declared bidirectional reference to a
        target element, it attempts to:
        1. Find the target element using its UUID via the repository.
        2. If the target element is found, it creates or updates the reverse
           reference in the target element to point back to the source element
           from the subset.

        Parameters
        ----------
        elements_subset : list[InfrastructureElement]
            A list of infrastructure elements for which to establish bidirectional references.
        """
        log.info(
            f"Starting to establish bidirectional references "
            f"for a subset of {len(elements)} elements."
        )
        if not elements:
            log.info("Element subset is empty. No references to process.")
            return

        for source in elements:
            self.establish_bidirectional_ref_for(source)

    # --- Future extension points (Beispiele) ---
    # def link_elements_to_metadata(self, metadata_repository: "IMetadataRepository"):
    #     log.info("Starting to link elements to metadata.")
    #     # ... Implementierung ...
    #     log.info("Finished linking elements to metadata.")

    # def establish_custom_links(self, link_definitions: list[dict]):
    #     log.info(f"Establishing custom links based on {len(link_definitions)} definitions.")
    #     # ... Implementierung ...
