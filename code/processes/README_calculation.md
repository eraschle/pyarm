# Calculation Process

This document explains the calculation process in the SortDesk Modeling Process Improvement system and how it interacts with the canonical data model.

## Overview

The calculation process is responsible for performing engineering calculations on infrastructure elements represented in the canonical data model. It extracts relevant properties, applies engineering formulas, and produces calculation results that can be used for design validation and analysis.

```
┌──────────────┐      ┌──────────────┐      ┌────────────────────┐
│  Repository  │──────▶  Canonical   │──────▶   Calculation      │
│   (JSON)     │      │  Data Model  │      │  Processing        │
└──────────────┘      └──────────────┘      └────────────────────┘
                                                      │
                                                      ▼
                                             ┌────────────────────┐
                                             │  Calculation       │
                                             │  Results (JSON)    │
                                             └────────────────────┘
```

## Canonical Data Model Integration

The calculation process leverages the canonical data model to ensure consistent engineering calculations across different client systems. Each element in the canonical model contains:

- Base attributes (UUID, name, element type)
- Parameters list with process-specific values
- Known parameters map for quick access

The calculation process specifically targets parameters marked with the `ProcessEnum.CALCULATION` identifier, ensuring that only calculation-relevant data is processed.

```python
# Example of accessing calculation parameters
element = repository.get_by_id("foundation-123")
material = element.get_param(ProcessEnum.MATERIAL)
width = element.get_param(ProcessEnum.FOUNDATION_WIDTH)
depth = element.get_param(ProcessEnum.FOUNDATION_DEPTH)
height = element.get_param(ProcessEnum.FOUNDATION_HEIGHT)
```

## Calculation-Specific Parameters

The calculation process relies on the following key parameters from the canonical model:

### Common Parameters for All Elements
- **Material**: Material properties for structural calculations
- **Position coordinates**: Used for spatial analysis
- **Element type**: Determines which calculation formulas apply

### Element-Specific Parameters

#### Foundations
- **Foundation type**: Influences structural behavior
- **Dimensions**: Width, depth, and height for volume and pressure calculations
- **Material density**: For weight calculations

#### Masts
- **Mast type**: Affects structural properties
- **Height**: Used in moment calculations
- **Profile type**: Determines cross-section properties
- **Connection to foundation**: For load transfer calculations

#### Tracks
- **Track type**: Influences bearing capacity
- **Gauge**: Used in lateral force calculations
- **Cant**: Important for calculating centrifugal forces

#### Curved Tracks
- **Clothoid parameter**: For transition curve calculations
- **Start/end radius**: Critical for lateral force calculations

#### Jochs (Cross-spans)
- **Joch type**: Structural type information
- **Span**: Key parameter for load and deflection calculations
- **Connection points**: For structural analysis

## Types of Engineering Calculations

The calculation process performs various types of engineering calculations, including:

### Structural Load Analysis
Calculates loads, moments, and forces for structural elements:

```python
# Example: Calculate structure load for a mast
load_data = calculation_service.calculate_structure_load("mast-123")
```

The result includes:
- Self-weight of the element
- Additional loads from connected elements
- Foundation moments
- Comparison with allowable limits

### Weight and Volume Calculations
Determines basic physical properties:

```python
# Foundation calculations
volume = width * depth * height  # m³
weight = volume * material_density  # kg
```

### Track Force Calculations
Analyzes forces on railway tracks based on speed and load:

```python
# Example: Calculate forces on a track
forces = calculation_service.calculate_track_forces(
    "track-123",  # Element ID
    15.0,         # Speed (m/s)
    25.0          # Load (kN/m)
)
```

The result includes:
- Vertical forces
- Lateral forces in curves
- Effect of track cant on force distribution

### Geometric Calculations
Determines spatial relationships and derived properties:

```python
# Calculate length of a linear element
length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5

# Calculate clothoid parameters
if radius > 0:
    clothoid_length = clothoid_parameter**2 / radius
```

## Calculation Process Flow

The calculation process follows these steps:

