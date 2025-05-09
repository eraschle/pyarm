"""
Client C spezifischer Datenkonverter für das FDK-Format.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, cast
from uuid import UUID

# Füge das Stammverzeichnis zum Pythonpfad hinzu, um absolute Importe zu ermöglichen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from code.common.enums.process_enums import ProcessEnum, ElementType, UnitEnum
from code.common.models.base_models import Parameter, InfrastructureElement
from code.common.utils.factory import create_element


class ClientCFdkConverter:
    """
    Konverter für FDK-Daten des Clients C.
    Konvertiert client-spezifische FDK-Daten in das kanonische Format.
    Besonderheit: Verarbeitet IFC-Daten und Bauphasen-Informationen.
    """
    
    @property
    def name(self) -> str:
        return "ClientCFdkConverter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_types(self) -> List[str]:
        return ["foundation", "mast", "track", "drainage", "building"]
    
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
        raw_data = data.get("data", [])
        
        converter_method = getattr(self, f"_convert_{element_type}", None)
        if converter_method:
            return converter_method(raw_data)
        
        # Fallback auf generischen Konverter
        return self._convert_generic(raw_data, element_type)
    
    def _convert_foundation(self, data: List[Dict[str, Any]]) -> List[InfrastructureElement]:
        """
        Konvertiert Fundament-Daten des Clients C aus dem FDK-Format.
        
        Args:
            data: Liste von Fundament-Daten
            
        Returns:
            Liste der konvertierten Fundament-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Fundament {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.FOUNDATION.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.FOUNDATION_TYPE),
                Parameter(name="material", value=item.get("material"), process=ProcessEnum.MATERIAL),
                Parameter(name="depth_m", value=item.get("depth_m"), process=ProcessEnum.FOUNDATION_DEPTH, unit=UnitEnum.METER),
                Parameter(name="volume_m3", value=item.get("volume_m3"), process=ProcessEnum.VOLUME, unit=UnitEnum.CUBIC_METER),
                Parameter(name="capacity_kn", value=item.get("capacity_kn"), process=ProcessEnum.CAPACITY, unit=UnitEnum.KILONEWTON),
            ]
            
            # Standortdaten
            if "km" in item:
                parameters.extend([
                    Parameter(name="km", value=item.get("km"), process=ProcessEnum.KILOMETER_POSITION, unit=UnitEnum.KILOMETER),
                    Parameter(name="gleis_id", value=item.get("gleis_id"), process=ProcessEnum.TRACK_REFERENCE),
                    Parameter(name="distance_m", value=item.get("distance_m"), process=ProcessEnum.DISTANCE, unit=UnitEnum.METER),
                ])
            
            # IFC-Daten
            if "ifc_data" in item:
                ifc = item["ifc_data"]
                parameters.extend([
                    Parameter(name="ifc_global_id", value=ifc.get("globalId"), process=ProcessEnum.IFC_GLOBAL_ID),
                    Parameter(name="ifc_type", value=ifc.get("type"), process=ProcessEnum.IFC_TYPE),
                    Parameter(name="ifc_material", value=ifc.get("material"), process=ProcessEnum.IFC_MATERIAL),
                    Parameter(name="ifc_category", value=ifc.get("category"), process=ProcessEnum.IFC_CATEGORY),
                ])
            
            # Bauphase
            if "bauphase" in item:
                bp = item["bauphase"]
                parameters.extend([
                    Parameter(name="bauphase_id", value=bp.get("id"), process=ProcessEnum.CONSTRUCTION_PHASE_ID),
                    Parameter(name="bauphase_name", value=bp.get("name"), process=ProcessEnum.CONSTRUCTION_PHASE_NAME),
                    Parameter(name="bauphase_start", value=bp.get("start_date"), process=ProcessEnum.CONSTRUCTION_PHASE_START),
                    Parameter(name="bauphase_end", value=bp.get("end_date"), process=ProcessEnum.CONSTRUCTION_PHASE_END),
                ])
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_mast(self, data: List[Dict[str, Any]]) -> List[InfrastructureElement]:
        """
        Konvertiert Mast-Daten des Clients C aus dem FDK-Format.
        
        Args:
            data: Liste von Mast-Daten
            
        Returns:
            Liste der konvertierten Mast-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Mast {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.MAST.value,
                "parameters": []
            }
            
            # Referenz zum Fundament
            if "foundation_id" in item:
                element_data["foundation_uuid"] = item.get("foundation_id")
            
            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.MAST_TYPE),
                Parameter(name="material", value=item.get("material"), process=ProcessEnum.MATERIAL),
                Parameter(name="height_m", value=item.get("height_m"), process=ProcessEnum.MAST_HEIGHT, unit=UnitEnum.METER),
            ]
            
            # Standortdaten
            if "km" in item:
                parameters.extend([
                    Parameter(name="km", value=item.get("km"), process=ProcessEnum.KILOMETER_POSITION, unit=UnitEnum.KILOMETER),
                    Parameter(name="gleis_id", value=item.get("gleis_id"), process=ProcessEnum.TRACK_REFERENCE),
                    Parameter(name="distance_m", value=item.get("distance_m"), process=ProcessEnum.DISTANCE, unit=UnitEnum.METER),
                ])
            
            # IFC-Daten
            if "ifc_data" in item:
                ifc = item["ifc_data"]
                parameters.extend([
                    Parameter(name="ifc_global_id", value=ifc.get("globalId"), process=ProcessEnum.IFC_GLOBAL_ID),
                    Parameter(name="ifc_type", value=ifc.get("type"), process=ProcessEnum.IFC_TYPE),
                    Parameter(name="ifc_material", value=ifc.get("material"), process=ProcessEnum.IFC_MATERIAL),
                    Parameter(name="ifc_category", value=ifc.get("category"), process=ProcessEnum.IFC_CATEGORY),
                ])
            
            # Bauphase
            if "bauphase" in item:
                bp = item["bauphase"]
                parameters.extend([
                    Parameter(name="bauphase_id", value=bp.get("id"), process=ProcessEnum.CONSTRUCTION_PHASE_ID),
                    Parameter(name="bauphase_name", value=bp.get("name"), process=ProcessEnum.CONSTRUCTION_PHASE_NAME),
                    Parameter(name="bauphase_start", value=bp.get("start_date"), process=ProcessEnum.CONSTRUCTION_PHASE_START),
                    Parameter(name="bauphase_end", value=bp.get("end_date"), process=ProcessEnum.CONSTRUCTION_PHASE_END),
                ])
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_track(self, data: List[Dict[str, Any]]) -> List[InfrastructureElement]:
        """
        Konvertiert Gleis-Daten des Clients C aus dem FDK-Format.
        
        Args:
            data: Liste von Gleis-Daten
            
        Returns:
            Liste der konvertierten Gleis-Elemente
        """
        results = []
        for item in data:
            # Prüfen, ob es sich um ein Kurvengleis handelt
            is_curved = item.get("is_curved", False)
            element_type = ElementType.TRACK.value
            
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Gleis {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.TRACK_TYPE),
                Parameter(name="length_m", value=item.get("length_m"), process=ProcessEnum.LENGTH, unit=UnitEnum.METER),
                Parameter(name="gauge_mm", value=item.get("gauge_mm"), process=ProcessEnum.TRACK_GAUGE, unit=UnitEnum.MILLIMETER),
            ]
            
            # Kurvenparameter, falls vorhanden
            if is_curved and "radius_m" in item:
                radius = item.get("radius_m")
                parameters.extend([
                    Parameter(name="radius_m", value=radius, process=ProcessEnum.RADIUS, unit=UnitEnum.METER),
                    # Für CurvedTrack werden sowohl start_radius als auch end_radius gesetzt
                    Parameter(name="start_radius_m", value=radius, process=ProcessEnum.START_RADIUS, unit=UnitEnum.METER),
                    Parameter(name="end_radius_m", value=radius, process=ProcessEnum.END_RADIUS, unit=UnitEnum.METER),
                ])
            
            # IFC-Daten
            if "ifc_data" in item:
                ifc = item["ifc_data"]
                parameters.extend([
                    Parameter(name="ifc_global_id", value=ifc.get("globalId"), process=ProcessEnum.IFC_GLOBAL_ID),
                    Parameter(name="ifc_type", value=ifc.get("type"), process=ProcessEnum.IFC_TYPE),
                    Parameter(name="ifc_material", value=ifc.get("material"), process=ProcessEnum.IFC_MATERIAL),
                    Parameter(name="ifc_category", value=ifc.get("category"), process=ProcessEnum.IFC_CATEGORY),
                ])
            
            # Bauphase
            if "bauphase" in item:
                bp = item["bauphase"]
                parameters.extend([
                    Parameter(name="bauphase_id", value=bp.get("id"), process=ProcessEnum.CONSTRUCTION_PHASE_ID),
                    Parameter(name="bauphase_name", value=bp.get("name"), process=ProcessEnum.CONSTRUCTION_PHASE_NAME),
                    Parameter(name="bauphase_start", value=bp.get("start_date"), process=ProcessEnum.CONSTRUCTION_PHASE_START),
                    Parameter(name="bauphase_end", value=bp.get("end_date"), process=ProcessEnum.CONSTRUCTION_PHASE_END),
                ])
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_drainage(self, data: List[Dict[str, Any]]) -> List[InfrastructureElement]:
        """
        Konvertiert Entwässerungs-Daten des Clients C aus dem FDK-Format.
        
        Args:
            data: Liste von Entwässerungs-Daten
            
        Returns:
            Liste der konvertierten Entwässerungs-Elemente
        """
        results = []
        for item in data:
            # Elementtyp bestimmen
            if item.get("type", "").lower() == "shaft":
                element_type = ElementType.DRAINAGE_SHAFT.value
            else:
                element_type = ElementType.DRAINAGE_PIPE.value
            
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Entwässerung {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type,
                "parameters": []
            }
            
            # Gemeinsame Parameter
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.DRAINAGE_TYPE),
                Parameter(name="material", value=item.get("material"), process=ProcessEnum.MATERIAL),
            ]
            
            # Spezifische Parameter je nach Typ
            if element_type == ElementType.DRAINAGE_SHAFT.value:
                parameters.extend([
                    Parameter(name="diameter_mm", value=item.get("diameter_mm"), process=ProcessEnum.SHAFT_DIAMETER, unit=UnitEnum.MILLIMETER),
                    Parameter(name="depth_m", value=item.get("depth_m"), process=ProcessEnum.SHAFT_DEPTH, unit=UnitEnum.METER),
                    # Standort für punktförmige Elemente
                    Parameter(name="km", value=item.get("km"), process=ProcessEnum.KILOMETER_POSITION, unit=UnitEnum.KILOMETER),
                ])
            else:  # DRAINAGE_PIPE
                parameters.extend([
                    Parameter(name="length_m", value=item.get("length_m"), process=ProcessEnum.LENGTH, unit=UnitEnum.METER),
                    # Standort für linienförmige Elemente
                    Parameter(name="km_start", value=item.get("km_start"), process=ProcessEnum.START_KILOMETER, unit=UnitEnum.KILOMETER),
                    Parameter(name="km_end", value=item.get("km_end"), process=ProcessEnum.END_KILOMETER, unit=UnitEnum.KILOMETER),
                ])
            
            # Gemeinsame Standortparameter
            if "gleis_id" in item:
                parameters.extend([
                    Parameter(name="gleis_id", value=item.get("gleis_id"), process=ProcessEnum.TRACK_REFERENCE),
                    Parameter(name="distance_m", value=item.get("distance_m"), process=ProcessEnum.DISTANCE, unit=UnitEnum.METER),
                ])
            
            # IFC-Daten
            if "ifc_data" in item:
                ifc = item["ifc_data"]
                parameters.extend([
                    Parameter(name="ifc_global_id", value=ifc.get("globalId"), process=ProcessEnum.IFC_GLOBAL_ID),
                    Parameter(name="ifc_type", value=ifc.get("type"), process=ProcessEnum.IFC_TYPE),
                    Parameter(name="ifc_material", value=ifc.get("material"), process=ProcessEnum.IFC_MATERIAL),
                    Parameter(name="ifc_category", value=ifc.get("category"), process=ProcessEnum.IFC_CATEGORY),
                ])
            
            # Bauphase
            if "bauphase" in item:
                bp = item["bauphase"]
                parameters.extend([
                    Parameter(name="bauphase_id", value=bp.get("id"), process=ProcessEnum.CONSTRUCTION_PHASE_ID),
                    Parameter(name="bauphase_name", value=bp.get("name"), process=ProcessEnum.CONSTRUCTION_PHASE_NAME),
                    Parameter(name="bauphase_start", value=bp.get("start_date"), process=ProcessEnum.CONSTRUCTION_PHASE_START),
                    Parameter(name="bauphase_end", value=bp.get("end_date"), process=ProcessEnum.CONSTRUCTION_PHASE_END),
                ])
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results

    def _convert_building(self, data: List[Dict[str, Any]]) -> List[InfrastructureElement]:
        """
        Konvertiert Gebäude-Daten des Clients C aus dem FDK-Format.
        
        Args:
            data: Liste von Gebäude-Daten
            
        Returns:
            Liste der konvertierten Gebäude-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", "Gebäude"),
                "uuid": item.get("id"),
                "element_type": ElementType.BUILDING.value,  # Diese Enum muss ggf. noch hinzugefügt werden
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="description", value=item.get("description"), process=ProcessEnum.DESCRIPTION),
                Parameter(name="year_built", value=item.get("year_built"), process=ProcessEnum.YEAR_BUILT),
                Parameter(name="renovation_year", value=item.get("renovation_year"), process=ProcessEnum.RENOVATION_YEAR),
                Parameter(name="floors", value=item.get("floors"), process=ProcessEnum.FLOORS),
            ]
            
            # Koordinaten
            if "coord_x" in item:
                parameters.extend([
                    Parameter(name="coord_x", value=item.get("coord_x"), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                    Parameter(name="coord_y", value=item.get("coord_y"), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                    Parameter(name="coord_z", value=item.get("coord_z"), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                ])
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_generic(self, data: List[Dict[str, Any]], element_type_str: str) -> List[InfrastructureElement]:
        """
        Generischer Konverter für unbekannte Datentypen aus dem FDK-Format.
        
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
            element_type = ElementType.UNDEFINED  # Fallback
        
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Element {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = []
            for key, value in item.items():
                if value is None:
                    continue
                
                # Spezialbehandlung für verschachtelte Daten
                if key == "ifc_data" and isinstance(value, dict):
                    for ifc_key, ifc_value in value.items():
                        ifc_param_name = f"ifc_{ifc_key}"
                        process_enum = None
                        for pe in ProcessEnum:
                            if pe.name.lower() == ifc_param_name.lower() or pe.name.lower() in ifc_param_name.lower():
                                process_enum = pe
                                break
                        parameters.append(Parameter(name=ifc_param_name, value=ifc_value, process=process_enum))
                    continue
                
                if key == "bauphase" and isinstance(value, dict):
                    for bp_key, bp_value in value.items():
                        bp_param_name = f"bauphase_{bp_key}"
                        process_enum = None
                        for pe in ProcessEnum:
                            if pe.name.lower() == bp_param_name.lower() or pe.name.lower() in bp_param_name.lower():
                                process_enum = pe
                                break
                        parameters.append(Parameter(name=bp_param_name, value=bp_value, process=process_enum))
                    continue
                
                # Prozess-Enum versuchen zu finden
                process_enum = None
                for pe in ProcessEnum:
                    # Prüfen auf exakte Übereinstimmung oder Teil des Schlüssels
                    if pe.name.lower() == key.lower() or pe.name.lower() in key.lower():
                        process_enum = pe
                        break
                
                # Einheit bestimmen
                unit = UnitEnum.NONE
                if key.endswith("_mm"):
                    unit = UnitEnum.MILLIMETER
                elif key.endswith("_m"):
                    unit = UnitEnum.METER
                elif key.endswith("_km"):
                    unit = UnitEnum.KILOMETER
                elif key.endswith("_m3"):
                    unit = UnitEnum.CUBIC_METER
                elif key.endswith("_kn"):
                    unit = UnitEnum.KILONEWTON
                
                parameters.append(Parameter(name=key, value=value, process=process_enum, unit=unit))
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results