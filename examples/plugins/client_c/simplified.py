#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Client C Plugin for testing purposes.
This module provides a simplified version of the ClientCPlugin without dependencies.
"""

import logging
import json
import re
import os
import sys
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

class SimplifiedClientCPlugin:
    """
    Simplified plugin for converting Client C data.
    This plugin doesn't depend on PyArm model classes.
    """
    
    def __init__(self):
        self._initialized = False
        self._config = {}
        
    @property
    def name(self) -> str:
        """Name of the plugin."""
        return "SimplifiedClientCPlugin"
        
    @property
    def version(self) -> str:
        """Version of the plugin."""
        return "1.0.0"
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        self._config = config
        self._initialized = True
        return True
        
    def get_supported_element_types(self) -> List[str]:
        """Return supported element types."""
        return [
            "foundation", 
            "mast", 
            "joch",  # Yoke
            "track",
            "curved_track",
            "drainage_pipe",
            "drainage_shaft",
            "fdk"  # Special type for FDK format
        ]
        
    def convert_element_simplified(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Convert data to an element of specified type without using model classes.
        This is a simplified version of convert_element for testing.
        """
        if element_type not in self.get_supported_element_types():
            log.warning(f"Element type {element_type} is not supported")
            return None

        # For FDK format
        if element_type == "fdk":
            return self._convert_fdk(data)

        # For SQL format
        element_data = data.get("data", [])
        project_id = data.get("project_id", "unknown")
        
        if not element_data:
            log.warning(f"No data available for element type {element_type}")
            return None

        # Choose conversion method
        converter_method = getattr(self, f"_convert_{element_type}", None)
        
        if converter_method is None:
            log.warning(f"No conversion method found for {element_type}")
            return None
        
        converted_elements = converter_method(element_data, project_id)
        
        if not converted_elements:
            log.warning(f"Conversion for {element_type} in project {project_id} yielded no elements")
            return None
        
        return {
            "element_type": element_type,
            "project_id": project_id,
            "elements": converted_elements,
            "converted_by": self.name
        }

    def _convert_foundation(self, foundation_data: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
        """
        Convert foundation data to canonical model.
        """
        converted_foundations = []
        
        for foundation in foundation_data:
            try:
                # Extract data from foundation dictionary
                foundation_id = self._extract_str(foundation, "id")
                name = self._extract_str(foundation, "name", f"Foundation-{foundation_id}")
                
                # Extract position coordinates (convert mm to m)
                x = self._extract_float(foundation, "x_coord") / 1000.0
                y = self._extract_float(foundation, "y_coord") / 1000.0
                z = self._extract_float(foundation, "z_coord", 0.0) / 1000.0
                
                # Extract dimensions (convert mm to m)
                length = self._extract_float(foundation, "length") / 1000.0
                width = self._extract_float(foundation, "width") / 1000.0
                height = self._extract_float(foundation, "height", 0.0) / 1000.0
                
                # Create element with components
                foundation_element = {
                    "uuid": str(uuid.uuid4()),
                    "name": name,
                    "element_type": "foundation",
                    "components": {
                        "location": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "dimension": {
                            "length": length,
                            "width": width,
                            "height": height
                        }
                    },
                    "metadata": {
                        "source": "client_c_sql",
                        "client_id": foundation_id,
                        "project_id": project_id,
                        "conversion_date": datetime.now().isoformat()
                    }
                }
                
                converted_foundations.append(foundation_element)
                
            except Exception as e:
                log.warning(f"Error converting foundation {foundation.get('id', 'unknown')}: {e}")
                continue
                
        log.info(f"{len(converted_foundations)} foundation elements converted")
        return converted_foundations

    def _convert_mast(self, mast_data: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
        """
        Convert mast data to canonical model.
        """
        converted_masts = []
        
        for mast in mast_data:
            try:
                # Extract data from mast dictionary
                mast_id = self._extract_str(mast, "id")
                name = self._extract_str(mast, "name", f"Mast-{mast_id}")
                
                # Extract position coordinates (convert mm to m)
                x = self._extract_float(mast, "x_coord") / 1000.0
                y = self._extract_float(mast, "y_coord") / 1000.0
                z = self._extract_float(mast, "z_coord", 0.0) / 1000.0
                
                # Extract dimensions (convert mm to m)
                length = self._extract_float(mast, "length", 0.3) / 1000.0
                width = self._extract_float(mast, "width", 0.3) / 1000.0
                height = self._extract_float(mast, "height") / 1000.0
                
                # Extract foundation reference
                foundation_id = self._extract_str(mast, "foundation_id", None)
                
                # Create element with components
                mast_element = {
                    "uuid": str(uuid.uuid4()),
                    "name": name,
                    "element_type": "mast",
                    "components": {
                        "location": {
                            "x": x,
                            "y": y,
                            "z": z
                        },
                        "dimension": {
                            "length": length,
                            "width": width,
                            "height": height
                        }
                    },
                    "metadata": {
                        "source": "client_c_sql",
                        "client_id": mast_id,
                        "project_id": project_id,
                        "conversion_date": datetime.now().isoformat()
                    }
                }
                
                # Add reference to foundation if available
                if foundation_id:
                    mast_element["components"]["reference"] = {
                        "foundation": foundation_id
                    }
                
                converted_masts.append(mast_element)
                
            except Exception as e:
                log.warning(f"Error converting mast {mast.get('id', 'unknown')}: {e}")
                continue
                
        log.info(f"{len(converted_masts)} mast elements converted")
        return converted_masts

    def _convert_fdk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert FDK data format to canonical model.
        """
        # For testing, we'll use either file path or direct JSON data
        fdk_data = None
        if "fdk_file" in data and os.path.exists(data["fdk_file"]):
            with open(data["fdk_file"], 'r', encoding='utf-8') as f:
                fdk_data = json.load(f)
        elif isinstance(data, dict) and "elements" not in data:  # Direct JSON data
            fdk_data = data

        if not fdk_data:
            log.error("No valid FDK data found")
            return None

        # Check if we have anlagenDaten structure
        if "anlagenDaten" in fdk_data:
            anlagen_daten = fdk_data["anlagenDaten"]
        else:
            anlagen_daten = fdk_data

        # Extract project info
        metadata = anlagen_daten.get("meta", {})
        project_id = metadata.get("projektNummer", "unknown")
        elements = []
        
        # Process tracks (gleisAnlagen)
        tracks = anlagen_daten.get("gleisAnlagen", [])
        for track in tracks:
            try:
                track_element = self._process_fdk_track(track, project_id)
                if track_element:
                    elements.append(track_element)
            except Exception as e:
                log.warning(f"Error processing FDK track: {e}")

        # Process masts
        masts = anlagen_daten.get("masten", [])
        for mast in masts:
            try:
                mast_element = self._process_fdk_mast(mast, project_id)
                if mast_element:
                    elements.append(mast_element)
            except Exception as e:
                log.warning(f"Error processing FDK mast: {e}")

        # Process foundations
        foundations = anlagen_daten.get("fundamente", [])
        for foundation in foundations:
            try:
                foundation_element = self._process_fdk_foundation(foundation, project_id)
                if foundation_element:
                    elements.append(foundation_element)
            except Exception as e:
                log.warning(f"Error processing FDK foundation: {e}")

        # Process drainage systems
        drainage_systems = anlagen_daten.get("entwässerungssysteme", [])
        for system in drainage_systems:
            try:
                # Process pipes
                for pipe in system.get("leitungen", []):
                    pipe_element = self._process_fdk_drainage_pipe(pipe, project_id)
                    if pipe_element:
                        elements.append(pipe_element)
                
                # Process shafts
                for shaft in system.get("schächte", []):
                    shaft_element = self._process_fdk_drainage_shaft(shaft, project_id)
                    if shaft_element:
                        elements.append(shaft_element)
            except Exception as e:
                log.warning(f"Error processing FDK drainage system: {e}")
        
        return {
            "element_type": "fdk",
            "project_id": project_id,
            "elements": elements,
            "converted_by": self.name,
            "metadata": {
                "source": "client_c_fdk",
                "version": metadata.get("version", "unknown"),
                "project_name": metadata.get("projektName", "unknown"),
                "conversion_date": datetime.now().isoformat()
            }
        }

    def _process_fdk_track(self, track: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Process FDK track data.
        """
        track_id = track.get("id", str(uuid.uuid4()))
        name = track.get("name", f"Track-{track_id}")
        
        # Get geometry data
        geometry = track.get("geometrie", {})
        is_curved = "kurve" in geometry
        
        if is_curved:
            # For curved track
            curve = geometry.get("kurve", {})
            element_type = "curved_track"
            
            # Get starting point (convert mm to m)
            start = curve.get("startPunkt", {})
            x = float(start.get("x", 0)) / 1000.0
            y = float(start.get("y", 0)) / 1000.0
            z = float(start.get("z", 0)) / 1000.0
            
            # Get curve parameters
            radius = float(curve.get("radius", 0)) / 1000.0
            angle = float(curve.get("winkel", 0))
            length = float(curve.get("länge", 0)) / 1000.0
            
            track_element = {
                "uuid": str(uuid.uuid4()),
                "name": name,
                "element_type": element_type,
                "components": {
                    "location": {
                        "x": x,
                        "y": y,
                        "z": z
                    },
                    "dimension": {
                        "radius": radius,
                        "angle": angle,
                        "length": length
                    }
                },
                "metadata": {
                    "source": "client_c_fdk",
                    "client_id": track_id,
                    "project_id": project_id,
                    "conversion_date": datetime.now().isoformat(),
                    "ifc_data": track.get("ifc", {})
                }
            }
        else:
            # For straight track
            line = geometry.get("linie", {})
            element_type = "track"
            
            # Get starting point (convert mm to m)
            start = line.get("startPunkt", {})
            x = float(start.get("x", 0)) / 1000.0
            y = float(start.get("y", 0)) / 1000.0
            z = float(start.get("z", 0)) / 1000.0
            
            # Get end point
            end = line.get("endPunkt", {})
            end_x = float(end.get("x", 0)) / 1000.0
            end_y = float(end.get("y", 0)) / 1000.0
            end_z = float(end.get("z", 0)) / 1000.0
            
            # Calculate length and direction
            from math import sqrt
            length = sqrt((end_x - x)**2 + (end_y - y)**2 + (end_z - z)**2)
            
            track_element = {
                "uuid": str(uuid.uuid4()),
                "name": name,
                "element_type": element_type,
                "components": {
                    "location": {
                        "x": x,
                        "y": y,
                        "z": z
                    },
                    "dimension": {
                        "length": length,
                        "end_x": end_x,
                        "end_y": end_y,
                        "end_z": end_z
                    }
                },
                "metadata": {
                    "source": "client_c_fdk",
                    "client_id": track_id,
                    "project_id": project_id,
                    "conversion_date": datetime.now().isoformat(),
                    "ifc_data": track.get("ifc", {}),
                    "bauphasen": track.get("bauphasen", [])
                }
            }
        
        return track_element

    def _process_fdk_mast(self, mast: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Process FDK mast data.
        """
        mast_id = mast.get("id", str(uuid.uuid4()))
        name = mast.get("name", f"Mast-{mast_id}")
        
        # Get position (convert mm to m)
        position = mast.get("position", {})
        x = float(position.get("x", 0)) / 1000.0
        y = float(position.get("y", 0)) / 1000.0
        z = float(position.get("z", 0)) / 1000.0
        
        # Get dimensions (convert mm to m)
        dimensions = mast.get("abmessungen", {})
        height = float(dimensions.get("höhe", 0)) / 1000.0
        width = float(dimensions.get("breite", 0.3)) / 1000.0
        depth = float(dimensions.get("tiefe", 0.3)) / 1000.0
        
        # Get foundation reference
        foundation_id = mast.get("fundamentID")
        
        mast_element = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "element_type": "mast",
            "components": {
                "location": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "dimension": {
                    "height": height,
                    "width": width,
                    "length": depth
                }
            },
            "metadata": {
                "source": "client_c_fdk",
                "client_id": mast_id,
                "project_id": project_id,
                "conversion_date": datetime.now().isoformat(),
                "ifc_data": mast.get("ifc", {}),
                "bauphasen": mast.get("bauphasen", [])
            }
        }
        
        # Add reference to foundation if available
        if foundation_id:
            mast_element["components"]["reference"] = {
                "foundation": foundation_id
            }
        
        return mast_element

    def _process_fdk_foundation(self, foundation: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Process FDK foundation data.
        """
        foundation_id = foundation.get("id", str(uuid.uuid4()))
        name = foundation.get("name", f"Foundation-{foundation_id}")
        
        # Get position (convert mm to m)
        position = foundation.get("position", {})
        x = float(position.get("x", 0)) / 1000.0
        y = float(position.get("y", 0)) / 1000.0
        z = float(position.get("z", 0)) / 1000.0
        
        # Get dimensions (convert mm to m)
        dimensions = foundation.get("abmessungen", {})
        length = float(dimensions.get("länge", 0)) / 1000.0
        width = float(dimensions.get("breite", 0)) / 1000.0
        height = float(dimensions.get("tiefe", 0)) / 1000.0
        
        foundation_element = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "element_type": "foundation",
            "components": {
                "location": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "dimension": {
                    "length": length,
                    "width": width,
                    "height": height
                }
            },
            "metadata": {
                "source": "client_c_fdk",
                "client_id": foundation_id,
                "project_id": project_id,
                "conversion_date": datetime.now().isoformat(),
                "ifc_data": foundation.get("ifc", {}),
                "bauphasen": foundation.get("bauphasen", [])
            }
        }
        
        return foundation_element

    def _process_fdk_drainage_pipe(self, pipe: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Process FDK drainage pipe data.
        """
        pipe_id = pipe.get("id", str(uuid.uuid4()))
        name = pipe.get("name", f"DrainagePipe-{pipe_id}")
        
        # Get start and end points (convert mm to m)
        start = pipe.get("startPunkt", {})
        start_x = float(start.get("x", 0)) / 1000.0
        start_y = float(start.get("y", 0)) / 1000.0
        start_z = float(start.get("z", 0)) / 1000.0
        
        end = pipe.get("endPunkt", {})
        end_x = float(end.get("x", 0)) / 1000.0
        end_y = float(end.get("y", 0)) / 1000.0
        end_z = float(end.get("z", 0)) / 1000.0
        
        # Calculate length
        from math import sqrt
        length = sqrt((end_x - start_x)**2 + (end_y - start_y)**2 + (end_z - start_z)**2)
        
        # Get diameter (convert mm to m)
        diameter = float(pipe.get("durchmesser", 0)) / 1000.0
        
        pipe_element = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "element_type": "drainage_pipe",
            "components": {
                "location": {
                    "x": start_x,
                    "y": start_y,
                    "z": start_z
                },
                "dimension": {
                    "length": length,
                    "end_x": end_x,
                    "end_y": end_y,
                    "end_z": end_z,
                    "diameter": diameter
                }
            },
            "metadata": {
                "source": "client_c_fdk",
                "client_id": pipe_id,
                "project_id": project_id,
                "conversion_date": datetime.now().isoformat(),
                "ifc_data": pipe.get("ifc", {}),
                "bauphasen": pipe.get("bauphasen", [])
            }
        }
        
        # Add references to shafts if available
        start_shaft_id = pipe.get("startSchachtID")
        end_shaft_id = pipe.get("endSchachtID")
        
        if start_shaft_id or end_shaft_id:
            references = {}
            if start_shaft_id:
                references["start_shaft"] = start_shaft_id
            if end_shaft_id:
                references["end_shaft"] = end_shaft_id
                
            pipe_element["components"]["reference"] = references
        
        return pipe_element

    def _process_fdk_drainage_shaft(self, shaft: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Process FDK drainage shaft data.
        """
        shaft_id = shaft.get("id", str(uuid.uuid4()))
        name = shaft.get("name", f"DrainageShaft-{shaft_id}")
        
        # Get position (convert mm to m)
        position = shaft.get("position", {})
        x = float(position.get("x", 0)) / 1000.0
        y = float(position.get("y", 0)) / 1000.0
        z = float(position.get("z", 0)) / 1000.0
        
        # Get dimensions (convert mm to m)
        diameter = float(shaft.get("durchmesser", 0)) / 1000.0
        depth = float(shaft.get("tiefe", 0)) / 1000.0
        
        shaft_element = {
            "uuid": str(uuid.uuid4()),
            "name": name,
            "element_type": "drainage_shaft",
            "components": {
                "location": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "dimension": {
                    "diameter": diameter,
                    "depth": depth
                }
            },
            "metadata": {
                "source": "client_c_fdk",
                "client_id": shaft_id,
                "project_id": project_id,
                "conversion_date": datetime.now().isoformat(),
                "ifc_data": shaft.get("ifc", {}),
                "bauphasen": shaft.get("bauphasen", [])
            }
        }
        
        return shaft_element

    # Helper methods for data extraction
    def _extract_str(self, data: Dict[str, Any], key: str, default: Optional[str] = None) -> str:
        """
        Extract string value from data.
        """
        value = data.get(key, default)
        if value is None:
            raise ValueError(f"Required parameter {key} is missing")
        
        # Remove quotes if present
        if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
            
        return str(value)
        
    def _extract_float(self, data: Dict[str, Any], key: str, default: Optional[float] = None) -> float:
        """
        Extract float value from data.
        """
        value = data.get(key, default)
        if value is None:
            raise ValueError(f"Required parameter {key} is missing")
            
        # If string, convert to float
        if isinstance(value, str):
            # Remove quotes if present
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"Cannot convert {key} value '{value}' to float")
                
        return float(value)