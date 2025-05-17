#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Client C data from SQL and FDK formats.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional, cast
import re
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# Add src directory to Python path if not already there
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import plugin module
plugins_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
if plugins_path not in sys.path:
    sys.path.insert(0, plugins_path)

# Direct imports for testing without requiring installation
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins"))

# Simplified implementation for testing purposes
class SimplePluginAdapter:
    def __init__(self, plugin):
        self.plugin = plugin

    def __getattr__(self, name):
        return getattr(self.plugin, name)

    def convert_element(self, data, element_type):
        """Adapter method to convert elements without requiring model classes."""
        result = self.plugin.convert_element_simplified(data, element_type)
        return result

# Import the plugin directly from simplified implementation
from plugins.client_c.simplified import SimplifiedClientCPlugin as ClientCPlugin

# Define a simple interface for testing
class PluginInterface:
    def name(self) -> str: ...
    def version(self) -> str: ...
    def initialize(self, config): ...
    def get_supported_element_types(self) -> List[str]: ...
    def convert_element(self, data, element_type): ...

def main():
    """
    Main function to import Client C data.
    """
    parser = argparse.ArgumentParser(description="Import Client C data from SQL and FDK formats.")
    parser.add_argument("--input_dir", required=True, help="Directory containing client C data")
    parser.add_argument("--output_dir", required=True, help="Directory for output files")
    parser.add_argument("--format", choices=["sql", "fdk", "both"], default="both", 
                        help="Format to import (sql, fdk, or both)")
    parser.add_argument("--project", help="Project name or ID (optional)")
    parser.add_argument("--logfile", help="Log file path (optional)")
    
    args = parser.parse_args()
    
    # Setup file logging if specified
    if args.logfile:
        file_handler = logging.FileHandler(args.logfile)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        log.addHandler(file_handler)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize Client C plugin directly
    plugin = ClientCPlugin()
    
    log.info(f"Initialisiere Plugin: {plugin.name} v{plugin.version}")
    plugin.initialize({})
    
    # Process data based on format
    if args.format in ["sql", "both"]:
        import_sql_data(args.input_dir, args.output_dir, args.project, plugin)
        
    if args.format in ["fdk", "both"]:
        import_fdk_data(args.input_dir, args.output_dir, plugin)
    
    log.info(f"Import abgeschlossen. Ergebnisse in: {args.output_dir}")

