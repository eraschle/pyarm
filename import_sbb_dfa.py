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
from pathlib import Path

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
    # Import SBB plugin
    from plugins.sbb_plugin import SBBPlugin
    from plugins.sbb_plugin.reader import DfaExcelReader

except ImportError as e:
    log.error(f"Failed to import required modules: {e}")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import SBB DFA Excel data and convert it to the canonical model."
    )

    parser.add_argument(
        "--input_file",
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
            "abwasser_haltung",
            "abwasser_schacht",
            "kabelschacht",
            "mast",
            "fundament",
            "ausleger",
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
    input_file = Path(args.input_file)
    if not input_file.exists():
        log.error(f"Input file does not exist: {input_file}")
        return 1

    # Setup output directory
    output_dir = Path(args.output_dir)
    if not setup_output_directory(output_dir):
        return 1

    # Initialize plugin
    plugin = SBBPlugin()
    if not plugin.initialize({}):
        log.error("Failed to initialize SBB plugin")
        return 1

    # Read Excel data
    try:
        log.info(f"Reading Excel file: {input_file}")
        excel_data = DfaExcelReader.read_excel(input_file)
        log.info(f"Excel data loaded: {len(excel_data['excel_data'])} rows")
        log.info(f"Found columns: {excel_data['metadata']['columns']}")
        if 'element_types' in excel_data['metadata']:
            log.info(f"Found element types: {excel_data['metadata']['element_types']}")
        if 'sheet_names' in excel_data['metadata']:
            log.info(f"Found sheets: {excel_data['metadata']['sheet_names']}")

        # Save metadata to output directory
        metadata_file = output_dir / "dfa_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(excel_data["metadata"], f, indent=2)
        log.info(f"Metadata saved to: {metadata_file}")

    except Exception as e:
        log.error(f"Failed to read Excel data: {e}")
        return 1

    # Process each element type
    successful_conversions = 0
    element_count = 0

    for element_type in args.element_types:
        try:
            log.info(f"Processing element type: {element_type}")
            input_data = {
                "excel_data": excel_data["excel_data"],
                "metadata": excel_data["metadata"],
            }

            result = plugin.convert_element(input_data, element_type)

            if result and "elements" in result and result["elements"]:
                # Save to JSON file
                output_file = output_dir / f"{element_type}_converted.json"
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)

                log.info(f"Converted {len(result['elements'])} {element_type} elements")
                log.info(f"Results saved to: {output_file}")

                successful_conversions += 1
                element_count += len(result["elements"])
            else:
                log.warning(f"No elements converted for type: {element_type}")

        except Exception as e:
            log.error(f"Error processing element type {element_type}: {e}")

    # Create combined visualization data
    try:
        visualization_data = {"project_name": "SBB DFA Import", "elements": []}

        # Collect all elements for visualization
        for element_type in args.element_types:
            element_file = output_dir / f"{element_type}_converted.json"
            if element_file.exists():
                with open(element_file, "r") as f:
                    data = json.load(f)
                    if "elements" in data:
                        visualization_data["elements"].extend(data["elements"])

        # Save visualization data
        viz_file = output_dir / "dfa_visualization.json"
        with open(viz_file, "w") as f:
            json.dump(visualization_data, f, indent=2)

        log.info(f"Combined visualization data saved to: {viz_file}")

    except Exception as e:
        log.error(f"Error creating visualization data: {e}")

    # Summary
    log.info(f"Import completed: {successful_conversions} element types processed")
    log.info(f"Total elements converted: {element_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
