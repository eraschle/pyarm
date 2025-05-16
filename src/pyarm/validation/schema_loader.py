"""
Schema-Loader für das Validierungssystem.

Dieses Modul stellt Funktionen zum Laden von Validierungsschemata aus JSON-Dateien bereit.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pyarm.models.parameter import DataType, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.schema import Constraint, ConstraintType, SchemaDefinition

log = logging.getLogger(__name__)


def _create_constraint_from_json(constraint_data: Dict[str, Any]) -> Optional[Constraint]:
    """
    Erstellt ein Constraint-Objekt aus JSON-Daten.

    Parameters
    ----------
    constraint_data : Dict[str, Any]
        Die JSON-Daten für den Constraint

    Returns
    -------
    Optional[Constraint]
        Das erstellte Constraint-Objekt oder None bei Fehlern
    """
    try:
        constraint_type = ConstraintType[constraint_data.get("constraint_type", "")]
        value = constraint_data.get("value")
        message = constraint_data.get("message")

        # Behandlung von benutzerdefinierten Validatoren
        custom_validator = None
        if constraint_type == ConstraintType.CUSTOM and "custom_validator" in constraint_data:
            validator_str = constraint_data["custom_validator"]
            try:
                # Vorsicht: eval() kann ein Sicherheitsrisiko sein!
                custom_validator = eval(validator_str)
            except Exception as e:
                log.error(f"Fehler beim Evaluieren des benutzerdefinierten Validators: {e}")
                return None

        return Constraint(
            constraint_type=constraint_type,
            value=value,
            message=message,
            custom_validator=custom_validator,
        )
    except (KeyError, ValueError) as e:
        log.error(f"Fehler beim Erstellen des Constraints: {e}")
        return None


def load_schema_from_json(file_path: Union[str, Path]) -> Optional[SchemaDefinition]:
    """
    Lädt ein Validierungsschema aus einer JSON-Datei.

    Parameters
    ----------
    file_path : Union[str, Path]
        Pfad zur JSON-Datei

    Returns
    -------
    Optional[SchemaDefinition]
        Das geladene Schema oder None bei Fehlern
    """
    try:
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            schema_data = json.load(f)

        # Element-Typ extrahieren
        element_type_str = schema_data.get("element_type")
        if not element_type_str:
            log.error(f"Kein Element-Typ in Schema-Datei {file_path} gefunden")
            return None

        try:
            element_type = ElementType(element_type_str)
        except ValueError:
            log.error(f"Ungültiger Element-Typ: {element_type_str}")
            return None

        # Schema erstellen
        schema = SchemaDefinition(element_type=element_type)

        # Erforderliche Parameter hinzufügen
        for param_name in schema_data.get("required_params", []):
            try:
                process_enum = ProcessEnum(param_name)
                schema.required_params.add(process_enum)
            except ValueError:
                log.warning(f"Unbekanntes ProcessEnum: {param_name}")

        # Parameter-Typen hinzufügen
        for param_name, type_str in schema_data.get("param_types", {}).items():
            try:
                process_enum = ProcessEnum(param_name)
                data_type = DataType(type_str)
                schema.param_types[process_enum] = data_type
            except ValueError:
                log.warning(f"Ungültiger Parameter oder Datentyp: {param_name}: {type_str}")

        # Parameter-Einheiten hinzufügen
        for param_name, unit_str in schema_data.get("param_units", {}).items():
            try:
                process_enum = ProcessEnum(param_name)
                unit = UnitEnum(unit_str)
                schema.param_units[process_enum] = unit
            except ValueError:
                log.warning(f"Ungültiger Parameter oder Einheit: {param_name}: {unit_str}")

        # Constraints hinzufügen
        for param_name, constraints_list in schema_data.get("constraints", {}).items():
            try:
                process_enum = ProcessEnum(param_name)
                for constraint_data in constraints_list:
                    constraint = _create_constraint_from_json(constraint_data)
                    if constraint:
                        schema.add_constraint(process_enum, constraint)
            except ValueError:
                log.warning(f"Unbekanntes ProcessEnum für Constraint: {param_name}")

        # Spezifische Validierungen hinzufügen
        for validation in schema_data.get("specific_validations", []):
            name = validation.get("name")
            description = validation.get("description")
            validation_code_str = validation.get("validation_code")
            error_message = validation.get("error_message")

            if name and validation_code_str and error_message:
                try:
                    validation_func = eval(validation_code_str)
                    schema.add_custom_constraint(
                        ProcessEnum.ELEMENT_TYPE,  # Wir verwenden ELEMENT_TYPE als Platzhalter
                        validation_func,
                        error_message,
                    )
                    log.info(f"Spezifische Validierung '{name}' hinzugefügt: {description}")
                except Exception as e:
                    log.error(f"Fehler beim Hinzufügen der spezifischen Validierung '{name}': {e}")

        return schema
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log.error(f"Fehler beim Laden des Schemas aus {file_path}: {e}")
        return None


def load_schemas_from_directory(directory: Union[str, Path]) -> Dict[ElementType, SchemaDefinition]:
    """
    Lädt alle Validierungsschemata aus einem Verzeichnis.

    Parameters
    ----------
    directory : Union[str, Path]
        Pfad zum Verzeichnis mit den Schema-Dateien

    Returns
    -------
    Dict[ElementType, SchemaDefinition]
        Dictionary mit den geladenen Schemata, indiziert nach Element-Typ
    """
    schemas = {}
    directory = Path(directory)

    if not directory.exists() or not directory.is_dir():
        log.error(f"Verzeichnis {directory} existiert nicht oder ist kein Verzeichnis")
        return schemas

    for file_path in directory.glob("*.json"):
        schema = load_schema_from_json(file_path)
        if schema:
            schemas[schema.element_type] = schema
            log.info(f"Schema für {schema.element_type.value} aus {file_path.name} geladen")

    return schemas
