"""
Client C spezifischer Datenkonverter.
"""

from typing import Any

from pyarm.models.base_models import InfrastructureElement, Parameter
from pyarm.models.process_enums import ElementType, ProcessEnum, UnitEnum
from pyarm.utils.factory import create_element


class ClientCConverter:
    """
    Konverter für Daten des Clients C.
    Konvertiert client-spezifische Daten in das kanonische Format.
    Besonderheit: Verarbeitet Daten aus SQL-Dateien mit Millimetern als Standardeinheit.
    """

    @property
    def name(self) -> str:
        return "ClientCConverter"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_types(self) -> list[str]:
        return ["foundation", "mast", "joch", "track", "curved_track", "drainage"]

    def can_convert(self, data: dict[str, Any]) -> bool:
        """
        Prüft, ob dieser Konverter die angegebenen Daten konvertieren kann.

        Args:
            data: Zu konvertierende Daten

        Returns:
            True, wenn dieser Konverter die Daten konvertieren kann
        """
        element_type = data.get("element_type", "").lower()
        return element_type in self.supported_types

    def convert(self, data: dict[str, Any]) -> list[InfrastructureElement]:
        """
        Konvertiert die angegebenen Daten in InfrastructureElement-Objekte.

        Args:
            data: Zu konvertierende Daten

        Returns:
            Liste der konvertierten Elemente
        """
        element_type = data.get("element_type", "").lower()
        raw_data = data.get("data", [])

        converter_method = getattr(self, f"_convert_{element_type}", None)
        if converter_method:
            return converter_method(raw_data)

        # Fallback auf generischen Konverter
        return self._convert_generic(raw_data, element_type)

    def _convert_foundation(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Fundament-Daten des Clients C.

        Args:
            data: Liste von Fundament-Daten

        Returns:
            Liste der konvertierten Fundament-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Fundament {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.FOUNDATION.value,
                "parameters": [],
            }

            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(
                    name="type",
                    value=item.get("type"),
                    process=ProcessEnum.FOUNDATION_TYPE,
                ),
                Parameter(
                    name="coord_x",
                    value=float(item.get("coord_x", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y",
                    value=float(item.get("coord_y", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z",
                    value=float(item.get("coord_z", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                # Umrechnung von Millimetern in Meter
                Parameter(
                    name="width_mm",
                    value=float(item.get("width_mm", 0)) / 1000,
                    process=ProcessEnum.FOUNDATION_WIDTH,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="depth_mm",
                    value=float(item.get("depth_mm", 0)) / 1000,
                    process=ProcessEnum.FOUNDATION_DEPTH,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="height_mm",
                    value=float(item.get("height_mm", 0)) / 1000,
                    process=ProcessEnum.FOUNDATION_HEIGHT,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="material",
                    value=item.get("material"),
                    process=ProcessEnum.MATERIAL,
                ),
            ]

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_mast(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Mast-Daten des Clients C.

        Args:
            data: Liste von Mast-Daten

        Returns:
            Liste der konvertierten Mast-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Mast {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.MAST.value,
                "parameters": [],
            }

            # Referenz zum Fundament
            if "foundation_id" in item:
                element_data["foundation_uuid"] = item.get("foundation_id")

            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.MAST_TYPE),
                Parameter(
                    name="coord_x",
                    value=float(item.get("coord_x", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y",
                    value=float(item.get("coord_y", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z",
                    value=float(item.get("coord_z", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                # Umrechnung von Millimetern in Meter
                Parameter(
                    name="height_mm",
                    value=float(item.get("height_mm", 0)) / 1000,
                    process=ProcessEnum.MAST_HEIGHT,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="azimuth",
                    value=float(item.get("azimuth", 0)),
                    process=ProcessEnum.AZIMUTH,
                    unit=UnitEnum.DEGREE,
                ),
                Parameter(
                    name="material",
                    value=item.get("material"),
                    process=ProcessEnum.MATERIAL,
                ),
                Parameter(
                    name="profile",
                    value=item.get("profile"),
                    process=ProcessEnum.MAST_PROFILE_TYPE,
                ),
            ]

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_joch(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Joch-Daten des Clients C.

        Args:
            data: Liste von Joch-Daten

        Returns:
            Liste der konvertierten Joch-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Joch {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.JOCH.value,
                "parameters": [],
            }

            # Referenzen zu den Masten
            if "mast_id1" in item:
                element_data["mast_uuid_1"] = item.get("mast_id1")
            if "mast_id2" in item:
                element_data["mast_uuid_2"] = item.get("mast_id2")

            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.JOCH_TYPE),
                Parameter(
                    name="coord_x1",
                    value=float(item.get("coord_x1", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y1",
                    value=float(item.get("coord_y1", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z1",
                    value=float(item.get("coord_z1", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_x2",
                    value=float(item.get("coord_x2", 0)),
                    process=ProcessEnum.X_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y2",
                    value=float(item.get("coord_y2", 0)),
                    process=ProcessEnum.Y_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z2",
                    value=float(item.get("coord_z2", 0)),
                    process=ProcessEnum.Z_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                # Umrechnung von Millimetern in Meter
                Parameter(
                    name="span_mm",
                    value=float(item.get("span_mm", 0)) / 1000,
                    process=ProcessEnum.JOCH_SPAN,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="material",
                    value=item.get("material"),
                    process=ProcessEnum.MATERIAL,
                ),
            ]

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_track(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Gleis-Daten des Clients C.

        Args:
            data: Liste von Gleis-Daten

        Returns:
            Liste der konvertierten Gleis-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Gleis {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.TRACK.value,
                "parameters": [],
            }

            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(
                    name="coord_x1",
                    value=float(item.get("coord_x1", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y1",
                    value=float(item.get("coord_y1", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z1",
                    value=float(item.get("coord_z1", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_x2",
                    value=float(item.get("coord_x2", 0)),
                    process=ProcessEnum.X_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y2",
                    value=float(item.get("coord_y2", 0)),
                    process=ProcessEnum.Y_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z2",
                    value=float(item.get("coord_z2", 0)),
                    process=ProcessEnum.Z_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                # Umrechnung von Millimetern in Meter
                Parameter(
                    name="gauge_mm",
                    value=float(item.get("gauge_mm", 0)) / 1000,
                    process=ProcessEnum.TRACK_GAUGE,
                    unit=UnitEnum.METER,
                ),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.TRACK_TYPE),
                Parameter(
                    name="cant_mm",
                    value=float(item.get("cant_mm", 0)),
                    process=ProcessEnum.TRACK_CANT,
                    unit=UnitEnum.MILLIMETER,
                ),
            ]

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_curved_track(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Kurvengleis-Daten des Clients C.

        Args:
            data: Liste von Kurvengleis-Daten

        Returns:
            Liste der konvertierten Kurvengleis-Elemente
        """
        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Kurvengleis {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": ElementType.TRACK.value,  # CurvedTrack ist ein spezieller Track
                "parameters": [],
            }

            # Startradius behandeln (kann NULL sein)
            start_radius = item.get("start_radius_m")
            if start_radius is None:
                start_radius = float("inf")

            # Parameter erstellen
            parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(
                    name="coord_x1",
                    value=float(item.get("coord_x1", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y1",
                    value=float(item.get("coord_y1", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z1",
                    value=float(item.get("coord_z1", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_x2",
                    value=float(item.get("coord_x2", 0)),
                    process=ProcessEnum.X_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y2",
                    value=float(item.get("coord_y2", 0)),
                    process=ProcessEnum.Y_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z2",
                    value=float(item.get("coord_z2", 0)),
                    process=ProcessEnum.Z_COORDINATE_END,
                    unit=UnitEnum.METER,
                ),
                # Umrechnung von Millimetern in Meter
                Parameter(
                    name="gauge_mm",
                    value=float(item.get("gauge_mm", 0)) / 1000,
                    process=ProcessEnum.TRACK_GAUGE,
                    unit=UnitEnum.METER,
                ),
                Parameter(name="type", value=item.get("type"), process=ProcessEnum.TRACK_TYPE),
                Parameter(
                    name="cant_mm",
                    value=float(item.get("cant_mm", 0)),
                    process=ProcessEnum.TRACK_CANT,
                    unit=UnitEnum.MILLIMETER,
                ),
                Parameter(
                    name="clothoid_param",
                    value=float(item.get("clothoid_param", 0)),
                    process=ProcessEnum.CLOTHOID_PARAMETER,
                ),
                Parameter(
                    name="start_radius_m",
                    value=start_radius,
                    process=ProcessEnum.START_RADIUS,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="end_radius_m",
                    value=float(item.get("end_radius_m", 0)),
                    process=ProcessEnum.END_RADIUS,
                    unit=UnitEnum.METER,
                ),
            ]

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_drainage(self, data: list[dict[str, Any]]) -> list[InfrastructureElement]:
        """
        Konvertiert Entwässerungs-Daten des Clients C.

        Args:
            data: Liste von Entwässerungs-Daten

        Returns:
            Liste der konvertierten Entwässerungs-Elemente
        """
        results = []
        for item in data:
            # Elementtyp bestimmen
            if item.get("type", "").lower() == "pipe":
                element_type = ElementType.DRAINAGE_PIPE.value
            elif item.get("type", "").lower() == "shaft":
                element_type = ElementType.DRAINAGE_SHAFT.value
            else:
                continue  # Unbekannter Typ

            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Entwässerung {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type,
                "parameters": [],
            }

            # Gemeinsame Parameter
            common_parameters = [
                Parameter(name="id", value=item.get("id"), process=ProcessEnum.UUID),
                Parameter(
                    name="coord_x1",
                    value=float(item.get("coord_x1", 0)),
                    process=ProcessEnum.X_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_y1",
                    value=float(item.get("coord_y1", 0)),
                    process=ProcessEnum.Y_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="coord_z1",
                    value=float(item.get("coord_z1", 0)),
                    process=ProcessEnum.Z_COORDINATE,
                    unit=UnitEnum.METER,
                ),
                Parameter(
                    name="material",
                    value=item.get("material"),
                    process=ProcessEnum.MATERIAL,
                ),
                # Durchmesser in Millimetern (bereits die korrekte Einheit)
                Parameter(
                    name="diameter_mm",
                    value=float(item.get("diameter_mm", 0)),
                    process=ProcessEnum.DIAMETER,
                    unit=UnitEnum.MILLIMETER,
                ),
            ]

            # Spezifische Parameter je nach Typ
            if element_type == ElementType.DRAINAGE_PIPE.value:
                # Bei Rohren können coord_x2, coord_y2, coord_z2 nicht NULL sein
                pipe_parameters = [
                    Parameter(
                        name="coord_x2",
                        value=float(item.get("coord_x2", 0)),
                        process=ProcessEnum.X_COORDINATE_END,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="coord_y2",
                        value=float(item.get("coord_y2", 0)),
                        process=ProcessEnum.Y_COORDINATE_END,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="coord_z2",
                        value=float(item.get("coord_z2", 0)),
                        process=ProcessEnum.Z_COORDINATE_END,
                        unit=UnitEnum.METER,
                    ),
                    Parameter(
                        name="slope_permille",
                        value=float(item.get("slope_permille", 0)),
                        process=ProcessEnum.PIPE_SLOPE,
                        unit=UnitEnum.PROMILLE,
                    ),
                ]
                parameters = common_parameters + pipe_parameters
            else:  # DRAINAGE_SHAFT
                # Spezifische Parameter für Schächte
                shaft_parameters = [
                    Parameter(
                        name="diameter_mm",
                        value=float(item.get("diameter_mm", 0)),
                        process=ProcessEnum.SHAFT_DIAMETER,
                        unit=UnitEnum.MILLIMETER,
                    ),
                ]
                parameters = common_parameters + shaft_parameters

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results

    def _convert_generic(
        self, data: list[dict[str, Any]], element_type_str: str
    ) -> list[InfrastructureElement]:
        """
        Generischer Konverter für unbekannte Datentypen.

        Args:
            data: Liste von Daten
            element_type_str: String-Repräsentation des Elementtyps

        Returns:
            Liste der konvertierten Elemente
        """
        # Elementtyp bestimmen
        element_type = None
        for et in ElementType:
            if et.value in element_type_str.lower():
                element_type = et
                break

        if not element_type:
            element_type = ElementType.UNDEFINED  # Fallback

        results = []
        for item in data:
            # Grundlegende Attribute
            element_data = {
                "name": item.get("name", f"Element {item.get('id', 'Unknown')}"),
                "uuid": item.get("id"),
                "element_type": element_type.value,
                "parameters": [],
            }

            # Parameter erstellen
            parameters = []
            for key, value in item.items():
                if value is None:
                    continue

                # Prozess-Enum versuchen zu finden
                process_enum = None
                for pe in ProcessEnum:
                    # Prüfen auf exakte Übereinstimmung oder Teil des Schlüssels
                    if pe.name.lower() == key.lower() or pe.name.lower() in key.lower():
                        process_enum = pe
                        break

                # Einheit bestimmen
                unit = UnitEnum.NONE
                if "_mm" in key.lower():
                    unit = UnitEnum.MILLIMETER
                    if "coord_" not in key.lower() and not isinstance(value, str):
                        # Umrechnung von Millimetern in Meter für nicht-Koordinaten
                        value = float(value) / 1000
                        unit = UnitEnum.METER
                elif "_m" in key.lower() and "coord_" not in key.lower():
                    unit = UnitEnum.METER
                elif "radius" in key.lower():
                    unit = UnitEnum.METER
                elif "azimuth" in key.lower() or "angle" in key.lower():
                    unit = UnitEnum.DEGREE
                elif "permille" in key.lower() or "promille" in key.lower():
                    unit = UnitEnum.PROMILLE

                parameters.append(Parameter(name=key, value=value, process=process_enum, unit=unit))

            element_data["parameters"] = parameters
            results.append(create_element(element_data))

        return results