def import_sql_data(input_dir: str, output_dir: str, project_id: Optional[str], plugin):
    """
    Import data from SQL format.
    """
    # Find SQL files
    sql_file = None
    if project_id:
        # Look for project-specific SQL file
        potential_path = os.path.join(input_dir, "clientC", "projects", f"{project_id}.sql")
        if os.path.exists(potential_path):
            sql_file = potential_path
    
    # If no project-specific file found, look for infrastructure.sql
    if not sql_file:
        potential_path = os.path.join(input_dir, "clientC", "projects", "infrastructure.sql")
        if os.path.exists(potential_path):
            sql_file = potential_path
    
    if not sql_file:
        log.error(f"Keine SQL-Datei gefunden in {input_dir}")
        return
    
    log.info(f"Verarbeite SQL-Datei: {sql_file}")
    
    # Extract data from SQL file
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Extract foundation data
        foundation_data = extract_foundation_data(sql_content)
        log.info(f"{len(foundation_data)} Foundation-Datensätze extrahiert")
        
        if foundation_data:
            # Convert foundation data
            data = {
                "data": foundation_data,
                "project_id": project_id or "unknown"
            }
            converted = plugin.convert_element_simplified(data, "foundation")
            
            if converted:
                # Save converted data
                output_file = os.path.join(output_dir, "clientC_foundation.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(converted, f, indent=2)
                log.info(f"Foundation-Daten konvertiert und in {output_file} gespeichert")
            else:
                log.error("Konvertierung der Foundation-Daten fehlgeschlagen")
        
        # TODO: Add support for other element types (mast, joch, drainage, etc.)
        
    except Exception as e:
        log.error(f"Fehler bei der Verarbeitung der SQL-Datei: {e}")

def import_fdk_data(input_dir: str, output_dir: str, plugin):
    """
    Import data from FDK format.
    """
    # Find FDK files
    fdk_file = os.path.join(input_dir, "clientC", "FDK", "anlagen_daten.json")
    if not os.path.exists(fdk_file):
        log.error(f"FDK-Datei nicht gefunden: {fdk_file}")
        return
    
    log.info(f"Verarbeite FDK-Datei: {fdk_file}")
    
    try:
        with open(fdk_file, 'r', encoding='utf-8') as f:
            fdk_data = json.load(f)
        
        # Convert FDK data
        converted = plugin.convert_element_simplified(fdk_data, "fdk")
        
        if converted:
            # Save converted data
            output_file = os.path.join(output_dir, "client_c_fdk.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(converted, f, indent=2)
            
            # Generate visualization data
            visualization_data = generate_visualization(converted)
            visualization_file = os.path.join(output_dir, "client_c_fdk_visualization.json")
            with open(visualization_file, 'w', encoding='utf-8') as f:
                json.dump(visualization_data, f, indent=2)
                
            log.info(f"FDK-Daten konvertiert und in {output_file} gespeichert")
            log.info(f"Visualisierungsdaten in {visualization_file} gespeichert")
        else:
            log.error("Konvertierung der FDK-Daten fehlgeschlagen")
            
    except Exception as e:
        log.error(f"Fehler bei der Verarbeitung der FDK-Datei: {e}")

def extract_foundation_data(sql_content: str) -> List[Dict[str, Any]]:
    """
    Extract foundation data from SQL content using regex.
    """
    foundation_pattern = r"INSERT INTO foundation\s+\(([^)]+)\)\s+VALUES\s+\(([^)]+)\)"
    foundations = []
    
    # Find all foundation inserts
    for match in re.finditer(foundation_pattern, sql_content, re.IGNORECASE):
        columns = [col.strip() for col in match.group(1).split(',')]
        values = []
        
        # Parse values accounting for quoted strings and commas in strings
        values_str = match.group(2)
        in_quotes = False
        current_value = ""
        
        for char in values_str:
            if char == "'" and (not in_quotes or (in_quotes and current_value and current_value[-1] != '\\')):
                in_quotes = not in_quotes
                current_value += char
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
                
        if current_value:
            values.append(current_value.strip())
        
        # Create foundation data dictionary
        if len(columns) == len(values):
            foundation_data = {columns[i]: values[i] for i in range(len(columns))}
            foundations.append(foundation_data)
    
    return foundations

def generate_visualization(converted_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate visualization data from converted elements.
    """
    elements = converted_data.get("elements", [])
    
    visualization = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "project_id": converted_data.get("project_id", "unknown"),
            "element_count": len(elements),
            "element_types": {}
        },
        "elements": []
    }
    
    element_types = {}
    
    for element in elements:
        element_type = element.get("element_type", "unknown")
        if element_type not in element_types:
            element_types[element_type] = 0
        element_types[element_type] += 1
        
        # Extract visualization properties
        viz_element = {
            "id": element.get("uuid", str(uuid.uuid4())),
            "type": element_type,
            "name": element.get("name", f"Element-{len(visualization['elements'])+1}"),
            "position": None,
            "dimensions": None,
            "references": []
        }
        
        # Extract position from location component
        components = element.get("components", {})
        if "location" in components:
            location = components["location"]
            viz_element["position"] = {
                "x": location.get("x", 0),
                "y": location.get("y", 0),
                "z": location.get("z", 0)
            }
        
        # Extract dimensions from dimension component
        if "dimension" in components:
            dimension = components["dimension"]
            viz_element["dimensions"] = {
                "length": dimension.get("length", 0),
                "width": dimension.get("width", 0),
                "height": dimension.get("height", 0)
            }
        
        # Extract references
        if "reference" in components:
            reference = components["reference"]
            for ref_type, ref_id in reference.items():
                viz_element["references"].append({
                    "type": ref_type,
                    "id": ref_id
                })
        
        visualization["elements"].append(viz_element)
    
    visualization["metadata"]["element_types"] = element_types
    
    return visualization

if __name__ == "__main__":
    main()