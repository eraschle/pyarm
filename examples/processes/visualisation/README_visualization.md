# Visualization Process

This document explains the visualization process in the SortDesk Modeling Process Improvement system and how it interacts with the canonical data model.

## Overview

The visualization process is responsible for transforming infrastructure elements from the canonical data model into a format suitable for 3D rendering in Revit. It extracts relevant geometric properties, positions, and visualization-specific parameters from the internal model.

```
┌──────────────┐      ┌──────────────┐      ┌────────────────────┐
│  Repository  │──────▶  Canonical   │──────▶   Visualization    │
│   (JSON)     │      │  Data Model  │      │  Transformation    │
└──────────────┘      └──────────────┘      └────────────────────┘
                                                      │
                                                      ▼
                                             ┌────────────────────┐
                                             │  Visualization     │
                                             │  JSON Output       │
                                             └────────────────────┘
```

## Canonical Data Model Integration

The visualization process uses the canonical data model to ensure a consistent representation of infrastructure elements across different client systems. Each element in the canonical model is represented by the `InfrastructureElement` class (or a subclass) which contains:

- Base attributes (UUID, name, element type)
- Parameters list with process-specific values
- Known parameters map for quick access

```python
# Example of a canonical model element
element = Mast(
    name="M-101",
    element_type=ElementType.MAST
)
element.x = 100.0  # Sets X_COORDINATE parameter
element.y = 200.0  # Sets Y_COORDINATE parameter
element.z = 15.0   # Sets Z_COORDINATE parameter
element.mast_type = "DP24"
element.height = 12.5
```

## Visualization Parameters

The visualization process uses the following key parameters from the canonical model:

### Common Parameters for All Elements
- **Position coordinates**: X, Y, Z coordinates for positioning the element in 3D space
- **Element type**: Determines which Revit family to use
- **UUID**: Unique identifier for the element

### Element-Specific Parameters

#### Foundations
- **Foundation type**: Type identifier (e.g., "A1", "DP1")
- **Dimensions**: Width, depth, and height for proper scaling

#### Masts
- **Mast type**: Type of mast (e.g., "DP18", "DP24")
- **Height**: Total height of the mast
- **Azimuth**: Rotation angle for proper orientation
- **Profile type**: Cross-section profile information

#### Tracks
- **Track type**: Rail type information
- **Gauge**: Distance between rails
- **Cant**: Track superelevation

#### Curved Tracks (extends Tracks)
- **Clothoid parameter**: Parameter for the transition curve
- **Start/end radius**: Radius values for curved sections

#### Jochs (Cross-spans)
- **Joch type**: Type of cross-span structure
- **Span**: Distance between supporting masts
- **Connection points**: Start and end coordinates

## Data Transformation Process

The visualization process transforms data through the following steps:

1. **Data Retrieval**: Fetch the infrastructure element from the repository
2. **Parameter Extraction**: Extract visualization-relevant parameters from the canonical model
3. **Enrichment**: Add derived properties and calculations needed for visualization
4. **Formatting**: Convert to the expected JSON format for Revit plugin consumption

### Example Transformation

```python
# Input: Canonical model element (Mast)
mast = repository.get_by_id("12345")

# Output: Visualization data structure
visualization_data = {
    "id": "12345",
    "name": "M-101",
    "type": "Mast",
    "position": {
        "x": 100.0,
        "y": 200.0,
        "z": 15.0,
        "azimuth": 45.0
    },
    "mast_type": "DP24",
    "height": 12.5
}
```

## Special Visualization Features

### Clothoid Curve Visualization

For curved track elements, the system can generate point sequences along clothoid curves for accurate visualization:

```python
# Calculate points along a clothoid curve
points = visualization_service.calculate_clothoid_points(
    element_id="track-123",
    start_station=0.0,
    end_station=100.0,
    step=1.0
)
```

The calculated points provide a discrete representation of the continuous curve with appropriate height values, enabling smooth visualization in Revit.

## Design Patterns

The visualization process uses several key design patterns:

### Repository Pattern
- Separates data access logic from the business logic
- Provides a uniform interface for data retrieval