1. **Element Retrieval**: Fetch infrastructure elements from the repository
2. **Parameter Extraction**: Extract calculation-relevant parameters from the canonical model
3. **Calculation**: Apply engineering formulas and algorithms
4. **Result Formatting**: Structure the calculation results
5. **Dependency Resolution**: Process related elements when needed
6. **Output Generation**: Save results as JSON files

### `CalculationElement` Data Structure

The calculation process uses a dedicated `CalculationElement` class to encapsulate calculation-specific data:

```python
# Example of a CalculationElement
calc_element = CalculationElement(
    uuid="mast-123",
    name="M-101",
    element_type="Mast"
)

# Add basic properties
calc_element.add_property("material", "Steel")
calc_element.add_property("height", 12.5)

# Add calculation results
calc_element.add_calculation_data("weight", 625.0)
calc_element.add_calculation_data("moment", 3906.25)

# Add dependencies
calc_element.add_dependency("foundation-123")
```

## Engineering Formulas and Algorithms

The calculation process uses various engineering formulas for different element types:

### Foundation Calculations
```
volume = width * depth * height  # m³
weight = volume * material_density  # kg
bottom_pressure = weight / (width * depth)  # kg/m²
```

### Mast Calculations
```
# Weight calculation based on mast type
weight_per_meter = {
    "DP18": 40.0,  # kg/m
    "DP20": 45.0,  # kg/m
    "DP22": 50.0,  # kg/m
    "DP24": 55.0   # kg/m
}
weight = height * weight_per_meter[mast_type]

# Foundation moment
moment = total_weight * height / 2.0  # Nm
```

### Track Force Calculations
```
# Vertical force
vertical_force = load * length  # kN

# Lateral force in curves
if radius > 0:
    # Centrifugal force
    centrifugal_force = load * speed² / radius  # kN
    
    # Reduction from track cant
    cant_effect = load * g * cant / gauge  # kN
    
    lateral_force = centrifugal_force - cant_effect
```

### Joch (Cross-span) Calculations
```
# Weight calculation
weight = span * 15.0  # kg (assuming 15 kg/m)

# Moment at center
moment = weight * span / 8.0  # Nm (assuming simple beam)

# Tension in the span
tension = weight * 0.5  # N
```

## Example Calculations

### Foundation Load Analysis

```python
# Calculate volume, weight and soil pressure
foundation = process.process_element("foundation-123")

"""
Result example:
{
  "uuid": "foundation-123",
  "name": "F-101",
  "element_type": "Foundation",
  "properties": {
    "foundation_type": "DP2",
    "material": "Concrete",
    "dimensions": {
      "width": 2.4,
      "depth": 2.4,
      "height": 1.8
    }
  },
  "calculation_data": {
    "volume": 10.368,
    "weight": 25920.0,
    "bottom_pressure": 4500.0
  }
}
"""
```

### Mast Stress Analysis

```python
# Calculate loads and moments on a mast
mast_data = process.process_element("mast-123")

"""
Result example:
{
  "uuid": "mast-123",
  "name": "M-101",
  "element_type": "Mast",
  "properties": {
    "mast_type": "DP24",
    "profile_type": "HEB",
    "material": "Steel",
    "height": 12.5
  },
  "calculation_data": {
    "weight": 687.5,
    "resistance_moment": 100.0
  },
  "dependencies": ["foundation-123"],
  "load_case": {
    "self_weight": 687.5,
    "cantilever_weight": 120.0,
    "total_weight": 807.5,
    "foundation_moment": 5046.875,
    "max_allowed_moment": 500.0
  }
}
"""
```

### Track Force Calculation

```python
# Calculate forces on a curved track section
forces = process.calculate_track_forces(
    "track-123",  # Element ID
    15.0,         # Speed (m/s)
    25.0          # Load (kN/m)
)

"""
Result example:
{
  "vertical_force": 2500.0,
  "lateral_force": 187.5,
  "length": 100.0,
  "weight": 5400.0,
  "is_curved": true,
  "radius": 500.0
}
"""
```

## Design Patterns

