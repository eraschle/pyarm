"""
SBB-Plugin für DFA Daten.
Dieses Plugin konvertiert Daten aus DFA Excel-Dateien in das kanonische Datenmodell.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional
from uuid import UUID

import pandas as pd

# Ensure pyarm is in the path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.join(base_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.pyarm.interfaces.plugin import PluginInterface
from src.pyarm.models.base_models import InfrastructureElement
from src.pyarm.models.element_models import (
    Cantilever,
    SewerPipe,
    SewerShaft,
    Foundation,
    Mast,
)
from src.pyarm.models.parameter import DataType, Parameter, UnitEnum
from src.pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class SBBPlugin(PluginInterface):
    """
    SBB-Plugin für DFA Daten.
    Implementiert die Konvertierung von DFA Excel-Daten in das kanonische Datenmodell.
    """

    def __init__(self):
        self.mapping = {}
        self._load_mapping()
        self._debug_mode = False

    def _load_mapping(self):
        """Load parameter mapping from the mapping file."""
        mapping_file = os.path.join(base_dir, "examples", "clients", "sbb", "dfa_report.json")
        try:
            import json

            with open(mapping_file, "r") as f:
                self.mapping = json.load(f)
            log.info(f"Loaded mapping from {mapping_file}")
        except Exception as e:
            log.error(f"Failed to load mapping from {mapping_file}: {e}")
            self.mapping = {}

    @property
    def name(self) -> str:
        return "SBB DFA Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin mit der Konfiguration."""
        log.info(f"Initialisiere {self.name} v{self.version}")
        log.debug(f"Konfiguration: {config}")

        # Set debug mode if specified
        if config and "debug" in config:
            self._debug_mode = config["debug"]
            if self._debug_mode:
                log.setLevel(logging.DEBUG)
                log.debug("Debug mode enabled")

        # Ensure mapping is loaded
        if not self.mapping:
            self._load_mapping()
            if not self.mapping:
                log.error("Failed to load parameter mapping")
                return False

        return True

    def _ensure_coordinates(self, element: InfrastructureElement, item: Dict[str, Any]) -> bool:
        """
        Ensures the element has all required coordinates.
        If missing, tries to add them from the raw data.

        Args:
            element: The infrastructure element to check
            item: The raw data item

        Returns:
            bool: True if all coordinates are present, False otherwise
        """
        # Check for X coordinate
        has_x = element.has_param(ProcessEnum.X_COORDINATE)
        if not has_x and "E" in item:
            value = (
                float(item["E"])
                if isinstance(item["E"], (int, float, str)) and item["E"] != ""
                else 0.0
            )
            param = Parameter(
                name="E",
                value=value,
                process=ProcessEnum.X_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            )
            element.parameters.append(param)
            element._update_known_params()
            if self._debug_mode:
                log.debug(f"Added missing X-coordinate from E: {value}")
        elif not has_x:
            log.error(f"Element {element.name} missing X-coordinate")
            return False

        # Check for Y coordinate
        has_y = element.has_param(ProcessEnum.Y_COORDINATE)
        if not has_y and "N" in item:
            value = (
                float(item["N"])
                if isinstance(item["N"], (int, float, str)) and item["N"] != ""
                else 0.0
            )
            param = Parameter(
                name="N",
                value=value,
                process=ProcessEnum.Y_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            )
            element.parameters.append(param)
            element._update_known_params()
            if self._debug_mode:
                log.debug(f"Added missing Y-coordinate from N: {value}")
        elif not has_y:
            log.error(f"Element {element.name} missing Y-coordinate")
            return False

        # Check for Z coordinate
        has_z = element.has_param(ProcessEnum.Z_COORDINATE)
        if not has_z and "H-RSRG" in item:
            value = (
                float(item["H-RSRG"])
                if isinstance(item["H-RSRG"], (int, float, str)) and item["H-RSRG"] != ""
                else 0.0
            )
            param = Parameter(
                name="H-RSRG",
                value=value,
                process=ProcessEnum.Z_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            )
            element.parameters.append(param)
            element._update_known_params()
            if self._debug_mode:
                log.debug(f"Added missing Z-coordinate from H-RSRG: {value}")
        elif not has_z:
            log.error(f"Element {element.name} missing Z-coordinate")
            return False

        return True

    def get_supported_element_types(self) -> List[str]:
        """Gibt die unterstützten Elementtypen zurück."""
        return [
            "abwasser_haltung",
            "abwasser_schacht",
            "kabelschacht",
            "ausleger",
            "mast",
            "fundament",
        ]

    def convert_element(self, data: Dict[str, Any], element_type: str) -> Optional[Dict[str, Any]]:
        """
        Konvertiert Daten in ein Element des angegebenen Typs.

        Args:
            data: Die zu konvertierenden Daten
            element_type: Der Elementtyp

        Returns:
            Konvertiertes Element oder None, wenn Konvertierung nicht möglich
        """
        if element_type not in self.get_supported_element_types():
            log.warning(f"Elementtyp {element_type} wird nicht unterstützt")
            return None

        # Get the appropriate data from Excel based on element type
        excel_data = data.get("excel_data", None)
        if excel_data is None or not isinstance(excel_data, pd.DataFrame):
            log.warning(f"Keine gültigen Excel-Daten für Elementtyp {element_type} vorhanden")
            return None

        # Check if Family column exists
        if "Family" not in excel_data.columns:
            log.warning("Excel-Daten enthalten keine 'Family'-Spalte")
            return None

        # Filter data by Family to match element type
        if element_type == "abwasser_haltung":
            family_value = "Abwasser - Leitung"
            mask = excel_data["Family"].astype(str) == family_value
            filtered_data = excel_data[mask]
            mapping_key = "Abwasser_Haltung"
        elif element_type == "abwasser_schacht":
            family_value = "Abwasser - Normschacht"
            mask = excel_data["Family"].astype(str) == family_value
            filtered_data = excel_data[mask]
            mapping_key = "Abwasser_Schacht"
        elif element_type == "kabelschacht":
            mask = excel_data["Family"].astype(str).str.contains("Kabelschacht", na=False)
            filtered_data = excel_data[mask]
            mapping_key = "Alle_Kabelschächte"
        elif element_type == "ausleger":
            mask = excel_data["Family"].astype(str).str.contains("Ausleger", na=False)
            filtered_data = excel_data[mask]
            mapping_key = "Ausleger"
        elif element_type == "mast":
            mask = excel_data["Family"].astype(str).str.contains("Mast", na=False)
            filtered_data = excel_data[mask]
            mapping_key = "Mast"
        elif element_type == "fundament":
            mask = excel_data["Family"].astype(str).str.contains("Fundament", na=False)
            filtered_data = excel_data[mask]
            mapping_key = "Fundament"
        else:
            log.warning(f"Keine Filterkonfiguration für Elementtyp {element_type}")
            return None

        # filtered_data = filtered_data.fillna("")  # Replace NaN with empty strings

        if filtered_data.empty:
            log.warning(f"Keine Daten für Elementtyp {element_type} nach Filterung vorhanden")
            return None

        # Convert data to list of dictionaries
        records = filtered_data.to_dict(orient="records")

        # Convert based on element type
        converter_method = getattr(self, f"_convert_{element_type}", None)
        if converter_method is None:
            log.warning(f"Keine Konvertierungsmethode für {element_type} gefunden")
            return None

        parameter_mapping = self.mapping.get(mapping_key, {})
        converted_elements = converter_method(records, parameter_mapping)

        if not converted_elements:
            log.warning(f"Konvertierung für {element_type} ergab keine Elemente")
            return None

        # Konvertiere die Elemente in ein Dictionary für die Serialisierung
        serialized_elements = [element.to_dict() for element in converted_elements]

        return {
            "element_type": element_type,
            "elements": serialized_elements,
            "converted_by": self.name,
        }

    def _convert_abwasser_haltung(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Abwasser-Leitungsdaten."""
        drainage_pipes = []

        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Family", "Unbenannte Abwasserleitung")
                uuid_str = item.get("UUID", "")

                drainage_pipe = SewerPipe(name=name)

                if uuid_str:
                    drainage_pipe.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter basierend auf Mapping hinzufügen
                parameters = []
                for excel_field, process_enum_str in mapping.items():
                    if excel_field not in item:
                        continue

                    # Get value and convert if necessary
                    value = item[excel_field]
                    process_enum = getattr(ProcessEnum, process_enum_str.split(".")[-1])

                    # Determine data type and unit
                    datatype = DataType.STRING
                    unit = UnitEnum.NONE

                    if process_enum in [
                        ProcessEnum.X_COORDINATE,
                        ProcessEnum.Y_COORDINATE,
                        ProcessEnum.Z_COORDINATE,
                        ProcessEnum.X_COORDINATE_END,
                        ProcessEnum.Y_COORDINATE_END,
                        ProcessEnum.Z_COORDINATE_END,
                        ProcessEnum.WIDTH,
                        ProcessEnum.DIAMETER,
                        ProcessEnum.DEPTH,
                    ]:
                        datatype = DataType.FLOAT
                        unit = UnitEnum.METER
                        value = float(value) if value != "" else 0.0

                    # Create parameter
                    parameter = Parameter(
                        name=excel_field,
                        value=value,
                        process=process_enum,
                        datatype=datatype,
                        unit=unit,
                    )
                    parameters.append(parameter)

                # Add material parameter if available
                if "Material" in item and item["Material"]:
                    parameters.append(
                        Parameter(
                            name="Material",
                            value=item.get("Material", ""),
                            process=ProcessEnum.PIPE_MATERIAL,
                            datatype=DataType.STRING,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Add parameters to the element
                drainage_pipe.parameters.extend(parameters)
                drainage_pipe._update_known_params()

                # Initialize components
                try:
                    # Ensure required coordinates are set
                    if not self._ensure_coordinates(drainage_pipe, item):
                        continue

                    # For pipes, we also need end coordinates
                    has_x_end = drainage_pipe.has_param(ProcessEnum.X_COORDINATE_END)
                    has_y_end = drainage_pipe.has_param(ProcessEnum.Y_COORDINATE_END)
                    has_z_end = drainage_pipe.has_param(ProcessEnum.Z_COORDINATE_END)

                    # Add missing end coordinates if available in raw data
                    if not has_x_end and "E2" in item:
                        value = (
                            float(item["E2"])
                            if isinstance(item["E2"], (int, float, str)) and item["E2"] != ""
                            else 0.0
                        )
                        param = Parameter(
                            name="E2",
                            value=value,
                            process=ProcessEnum.X_COORDINATE_END,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        drainage_pipe.parameters.append(param)
                        drainage_pipe._update_known_params()
                    elif not has_x_end:
                        log.error(f"Drainage pipe {name} missing X-coordinate-end")
                        continue

                    if not has_y_end and "N2" in item:
                        value = (
                            float(item["N2"])
                            if isinstance(item["N2"], (int, float, str)) and item["N2"] != ""
                            else 0.0
                        )
                        param = Parameter(
                            name="N2",
                            value=value,
                            process=ProcessEnum.Y_COORDINATE_END,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        drainage_pipe.parameters.append(param)
                        drainage_pipe._update_known_params()
                    elif not has_y_end:
                        log.error(f"Drainage pipe {name} missing Y-coordinate-end")
                        continue

                    if not has_z_end and "H-RSRG_2" in item:
                        value = (
                            float(item["H-RSRG_2"])
                            if isinstance(item["H-RSRG_2"], (int, float, str))
                            and item["H-RSRG_2"] != ""
                            else 0.0
                        )
                        param = Parameter(
                            name="H-RSRG_2",
                            value=value,
                            process=ProcessEnum.Z_COORDINATE_END,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        drainage_pipe.parameters.append(param)
                        drainage_pipe._update_known_params()
                    elif not has_z_end:
                        log.error(f"Drainage pipe {name} missing Z-coordinate-end")
                        continue

                    drainage_pipe._initialize_components()
                    drainage_pipes.append(drainage_pipe)
                except Exception as e:
                    log.error(f"Error initializing components for drainage pipe {name}: {e}")
                    continue

            except Exception as e:
                log.error(f"Error converting drainage pipe: {e}")
                continue

        return drainage_pipes

    def _convert_abwasser_schacht(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Abwasser-Schachtdaten."""
        drainage_shafts = []

        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Family", "Unbenannter Abwasserschacht")
                uuid_str = item.get("UUID", "")

                drainage_shaft = SewerShaft(name=name)

                if uuid_str:
                    drainage_shaft.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter basierend auf Mapping hinzufügen
                parameters = []
                for excel_field, process_enum_str in mapping.items():
                    if excel_field not in item:
                        continue

                    # Get value and convert if necessary
                    value = item[excel_field]
                    process_enum = getattr(ProcessEnum, process_enum_str.split(".")[-1])

                    # Determine data type and unit
                    datatype = DataType.STRING
                    unit = UnitEnum.NONE

                    if process_enum in [
                        ProcessEnum.X_COORDINATE,
                        ProcessEnum.Y_COORDINATE,
                        ProcessEnum.Z_COORDINATE,
                        ProcessEnum.WIDTH,
                        ProcessEnum.DIAMETER,
                        ProcessEnum.SHAFT_MANHOLE_DIAMETER,
                    ]:
                        datatype = DataType.FLOAT
                        unit = (
                            UnitEnum.METER
                            if process_enum != ProcessEnum.SHAFT_MANHOLE_DIAMETER
                            else UnitEnum.MILLIMETER
                        )
                        value = float(value) if value != "" else 0.0

                    # Create parameter
                    parameter = Parameter(
                        name=excel_field,
                        value=value,
                        process=process_enum,
                        datatype=datatype,
                        unit=unit,
                    )
                    parameters.append(parameter)

                # Add parameters to the element
                drainage_shaft.parameters.extend(parameters)
                drainage_shaft._update_known_params()

                # Initialize components
                try:
                    # Ensure required coordinates are set
                    if not self._ensure_coordinates(drainage_shaft, item):
                        continue

                    drainage_shaft._initialize_components()
                    drainage_shafts.append(drainage_shaft)
                except Exception as e:
                    log.error(f"Error initializing components for drainage shaft {name}: {e}")
                    continue

            except Exception as e:
                log.error(f"Error converting drainage shaft: {e}")
                continue

        return drainage_shafts

    def _convert_kabelschacht(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Kabelschacht-Daten."""
        # Kabelschächte werden auch als DrainageShaft modelliert, mit eigenen Parametern
        return self._convert_abwasser_schacht(data, mapping)

    def _convert_mast(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten."""
        masts = []

        for item in data:
            try:
                # Parameter basierend auf Mapping hinzufügen
                parameters = []
                for excel_field, process_enum_str in mapping.items():
                    if excel_field not in item:
                        continue

                    # Get value and convert if necessary
                    value = item[excel_field]
                    process_enum = getattr(ProcessEnum, process_enum_str.split(".")[-1])

                    # Determine data type and unit
                    datatype = DataType.STRING
                    unit = UnitEnum.NONE

                    if process_enum in [
                        ProcessEnum.X_COORDINATE,
                        ProcessEnum.Y_COORDINATE,
                        ProcessEnum.Z_COORDINATE,
                        ProcessEnum.X_COORDINATE_END,
                        ProcessEnum.Y_COORDINATE_END,
                        ProcessEnum.Z_COORDINATE_END,
                        ProcessEnum.WIDTH,
                        ProcessEnum.DIAMETER,
                        ProcessEnum.HEIGHT,
                    ]:
                        datatype = DataType.FLOAT
                        unit = UnitEnum.METER
                        value = float(value) if value != "" else 0.0

                    # Create parameter
                    parameter = Parameter(
                        name=excel_field,
                        value=value,
                        process=process_enum,
                        datatype=datatype,
                        unit=unit,
                    )
                    parameters.append(parameter)

                # Add parameters to the element
                # Basisparameter erstellen
                name = item.get("Family", "Unbenannter Mast")
                uuid_str = item.get("UUID", "")
                mast = Mast(name=name, uuid=UUID(uuid_str), parameters=parameters)
                masts.append(mast)

            except Exception as e:
                log.error(f"Error converting mast: {e}")
                continue

        return masts

    def _convert_fundament(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten."""
        foundations = []

        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Family", "Unbenanntes Fundament")
                uuid_str = item.get("UUID", "")

                foundation = Foundation(name=name)

                if uuid_str:
                    foundation.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter basierend auf Mapping hinzufügen
                parameters = []
                for excel_field, process_enum_str in mapping.items():
                    if excel_field not in item:
                        continue

                    # Get value and convert if necessary
                    value = item[excel_field]
                    process_enum = getattr(ProcessEnum, process_enum_str.split(".")[-1])

                    # Determine data type and unit
                    datatype = DataType.STRING
                    unit = UnitEnum.NONE

                    if process_enum in [
                        ProcessEnum.X_COORDINATE,
                        ProcessEnum.Y_COORDINATE,
                        ProcessEnum.Z_COORDINATE,
                        ProcessEnum.WIDTH,
                        ProcessEnum.DIAMETER,
                        ProcessEnum.HEIGHT,
                    ]:
                        datatype = DataType.FLOAT
                        unit = UnitEnum.METER
                        value = float(value) if value != "" else 0.0

                    # For UUID references, ensure it's a UUID object
                    if process_enum == ProcessEnum.FOUNDATION_TO_MAST_UUID and value:
                        if isinstance(value, str) and value.strip():
                            if "-" not in value:
                                value = f"{value}-0000-0000-0000-000000000000"
                            value = UUID(value)
                            datatype = DataType.STRING

                    # Create parameter
                    parameter = Parameter(
                        name=excel_field,
                        value=value,
                        process=process_enum,
                        datatype=datatype,
                        unit=unit,
                    )
                    parameters.append(parameter)

                # Add parameters to the element
                foundation.parameters.extend(parameters)
                foundation._update_known_params()

                # Initialize components
                try:
                    # Ensure required coordinates are set
                    has_x = foundation.has_param(ProcessEnum.X_COORDINATE)
                    has_y = foundation.has_param(ProcessEnum.Y_COORDINATE)
                    has_z = foundation.has_param(ProcessEnum.Z_COORDINATE)

                    # Debug output
                    log.debug(f"Foundation {name} coordinates: X={has_x}, Y={has_y}, Z={has_z}")

                    # Manually add missing parameters if needed
                    if not has_x and "E" in item:
                        value = float(item["E"]) if item["E"] != "" else 0.0
                        param = Parameter(
                            name="E",
                            value=value,
                            process=ProcessEnum.X_COORDINATE,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        foundation.parameters.append(param)
                        foundation._update_known_params()
                        log.debug(f"Added missing X-coordinate from E: {value}")
                    elif not has_x:
                        log.error(f"Foundation {name} missing X-coordinate")
                        continue

                    if not has_y and "N" in item:
                        value = float(item["N"]) if item["N"] != "" else 0.0
                        param = Parameter(
                            name="N",
                            value=value,
                            process=ProcessEnum.Y_COORDINATE,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        foundation.parameters.append(param)
                        foundation._update_known_params()
                        log.debug(f"Added missing Y-coordinate from N: {value}")
                    elif not has_y:
                        log.error(f"Foundation {name} missing Y-coordinate")
                        continue

                    if not has_z and "H-RSRG" in item:
                        value = float(item["H-RSRG"]) if item["H-RSRG"] != "" else 0.0
                        param = Parameter(
                            name="H-RSRG",
                            value=value,
                            process=ProcessEnum.Z_COORDINATE,
                            datatype=DataType.FLOAT,
                            unit=UnitEnum.METER,
                        )
                        foundation.parameters.append(param)
                        foundation._update_known_params()
                        log.debug(f"Added missing Z-coordinate from H-RSRG: {value}")
                    elif not has_z:
                        log.error(f"Foundation {name} missing Z-coordinate")
                        continue

                    foundation._initialize_components()
                    foundations.append(foundation)
                except Exception as e:
                    log.error(f"Error initializing components for foundation {name}: {e}")
                    continue

            except Exception as e:
                log.error(f"Error converting foundation: {e}")
                continue

        return foundations

    def _convert_ausleger(
        self, data: List[Dict[str, Any]], mapping: Dict[str, str]
    ) -> List[InfrastructureElement]:
        """Konvertiert Ausleger-Daten."""
        cantilevers = []

        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Family", "Unbenannter Ausleger")
                uuid_str = item.get("UUID", "")

                cantilever = Cantilever(name=name)

                if uuid_str:
                    cantilever.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter basierend auf Mapping hinzufügen
                parameters = []
                for excel_field, process_enum_str in mapping.items():
                    if excel_field not in item:
                        continue

                    # Get value and convert if necessary
                    value = item[excel_field]
                    process_enum = getattr(ProcessEnum, process_enum_str.split(".")[-1])

                    # Determine data type and unit
                    datatype = DataType.STRING
                    unit = UnitEnum.NONE

                    if process_enum in [
                        ProcessEnum.X_COORDINATE,
                        ProcessEnum.Y_COORDINATE,
                        ProcessEnum.Z_COORDINATE,
                        ProcessEnum.X_COORDINATE_END,
                        ProcessEnum.Y_COORDINATE_END,
                        ProcessEnum.Z_COORDINATE_END,
                        ProcessEnum.WIDTH,
                        ProcessEnum.DIAMETER,
                        ProcessEnum.DEPTH,
                    ]:
                        datatype = DataType.FLOAT
                        unit = UnitEnum.METER
                        value = float(value) if value != "" else 0.0

                    # For UUID references, ensure it's a UUID object
                    if process_enum == ProcessEnum.CANTILEVER_TO_MAST_UUID and value:
                        if isinstance(value, str) and value.strip():
                            if "-" not in value:
                                value = f"{value}-0000-0000-0000-000000000000"
                            value = UUID(value)
                            datatype = DataType.STRING

                    # Create parameter
                    parameter = Parameter(
                        name=excel_field,
                        value=value,
                        process=process_enum,
                        datatype=datatype,
                        unit=unit,
                    )
                    parameters.append(parameter)

                # Add parameters to the element
                cantilever.parameters.extend(parameters)
                cantilever._update_known_params()

                # Initialize components
                try:
                    # Ensure required coordinates are set
                    if not cantilever.has_param(ProcessEnum.X_COORDINATE):
                        log.error(f"Cantilever {name} missing X-coordinate")
                        continue
                    if not cantilever.has_param(ProcessEnum.Y_COORDINATE):
                        log.error(f"Cantilever {name} missing Y-coordinate")
                        continue
                    if not cantilever.has_param(ProcessEnum.Z_COORDINATE):
                        log.error(f"Cantilever {name} missing Z-coordinate")
                        continue

                    cantilever._initialize_components()
                    cantilevers.append(cantilever)
                except Exception as e:
                    log.error(f"Error initializing components for cantilever {name}: {e}")
                    continue

            except Exception as e:
                log.error(f"Error converting cantilever: {e}")
                continue

        return cantilevers