```python
# Repository usage example
repository = JsonElementRepository(repository_path)
element = repository.get_by_id(element_id)
```

### Service Layer
- Encapsulates business logic related to visualization
- Provides a clean API for other components to interact with

```python
# Service usage example
visualization_service = VisualizationService(repository)
visualization_data = visualization_service.get_element(element_id)
```

### Type Guards
- Helper functions to safely check element types
- Ensures correct type-specific processing

```python
# Type guard example
if is_foundation(element):
    # Process foundation-specific attributes
    ...
elif is_mast(element):
    # Process mast-specific attributes
    ...
```

### Data Transformation Pipeline
- Sequential processing of elements through distinct transformation steps
- Allows for modular enhancement of the visualization process

## Example Usage Scenarios

### Visualizing a Foundation

```python
# Create visualization process
process = VisualizationProcess(
    repository_path="/data/repository",
    output_path="/data/output/visualization"
)

# Process a single foundation
foundation_data = process.process_element("foundation-123")

# Foundation-specific visualization data includes:
# - 3D position
# - Foundation dimensions
# - Foundation type
# - Material properties for rendering
```

### Visualizing a Rail Track Network

```python
# Get all track elements
track_data = process.process_elements_by_type(ElementType.TRACK)

# For curved sections, generate detailed points
for track in track_data:
    if track.get("is_curved", False):
        curve_points = process.calculate_clothoid_points(
            track["id"], 
            start_station=0.0, 
            end_station=track["length"], 
            step=1.0
        )
```

### Generating Complete Visualization

```python
# Run the complete visualization process
process.run()
# This will:
# 1. Load all elements from the repository
# 2. Transform them for visualization
# 3. Group them by element type
# 4. Save the visualization data as JSON files
# 5. Create an overview summary
```

## Integration with Revit Plugin

The visualization process outputs JSON files that can be directly consumed by the Revit plugin. The JSON structure matches the expected format:

```json
{
  "element_counts": {
    "Mast": 24,
    "Foundation": 24,
    "Joch": 12,
    "Track": 18
  },
  "total_elements": 78
}
```

Individual element files contain the detailed visualization data:

```json
[
  {
    "id": "mast-123",
    "name": "M-101",
    "type": "Mast",
    "position": {
      "x": 100.0,
      "y": 200.0,
      "z": 15.0,
      "azimuth": 45.0
    },
    "mast_type": "DP24",
    "height": 12.5,
    "foundation_id": "foundation-123"
  }
]
```

## Advanced Visualization Techniques

### Contextual Visualization
Elements can be visualized with their related components (e.g., a mast with its foundation and attached cantilevers) by following the object references in the canonical model.

### Level of Detail Control
The visualization process can adjust the level of detail based on requirements:
- **High detail**: Full parameter set with additional calculated points for curved elements
- **Medium detail**: Basic geometry with main parameters
- **Low detail**: Simplified representations for overview visualizations

### Material Mapping
The visualization service can map internal material identifiers to specific Revit materials for realistic rendering.

## Extending the Visualization Process

To add support for new element types:

1. Define the new element type in the canonical data model
2. Create type-specific parameter handling in the visualization service
3. Implement necessary calculations and transformations
4. Update the output format to include the new element's properties

Example for adding a new element type:

```python
def _add_new_element_attributes(self, result: Dict[str, Any], element: InfrastructureElement) -> None:
    """
    Adds new element specific attributes for visualization.
    
    Args:
        result: Result dictionary
        element: The element
    """
    result["new_element_type"] = element.get_param(ProcessEnum.NEW_ELEMENT_TYPE, "")
    result["dimensions"] = {
        "param1": element.get_param(ProcessEnum.PARAM1, 0.0),
        "param2": element.get_param(ProcessEnum.PARAM2, 0.0)
    }
    
    # Add visualization-specific calculated values
    calculated_value = compute_visualization_value(element)
    result["calculated_property"] = calculated_value
```

## Summary

The visualization process is a key component that transforms the canonical data model into visualization-ready formats. By separating the visualization concerns from the core data model, we maintain a clean architecture while providing rich visualization capabilities for infrastructure elements in Revit.