The calculation process uses several key design patterns:

### Repository Pattern
- Provides uniform access to element data
- Hides the details of data storage and retrieval

```python
# Repository usage
repository = JsonElementRepository(repository_path)
element = repository.get_by_id(element_id)
```

### Service Layer
- Encapsulates calculation business logic
- Exposes clean API for performing calculations

```python
# Service usage
calculation_service = CalculationService(repository)
result = calculation_service.calculate_structure_load(element_id)
```

### Type Guards
- Ensures type-specific calculations are applied correctly
- Improves code safety and readability

```python
# Type guard example
if is_foundation(element):
    # Apply foundation-specific calculations
    ...
elif is_mast(element):
    # Apply mast-specific calculations
    ...
```

### Decorator Pattern (for Parameters)
- Enriches elements with calculation-specific data
- Maintains separation of concerns

```python
# Parameter decoration example
calc_element.add_calculation_data("theoretical_cant", theoretical_cant)
calc_element.add_calculation_data("cant_deficiency", theoretical_cant - cant)
```

### Dependency Resolution
- Tracks and resolves dependencies between elements
- Enables complex calculations involving multiple elements

```python
# Dependency handling
for dep_id in calc_element.dependencies:
    dep_element = repository.get_by_id(dep_id)
    if dep_element:
        dependencies.append(service._prepare_element_for_calculation(dep_element).to_dict())
```

## Extending the Calculation System

The calculation system is designed to be extended for new formulas and element types:

### Adding a New Element Type

1. Define the new element type in the canonical model
2. Create a type guard for the new element
3. Implement calculation methods in the service layer
4. Add a handler method for the new element type

```python
def _add_new_element_calculation(self, calc_element: CalculationElement, element: InfrastructureElement) -> None:
    """
    Adds new element specific calculation data.
    
    Args:
        calc_element: Calculation element
        element: The infrastructure element
    """
    # Add properties
    calc_element.add_property("new_property", element.get_param(ProcessEnum.NEW_PROPERTY, ""))
    
    # Perform calculations
    param1 = element.get_param(ProcessEnum.PARAM1, 0.0)
    param2 = element.get_param(ProcessEnum.PARAM2, 0.0)
    result = specialized_calculation_formula(param1, param2)
    
    # Add calculation results
    calc_element.add_calculation_data("new_calculation", result)
```

### Adding a New Calculation Method

To add a new calculation method:

1. Define the method in the `CalculationService` class
2. Extract relevant parameters from the canonical model
3. Implement the calculation logic
4. Format and return the results

```python
def calculate_new_property(self, element_id: Union[UUID, str], param1: float) -> Dict[str, Any]:
    """
    Calculates a new property for an element.
    
    Args:
        element_id: ID of the element
        param1: Input parameter for calculation
        
    Returns:
        Calculation results
        
    Raises:
        ValueError: If the element doesn't support this calculation
    """
    element = self.repository.get_by_id(element_id)
    if not element or not supports_calculation(element):
        raise ValueError(f"Element {element_id} doesn't support this calculation")
    
    # Extract parameters
    param2 = element.get_param(ProcessEnum.PARAM2, 0.0)
    
    # Perform calculation
    result = specialized_calculation_formula(param1, param2)
    
    # Return formatted results
    return {
        "input_parameters": {
            "param1": param1,
            "param2": param2
        },
        "calculation_result": result,
        "is_valid": result < max_allowed_value
    }
```

## Integration with Analysis Tools

The calculation results can be exported to various formats for further analysis:

- **JSON**: Primary output format for Revit and internal tools
- **CSV**: For spreadsheet and statistical analysis
- **Engineering analysis software**: Through specific adapters

## Summary

The calculation process provides a robust framework for performing engineering calculations on infrastructure elements using the canonical data model. It supports various types of calculations including structural analysis, force calculations, and geometric computations.

The modular design allows for easy extension with new calculation methods and element types, while maintaining consistency through the canonical data model. By implementing standard engineering formulas within a clean architecture, the system ensures reliable and traceable calculation results for infrastructure design and validation.