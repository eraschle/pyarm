#!/usr/bin/env python
"""
Test script for SBB DFA Plugin.
This script tests the SBB plugin functionality with DFA Excel data.
"""

import logging
import os
import sys
import unittest
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

log = logging.getLogger("test_sbb_plugin")

# Ensure pyarm module can be imported
base_dir = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(base_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import SBB plugin
from plugins.sbb_plugin import SBBPlugin
from plugins.sbb_plugin.reader import DfaExcelReader


class TestSBBPlugin(unittest.TestCase):
    """Test cases for SBB DFA Plugin."""

    def setUp(self):
        """Set up test environment."""
        self.plugin = SBBPlugin()
        self.plugin.initialize({})
        
        # Path to test data
        self.test_data_path = Path(base_dir) / "examples" / "clients" / "sbb" / "dfa_export.xlsx"
        
        # Ensure test data exists
        if not self.test_data_path.exists():
            log.error(f"Test data not found: {self.test_data_path}")
            self.skipTest("Test data not available")

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        # Plugin should have name and version attributes
        self.assertEqual(self.plugin.name, "SBB DFA Plugin")
        self.assertEqual(self.plugin.version, "1.0.0")
        
        # Plugin should load mapping
        self.assertIsNotNone(self.plugin.mapping)
        self.assertGreater(len(self.plugin.mapping), 0)

    def test_supported_element_types(self):
        """Test supported element types."""
        supported_types = self.plugin.get_supported_element_types()
        expected_types = ["abwasser_haltung", "abwasser_schacht", "kabelschacht", "ausleger", "mast", "fundament"]
        
        # All expected types should be supported
        for element_type in expected_types:
            self.assertIn(element_type, supported_types)

    def test_excel_reader(self):
        """Test DFA Excel reader."""
        try:
            # Read Excel data
            excel_data = DfaExcelReader.read_excel(self.test_data_path)
            
            # Verify data structure
            self.assertIn("excel_data", excel_data)
            self.assertIn("metadata", excel_data)
            
            # Verify Excel data
            self.assertIsNotNone(excel_data["excel_data"])
            self.assertGreater(len(excel_data["excel_data"]), 0)
            
            # Verify metadata
            self.assertIn("file_name", excel_data["metadata"])
            self.assertIn("row_count", excel_data["metadata"])
            self.assertEqual(excel_data["metadata"]["file_name"], "dfa_export.xlsx")
            
        except Exception as e:
            self.fail(f"Excel reader failed: {e}")

    def test_element_conversion(self):
        """Test element conversion with plugin."""
        try:
            # Read Excel data
            excel_data = DfaExcelReader.read_excel(self.test_data_path)
            
            # Test each supported element type
            element_types = self.plugin.get_supported_element_types()
            
            # Count successful conversions
            successful_conversions = 0
            
            for element_type in element_types:
                input_data = {
                    "excel_data": excel_data["excel_data"],
                    "metadata": excel_data["metadata"]
                }
                
                result = self.plugin.convert_element(input_data, element_type)
                
                # Check if conversion succeeded
                if result and "elements" in result:
                    log.info(f"Successfully converted {len(result['elements'])} {element_type} elements")
                    successful_conversions += 1
                else:
                    log.warning(f"No elements converted for type: {element_type}")
            
            # At least some element types should be convertible
            self.assertGreater(successful_conversions, 0)
            
        except Exception as e:
            self.fail(f"Element conversion failed: {e}")


if __name__ == "__main__":
    unittest.main()