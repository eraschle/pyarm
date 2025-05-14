"""
Example for using metadata components with the infrastructure elements and parameters.
"""

import logging
from datetime import datetime
from uuid import uuid4

from pyarm.components.metadata import (
    BuildingPhase,
    BuildingPhaseComponent,
    IfcConfigurationComponent,
    MetadataRepository,
)
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Initialize the metadata repository
    metadata_repo = MetadataRepository.get_instance()
    
    # Add building phases to the repository
    phase1 = BuildingPhase(
        id="planning",
        name="Planning Phase",
        start_date="2023-01-01",
        end_date="2023-03-31",
        description="Initial planning and design"
    )
    metadata_repo.add_building_phase(phase1)
    
    phase2 = BuildingPhase(
        id="construction",
        name="Construction Phase",
        start_date="2023-04-01",
        end_date="2023-12-31",
        description="Main construction phase"
    )
    metadata_repo.add_building_phase(phase2)
    
    # Add IFC entity types to the repository
    metadata_repo.add_ifc_entity_type("IfcBeam", "Beam element in the IFC schema")
    metadata_repo.add_ifc_entity_type("IfcColumn", "Column element in the IFC schema")
    
    # Create an element
    mast = InfrastructureElement(name="Mast123", element_type=ElementType.MAST)
    
    # Add a parameter with component
    height_param = Parameter(
        name="Height",
        value=12.5,
        datatype=DataType.FLOAT,
        process=ProcessEnum.HEIGHT,
        unit=UnitEnum.METER
    )
    
    # Add building phase component to the parameter
    phase_comp = BuildingPhaseComponent()
    phase_comp.add_phase_reference("planning")  # Reference to planning phase
    height_param.add_component(phase_comp)
    
    # Add the parameter to the element
    mast.parameters.append(height_param)
    mast.known_params[ProcessEnum.HEIGHT] = height_param
    
    # Add IFC configuration to the element
    ifc_config = IfcConfigurationComponent()
    ifc_config.set_ifc_entity_type("IfcColumn")
    ifc_config.set_ifc_global_id(str(uuid4()))
    ifc_config.set_ifc_predefined_type("COLUMN")
    mast.add_component(ifc_config)
    
    # Add building phase component to the element
    element_phase_comp = BuildingPhaseComponent()
    element_phase_comp.add_phase_reference("construction")  # Reference to construction phase
    mast.add_component(element_phase_comp)
    
    # Display the element with its components
    logger.info(f"Element: {mast.name} ({mast.element_type.value})")
    logger.info(f"UUID: {mast.uuid}")
    logger.info("Parameters:")
    for param in mast.parameters:
        logger.info(f"  {param}")
        # Show parameter components if any
        for comp_name, comp in param.components.items():
            if isinstance(comp, BuildingPhaseComponent):
                phases = comp.get_phases()
                phase_names = [p.name for p in phases]
                logger.info(f"    - Component: {comp_name} (Building Phases: {', '.join(phase_names)})")
    
    logger.info("Components:")
    for comp_name, comp in mast.components.items():
        if isinstance(comp, IfcConfigurationComponent):
            logger.info(f"  - {comp_name} (IFC Type: {comp.ifc_entity_type}, Global ID: {comp.ifc_global_id})")
        elif isinstance(comp, BuildingPhaseComponent):
            phases = comp.get_phases()
            phase_names = [p.name for p in phases]
            logger.info(f"  - {comp_name} (Building Phases: {', '.join(phase_names)})")
        else:
            logger.info(f"  - {comp_name} ({comp.component_type.value})")


if __name__ == "__main__":
    main()