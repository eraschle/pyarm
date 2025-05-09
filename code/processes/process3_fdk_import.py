"""
Process zur Verarbeitung und Import von FDK-Daten für Client C.
Implementiert einen spezialisierten Prozess für die Verarbeitung von FDK-Daten mit
Unterstützung für IFC-Daten und Bauphasen-Informationen.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import logging

# Füge das Stammverzeichnis zum Pythonpfad hinzu, um absolute Importe zu ermöglichen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from code.common.enums.process_enums import ElementType
from code.services.visualization_service import VisualizationService
from code.repository.json_repository import JsonElementRepository

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FdkImportProcess:
    """
    Prozess zur Verarbeitung und Import von FDK-Daten des Clients C.
    
    Dieser Prozess:
    1. Liest FDK-JSON-Daten aus einer angegebenen Datei
    2. Extrahiert und verarbeitet IFC-Daten und Bauphasen-Informationen
    3. Konvertiert die Daten in das kanonische Datenmodell
    4. Speichert die Daten im Repository und generiert optionale Visualisierungen
    """
    
    def __init__(self, fdk_file_path: str, repository_path: str, output_path: Optional[str] = None):
        """
        Initialisiert den FDK-Import-Prozess.
        
        Args:
            fdk_file_path: Pfad zur FDK-JSON-Datei
            repository_path: Pfad zum Repository
            output_path: Optionaler Pfad für Ausgabedaten
        """
        self.fdk_file_path = fdk_file_path
        self.repository_path = repository_path
        self.output_path = output_path or os.path.join(os.path.dirname(repository_path), "output")
        self.visualization_service = VisualizationService(repository_path)
        
        # FDK-spezifische Importe
        from ...clients.clientC.code.fdk_reader import ClientCFdkReader
        from ...clients.clientC.code.fdk_converter import ClientCFdkConverter
        
        self.reader = ClientCFdkReader()
        self.converter = ClientCFdkConverter()
    
    def run(self) -> Dict[str, Any]:
        """
        Führt den FDK-Import-Prozess aus.
        
        Returns:
            Dictionary mit Informationen zur Prozessausführung
        """
        logger.info(f"Starte FDK-Import-Prozess für Datei: {self.fdk_file_path}")
        
        # Schritt 1: FDK-Daten lesen
        try:
            fdk_data = self.reader.read_data(self.fdk_file_path)
            if not fdk_data:
                logger.error("Keine FDK-Daten gefunden oder Format nicht unterstützt.")
                return {"status": "error", "message": "Keine gültigen FDK-Daten gefunden."}
            
            logger.info(f"FDK-Daten erfolgreich gelesen. Gefundene Elementtypen: {self.reader.get_element_types(fdk_data)}")
        except Exception as e:
            logger.error(f"Fehler beim Lesen der FDK-Daten: {str(e)}")
            return {"status": "error", "message": f"Fehler beim Lesen der FDK-Daten: {str(e)}"}
        
        # Schritt 2: Prüfen, ob Metadaten und Bauphasen vorhanden sind
        meta_info = {}
        if "meta" in fdk_data and fdk_data["meta"]:
            meta_info = fdk_data["meta"]
            logger.info(f"Metadaten gefunden: Version {meta_info.get('version', 'unbekannt')}, Projekt: {meta_info.get('projektName', 'unbekannt')}")
        
        bauphasen_info = []
        if "bauphasen" in fdk_data and fdk_data["bauphasen"]:
            bauphasen_info = fdk_data["bauphasen"]
            logger.info(f"{len(bauphasen_info)} Bauphasen gefunden")
        
        # Schritt 3: Daten konvertieren und in Repository speichern
        repository = JsonElementRepository(self.repository_path)
        
        conversion_stats = {
            "total_elements": 0,
            "converted_elements": 0,
            "by_type": {}
        }
        
        # Alle Elementtypen verarbeiten
        for element_type in self.reader.get_element_types(fdk_data):
            if element_type in ["bauphasen", "meta"]:
                continue  # Metadaten überspringen
                
            # Daten für den aktuellen Typ extrahieren
            type_data = self.reader.get_data_for_type(fdk_data, element_type)
            raw_elements = type_data.get("data", [])
            conversion_stats["by_type"][element_type] = {
                "raw_count": len(raw_elements),
                "converted_count": 0
            }
            conversion_stats["total_elements"] += len(raw_elements)
            
            # Konvertieren
            try:
                if self.converter.can_convert(type_data):
                    converted_elements = self.converter.convert(type_data)
                    logger.info(f"{len(converted_elements)} Elemente vom Typ {element_type} konvertiert")
                    conversion_stats["by_type"][element_type]["converted_count"] = len(converted_elements)
                    conversion_stats["converted_elements"] += len(converted_elements)
                    
                    # In Repository speichern
                    repository.save_all(converted_elements)
                else:
                    logger.warning(f"Konverter unterstützt Elementtyp {element_type} nicht")
            except Exception as e:
                logger.error(f"Fehler bei der Konvertierung von {element_type}: {str(e)}")
        
        # Schritt 4: Metadaten und Bauphasen in separate JSON-Datei speichern
        if meta_info or bauphasen_info:
            metadata_output = os.path.join(self.output_path, "fdk_metadata.json")
            os.makedirs(os.path.dirname(metadata_output), exist_ok=True)
            
            with open(metadata_output, "w", encoding="utf-8") as f:
                json.dump({
                    "meta": meta_info,
                    "bauphasen": bauphasen_info
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadaten und Bauphasen in {metadata_output} gespeichert")
        
        # Schritt 5: Optionalen Visualisierungsprozess starten
        if self.output_path:
            try:
                # Einfache Visualisierung der importierten Elemente
                visualization_output = os.path.join(self.output_path, "fdk_visualization.json")
                visualization_data = self._generate_visualization_data(repository)
                
                with open(visualization_output, "w", encoding="utf-8") as f:
                    json.dump(visualization_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Visualisierungsdaten in {visualization_output} gespeichert")
            except Exception as e:
                logger.error(f"Fehler bei der Generierung der Visualisierung: {str(e)}")
        
        logger.info("FDK-Import-Prozess abgeschlossen")
        return {
            "status": "success",
            "conversion_stats": conversion_stats,
            "metadata": {
                "project": meta_info.get("projektName", ""),
                "version": meta_info.get("version", ""),
                "construction_phases": len(bauphasen_info)
            }
        }
    
    def _generate_visualization_data(self, repository: JsonElementRepository) -> Dict[str, Any]:
        """
        Generiert eine einfache Visualisierung der importierten FDK-Daten.
        
        Args:
            repository: Repository mit den importierten Elementen
            
        Returns:
            Visualisierungsdaten
        """
        # Alle importierten Elemente aus dem Repository abrufen
        elements = repository.get_all()
        
        # Nach Typen gruppieren
        elements_by_type = {}
        for element in elements:
            element_type = element.element_type.value
            if element_type not in elements_by_type:
                elements_by_type[element_type] = []
            elements_by_type[element_type].append(element)
        
        # Zählung nach Typen
        type_counts = {et: len(els) for et, els in elements_by_type.items()}
        
        # Einfache Visualisierungsdaten erstellen
        visualization_data = {
            "summary": {
                "total_elements": len(elements),
                "type_counts": type_counts
            },
            "elements_by_type": {}
        }
        
        # Alle Elementtypen verarbeiten
        for element_type, elements_list in elements_by_type.items():
            element_data = []
            for element in elements_list:
                # Basisinformationen extrahieren
                element_info = {
                    "id": str(element.uuid),
                    "name": element.name,
                    "type": element.element_type.value
                }
                
                # IFC-Daten extrahieren, falls vorhanden
                ifc_global_id = element.get_param("IFC_GLOBAL_ID") or element.get_param("ifc_global_id")
                if ifc_global_id:
                    element_info["ifc"] = {
                        "globalId": ifc_global_id,
                        "type": element.get_param("IFC_TYPE") or element.get_param("ifc_type"),
                        "category": element.get_param("IFC_CATEGORY") or element.get_param("ifc_category")
                    }
                
                # Bauphasendaten extrahieren, falls vorhanden
                bauphase_id = element.get_param("CONSTRUCTION_PHASE_ID") or element.get_param("bauphase_id")
                if bauphase_id:
                    element_info["construction_phase"] = {
                        "id": bauphase_id,
                        "name": element.get_param("CONSTRUCTION_PHASE_NAME") or element.get_param("bauphase_name"),
                        "start": element.get_param("CONSTRUCTION_PHASE_START") or element.get_param("bauphase_start"),
                        "end": element.get_param("CONSTRUCTION_PHASE_END") or element.get_param("bauphase_end")
                    }
                
                element_data.append(element_info)
            
            visualization_data["elements_by_type"][element_type] = element_data
        
        return visualization_data