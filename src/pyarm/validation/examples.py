"""
Beispiele für die Implementierung und Verwendung von Validatoren.

Dieses Modul enthält Beispielimplementierungen von elementtyp-spezifischen
Validatoren und Beispielcode zur Demonstration der Verwendung des
Validierungssystems.
"""

import logging
import math
from typing import Any, Dict, Optional

from pyarm.models.parameter import DataType, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.validation.errors import (
    ValidationResult,
    ValidationWarning,
)
from pyarm.validation.validators import ElementValidator

log = logging.getLogger(__name__)


class FoundationValidator(ElementValidator):
    """
    Validiert speziell Foundation-Elemente mit zusätzlichen Prüfungen.
    """

    def __init__(self):
        """Initialisiert den FoundationValidator."""
        super().__init__(ElementType.FOUNDATION)

        # Zusätzliche Constraints für Foundation-spezifische Parameter
        schema = self._schemas[ElementType.FOUNDATION]

        # Typ-Constraints für zusätzliche Parameter
        schema.param_types.update(
            {
                ProcessEnum.FOUNDATION_TYPE: DataType.STRING,
                ProcessEnum.FOUNDATION_TO_MAST_UUID: DataType.STRING,
            }
        )

        # Dimension-Constraints
        schema.add_range_constraint(
            ProcessEnum.WIDTH,
            min_value=0.5,
            max_value=10.0,
            message="Foundation-Breite muss zwischen 0.5m und 10m liegen (ist: {value}m)",
        )
        schema.add_range_constraint(
            ProcessEnum.HEIGHT,
            min_value=0.3,
            max_value=5.0,
            message="Foundation-Höhe muss zwischen 0.3m und 5m liegen (ist: {value}m)",
        )
        schema.add_range_constraint(
            ProcessEnum.DEPTH,
            min_value=0.5,
            max_value=10.0,
            message="Foundation-Tiefe muss zwischen 0.5m und 10m liegen (ist: {value}m)",
        )

        # Enum-Constraint für Foundation-Typ
        schema.add_enum_constraint(
            ProcessEnum.FOUNDATION_TYPE,
            valid_values=["Block", "Platte", "Pfahl", "Streifenfundament", "Sonderfundament"],
            message="Foundation-Typ {value} ist ungültig. "
            "Gültige Werte: Block, Platte, Pfahl, Streifenfundament, Sonderfundament",
        )

        # Benutzerdefinierter Constraint für das Volumen
        # def validate_volume(
        #     width: Optional[float] = None,
        #     height: Optional[float] = None,
        #     depth: Optional[float] = None,
        # ) -> bool:
        #     """Prüft, ob ein sinnvolles Volumen vorliegt."""
        #     if width is None or height is None or depth is None:
        #         return False
        #     volume = width * height * depth
        #     return 0.1 <= volume <= 100.0  # Volumen in m³

        # Diesen Constraint können wir nicht direkt hinzufügen, da er mehrere Parameter betrifft
        # Stattdessen implementieren wir ihn in _validate_specific

    def _validate_specific(
        self,
        data: Dict[str, Any],
        element_type: ElementType,
        result: ValidationResult,
        element_id: Optional[str] = None,
    ) -> None:
        """
        Führt spezifische Validierung für Foundation-Elemente durch.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu validierenden Daten
        element_type : ElementType
            Der Elementtyp
        result : ValidationResult
            Das Validierungsergebnis, zu dem Fehler und Warnungen hinzugefügt werden können
        element_id : Optional[str]
            Die ID des Elements, falls verfügbar
        """
        super()._validate_specific(data, element_type, result, element_id)

        # Parameter aus den Daten extrahieren
        params = data.get("parameters", [])

        # Dimensionen für Volumenberechnung
        width, height, depth = None, None, None

        for param in params:
            if isinstance(param, dict):
                process = param.get("process")
                value = param.get("value")

                if process == ProcessEnum.WIDTH.value:
                    width = float(value) if value is not None else None
                elif process == ProcessEnum.HEIGHT.value:
                    height = float(value) if value is not None else None
                elif process == ProcessEnum.DEPTH.value:
                    depth = float(value) if value is not None else None

        # Volumenprüfung
        if width is not None and height is not None and depth is not None:
            volume = width * height * depth
            if volume < 0.1:
                result.add_warning(
                    ValidationWarning(
                        message=f"Foundation-Volumen ist sehr klein: {volume:.2f}m³",
                        context={
                            "width": width,
                            "height": height,
                            "depth": depth,
                            "volume": volume,
                        },
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )
            elif volume > 100.0:
                result.add_warning(
                    ValidationWarning(
                        message=f"Foundation-Volumen ist sehr groß: {volume:.2f}m³",
                        context={
                            "width": width,
                            "height": height,
                            "depth": depth,
                            "volume": volume,
                        },
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )

        # Prüfung auf plausibles Höhe-zu-Breite-Verhältnis
        if width is not None and height is not None:
            ratio = height / width if width > 0 else float("inf")
            if ratio > 5.0:
                result.add_warning(
                    ValidationWarning(
                        message=f"Ungewöhnliches Höhe-zu-Breite-Verhältnis: {ratio:.2f}",
                        context={"width": width, "height": height, "ratio": ratio},
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )


class MastValidator(ElementValidator):
    """
    Validiert speziell Mast-Elemente mit zusätzlichen Prüfungen.
    """

    def __init__(self):
        """Initialisiert den MastValidator."""
        super().__init__(ElementType.MAST)

        # Zusätzliche Constraints für Mast-spezifische Parameter
        schema = self._schemas[ElementType.MAST]

        # Mast-Typ und Profiltyp sind erforderlich
        schema.required_params.update(
            {
                ProcessEnum.MAST_TYPE,
                ProcessEnum.MAST_PROFILE_TYPE,
            }
        )

        # Typ-Constraints
        schema.param_types.update(
            {
                ProcessEnum.MAST_TYPE: DataType.STRING,
                ProcessEnum.MAST_PROFILE_TYPE: DataType.STRING,
                ProcessEnum.MAST_TO_FOUNDATION_UUID: DataType.STRING,
                ProcessEnum.MAST_TO_CANTILEVER_UUID: DataType.STRING,
                ProcessEnum.MAST_TO_JOCH_UUID: DataType.STRING,
                ProcessEnum.Z_ROTATION: DataType.FLOAT,
            }
        )

        # Einheiten
        schema.param_units.update(
            {
                ProcessEnum.Z_ROTATION: UnitEnum.DEGREE,
            }
        )

        # Höhenbeschränkungen
        schema.add_range_constraint(
            ProcessEnum.HEIGHT,
            min_value=3.0,
            max_value=50.0,
            message="Mast-Höhe muss zwischen 3m und 50m liegen (ist: {value}m)",
        )

        # Rotationsbeschränkungen
        schema.add_range_constraint(
            ProcessEnum.Z_ROTATION,
            min_value=0.0,
            max_value=360.0,
            message="Z-Rotation muss zwischen 0° und 360° liegen (ist: {value}°)",
        )

        # Enum-Constraint für Mast-Typ
        schema.add_enum_constraint(
            ProcessEnum.MAST_TYPE,
            valid_values=["Stahlmast", "Betonmast", "Holzmast", "Gittermast", "Sondermast"],
            message="Mast-Typ {value} ist ungültig. Gültige Werte: Stahlmast, "
            "Betonmast, Holzmast, Gittermast, Sondermast",
        )

    def _validate_specific(
        self,
        data: Dict[str, Any],
        element_type: ElementType,
        result: ValidationResult,
        element_id: Optional[str] = None,
    ) -> None:
        """
        Führt spezifische Validierung für Mast-Elemente durch.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu validierenden Daten
        element_type : ElementType
            Der Elementtyp
        result : ValidationResult
            Das Validierungsergebnis, zu dem Fehler und Warnungen hinzugefügt werden können
        element_id : Optional[str]
            Die ID des Elements, falls verfügbar
        """
        super()._validate_specific(data, element_type, result, element_id)

        # Parameter aus den Daten extrahieren
        params = data.get("parameters", [])

        # Relevante Parameter
        height, mast_type, foundation_ref = None, None, None

        for param in params:
            if isinstance(param, dict):
                process = param.get("process")
                value = param.get("value")

                if process == ProcessEnum.HEIGHT.value:
                    height = float(value) if value is not None else None
                elif process == ProcessEnum.MAST_TYPE.value:
                    mast_type = value
                elif process == ProcessEnum.MAST_TO_FOUNDATION_UUID.value:
                    foundation_ref = value

        # Prüfung auf fehlende Foundation-Referenz
        if not foundation_ref:
            result.add_warning(
                ValidationWarning(
                    message="Mast hat keine Referenz zu einem Fundament",
                    context={"mast_id": element_id},
                    element_type=element_type.value,
                    element_id=element_id,
                )
            )

        # Typ-spezifische Höhenprüfungen
        if height is not None and mast_type is not None:
            if mast_type == "Holzmast" and height > 15.0:
                result.add_warning(
                    ValidationWarning(
                        message=f"Holzmast mit ungewöhnlicher Höhe: {height}m (üblich bis 15m)",
                        context={"height": height, "mast_type": mast_type},
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )
            elif mast_type == "Stahlmast" and height < 5.0:
                result.add_warning(
                    ValidationWarning(
                        message=f"Stahlmast mit ungewöhnlich geringer Höhe: "
                        f"{height}m (üblich ab 5m)",
                        context={"height": height, "mast_type": mast_type},
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )


class TrackValidator(ElementValidator):
    """
    Validiert speziell Track-Elemente mit zusätzlichen Prüfungen.
    """

    def __init__(self):
        """Initialisiert den TrackValidator."""
        super().__init__(ElementType.TRACK)

        # Zusätzliche Constraints für Track-spezifische Parameter
        schema = self._schemas[ElementType.TRACK]

        # Endpunkte sind erforderlich
        schema.required_params.update(
            {
                ProcessEnum.X_COORDINATE_END,
                ProcessEnum.Y_COORDINATE_END,
                ProcessEnum.Z_COORDINATE_END,
                ProcessEnum.TRACK_GAUGE,
                ProcessEnum.TRACK_TYPE,
            }
        )

        # Typ-Constraints
        schema.param_types.update(
            {
                ProcessEnum.X_COORDINATE_END: DataType.FLOAT,
                ProcessEnum.Y_COORDINATE_END: DataType.FLOAT,
                ProcessEnum.Z_COORDINATE_END: DataType.FLOAT,
                ProcessEnum.TRACK_GAUGE: DataType.FLOAT,
                ProcessEnum.TRACK_TYPE: DataType.STRING,
                ProcessEnum.TRACK_CANT: DataType.FLOAT,
            }
        )

        # Einheiten
        schema.param_units.update(
            {
                ProcessEnum.X_COORDINATE_END: UnitEnum.METER,
                ProcessEnum.Y_COORDINATE_END: UnitEnum.METER,
                ProcessEnum.Z_COORDINATE_END: UnitEnum.METER,
                ProcessEnum.TRACK_GAUGE: UnitEnum.METER,
                ProcessEnum.TRACK_CANT: UnitEnum.MILLIMETER,
            }
        )

        # Spurweitenbeschränkungen
        schema.add_range_constraint(
            ProcessEnum.TRACK_GAUGE,
            min_value=0.6,
            max_value=1.676,
            message="Spurweite muss zwischen 0.6m und 1.676m liegen (ist: {value}m)",
        )

        # Überhöhungsbeschränkungen
        schema.add_range_constraint(
            ProcessEnum.TRACK_CANT,
            min_value=0.0,
            max_value=180.0,
            message="Überhöhung muss zwischen 0mm und 180mm liegen (ist: {value}mm)",
        )

        # Enum-Constraint für Gleistyp
        schema.add_enum_constraint(
            ProcessEnum.TRACK_TYPE,
            valid_values=["Hauptgleis", "Nebengleis", "Abstellgleis", "Rangiergleis"],
            message="Gleistyp {value} ist ungültig. Gültige Werte: Hauptgleis, "
            "Nebengleis, Abstellgleis, Rangiergleis",
        )

    def _validate_specific(
        self,
        data: Dict[str, Any],
        element_type: ElementType,
        result: ValidationResult,
        element_id: Optional[str] = None,
    ) -> None:
        """
        Führt spezifische Validierung für Track-Elemente durch.

        Parameters
        ----------
        data : Dict[str, Any]
            Die zu validierenden Daten
        element_type : ElementType
            Der Elementtyp
        result : ValidationResult
            Das Validierungsergebnis, zu dem Fehler und Warnungen hinzugefügt werden können
        element_id : Optional[str]
            Die ID des Elements, falls verfügbar
        """
        super()._validate_specific(data, element_type, result, element_id)

        # Parameter aus den Daten extrahieren
        params = data.get("parameters", [])

        # Koordinaten für Längenberechnung
        x, y, z = None, None, None
        x_end, y_end, z_end = None, None, None
        track_type, track_gauge = None, None

        for param in params:
            if not isinstance(param, dict):
                continue
            process = param.get("process")
            value = param.get("value")

            if process == ProcessEnum.X_COORDINATE.value:
                x = float(value) if value is not None else None
            elif process == ProcessEnum.Y_COORDINATE.value:
                y = float(value) if value is not None else None
            elif process == ProcessEnum.Z_COORDINATE.value:
                z = float(value) if value is not None else None
            elif process == ProcessEnum.X_COORDINATE_END.value:
                x_end = float(value) if value is not None else None
            elif process == ProcessEnum.Y_COORDINATE_END.value:
                y_end = float(value) if value is not None else None
            elif process == ProcessEnum.Z_COORDINATE_END.value:
                z_end = float(value) if value is not None else None
            elif process == ProcessEnum.TRACK_TYPE.value:
                track_type = value
            elif process == ProcessEnum.TRACK_GAUGE.value:
                track_gauge = float(value) if value is not None else None

        if x is None or y is None or z is None:
            result.add_warning(
                ValidationWarning(
                    message="Track-Element hat komplette Koordinaten (x, y, z) nicht definiert",
                    context={
                        "track_id": element_id,
                        "x-value": x,
                        "y-value": y,
                        "z-value": z,
                    },
                    element_type=element_type.value,
                    element_id=element_id,
                )
            )

        if x_end is None or y_end is None or z_end is None:
            result.add_warning(
                ValidationWarning(
                    message="Track-Element hat Endkoordinaten (x_end, y_end, z_end) "
                    "nicht definiert",
                    context={
                        "track_id": element_id,
                        "x_end-value": x_end,
                        "y_end-value": y_end,
                        "z_end-value": z_end,
                    },
                    element_type=element_type.value,
                    element_id=element_id,
                )
            )

        if x and y and z and x_end and y_end and z_end:
            # gleislänge berechnen
            dx = x_end - x
            dy = y_end - y
            dz = z_end - z
            length = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Zu kurzes Gleis?
            if length < 1.0:
                result.add_warning(
                    ValidationWarning(
                        message=f"Gleislänge ist sehr kurz: {length:.2f}m",
                        context={
                            "length": length,
                            "start": (x, y, z),
                            "end": (x_end, y_end, z_end),
                        },
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )

            # Steigung/Gefälle berechnen
            if abs(dx) > 0.001 or abs(dy) > 0.001:  # Vermeiden einer Division durch 0
                horizontal_distance = math.sqrt(dx * dx + dy * dy)
                slope_percent = abs(dz / horizontal_distance) * 100

                # Zu steiles Gefälle?
                if slope_percent > 4.0:
                    result.add_warning(
                        ValidationWarning(
                            message=f"Gleissteigung ist sehr steil: {slope_percent:.2f}%",
                            context={"slope_percent": slope_percent},
                            element_type=element_type.value,
                            element_id=element_id,
                        )
                    )

        # Spurweitenprüfung für Hauptgleise
        if track_type == "Hauptgleis" and track_gauge is not None:
            if not math.isclose(track_gauge, 1.435, abs_tol=0.01):
                result.add_warning(
                    ValidationWarning(
                        message=f"Hauptgleis mit ungewöhnlicher Spurweite: "
                        f"{track_gauge}m (Normalspur: 1.435m)",
                        context={"track_gauge": track_gauge, "track_type": track_type},
                        element_type=element_type.value,
                        element_id=element_id,
                    )
                )


def example_usage():
    """
    Beispielhafte Verwendung des Validierungssystems.
    """
    from pyarm.validation.service import ValidationService

    # ValidationService erstellen
    validation_service = ValidationService()

    # Validatoren erstellen und registrieren
    foundation_validator = FoundationValidator()
    mast_validator = MastValidator()
    track_validator = TrackValidator()

    validation_service.register_validator(foundation_validator)
    validation_service.register_validator(mast_validator)
    validation_service.register_validator(track_validator)

    # Beispiel für die Verwendung mit einem Plugin
    """
    # Plugin laden
    client_plugin = ClientAPlugin()

    # Plugin mit Validierung umhüllen
    validated_plugin = ValidationPluginWrapper.wrap_plugin(client_plugin, validation_service)

    # Plugin initialisieren
    config = {
        "validation": {
            "strict_mode": True,
            "ignore_warnings": False,
            "log_level": "INFO"
        },
        "other_config": "..."
    }
    validated_plugin.initialize(config)

    # Daten konvertieren (mit Validierung)
    data = {
        "project_id": "project1",
        "data": [
            {
                "Bezeichnung": "Fundament-1",
                "ID": "F001",
                "E": 1000.0,
                "N": 2000.0,
                "Z": 100.0,
                "Breite": 2.0,
                "Tiefe": 2.0,
                "Höhe": 1.0,
                "Typ": "Block",
                "Material": "Beton"
            }
        ]
    }

    result = validated_plugin.convert_element(data, "foundation")
    """

    # Direktes Beispiel zur Validierung eines Elements
    foundation_data = {
        "name": "Fundament-1",
        "uuid": "F001",
        "element_type": "foundation",
        "parameters": [
            {"name": "UUID", "value": "F001", "process": "uuid", "datatype": "str", "unit": ""},
            {
                "name": "Name",
                "value": "Fundament-1",
                "process": "name",
                "datatype": "str",
                "unit": "",
            },
            {
                "name": "ElementType",
                "value": "foundation",
                "process": "element_type",
                "datatype": "str",
                "unit": "",
            },
            {
                "name": "E",
                "value": 1000.0,
                "process": "x_coordinate",
                "datatype": "float",
                "unit": "m",
            },
            {
                "name": "N",
                "value": 2000.0,
                "process": "y_coordinate",
                "datatype": "float",
                "unit": "m",
            },
            {
                "name": "Z",
                "value": 100.0,
                "process": "z_coordinate",
                "datatype": "float",
                "unit": "m",
            },
            {"name": "Breite", "value": 2.0, "process": "width", "datatype": "float", "unit": "m"},
            {"name": "Tiefe", "value": 2.0, "process": "depth", "datatype": "float", "unit": "m"},
            {"name": "Höhe", "value": 1.0, "process": "height", "datatype": "float", "unit": "m"},
            {
                "name": "Typ",
                "value": "Block",
                "process": "foundation_type",
                "datatype": "str",
                "unit": "",
            },
            {
                "name": "Material",
                "value": "Beton",
                "process": "ifc_material",
                "datatype": "str",
                "unit": "",
            },
        ],
    }

    result = validation_service.validate_element(foundation_data, "foundation")
    log.info(f"Validierungsergebnis: {result}")

    # Mit einem Fehler (falsche Höhe)
    foundation_data_with_error = foundation_data.copy()
    # Parameter mit Tiefe 0 (ungültig)
    for param in foundation_data_with_error["parameters"]:
        if param["process"] == "height":
            param["value"] = 0.0

    result_with_error = validation_service.validate_element(
        foundation_data_with_error, "foundation"
    )
    log.info(f"Validierungsergebnis (mit Fehler): {result_with_error}")


if __name__ == "__main__":
    # Logging konfigurieren
    logging.basicConfig(level=logging.INFO)
    # Beispielverwendung ausführen
    example_usage()
