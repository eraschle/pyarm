"""Tests für die BuildingPhaseComponent."""

import pytest
from pyarm.components.metadata import BuildingPhase, BuildingPhaseComponent, MetadataRepository


class TestBuildingPhaseComponent:
    """Tests für die BuildingPhaseComponent."""
    
    def setup_method(self):
        """Testumgebung aufsetzen."""
        # Repository für Testdaten vorbereiten
        self.repo = MetadataRepository.get_instance()
        # Repository leeren (für saubere Tests)
        for phase in self.repo.get_all_building_phases():
            self.repo.remove_building_phase(phase.id)
        
        # Testphasen hinzufügen
        self.repo.add_building_phase(BuildingPhase(id="phase1", name="Entwurf"))
        self.repo.add_building_phase(BuildingPhase(id="phase2", name="Ausführung"))
    
    def test_component_manages_phase_references(self):
        """Test: Die Komponente verwaltet Referenzen auf Bauphasen."""
        # GIVEN eine leere BuildingPhaseComponent
        component = BuildingPhaseComponent()
        
        # WHEN Phasenreferenzen hinzugefügt werden
        component.add_phase_reference("phase1")
        component.add_phase_reference("phase2")
        
        # THEN enthält die Komponente die Referenzen
        phase_ids = component.get_phase_ids()
        assert "phase1" in phase_ids
        assert "phase2" in phase_ids
        
        # AND kann Referenzen auf Phasen zurückgeben
        phases = component.get_phases()
        assert len(phases) == 2
        assert phases[0].name in ["Entwurf", "Ausführung"]
        assert phases[1].name in ["Entwurf", "Ausführung"]
        
        # AND kann Referenzen entfernen
        assert component.remove_phase_reference("phase1") is True
        assert "phase1" not in component.get_phase_ids()
        assert len(component.get_phases()) == 1
    
    def test_component_handles_nonexistent_phases(self):
        """Test: Die Komponente geht korrekt mit nicht existierenden Phasen um."""
        # GIVEN eine Komponente mit einer existierenden und einer nicht existierenden Phase
        component = BuildingPhaseComponent()
        component.add_phase_reference("phase1")  # Existiert
        component.add_phase_reference("nonexistent")  # Existiert nicht
        
        # WHEN die Phasen abgerufen werden
        phases = component.get_phases()
        
        # THEN werden nur existierende Phasen zurückgegeben
        assert len(phases) == 1
        assert phases[0].id == "phase1"
        
        # BUT die ID der nicht existierenden Phase ist trotzdem gespeichert
        assert "nonexistent" in component.get_phase_ids()
    
    def test_component_serialization(self):
        """Test: Die Komponente kann serialisiert werden."""
        # GIVEN eine Komponente mit Phasenreferenzen
        component = BuildingPhaseComponent(name="custom_phases")
        component.add_phase_reference("phase1")
        component.add_phase_reference("phase2")
        
        # WHEN die Komponente serialisiert wird
        data = component.to_dict()
        
        # THEN enthält das Ergebnis alle wichtigen Informationen
        assert data["name"] == "custom_phases"
        assert data["component_type"] == "building_phase"
        assert set(data["phase_ids"]) == {"phase1", "phase2"}