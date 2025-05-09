"""
Client A spezifischer Datenkonverter.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID

from ..common.enums.process_enums import ProcessEnum, ElementType, UnitEnum
from ..common.models.base_models import Parameter, InfrastructureElement
from ..common.utils.factory import create_element


class ClientAConverter:
    """
    Konverter für Daten des Clients A.
    Konvertiert client-spezifische Daten in das kanonische Format.
    """
    
    @property
    def name(self) -> str:
        return "ClientAConverter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_types(self) -> List[str]:
        return ["foundation", "mast", "joch", "track", "curved_track", "drainage"]
    
    def can_convert(self, data: Dict[str, Any]) -> bool:
        """
        Prüft, ob dieser Konverter die angegebenen Daten konvertieren kann.
        
        Args:
            data: Zu konvertierende Daten
            
        Returns:
            True, wenn dieser Konverter die Daten konvertieren kann
        """
        element_type = data.get("element_type", "").lower()
        return element_type in self.supported_types
    
    def convert(self, data: Dict[str, Any]) -> List[InfrastructureElement]:
        """
        Konvertiert die angegebenen Daten in InfrastructureElement-Objekte.
        
        Args:
            data: Zu konvertierende Daten
            
        Returns:
            Liste der konvertierten Elemente
        """
        element_type = data.get("element_type", "").lower()
        project_id = data.get("project_id", "unknown")
        raw_data = data.get("data", [])
        
        converter_method = getattr(self, f"_convert_{element_type}", None)
        if converter_method:
            if project_id == "project1":
                return converter_method(raw_data, project_id)
            elif project_id == "project2":
                # Für Projekt 2 verwenden wir die Project2-Konverter
                converter_method = getattr(self, f"_convert_{element_type}_project2", None)
                if converter_method:
                    return converter_method(raw_data, project_id)
                # Fallback auf den Standard-Konverter, wenn kein spezieller existiert
                return self._convert_generic(raw_data, element_type)
        
        # Fallback auf generischen Konverter
        return self._convert_generic(raw_data, element_type)
    
    def _convert_foundation(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Fundament-Daten des Clients A (Projekt 1).
        
        Args:
            data: Liste von Fundament-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Fundament-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Fundament {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": ElementType.FOUNDATION.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="Typ", value=item.get("Typ"), process=ProcessEnum.FOUNDATION_TYPE),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Breite", value=float(item.get("Breite", 0)), process=ProcessEnum.FOUNDATION_WIDTH, unit=UnitEnum.METER),
                Parameter(name="Tiefe", value=float(item.get("Tiefe", 0)), process=ProcessEnum.FOUNDATION_DEPTH, unit=UnitEnum.METER),
                Parameter(name="Höhe", value=float(item.get("Höhe", 0)), process=ProcessEnum.FOUNDATION_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
            ]
            
            if "MastID" in item:
                parameters.append(Parameter(name="MastID", value=item.get("MastID"), process=None))
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_foundation_project2(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Fundament-Daten des Clients A (Projekt 2).
        
        Args:
            data: Liste von Fundament-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Fundament-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Name", f"Fundament {item.get('UUID', 'Unknown')}"),
                "uuid": item.get("UUID"),
                "element_type": ElementType.FOUNDATION.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="UUID", value=item.get("UUID"), process=ProcessEnum.UUID),
                Parameter(name="FoundationType", value=item.get("FoundationType"), process=ProcessEnum.FOUNDATION_TYPE),
                Parameter(name="East", value=float(item.get("East", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="North", value=float(item.get("North", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Height", value=float(item.get("Height", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Width", value=float(item.get("Width", 0)), process=ProcessEnum.FOUNDATION_WIDTH, unit=UnitEnum.METER),
                Parameter(name="Depth", value=float(item.get("Depth", 0)), process=ProcessEnum.FOUNDATION_DEPTH, unit=UnitEnum.METER),
                Parameter(name="HeightFoundation", value=float(item.get("HeightFoundation", 0)), process=ProcessEnum.FOUNDATION_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
            ]
            
            if "MastReference" in item:
                parameters.append(Parameter(name="MastReference", value=item.get("MastReference"), process=None))
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_mast(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Mast-Daten des Clients A (Projekt 1).
        
        Args:
            data: Liste von Mast-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Mast-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Mast {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": ElementType.MAST.value,
                "parameters": []
            }
            
            # Referenz zum Fundament
            if "FundamentID" in item:
                element_data["foundation_uuid"] = item.get("FundamentID")
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="Typ", value=item.get("Typ"), process=ProcessEnum.MAST_TYPE),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Höhe", value=float(item.get("Höhe", 0)), process=ProcessEnum.MAST_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Azimut", value=float(item.get("Azimut", 0)), process=ProcessEnum.AZIMUTH, unit=UnitEnum.DEGREE),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
                Parameter(name="Profiltyp", value=item.get("Profiltyp"), process=ProcessEnum.MAST_PROFILE_TYPE),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_mast_project2(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Mast-Daten des Clients A (Projekt 2).
        
        Args:
            data: Liste von Mast-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Mast-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Name", f"Mast {item.get('UUID', 'Unknown')}"),
                "uuid": item.get("UUID"),
                "element_type": ElementType.MAST.value,
                "parameters": []
            }
            
            # Referenz zum Fundament
            if "FoundationReference" in item:
                element_data["foundation_uuid"] = item.get("FoundationReference")
            
            # Parameter erstellen
            parameters = [
                Parameter(name="UUID", value=item.get("UUID"), process=ProcessEnum.UUID),
                Parameter(name="MastType", value=item.get("MastType"), process=ProcessEnum.MAST_TYPE),
                Parameter(name="East", value=float(item.get("East", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="North", value=float(item.get("North", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Height", value=float(item.get("Height", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="HeightMast", value=float(item.get("HeightMast", 0)), process=ProcessEnum.MAST_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Azimuth", value=float(item.get("Azimuth", 0)), process=ProcessEnum.AZIMUTH, unit=UnitEnum.DEGREE),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
                Parameter(name="ProfileType", value=item.get("ProfileType"), process=ProcessEnum.MAST_PROFILE_TYPE),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_joch(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Joch-Daten des Clients A.
        
        Args:
            data: Liste von Joch-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Joch-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Joch {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": ElementType.JOCH.value,
                "parameters": []
            }
            
            # Referenzen zu den Masten
            if "Mast1ID" in item:
                element_data["mast_uuid_1"] = item.get("Mast1ID")
            if "Mast2ID" in item:
                element_data["mast_uuid_2"] = item.get("Mast2ID")
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="Typ", value=item.get("Typ"), process=ProcessEnum.JOCH_TYPE),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="E2", value=float(item.get("E2", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="N2", value=float(item.get("N2", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Z2", value=float(item.get("Z2", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Spannweite", value=float(item.get("Spannweite", 0)), process=ProcessEnum.JOCH_SPAN, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_track(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Gleis-Daten des Clients A (Projekt 1).
        
        Args:
            data: Liste von Gleis-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Gleis-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Gleis {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": ElementType.TRACK.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="E2", value=float(item.get("E2", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="N2", value=float(item.get("N2", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Z2", value=float(item.get("Z2", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Spurweite", value=float(item.get("Spurweite", 0)), process=ProcessEnum.TRACK_GAUGE, unit=UnitEnum.METER),
                Parameter(name="Gleistyp", value=item.get("Gleistyp"), process=ProcessEnum.TRACK_TYPE),
                Parameter(name="Überhöhung", value=float(item.get("Überhöhung", 0)), process=ProcessEnum.TRACK_CANT, unit=UnitEnum.MILLIMETER),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_track_project2(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Gleis-Daten des Clients A (Projekt 2).
        
        Args:
            data: Liste von Gleis-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Gleis-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Name", f"Gleis {item.get('UUID', 'Unknown')}"),
                "uuid": item.get("UUID"),
                "element_type": ElementType.TRACK.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="UUID", value=item.get("UUID"), process=ProcessEnum.UUID),
                Parameter(name="East", value=float(item.get("East", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="North", value=float(item.get("North", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Height", value=float(item.get("Height", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="East2", value=float(item.get("East2", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="North2", value=float(item.get("North2", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Height2", value=float(item.get("Height2", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="TrackGauge", value=float(item.get("TrackGauge", 0)), process=ProcessEnum.TRACK_GAUGE, unit=UnitEnum.METER),
                Parameter(name="TrackType", value=item.get("TrackType"), process=ProcessEnum.TRACK_TYPE),
                Parameter(name="TrackCant", value=float(item.get("TrackCant", 0)), process=ProcessEnum.TRACK_CANT, unit=UnitEnum.MILLIMETER),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_curved_track(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Kurvengleis-Daten des Clients A.
        
        Args:
            data: Liste von Kurvengleis-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Kurvengleis-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Kurvengleis {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": ElementType.TRACK.value,  # CurvedTrack ist ein spezieller Track
                "parameters": []
            }
            
            # Klothoidenparameter für die Erkennung als Kurvengleis
            startradius = item.get("Startradius")
            if startradius == "inf" or startradius == "":
                startradius = float('inf')
            else:
                startradius = float(startradius) if startradius else None
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="E2", value=float(item.get("E2", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="N2", value=float(item.get("N2", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Z2", value=float(item.get("Z2", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                Parameter(name="Spurweite", value=float(item.get("Spurweite", 0)), process=ProcessEnum.TRACK_GAUGE, unit=UnitEnum.METER),
                Parameter(name="Gleistyp", value=item.get("Gleistyp"), process=ProcessEnum.TRACK_TYPE),
                Parameter(name="Überhöhung", value=float(item.get("Überhöhung", 0)), process=ProcessEnum.TRACK_CANT, unit=UnitEnum.MILLIMETER),
                Parameter(name="Klothoidenparameter", value=float(item.get("Klothoidenparameter", 0)), process=ProcessEnum.CLOTHOID_PARAMETER),
                Parameter(name="Startradius", value=startradius, process=ProcessEnum.START_RADIUS, unit=UnitEnum.METER),
                Parameter(name="Endradius", value=float(item.get("Endradius", 0)), process=ProcessEnum.END_RADIUS, unit=UnitEnum.METER),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_drainage(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Entwässerungs-Daten des Clients A.
        
        Args:
            data: Liste von Entwässerungs-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Entwässerungs-Elemente
        """
        results = []
        for item in data:
            # Elementtyp bestimmen
            if item.get("Typ", "").lower() == "pipe":
                element_type = ElementType.DRAINAGE_PIPE.value
            elif item.get("Typ", "").lower() == "shaft":
                element_type = ElementType.DRAINAGE_SHAFT.value
            else:
                continue  # Unbekannter Typ
            
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Bezeichnung", f"Entwässerung {item.get('ID', 'Unknown')}"),
                "uuid": item.get("ID"),
                "element_type": element_type,
                "parameters": []
            }
            
            # Gemeinsame Parameter
            common_parameters = [
                Parameter(name="ID", value=item.get("ID"), process=ProcessEnum.UUID),
                Parameter(name="E", value=float(item.get("E", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="N", value=float(item.get("N", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("Z", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("Material"), process=ProcessEnum.MATERIAL),
            ]
            
            # Spezifische Parameter je nach Typ
            if element_type == ElementType.DRAINAGE_PIPE.value:
                pipe_parameters = [
                    Parameter(name="E2", value=float(item.get("E2", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="N2", value=float(item.get("N2", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="Z2", value=float(item.get("Z2", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="Durchmesser", value=float(item.get("Durchmesser", 0)), process=ProcessEnum.PIPE_DIAMETER, unit=UnitEnum.MILLIMETER),
                    Parameter(name="Gefälle", value=float(item.get("Gefälle", 0)), process=ProcessEnum.PIPE_SLOPE, unit=UnitEnum.PROMILLE),
                ]
                parameters = common_parameters + pipe_parameters
            else:  # DRAINAGE_SHAFT
                shaft_parameters = [
                    Parameter(name="Durchmesser", value=float(item.get("Durchmesser", 0)), process=ProcessEnum.SHAFT_DIAMETER, unit=UnitEnum.MILLIMETER),
                ]
                parameters = common_parameters + shaft_parameters
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_generic(self, data: List[Dict[str, Any]], element_type_str: str) -> List[InfrastructureElement]:
        """
        Generischer Konverter für unbekannte Datentypen.
        
        Args:
            data: Liste von Daten
            element_type_str: String-Repräsentation des Elementtyps
            
        Returns:
            Liste der konvertierten Elemente
        """
        # Elementtyp bestimmen
        element_type = None
        for et in ElementType:
            if et.value in element_type_str.lower():
                element_type = et
                break
        
        if not element_type:
            element_type = ElementType.FOUNDATION  # Fallback
        
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("Name", item.get("Bezeichnung", f"Element {item.get('UUID', item.get('ID', 'Unknown'))}")),
                "uuid": item.get("UUID", item.get("ID")),
                "element_type": element_type.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = []
            for key, value in item.items():
                # Prozess-Enum versuchen zu finden
                process_enum = None
                for pe in ProcessEnum:
                    if pe.name.lower() in key.lower():
                        process_enum = pe
                        break
                
                # Typumwandlung, wenn nötig
                if isinstance(value, str) and value.replace('.', '', 1).isdigit():
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                
                # Einheit bestimmen
                unit = UnitEnum.NONE
                if process_enum in [ProcessEnum.X_COORDINATE, ProcessEnum.Y_COORDINATE, ProcessEnum.Z_COORDINATE,
                                    ProcessEnum.X_COORDINATE_END, ProcessEnum.Y_COORDINATE_END, ProcessEnum.Z_COORDINATE_END]:
                    unit = UnitEnum.METER
                
                parameters.append(Parameter(name=key, value=value, process=process_enum, unit=unit))
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results