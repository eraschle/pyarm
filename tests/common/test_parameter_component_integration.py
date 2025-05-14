"""Tests für die Integration von Komponenten mit Parametern."""

import pytest
from pyarm.components.base import ComponentType
from pyarm.components.metadata import BuildingPhaseComponent
from pyarm.models.parameter import DataType, Parameter, UnitEnum
from pyarm.models.process_enums import ProcessEnum


class TestParameterComponentIntegration:
    """Tests für die Integration von Komponenten mit Parametern."""
    
    def test_parameter_can_hold_components(self):
        """Test: Parameter können Komponenten aufnehmen und verwalten."""
        # GIVEN ein Parameter
        param = Parameter(
            name="Höhe", 
            value=12.5, 
            datatype=DataType.FLOAT,
            process=ProcessEnum.HEIGHT,
            unit=UnitEnum.METER
        )
        
        # WHEN eine Komponente hinzugefügt wird
        component = BuildingPhaseComponent(name="custom_phases")
        component.add_phase_reference("phase1")
        param.add_component(component)
        
        # THEN kann der Parameter die Komponente halten und abrufen
        assert len(param.components) == 1
        assert "custom_phases" in param.components
        
        retrieved = param.get_component("custom_phases")
        assert retrieved is not None
        assert retrieved.name == "custom_phases"
        assert "phase1" in retrieved.get_phase_ids()
        
        # AND kann Komponenten nach Typ abrufen
        comps = param.get_components_by_type(ComponentType.BUILDING_PHASE)
        assert len(comps) == 1
        assert comps[0].name == "custom_phases"
        
        # AND kann Komponenten entfernen
        assert param.remove_component("custom_phases") is True
        assert len(param.components) == 0
    
    def test_parameter_to_dict_includes_components(self):
        """Test: Parameter-Serialisierung schließt Komponenten ein."""
        # GIVEN ein Parameter mit einer Komponente
        param = Parameter(
            name="Breite", 
            value=2.5, 
            datatype=DataType.FLOAT,
            process=ProcessEnum.WIDTH
        )
        
        component = BuildingPhaseComponent()
        component.add_phase_reference("phase1")
        param.add_component(component)
        
        # WHEN der Parameter serialisiert wird
        data = param.to_dict()
        
        # THEN enthält das Ergebnis die Komponenten-Informationen
        assert "components" in data
        assert "building_phases" in data["components"]
        assert "phase_ids" in data["components"]["building_phases"]
        assert "phase1" in data["components"]["building_phases"]["phase_ids"]
    
    def test_parameter_string_representation_shows_components(self):
        """Test: Die String-Darstellung zeigt Komponenten an."""
        # GIVEN ein Parameter ohne und mit Komponenten
        param1 = Parameter(name="P1", value="Test", datatype=DataType.STRING)
        param2 = Parameter(name="P2", value="Test", datatype=DataType.STRING)
        param2.add_component(BuildingPhaseComponent())
        
        # WHEN die String-Darstellung abgerufen wird
        str1 = str(param1)
        str2 = str(param2)
        
        # THEN zeigt param2 Komponenten an, param1 nicht
        assert "+1 components" in str2
        assert "components" not in str1