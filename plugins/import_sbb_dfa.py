#!/usr/bin/env python
"""
Import script for SBB DFA Excel data.
This script reads DFA Excel data and converts it to the canonical model using the SBB plugin.
"""

import argparse
import json
import logging
import os
import sys
import traceback
from pathlib import Path

from pyarm.validation.pipeline import ValidationPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

log = logging.getLogger("import_sbb_dfa")

# Ensure pyarm module can be imported
base_dir = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(base_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    # Import SBB plugin and models
    from plugins.dfa_plugin import SBBPlugin
    from pyarm.models.process_enums import ElementType

except ImportError as e:
    log.error(f"Failed to import required modules: {e}")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import SBB DFA Excel data and convert it to the canonical model."
    )

    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Path to the DFA Excel file",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="tests/output/sbb",
        help="Directory to save the output files",
    )

    parser.add_argument(
        "--element_types",
        type=str,
        nargs="+",
        default=[
            ElementType.SEWER_PIPE,
            ElementType.SEWER_SHAFT,
            ElementType.MAST,
            ElementType.FOUNDATION,
            ElementType.CANTILEVER,
            ElementType.JOCH,
            ElementType.CABLE_SHAFT,
        ],
        help="Element types to import (default: all supported types)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def setup_output_directory(output_dir):
    """Create output directory if it doesn't exist."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        log.info(f"Output directory: {output_dir}")
        return True
    except Exception as e:
        log.error(f"Failed to create output directory: {e}")
        return False


def main():
    """Main function to import DFA data."""
    args = parse_args()

    # Set log level
    if args.verbose:
        log.setLevel(logging.DEBUG)

    # Check input file
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        log.error(f"Input directory does not exist: {input_dir}")
        return 1

    # Setup output directory
    output_dir = Path(args.output_dir)
    if not setup_output_directory(output_dir):
        return 1

    # Initialize plugin
    plugin = SBBPlugin()
    if not plugin.initialize({}):
        log.error("Failed to initialize DfA plugin")
        return 1

    # Lade Daten direkt aus dem Verzeichnis mit dem Plugin
    log.info(f"Loading data from directory: {input_dir}")
    plugin.load_data_from_directory(input_dir)
    
    # Create validation pipeline
    validation_pipeline = ValidationPipeline()
    validation_pipeline.register_process(plugin)

    # Verarbeite jeden Elementtyp
    successful_conversions = 0
    element_count = 0

    converted_elements = []
    for element_type in plugin.get_supported_element_types():
        try:
            log.info(f"Processing: {element_type}")

            # Konvertiere Daten mit dem Plugin
            result = plugin.convert_element(element_type)

            if result and result.elements:
                # Validate the converted elements
                for element in result.elements:
                    validation_result = validation_pipeline.validate_for_process(
                        plugin.get_process_name(),
                        str(element_type),
                        element.to_dict()
                    )
                    if not validation_result.is_valid():
                        log.warning(f"Validation issues for {element_type}: {validation_result}")
                
                # Elementtyp als String für Dateinamen verwenden
                elements = [ele.to_dict() for ele in result.elements if ele]
                converted_elements.append(elements)
                type_str = str(element_type).split(".")[-1].lower()
                output_file = output_dir / f"{type_str}_converted.json"
                with open(output_file, "w") as f:
                    json.dump(elements, f, indent=2, ensure_ascii=False)

                log.info(f"Converted {len(result.elements)} elements saved to: {output_file}")

                successful_conversions += 1
                element_count += len(result.elements)
            else:
                log.warning(f"No elements found for {element_type}")

        except Exception as e:
            log.error(f"Error while processing {element_type}: {e} {traceback.format_exc()}")

    # Erstelle kombinierte Visualisierungsdaten
    try:
        visualization_data = {
            "project_name": "DFA Import",
            "elements": converted_elements,
        }

        # Speichere Visualisierungsdaten
        viz_file = output_dir / "dfa_visualization.json"
        with open(viz_file, "w") as f:
            json.dump(visualization_data, f, indent=2)

        log.info(f"Visualisation data saved to: {viz_file}")

    except Exception as e:
        log.error(f"Error while creating visualization data: {e}")

    # Zusammenfassung
    log.info(f"Successfully converted {successful_conversions} elements.")
    log.info(f"Total elements processed: {element_count}")

    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        root = Path(__file__).resolve().parent
        input_dir = root / "examples/clients/sbb"
        sys.argv.append("--input_dir")
        sys.argv.append(str(input_dir))
        output_dir = root / "examples/clients/sbb/converted"
        sys.argv.append("--output_dir")
        sys.argv.append(str(output_dir))
    sys.exit(main())
