"""
SBB-Plugin für DFA Daten.
Dieses Plugin konvertiert Daten aus DFA Excel-Dateien in das kanonische Datenmodell.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pyarm.factories.parameter import ParameterFactory
from pyarm.interfaces.plugin import ConversionResult, PluginInterface
from pyarm.linking.element_linker import ElementLinker, LinkDefinition
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.element_models import (
    CableShaft,
    Cantilever,
    Foundation,
    Mast,
    SewerPipe,
    SewerShaft,
)
from pyarm.models.parameter import Parameter
from pyarm.models.process_enums import ElementType, ProcessEnum

from . import parameters as param
from .reader import DfaExcelReader

log = logging.getLogger(__name__)


class SBBPlugin(PluginInterface):
    """
    SBB-Plugin für DFA Daten.
    Implementiert die Konvertierung von DFA Excel-Daten in das kanonische Datenmodell.
    """

    def __init__(self):
        self.mapping: Dict[str, Dict[str, ProcessEnum]] = {}
        self._debug_mode = False
        self.data: Dict[str, Any] = {}
        self.element_type_map: Dict[ElementType, str] = {}

    @property
    def name(self) -> str:
        return "DFA Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin mit der Konfiguration."""
        log.info(f"Initialisiere {self.name} v{self.version}")
        log.debug(f"Konfiguration: {config}")

        self.element_type_map = {
            ElementType.SEWER_PIPE: "Abwasser_Haltung",
            ElementType.SEWER_SHAFT: "Abwasser_Schacht",
            ElementType.MAST: "Mast",
            ElementType.CANTILEVER: "Ausleger",
            ElementType.JOCH: "Joch",
            ElementType.FOUNDATION: "Fundament",
            ElementType.CABLE_SHAFT: "Alle Kabelschacht",
        }

        # Set debug mode if specified
        if config and "debug" in config:
            self._debug_mode = config["debug"]
            if self._debug_mode:
                log.setLevel(logging.DEBUG)
                log.debug("Debug mode enabled")

        return True

    def load_data_from_directory(self, directory_path: Union[str, Path]) -> None:
        """Lädt alle relevanten Daten aus dem angegebenen Verzeichnis."""
        directory = Path(directory_path) if isinstance(directory_path, str) else directory_path
        excel_files = [xls for xls in directory.glob("*.xlsx") if not xls.name.startswith("~")]

        if not excel_files:
            log.warning(f"Keine Excel-Dateien im Verzeichnis gefunden: {directory}")
            return

        excel_file = excel_files[0]
        log.info(f"Lese Excel-Datei: {excel_file}")

        try:
            # Reader verwenden, um die Datei zu lesen
            reader = DfaExcelReader()
            self.data = reader.read_excel(excel_file)

        except Exception as e:
            log.error(f"Fehler beim Lesen der Excel-Datei {excel_file}: {e}")

        mapping_file = directory / "dfa_report.json"
        try:
            # Reader verwenden, um die Datei zu lesen
            with open(mapping_file, "r", encoding="utf-8") as jf:
                mapping = json.load(jf)
            if not isinstance(mapping, dict):
                raise ValueError(f"{mapping_file}: Expected dict, got {type(mapping)}")
            for sheet, sheet_map in mapping.items():
                sheet_map = {key: getattr(ProcessEnum, value) for key, value in sheet_map.items()}
                self.mapping[sheet] = sheet_map

        except Exception as e:
            log.error(f"Error reading mapping file {mapping_file}: {e}")

        custom_definitions = param.get_custom_definitions(self.data["excel_data"])
        ParameterFactory.add_custom_definitions(custom_definitions)

    def get_supported_element_types(self) -> List[ElementType]:
        """Gibt die unterstützten Elementtypen zurück."""
        return list(self.element_type_map.keys())

    def convert_element(self, element_type: ElementType) -> Optional[ConversionResult]:
        if element_type not in self.get_supported_element_types():
            log.warning(f"Elementtyp {element_type} wird nicht unterstützt")
            return None

        # String-Elementtyp für interne Konvertierungen verwenden
        sheet_name = self.element_type_map.get(element_type)
        if sheet_name is None:
            log.warning(f"Keine Mapping-Konfiguration für Elementtyp {element_type}")
            return None

        # Get the appropriate data from Excel based on element type
        excel_data = self.data.get("excel_data", None)
        if excel_data is None:
            log.warning(f"Keine gültigen Excel-Daten für Elementtyp {element_type} vorhanden")
            return None

        sheet_data = excel_data.get(sheet_name, None)
        if sheet_data is None:
            log.warning(f"Keine gültige Excel-Daten für {sheet_name} vorhanden")
            return None

        # Check if Family column exists
        if "Family" not in sheet_data.columns:
            log.warning("Excel-Daten enthalten keine 'Family'-Spalte")
            return None

        # Convert data to list of dictionaries
        records = sheet_data.to_dict(orient="records")
        parameter_mapping = self.mapping.get(sheet_name, {})

        # Convert based on element type string
        function_name = f"_convert_{element_type.name.lower()}"
        converter_method = getattr(self, function_name, None)
        if converter_method is None:
            log.warning(f"Keine Konvertierungsmethode für {element_type} gefunden")
            return None

        converted_elements = converter_method(records, parameter_mapping)

        if not converted_elements:
            log.warning(f"Konvertierung für {element_type} ergab keine Elemente")
            return None

        return ConversionResult(
            element_type=element_type,
            elements=converted_elements,
            plugin_name=self.name,
        )

    def _create_element_name(self, data: Dict[str, Any], element_type: ElementType) -> str:
        family_name = data.get("Family", f"Unbenannte {element_type.name}")
        type_name = data.get("TypeName", "NO TYPE NAME")
        return f"{family_name} - {type_name}"

    def _convert_parameters(
        self, data: Dict[str, Any], mapping: Dict[str, ProcessEnum]
    ) -> List[Parameter]:
        parameters = []
        for column, value in data.items():
            process_enum = mapping.get(column, None)
            parameter = ParameterFactory.create(column, process_enum, value)
            parameters.append(parameter)
        return parameters

    def _convert_sewer_pipe(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Abwasser-Leitungsdaten."""
        drainage_pipes = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.SEWER_PIPE)
                parameters = self._convert_parameters(item, mapping)
                element = SewerPipe(name=name, parameters=parameters)
                drainage_pipes.append(element)

            except Exception as e:
                log.error(f"Error converting drainage pipe: {e}")
                continue

        return drainage_pipes

    def _convert_sewer_shaft(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Abwasser-Schachtdaten."""
        drainage_shafts = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.SEWER_SHAFT)
                parameters = self._convert_parameters(item, mapping)
                element = SewerShaft(name=name, parameters=parameters)
                drainage_shafts.append(element)

            except Exception as e:
                log.error(f"Error converting drainage shaft: {e}")
                continue

        return drainage_shafts

    def _convert_cable_shaft(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Kabelschacht-Daten."""
        cable_shafts = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.CABLE_SHAFT)
                parameters = self._convert_parameters(item, mapping)
                element = CableShaft(name=name, parameters=parameters)
                cable_shafts.append(element)

            except Exception as e:
                log.error(f"Error converting drainage shaft: {e}")
                continue

        return cable_shafts

    def _convert_mast(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten."""
        masts = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.MAST)
                parameters = self._convert_parameters(item, mapping)
                element = Mast(name=name, parameters=parameters)
                masts.append(element)

            except Exception as e:
                log.error(f"Error converting mast: {e}")
                continue

        return masts

    def _convert_foundation(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten."""
        foundations = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.FOUNDATION)
                parameters = self._convert_parameters(item, mapping)
                element = Foundation(name=name, parameters=parameters)
                foundations.append(element)
            except Exception as e:
                log.error(f"Error converting foundation: {e}")
                continue

        return foundations

    def _link_foundation(self, manager: ElementLinker) -> None:
        """Konvertiert Ausleger-Daten."""
        definition = LinkDefinition(
            source_type=Foundation,
            source_param_name="Mast Master FID",
            target_type=Mast,
            target_param_name="FID",
            bidirectional=True,
        )
        manager.register_link_definition(definition)

    def _convert_cantilever(
        self, data: List[Dict[str, Any]], mapping: Dict[str, ProcessEnum]
    ) -> List[InfrastructureElement]:
        """Konvertiert Ausleger-Daten."""
        cantilevers = []

        for item in data:
            try:
                name = self._create_element_name(item, ElementType.CANTILEVER)
                parameters = self._convert_parameters(item, mapping)
                element = Cantilever(name=name, parameters=parameters)
                cantilevers.append(element)
            except Exception as e:
                log.error(f"Error converting cantilever: {e}")
                continue

        return cantilevers

    def _link_cantilever(self, manager: ElementLinker) -> None:
        """Konvertiert Ausleger-Daten."""
        definition = LinkDefinition(
            source_type=Cantilever,
            source_param_name="MasterFID",
            target_type=Mast,
            target_param_name="FID",
            bidirectional=True,
            try_link_with_coordinate=True,
            offset_coordinate=0.3,
        )
        manager.register_link_definition(definition)

    def define_element_links(self, linker_manager: ElementLinker) -> None:
        # Convert based on element type string
        for element_type in self.get_supported_element_types():
            link_method = getattr(self, f"_link_{element_type}", None)
            if link_method is None:
                log.debug(f"Keine Link-Methode für {element_type} gefunden")
                continue
            link_method(linker_manager)
