# SBB DFA Plugin

This plugin converts SBB DFA Excel data to the PyArm canonical model.

## Overview

The SBB DFA Plugin reads Excel files containing infrastructure data from the SBB DFA system and converts it into the PyArm canonical model. It supports various infrastructure elements like drainage pipes, drainage shafts, masts, foundations, and cantilevers.

## Supported Element Types

The plugin supports the following element types:

- `abwasser_haltung` - Drainage pipes (Abwasser-Leitungen)
- `abwasser_schacht` - Drainage shafts (Abwasser-Normschächte)
- `kabelschacht` - Cable shafts (Kabelschächte)
- `mast` - Masts (Masten)
- `fundament` - Foundations (Fundamente)
- `ausleger` - Cantilevers (Ausleger)

## Parameter Mapping

The plugin uses a mapping file (`dfa_report.json`) to map Excel column names to ProcessEnum values. This allows for flexible mapping of DFA data to the canonical model.

## Usage

### Importing the Plugin

```python
from plugins.sbb_plugin import SBBPlugin
from plugins.sbb_plugin.reader import DfaExcelReader

# Initialize the plugin
plugin = SBBPlugin()
plugin.initialize({})

# Read Excel data
excel_path = "path/to/dfa_export.xlsx"
excel_data = DfaExcelReader.read_excel(excel_path)

# Convert drainage pipes
element_type = "abwasser_haltung"
input_data = {
    "excel_data": excel_data["excel_data"],
    "metadata": excel_data["metadata"]
}
result = plugin.convert_element(input_data, element_type)

# Process the results
if result:
    elements = result["elements"]
    print(f"Converted {len(elements)} {element_type} elements")
    # Do something with the elements...
```

### Command Line Script

A sample script for using the plugin is provided in `import_sbb_dfa.py`.

## Requirements

- Python 3.8+
- pandas
- openpyxl

## Notes

- The plugin relies on the `Family` column in the Excel data to identify element types
- The plugin uses the mapping defined in `dfa_report.json` to map Excel columns to ProcessEnum values
- The plugin handles both point-based elements (like masts and shafts) and line-based elements (like pipes)