"""
Client B spezifischer Datenkonverter.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID

from ...code.common.enums.process_enums import ProcessEnum, ElementType, UnitEnum
from ...code.common.models.base_models import Parameter, InfrastructureElement
from ...code.common.utils.factory import create_element


class ClientBConverter:
    """
    Konverter für Daten des Clients B.
    Konvertiert client-spezifische Daten in das kanonische Format.
    """
    
    @property
    def name(self) -> str:
        return "ClientBConverter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def supported_types(self) -> List[str]:
        return ["foundation", "mast", "drainage"]
    
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
            return converter_method(raw_data, project_id)
        
        # Fallback auf generischen Konverter
        return self._convert_generic(raw_data, element_type)
    
    def _convert_foundation(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Fundament-Daten des Clients B.
        
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
                "name": item.get("bezeichnung", f"Fundament {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.FOUNDATION.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="Typ", value=item.get("fundament_typ"), process=ProcessEnum.FOUNDATION_TYPE),
                Parameter(name="X", value=float(item.get("x_wert", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Y", value=float(item.get("y_wert", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("z_wert", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Breite", value=float(item.get("breite_m", 0)), process=ProcessEnum.FOUNDATION_WIDTH, unit=UnitEnum.METER),
                Parameter(name="Tiefe", value=float(item.get("tiefe_m", 0)), process=ProcessEnum.FOUNDATION_DEPTH, unit=UnitEnum.METER),
                Parameter(name="Höhe", value=float(item.get("hoehe_m", 0)), process=ProcessEnum.FOUNDATION_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("material"), process=ProcessEnum.MATERIAL),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_mast(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Mast-Daten des Clients B.
        
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
                "name": item.get("bezeichnung", f"Mast {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.MAST.value,
                "parameters": []
            }
            
            # Referenz zum Fundament, falls vorhanden
            if "fundament_id" in item:
                element_data["foundation_uuid"] = item.get("fundament_id")
            
            # Parameter erstellen
            parameters = [
                Parameter(name="ID", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="Typ", value=item.get("mast_typ"), process=ProcessEnum.MAST_TYPE),
                Parameter(name="X", value=float(item.get("x_wert", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Y", value=float(item.get("y_wert", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("z_wert", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Höhe", value=float(item.get("hoehe_m", 0)), process=ProcessEnum.MAST_HEIGHT, unit=UnitEnum.METER),
                Parameter(name="Azimut", value=float(item.get("azimut_grad", 0)), process=ProcessEnum.AZIMUTH, unit=UnitEnum.DEGREE),
                Parameter(name="Material", value=item.get("material"), process=ProcessEnum.MATERIAL),
                Parameter(name="Profiltyp", value=item.get("profil_typ"), process=ProcessEnum.MAST_PROFILE_TYPE),
            ]
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_drainage(self, data: List[Dict[str, Any]], project_id: str) -> List[InfrastructureElement]:
        """
        Konvertiert Entwässerungs-Daten des Clients B.
        
        Args:
            data: Liste von Entwässerungs-Daten
            project_id: ID des Projekts
            
        Returns:
            Liste der konvertierten Entwässerungs-Elemente
        """
        results = []
        for item in data:
            # Elementtyp bestimmen
            if item.get("typ", "").lower() == "pipe":
                element_type = ElementType.DRAINAGE_PIPE.value
            elif item.get("typ", "").lower() == "shaft":
                element_type = ElementType.DRAINAGE_SHAFT.value
            else:
                continue  # Unbekannter Typ
            
            # Grundlegende Attribute
            element_data = {
                "name": item.get("bezeichnung", f"Entwässerung {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type,
                "parameters": []
            }
            
            # Gemeinsame Parameter
            common_parameters = [
                Parameter(name="ID", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="X", value=float(item.get("x_wert", 0)), process=ProcessEnum.X_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Y", value=float(item.get("y_wert", 0)), process=ProcessEnum.Y_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Z", value=float(item.get("z_wert", 0)), process=ProcessEnum.Z_COORDINATE, unit=UnitEnum.METER),
                Parameter(name="Material", value=item.get("material"), process=ProcessEnum.MATERIAL),
            ]
            
            # Spezifische Parameter je nach Typ
            if element_type == ElementType.DRAINAGE_PIPE.value:
                # Konvertiere Durchmesser von mm nach m
                diameter_mm = float(item.get("durchmesser_mm", 0))
                diameter_m = diameter_mm / 1000.0  # mm zu m
                
                pipe_parameters = [
                    Parameter(name="X2", value=float(item.get("x_wert_ende", 0)), process=ProcessEnum.X_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="Y2", value=float(item.get("y_wert_ende", 0)), process=ProcessEnum.Y_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="Z2", value=float(item.get("z_wert_ende", 0)), process=ProcessEnum.Z_COORDINATE_END, unit=UnitEnum.METER),
                    Parameter(name="Durchmesser", value=diameter_m, process=ProcessEnum.PIPE_DIAMETER, unit=UnitEnum.METER),
                    Parameter(name="Gefälle", value=float(item.get("gefaelle_promille", 0)), process=ProcessEnum.PIPE_SLOPE, unit=UnitEnum.PROMILLE),
                ]
                parameters = common_parameters + pipe_parameters
            else:  # DRAINAGE_SHAFT
                # Konvertiere Durchmesser von mm nach m
                diameter_mm = float(item.get("durchmesser_mm", 0))
                diameter_m = diameter_mm / 1000.0  # mm zu m
                
                shaft_parameters = [
                    Parameter(name="Durchmesser", value=diameter_m, process=ProcessEnum.SHAFT_DIAMETER, unit=UnitEnum.METER),
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
            if et.value in element_type_str.lower() or element_type_str.lower() in et.value:
                element_type = et
                break
        
        if not element_type:
            element_type = ElementType.UNDEFINED  # Fallback
        
        results = []
        for item in data:
            # ID und Name bestimmen
            id_value = item.get("id", None)
            if id_value is None:
                id_value = item.get("ID", None)
            
            name = item.get("bezeichnung", None)
            if name is None:
                name = item.get("Bezeichnung", None)
            if name is None:
                name = f"Element {id_value or 'Unknown'}"
            
            # Grundlegende Attribute
            element_data = {
                "name": name,
                "uuid": id_value,
                "element_type": element_type.value,
                "parameters": []
            }
            
            # Parameter erstellen
            parameters = []
            for key, value in item.items():
                # Prozess-Enum versuchen zu finden
                process_enum = None
                
                # Mapping von ClientB-Feldnamen zu ProcessEnum
                field_mapping = {
                    "id": ProcessEnum.UUID,
                    "bezeichnung": ProcessEnum.NAME,
                    "x_wert": ProcessEnum.X_COORDINATE,
                    "y_wert": ProcessEnum.Y_COORDINATE,
                    "z_wert": ProcessEnum.Z_COORDINATE,
                    "x_wert_ende": ProcessEnum.X_COORDINATE_END,
                    "y_wert_ende": ProcessEnum.Y_COORDINATE_END,
                    "z_wert_ende": ProcessEnum.Z_COORDINATE_END,
                    "material": ProcessEnum.MATERIAL,
                    "breite_m": ProcessEnum.WIDTH,
                    "hoehe_m": ProcessEnum.HEIGHT,
                    "tiefe_m": ProcessEnum.DEPTH,
                    "durchmesser_mm": ProcessEnum.DIAMETER,
                    "azimut_grad": ProcessEnum.AZIMUTH,
                }
                
                if key in field_mapping:
                    process_enum = field_mapping[key]
                else:
                    # Versuche ProcessEnum anhand des Namens zu finden
                    for pe in ProcessEnum:
                        if pe.name.lower() in key.lower() or key.lower() in pe.name.lower():
                            process_enum = pe
                            break
                
                # Typumwandlung, wenn nötig
                if isinstance(value, str):
                    if value.replace('.', '', 1).isdigit():
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    elif value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                
                # Einheit bestimmen
                unit = UnitEnum.NONE
                if process_enum in [ProcessEnum.X_COORDINATE, ProcessEnum.Y_COORDINATE, ProcessEnum.Z_COORDINATE,
                                    ProcessEnum.X_COORDINATE_END, ProcessEnum.Y_COORDINATE_END, ProcessEnum.Z_COORDINATE_END]:
                    unit = UnitEnum.METER
                elif process_enum == ProcessEnum.AZIMUTH:
                    unit = UnitEnum.DEGREE
                elif "breite_m" in key or "hoehe_m" in key or "tiefe_m" in key:
                    unit = UnitEnum.METER
                elif "durchmesser_mm" in key:
                    unit = UnitEnum.MILLIMETER
                elif "gefaelle_promille" in key:
                    unit = UnitEnum.PROMILLE
                
                parameters.append(Parameter(name=key, value=value, process=process_enum, unit=unit))
            
            element_data["parameters"] = parameters
            results.append(create_element(element_data))
        
        return results
    
    def _convert_decimal_format(self, value: str) -> float:
        """
        Konvertiert einen String mit deutschem Dezimalformat zu float.
        
        Args:
            value: Zahlwert als String (z.B. "1,23")
            
        Returns:
            Konvertierter Wert als float
        """
        if isinstance(value, str) and ',' in value:
            return float(value.replace(',', '.'))
        return float(value)