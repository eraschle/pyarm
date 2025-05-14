"""Tests für das MetadataRepository."""

import pytest
from pyarm.components.metadata import BuildingPhase, MetadataRepository


class TestMetadataRepository:
    """Tests für das zentrale Metadaten-Repository."""
    
    def setup_method(self):
        """Testumgebung aufsetzen."""
        # Neues Repository für jeden Test erstellen
        # Anmerkung: Für den Singleton-Test verwenden wir get_instance()
        self.repo = MetadataRepository()
        
    def test_repository_manages_building_phases(self):
        """Test: Das Repository verwaltet Bauphasen korrekt."""
        # GIVEN ein leeres Repository
        repo = self.repo
        
        # WHEN Bauphasen hinzugefügt werden
        phase1 = BuildingPhase(id="phase1", name="Planungsphase")
        phase2 = BuildingPhase(id="phase2", name="Bauphase")
        repo.add_building_phase(phase1)
        repo.add_building_phase(phase2)
        
        # THEN können die Phasen abgefragt werden
        assert len(repo.get_all_building_phases()) == 2
        
        retrieved_phase = repo.get_building_phase("phase1")
        assert retrieved_phase is not None
        assert retrieved_phase.id == "phase1"
        assert retrieved_phase.name == "Planungsphase"
        
        # AND können Phasen entfernt werden
        assert repo.remove_building_phase("phase1") is True
        assert repo.get_building_phase("phase1") is None
        assert len(repo.get_all_building_phases()) == 1
        
        # AND nicht existierende Phasen zu entfernen gibt False zurück
        assert repo.remove_building_phase("not_exists") is False
    
    def test_repository_manages_ifc_entity_types(self):
        """Test: Das Repository verwaltet IFC-Entity-Typen korrekt."""
        # GIVEN ein leeres Repository
        repo = self.repo
        
        # WHEN IFC-Entity-Typen hinzugefügt werden
        repo.add_ifc_entity_type("IfcBeam", "Beam element in the IFC schema")
        repo.add_ifc_entity_type("IfcColumn", "Column element in the IFC schema")
        
        # THEN können die Typen abgefragt werden
        assert repo.get_ifc_entity_type_description("IfcBeam") == "Beam element in the IFC schema"
        assert repo.get_ifc_entity_type_description("IfcColumn") == "Column element in the IFC schema"
        
        # AND nicht existierende Typen geben None zurück
        assert repo.get_ifc_entity_type_description("IfcNonExistent") is None
        
        # AND alle Typen können als Dictionary abgerufen werden
        types = repo.get_all_ifc_entity_types()
        assert len(types) == 2
        assert types["IfcBeam"] == "Beam element in the IFC schema"
        assert types["IfcColumn"] == "Column element in the IFC schema"
    
    def test_repository_manages_custom_metadata(self):
        """Test: Das Repository verwaltet benutzerdefinierte Metadaten korrekt."""
        # GIVEN ein leeres Repository
        repo = self.repo
        
        # WHEN benutzerdefinierte Metadaten hinzugefügt werden
        repo.add_custom_metadata("project", "client", "Example Corp")
        repo.add_custom_metadata("project", "start_date", "2023-01-01")
        repo.add_custom_metadata("technical", "software_version", "1.0.0")
        
        # THEN können die Metadaten abgefragt werden
        assert repo.get_custom_metadata("project", "client") == "Example Corp"
        assert repo.get_custom_metadata("project", "start_date") == "2023-01-01"
        assert repo.get_custom_metadata("technical", "software_version") == "1.0.0"
        
        # AND nicht existierende Metadaten geben None zurück
        assert repo.get_custom_metadata("project", "non_existent") is None
        assert repo.get_custom_metadata("non_existent", "key") is None
        
        # AND alle Metadaten einer Kategorie können abgerufen werden
        project_metadata = repo.get_all_custom_metadata("project")
        assert len(project_metadata) == 2
        assert project_metadata["client"] == "Example Corp"
        assert project_metadata["start_date"] == "2023-01-01"
        
        # AND alle Metadaten können abgerufen werden
        all_metadata = repo.get_all_custom_metadata()
        assert len(all_metadata) == 2  # Zwei Kategorien
        assert "project" in all_metadata
        assert "technical" in all_metadata
    
    def test_repository_serialization_and_deserialization(self):
        """Test: Das Repository kann serialisiert und deserialisiert werden."""
        # GIVEN ein Repository mit Daten
        repo1 = self.repo
        repo1.add_building_phase(BuildingPhase(id="phase1", name="Phase 1", 
                                              start_date="2023-01-01"))
        repo1.add_ifc_entity_type("IfcBeam", "Beam element")
        repo1.add_custom_metadata("project", "client", "Example Corp")
        
        # WHEN das Repository serialisiert und deserialisiert wird
        data = repo1.to_dict()
        repo2 = MetadataRepository.from_dict(data)
        
        # THEN enthält das neue Repository die gleichen Daten
        phase = repo2.get_building_phase("phase1")
        assert phase is not None
        assert phase.name == "Phase 1"
        assert phase.start_date == "2023-01-01"
        
        assert repo2.get_ifc_entity_type_description("IfcBeam") == "Beam element"
        assert repo2.get_custom_metadata("project", "client") == "Example Corp"
    
    def test_repository_singleton_behavior(self):
        """Test: Das Repository funktioniert als Singleton."""
        # GIVEN zwei Instanzen, die über die get_instance Methode geholt werden
        repo1 = MetadataRepository.get_instance()
        repo1.add_building_phase(BuildingPhase(id="phase_x", name="X"))
        
        # WHEN eine zweite Instanz geholt wird
        repo2 = MetadataRepository.get_instance()
        
        # THEN sind beide Instanzen identisch
        assert repo1 is repo2
        assert repo2.get_building_phase("phase_x") is not None
        
        # AND Änderungen an einer Instanz wirken sich auf die andere aus
        repo2.add_building_phase(BuildingPhase(id="phase_y", name="Y"))
        assert repo1.get_building_phase("phase_y") is not None
        
        # BUT direkt erstellte Instanzen sind nicht der Singleton
        repo3 = MetadataRepository()
        assert repo3 is not repo1
        assert repo3.get_building_phase("phase_x") is None