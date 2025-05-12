"""
Client-Plugin für ClientA.
Dieses Plugin konvertiert Daten des ClientA in das kanonische Datenmodell.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional
from uuid import UUID

# Ensure pyarm is in the path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
src_path = os.path.join(base_dir, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from pyarm.interfaces.plugin import PluginInterface
    from pyarm.models.base_models import InfrastructureElement
    from pyarm.models.element_models import (
        CurvedTrack,
        DrainagePipe,
        DrainageShaft,
        Foundation,
        Joch,
        Mast,
        Track,
    )
    from pyarm.models.parameter import DataType, Parameter, UnitEnum
    from pyarm.models.process_enums import ProcessEnum
except ImportError:
    # If that fails, try direct import from src
    from src.pyarm.interfaces.plugin import PluginInterface
    from src.pyarm.models.base_models import InfrastructureElement
    from src.pyarm.models.element_models import (
        CurvedTrack,
        DrainagePipe,
        DrainageShaft,
        Foundation,
        Joch,
        Mast,
        Track,
    )
    from src.pyarm.models.parameter import DataType, Parameter, UnitEnum
    from src.pyarm.models.process_enums import ProcessEnum

log = logging.getLogger(__name__)


class ClientAPlugin(PluginInterface):
    """
    Client-Plugin für ClientA.
    Implementiert die Konvertierung von ClientA-Daten in das kanonische Datenmodell.
    """

    @property
    def name(self) -> str:
        return "ClientA Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialisiert das Plugin mit der Konfiguration."""
        log.info(f"Initialisiere {self.name} v{self.version}")
        log.debug(f"Konfiguration: {config}")
        return True

    def get_supported_element_types(self) -> List[str]:
        """Gibt die unterstützten Elementtypen zurück."""
        return ["foundation", "mast", "joch", "track", "curved_track", "drainage"]

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

        element_data = data.get("data", [])
        project_id = data.get("project_id", "unknown")

        if not element_data:
            log.warning(f"Keine Daten für Elementtyp {element_type} vorhanden")
            return None

        # Je nach Projekt unterschiedliche Konvertierungsfunktionen verwenden
        converter_method = None
        if project_id == "project1":
            converter_method = getattr(self, f"_convert_{element_type}_project1", None)
        elif project_id == "project2":
            converter_method = getattr(self, f"_convert_{element_type}_project2", None)

        if converter_method is None:
            converter_method = getattr(self, f"_convert_{element_type}", None)

        if converter_method is None:
            log.warning(
                f"Keine Konvertierungsmethode für {element_type} in Projekt {project_id} gefunden"
            )
            return None

        converted_elements = converter_method(element_data, project_id)

        if not converted_elements:
            log.warning(
                f"Konvertierung für {element_type} in Projekt {project_id} ergab keine Elemente"
            )
            return None

        # Konvertiere die Elemente in ein Dictionary für die Serialisierung
        serialized_elements = [element.to_dict() for element in converted_elements]

        return {
            "element_type": element_type,
            "project_id": project_id,
            "elements": serialized_elements,
            "converted_by": self.name,
        }

    def _convert_foundation(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten (generische Methode)."""
        if project_id == "project1":
            return self._convert_foundation_project1(data, project_id)
        elif project_id == "project2":
            return self._convert_foundation_project2(data, project_id)
        else:
            log.warning(f"Unbekanntes Projekt {project_id} für Fundamentkonvertierung")
            return []

    def _convert_foundation_project1(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten aus Projekt 1."""
        foundations = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Bezeichnung", "Unbenanntes Fundament")
                uuid_str = item.get("ID", "")

                foundation = Foundation(name=name)

                if uuid_str:
                    foundation.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Breite",
                        value=float(item.get("Breite", 0)),
                        process=ProcessEnum.WIDTH,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Tiefe",
                        value=float(item.get("Tiefe", 0)),
                        process=ProcessEnum.DEPTH,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Höhe",
                        value=float(item.get("Höhe", 0)),
                        process=ProcessEnum.HEIGHT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Typ",
                        value=item.get("Typ", ""),
                        process=ProcessEnum.FOUNDATION_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Material",
                        value=item.get("Material", ""),
                        process=ProcessEnum.IFC_MATERIAL,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                ]

                # Referenz zum Mast hinzufügen, falls vorhanden
                if "MastID" in item and item["MastID"]:
                    mast_uuid = item["MastID"]
                    if "-" not in mast_uuid:
                        mast_uuid = f"{mast_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="MastID",
                            value=UUID(mast_uuid),
                            process=ProcessEnum.FOUNDATION_TO_MAST_UUID,
                            datatype=DataType.STRING,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Parameter zur Foundation hinzufügen
                foundation.parameters.extend(parameters)
                foundation._update_known_params()

                # Komponenten manuell initialisieren mit expliziter Überprüfung
                try:
                    # Manuell sicherstellen, dass die erforderlichen Koordinaten gesetzt sind
                    if not foundation.has_param(ProcessEnum.X_COORDINATE):
                        log.error(f"Fundament {name} fehlt X-Koordinate")
                        continue
                    if not foundation.has_param(ProcessEnum.Y_COORDINATE):
                        log.error(f"Fundament {name} fehlt Y-Koordinate")
                        continue
                    if not foundation.has_param(ProcessEnum.Z_COORDINATE):
                        log.error(f"Fundament {name} fehlt Z-Koordinate")
                        continue

                    # Jetzt können wir die Komponenten initialisieren
                    foundation._initialize_components()
                    foundations.append(foundation)
                except Exception as e:
                    log.error(
                        f"Fehler bei der Initialisierung der Komponenten für Fundament {name}: {e}"
                    )
                    continue

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Fundament: {e}")
                continue

        return foundations

    def _convert_foundation_project2(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Fundament-Daten aus Projekt 2 (andere Namenskonvention)."""
        foundations = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Name", "Unbenanntes Fundament")
                uuid_str = item.get("UUID", "")

                foundation = Foundation(name=name)

                if uuid_str:
                    foundation.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="UUID",
                        value=item.get("UUID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Name",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="East",
                        value=float(item.get("East", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="North",
                        value=float(item.get("North", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Height",
                        value=float(item.get("Height", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Width",
                        value=float(item.get("Width", 0)),
                        process=ProcessEnum.WIDTH,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Depth",
                        value=float(item.get("Depth", 0)),
                        process=ProcessEnum.DEPTH,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="HeightFoundation",
                        value=float(item.get("HeightFoundation", 0)),
                        process=ProcessEnum.HEIGHT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="FoundationType",
                        value=item.get("FoundationType", ""),
                        process=ProcessEnum.FOUNDATION_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Material",
                        value=item.get("Material", ""),
                        process=ProcessEnum.IFC_MATERIAL,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                ]

                # Referenz zum Mast hinzufügen, falls vorhanden
                if "MastReference" in item and item["MastReference"]:
                    mast_uuid = item["MastReference"]
                    if "-" not in mast_uuid:
                        mast_uuid = f"{mast_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="MastReference",
                            value=UUID(mast_uuid),
                            process=ProcessEnum.FOUNDATION_TO_MAST_UUID,
                            datatype=DataType.UUID,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Parameter zur Foundation hinzufügen
                foundation.parameters.extend(parameters)
                foundation._update_known_params()

                # Komponenten manuell initialisieren mit expliziter Überprüfung
                try:
                    # Manuell sicherstellen, dass die erforderlichen Koordinaten gesetzt sind
                    if not foundation.has_param(ProcessEnum.X_COORDINATE):
                        log.error(f"Fundament {name} fehlt X-Koordinate")
                        continue
                    if not foundation.has_param(ProcessEnum.Y_COORDINATE):
                        log.error(f"Fundament {name} fehlt Y-Koordinate")
                        continue
                    if not foundation.has_param(ProcessEnum.Z_COORDINATE):
                        log.error(f"Fundament {name} fehlt Z-Koordinate")
                        continue

                    # Jetzt können wir die Komponenten initialisieren
                    foundation._initialize_components()
                    foundations.append(foundation)
                except Exception as e:
                    log.error(
                        f"Fehler bei der Initialisierung der Komponenten für Fundament {name}: {e}"
                    )
                    continue

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Fundament (Projekt 2): {e}")
                continue

        return foundations

    def _convert_mast(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten (generische Methode)."""
        if project_id == "project1":
            return self._convert_mast_project1(data, project_id)
        elif project_id == "project2":
            return self._convert_mast_project2(data, project_id)
        else:
            log.warning(f"Unbekanntes Projekt {project_id} für Mastkonvertierung")
            return []

    def _convert_mast_project1(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten aus Projekt 1."""
        masts = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Bezeichnung", "Unbenannter Mast")
                uuid_str = item.get("ID", "")

                mast = Mast(name=name)

                if uuid_str:
                    mast.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Höhe",
                        value=float(item.get("Höhe", 0)),
                        process=ProcessEnum.HEIGHT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Azimut",
                        value=float(item.get("Azimut", 0)),
                        process=ProcessEnum.Z_ROTATION,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.DEGREE,
                    ),
                    Parameter(
                        name="Typ",
                        value=item.get("Typ", ""),
                        process=ProcessEnum.MAST_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Profiltyp",
                        value=item.get("Profiltyp", ""),
                        process=ProcessEnum.MAST_PROFILE_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Material",
                        value=item.get("Material", ""),
                        process=ProcessEnum.IFC_MATERIAL,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                ]

                # Referenz zum Fundament hinzufügen, falls vorhanden
                if "FundamentID" in item and item["FundamentID"]:
                    fund_uuid = item["FundamentID"]
                    if "-" not in fund_uuid:
                        fund_uuid = f"{fund_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="FundamentID",
                            value=UUID(fund_uuid),
                            process=ProcessEnum.MAST_TO_FOUNDATION_UUID,
                            datatype=DataType.STRING,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Parameter zum Mast hinzufügen
                mast.parameters.extend(parameters)
                mast._update_known_params()
                mast._initialize_components()

                masts.append(mast)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Mast: {e}")
                continue

        return masts

    def _convert_mast_project2(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Mast-Daten aus Projekt 2 (andere Namenskonvention)."""
        masts = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Name", "Unbenannter Mast")
                uuid_str = item.get("UUID", "")

                mast = Mast(name=name)

                if uuid_str:
                    mast.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="UUID",
                        value=item.get("UUID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Name",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="East",
                        value=float(item.get("East", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="North",
                        value=float(item.get("North", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Height",
                        value=float(item.get("Height", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="MastHeight",
                        value=float(item.get("MastHeight", 0)),
                        process=ProcessEnum.HEIGHT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Azimuth",
                        value=float(item.get("Azimuth", 0)),
                        process=ProcessEnum.Z_ROTATION,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.DEGREE,
                    ),
                    Parameter(
                        name="MastType",
                        value=item.get("MastType", ""),
                        process=ProcessEnum.MAST_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="ProfileType",
                        value=item.get("ProfileType", ""),
                        process=ProcessEnum.MAST_PROFILE_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Material",
                        value=item.get("Material", ""),
                        process=ProcessEnum.IFC_MATERIAL,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                ]

                # Referenz zum Fundament hinzufügen, falls vorhanden
                if "FoundationReference" in item and item["FoundationReference"]:
                    fund_uuid = item["FoundationReference"]
                    if "-" not in fund_uuid:
                        fund_uuid = f"{fund_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="FoundationReference",
                            value=UUID(fund_uuid),
                            process=ProcessEnum.MAST_TO_FOUNDATION_UUID,
                            datatype=DataType.UUID,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Parameter zum Mast hinzufügen
                mast.parameters.extend(parameters)
                mast._update_known_params()
                mast._initialize_components()

                masts.append(mast)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Mast (Projekt 2): {e}")
                continue

        return masts

    def _convert_joch(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Joch-Daten."""
        jochs = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Bezeichnung", "Unbenanntes Joch")
                uuid_str = item.get("ID", "")

                joch = Joch(name=name)

                if uuid_str:
                    joch.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="E2",
                        value=float(item.get("E2", 0)),
                        process=ProcessEnum.X_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N2",
                        value=float(item.get("N2", 0)),
                        process=ProcessEnum.Y_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z2",
                        value=float(item.get("Z2", 0)),
                        process=ProcessEnum.Z_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Spannweite",
                        value=float(item.get("Spannweite", 0)),
                        process=ProcessEnum.JOCH_SPAN,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Typ",
                        value=item.get("Typ", ""),
                        process=ProcessEnum.JOCH_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Material",
                        value=item.get("Material", ""),
                        process=ProcessEnum.IFC_MATERIAL,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                ]

                # Referenzen zu den Masten hinzufügen, falls vorhanden
                if "Mast1ID" in item and item["Mast1ID"]:
                    mast_uuid = item["Mast1ID"]
                    if "-" not in mast_uuid:
                        mast_uuid = f"{mast_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="Mast1ID",
                            value=UUID(mast_uuid),
                            process=ProcessEnum.JOCH_TO_MAST_UUID,
                            datatype=DataType.STRING,
                            unit=UnitEnum.NONE,
                        )
                    )

                if "Mast2ID" in item and item["Mast2ID"]:
                    mast_uuid = item["Mast2ID"]
                    if "-" not in mast_uuid:
                        mast_uuid = f"{mast_uuid}-0000-0000-0000-000000000000"

                    parameters.append(
                        Parameter(
                            name="Mast2ID",
                            value=UUID(mast_uuid),
                            process=ProcessEnum.JOCH_TO_MAST_UUID,
                            datatype=DataType.STRING,
                            unit=UnitEnum.NONE,
                        )
                    )

                # Parameter zum Joch hinzufügen
                joch.parameters.extend(parameters)
                joch._update_known_params()
                joch._initialize_components()

                jochs.append(joch)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Joch: {e}")
                continue

        return jochs

    def _convert_track(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Gleis-Daten."""
        tracks = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Bezeichnung", "Unbenanntes Gleis")
                uuid_str = item.get("ID", "")

                track = Track(name=name)

                if uuid_str:
                    track.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="E2",
                        value=float(item.get("E2", 0)),
                        process=ProcessEnum.X_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N2",
                        value=float(item.get("N2", 0)),
                        process=ProcessEnum.Y_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z2",
                        value=float(item.get("Z2", 0)),
                        process=ProcessEnum.Z_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Spurweite",
                        value=float(item.get("Spurweite", 1.435)),
                        process=ProcessEnum.TRACK_GAUGE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Gleistyp",
                        value=item.get("Gleistyp", ""),
                        process=ProcessEnum.TRACK_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Überhöhung",
                        value=float(item.get("Überhöhung", 0)),
                        process=ProcessEnum.TRACK_CANT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.MILLIMETER,
                    ),
                ]

                # Parameter zum Track hinzufügen
                track.parameters.extend(parameters)
                track._update_known_params()
                track._initialize_components()

                tracks.append(track)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Gleis: {e}")
                continue

        return tracks

    def _convert_curved_track(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Kurvengleis-Daten."""
        curved_tracks = []
        for item in data:
            try:
                # Basisparameter erstellen
                name = item.get("Bezeichnung", "Unbenanntes Kurvengleis")
                uuid_str = item.get("ID", "")

                curved_track = CurvedTrack(name=name)

                if uuid_str:
                    curved_track.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="E2",
                        value=float(item.get("E2", 0)),
                        process=ProcessEnum.X_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N2",
                        value=float(item.get("N2", 0)),
                        process=ProcessEnum.Y_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z2",
                        value=float(item.get("Z2", 0)),
                        process=ProcessEnum.Z_COORDINATE_END,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Spurweite",
                        value=float(item.get("Spurweite", 1.435)),
                        process=ProcessEnum.TRACK_GAUGE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Gleistyp",
                        value=item.get("Gleistyp", ""),
                        process=ProcessEnum.TRACK_TYPE,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Überhöhung",
                        value=float(item.get("Überhöhung", 0)),
                        process=ProcessEnum.TRACK_CANT,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.MILLIMETER,
                    ),
                    Parameter(
                        name="Klothoidenparameter",
                        value=float(item.get("Klothoidenparameter", 0)),
                        process=ProcessEnum.CLOTHOID_PARAMETER,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Startradius",
                        value=float(item.get("Startradius", 0)),
                        process=ProcessEnum.START_RADIUS,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Endradius",
                        value=float(item.get("Endradius", 0)),
                        process=ProcessEnum.END_RADIUS,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                ]

                # Parameter zum CurvedTrack hinzufügen
                curved_track.parameters.extend(parameters)
                curved_track._update_known_params()
                curved_track._initialize_components()

                curved_tracks.append(curved_track)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Kurvengleis: {e}")
                continue

        return curved_tracks

    def _convert_drainage(
        self, data: List[Dict[str, Any]], project_id: str
    ) -> List[InfrastructureElement]:
        """Konvertiert Entwässerungs-Daten."""
        drainage_elements = []
        for item in data:
            try:
                # Element-Typ bestimmen
                element_typ = item.get("Typ", "").lower()
                name = item.get("Bezeichnung", "Unbenannte Entwässerung")
                uuid_str = item.get("ID", "")

                if element_typ == "pipe":
                    # Entwässerungsleitung erstellen
                    element = DrainagePipe(name=name)
                elif element_typ in ["shaft", "manhole"]:
                    # Entwässerungsschacht erstellen
                    element = DrainageShaft(name=name)
                else:
                    log.warning(f"Unbekannter Entwässerungstyp: {element_typ}")
                    continue

                if uuid_str:
                    element.uuid = (
                        UUID(uuid_str)
                        if "-" in uuid_str
                        else UUID(f"{uuid_str}-0000-0000-0000-000000000000")
                    )

                # Parameter hinzufügen
                parameters = [
                    Parameter(
                        name="ID",
                        value=item.get("ID", ""),
                        process=ProcessEnum.UUID,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="Bezeichnung",
                        value=name,
                        process=ProcessEnum.NAME,
                        datatype=DataType.STRING,
                        unit=UnitEnum.NONE,
                    ),
                    Parameter(
                        name="E",
                        value=float(item.get("E", 0)),
                        process=ProcessEnum.X_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="N",
                        value=float(item.get("N", 0)),
                        process=ProcessEnum.Y_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="Z",
                        value=float(item.get("Z", 0)),
                        process=ProcessEnum.Z_COORDINATE,
                        datatype=DataType.FLOAT,
                        unit=UnitEnum.METER,
                    ),
                ]

                # Typspezifische Parameter
                if element_typ == "pipe":
                    # Endpunkt für Leitungen
                    parameters.extend(
                        [
                            Parameter(
                                name="E2",
                                value=float(item.get("E2", 0)),
                                process=ProcessEnum.X_COORDINATE_END,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.METER,
                            ),
                            Parameter(
                                name="N2",
                                value=float(item.get("N2", 0)),
                                process=ProcessEnum.Y_COORDINATE_END,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.METER,
                            ),
                            Parameter(
                                name="Z2",
                                value=float(item.get("Z2", 0)),
                                process=ProcessEnum.Z_COORDINATE_END,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.METER,
                            ),
                            Parameter(
                                name="Durchmesser",
                                value=float(item.get("Durchmesser", 0)),
                                process=ProcessEnum.DIAMETER,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.MILLIMETER,
                            ),
                            Parameter(
                                name="Material",
                                value=item.get("Material", ""),
                                process=ProcessEnum.PIPE_MATERIAL,
                                datatype=DataType.STRING,
                                unit=UnitEnum.NONE,
                            ),
                            Parameter(
                                name="Gefälle",
                                value=float(item.get("Gefälle", 0)),
                                process=ProcessEnum.SLOPE,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.PROMILLE,
                            ),
                        ]
                    )
                elif element_typ in ["shaft", "manhole"]:
                    # Parameter für Schächte
                    if "Z2" in item and item["Z2"]:
                        # Z2 wird für Schächte als Durchmesser verwendet
                        parameters.append(
                            Parameter(
                                name="Z2",
                                value=float(item.get("Z2", 0)),
                                process=ProcessEnum.SHAFT_MANHOLE_DIAMETER,
                                datatype=DataType.FLOAT,
                                unit=UnitEnum.MILLIMETER,
                            )
                        )

                    if "Material" in item and item["Material"]:
                        parameters.append(
                            Parameter(
                                name="Material",
                                value=item.get("Material", ""),
                                process=ProcessEnum.IFC_MATERIAL,
                                datatype=DataType.STRING,
                                unit=UnitEnum.NONE,
                            )
                        )

                # Parameter zum Element hinzufügen
                element.parameters.extend(parameters)
                element._update_known_params()
                element._initialize_components()

                drainage_elements.append(element)

            except Exception as e:
                log.error(f"Fehler bei Konvertierung von Entwässerungselement: {e}")
                continue

        return drainage_elements
