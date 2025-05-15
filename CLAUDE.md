# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyArm (Python Architecture Restructuring Model) is a plugin-based system for modeling infrastructure elements. It provides a flexible architecture that allows different data sources and formats to be processed through a unified canonical model.

Key features:
- Plugin-based architecture for modular development
- Canonical data model with parameter mapping
- Multi-layered repository pattern for data storage
- Process-specific services for visualization and calculation

## Repository Structure

- **src/pyarm/** - Core source code
  - **interfaces/** - Protocol definitions for plugins
  - **models/** - Canonical data models
  - **plugins/** - Plugin discovery and management
  - **repository/** - Data storage layer
  - **utils/** - Helper functions

- **examples/** - Example implementations
  - **clients/** - Client-specific plugin implementations
  - **processes/** - Process implementations (visualization, calculation)

- **tests/** - Unit tests
  - **common/** - Tests for core components
  - **output/** - Output data for test cases

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Virtual environment (venv, conda, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/username/pyarm.git
cd pyarm

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode with dev dependencies
uv pip install -e ".[dev]"
```

## Common Commands

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/common/test_base_models.py

# Run tests with specific markers
python -m pytest -m "not integration"

# Run tests with verbose output
python -m pytest -v
```

### Linting and Code Quality

```bash
# Run ruff linter
ruff check

# Fix linting issues automatically
ruff check --fix
```

### Running the Application

The application is designed to import data from different client formats through a plugin system. Example scripts are provided:

```bash
# Import Client A data 
python import_client_a.py --input_dir examples/clients --project project1 --output_dir tests/output/client-a

# Import Client B data
python import_client_b.py --input_dir examples/clients --output_dir tests/output/client-b

# Import Client C data
python import_client_c.py --input_dir examples/clients --output_dir tests/output/client-c
```

## Architecture

### Plugin System

PyArm uses a plugin architecture where each plugin implements the `PluginInterface`:

```python
class PluginInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin."""
        pass
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass
        
    @abstractmethod
    def get_supported_element_types(self) -> List[ElementType]:
        """Return supported element types."""
        pass
        
    @abstractmethod
    def convert_element(self, element_type: str) -> Optional[Dict[str, Any]]:
        """Convert data to an element of specified type."""
        pass
```

Plugins are discovered from:
1. Built-in plugins in `pyarm.plugins`
2. Custom directories specified in configuration
3. Installed packages with entry points

### Canonical Data Model

The system uses a central data model to represent infrastructure elements:

```python
class InfrastructureElement:
    name: str
    uuid: UUID
    element_type: ElementType
    parameters: List[Parameter]  # For flexibility
    known_params: Dict[ProcessEnum, Any]  # For quick access
    
    def get_param(self, process_enum: ProcessEnum, default: Any = None) -> Any:
        return self.known_params.get(process_enum, default)
        
    def set_param(self, process_enum: ProcessEnum, value: Any) -> None:
        self.known_params[process_enum] = value
```

This model allows flexible parameter storage while providing quick access through enum-based lookups.

### Repository Pattern

Data is stored using a repository pattern:

```python
class IElementRepository(Protocol):
    def get_all(self) -> List[InfrastructureElement]: ...
    def get_by_id(self, uuid: str) -> Optional[InfrastructureElement]: ...
    def get_by_type(self, element_type: ElementType) -> List[InfrastructureElement]: ...
    def save(self, element: InfrastructureElement) -> None: ...
    def save_all(self, elements: List[InfrastructureElement]) -> None: ...
    def delete(self, uuid: str) -> bool: ...
```

## Creating Plugins

To create a new plugin:

1. Create a new directory in `plugins/` or `client_plugins/`
2. Implement the `PluginInterface` in the `__init__.py` file
3. Register the plugin in the configuration, or rely on auto-discovery

Example plugin structure:
```
plugins/
└── my_plugin/
    └── __init__.py  # Contains the plugin class
```

## Testing Strategy

Tests are organized by component:
- `test_base_models.py` - Tests for basic data models
- `test_element_models.py` - Tests for specialized elements
- `test_enums.py` - Tests for enumerations
- `test_type_guards.py` - Tests for type guards
- `test_json_repository.py` - Tests for JSON repository
- `test_calculation_service.py` - Tests for calculation service
- `test_visualization_service.py` - Tests for visualization service
- `test_visualization_process.py` - Tests for visualization process
- `test_factory.py` - Tests for element factory

## Configuration

The system looks for configuration in the following order:
1. Environment variable `PYARM_CONFIG` (path to config file)
2. `./config/plugins.json` (in project directory)
3. `~/.pyarm/plugins.json` (in user's home directory)

Configuration includes:
- Plugin paths (relative to project)
- External plugin paths (absolute)
- Disabled plugins
- Plugin-specific settings
