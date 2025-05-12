"""
Service für die Visualisierung von Infrastrukturelementen (Prozess 1).
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from pyarm.models.process_enums import ElementType, ProcessEnum
from pyarm.models.base_models import InfrastructureElement
from pyarm.models.element_models import Joch, Mast
from pyarm.interfaces.protocols import HasClothoid
from pyarm.utils.type_guards import (
    has_clothoid_capability,
    is_foundation,
    is_joch,
    is_mast,
    is_track,
)


class VisualizationService:
    """
    Service für die Visualisierung von Infrastrukturelementen.
    Bereitet Daten für den Visualisierungsprozess auf.
    """

    def __init__(self, repository):
        """
        Initialisiert den Service.

        Args:
            repository: Repository für den Zugriff auf Elemente
        """
        self.repository = repository

    def get_element(self, uuid: Union[UUID, str]) -> Optional[Dict[str, Any]]:
        """
        Ruft ein Element für die Visualisierung ab.

        Args:
            uuid: UUID des Elements

        Returns:
            Visualisierungsdaten für das Element oder None
        """
        element = self.repository.get_by_id(uuid)
        if element:
            return self._prepare_element_for_visualization(element)
        return None

    def get_elements_by_type(self, element_type: ElementType) -> List[Dict[str, Any]]:
        """
        Ruft Elemente eines bestimmten Typs für die Visualisierung ab.

        Args:
            element_type: Typ der abzurufenden Elemente

        Returns:
            Liste der Visualisierungsdaten für die Elemente
        """
        elements = self.repository.get_by_type(element_type)
        return [self._prepare_element_for_visualization(element) for element in elements]

    def get_all_elements(self) -> List[Dict[str, Any]]:
        """
        Ruft alle Elemente für die Visualisierung ab.

        Returns:
            Liste der Visualisierungsdaten für alle Elemente
        """
        elements = self.repository.get_all()
        return [self._prepare_element_for_visualization(element) for element in elements]

    def _prepare_element_for_visualization(self, element: InfrastructureElement) -> Dict[str, Any]:
        """
        Bereitet ein Element für die Visualisierung auf.

        Args:
            element: Das aufzubereitende Element

        Returns:
            Visualisierungsdaten für das Element
        """
        # Basisattribute für jedes Element
        result = {
            "id": str(element.uuid),
            "name": element.name,
            "type": element.element_type.value,
            "position": self._get_element_position(element),
        }

        # Elementspezifische Attribute hinzufügen
        if is_foundation(element):
            self._add_foundation_attributes(result, element)
        elif is_mast(element):
            self._add_mast_attributes(result, element)
        elif is_joch(element):
            self._add_joch_attributes(result, element)
        elif is_track(element):
            self._add_track_attributes(result, element)
            if has_clothoid_capability(element):
                self._add_curved_track_attributes(result, element)

        return result

    def _get_element_position(self, element: InfrastructureElement) -> Dict[str, Any]:
        """
        Extrahiert die Positionsdaten eines Elements.

        Args:
            element: Das Element

        Returns:
            Positionsdaten des Elements
        """
        position = {
            "x": element.get_param(ProcessEnum.X_COORDINATE, 0.0),
            "y": element.get_param(ProcessEnum.Y_COORDINATE, 0.0),
            "z": element.get_param(ProcessEnum.Z_COORDINATE, 0.0),
        }

        # Für lineare Elemente auch Endpunkt hinzufügen
        if element.get_param(ProcessEnum.X_COORDINATE_END) is not None:
            position["x2"] = element.get_param(ProcessEnum.X_COORDINATE_END, 0.0)
            position["y2"] = element.get_param(ProcessEnum.Y_COORDINATE_END, 0.0)
            position["z2"] = element.get_param(ProcessEnum.Z_COORDINATE_END, 0.0)

        # Azimut hinzufügen, wenn vorhanden
        azimuth = element.get_param(ProcessEnum.AZIMUTH)
        if azimuth is not None:
            position["azimuth"] = azimuth

        return position

    def _add_foundation_attributes(
        self, result: Dict[str, Any], element: InfrastructureElement
    ) -> None:
        """
        Fügt Foundation-spezifische Attribute hinzu.

        Args:
            result: Ergebnisdictionary
            element: Das Element
        """
        result["foundation_type"] = element.get_param(ProcessEnum.FOUNDATION_TYPE, "")
        result["dimensions"] = {
            "width": element.get_param(ProcessEnum.FOUNDATION_WIDTH, 0.0),
            "depth": element.get_param(ProcessEnum.FOUNDATION_DEPTH, 0.0),
            "height": element.get_param(ProcessEnum.FOUNDATION_HEIGHT, 0.0),
        }

    def _add_mast_attributes(self, result: Dict[str, Any], element: InfrastructureElement) -> None:
        """
        Fügt Mast-spezifische Attribute hinzu.

        Args:
            result: Ergebnisdictionary
            element: Das Element
        """
        result["mast_type"] = element.get_param(ProcessEnum.MAST_TYPE, "")
        result["height"] = element.get_param(ProcessEnum.MAST_HEIGHT, 0.0)

        # Referenz zum Fundament, falls vorhanden
        if isinstance(element, Mast) and element.foundation_uuid:
            result["foundation_id"] = str(element.foundation_uuid)

    def _add_joch_attributes(self, result: Dict[str, Any], element: InfrastructureElement) -> None:
        """
        Fügt Joch-spezifische Attribute hinzu.

        Args:
            result: Ergebnisdictionary
            element: Das Element
        """
        result["joch_type"] = element.get_param(ProcessEnum.JOCH_TYPE, "")
        result["span"] = element.get_param(ProcessEnum.JOCH_SPAN, 0.0)

        # Referenzen zu den Masten, falls vorhanden
        if isinstance(element, Joch):
            result["mast_id_1"] = str(element.mast_uuid_1)
            result["mast_id_2"] = str(element.mast_uuid_2)

    def _add_track_attributes(self, result: Dict[str, Any], element: InfrastructureElement) -> None:
        """
        Fügt Track-spezifische Attribute hinzu.

        Args:
            result: Ergebnisdictionary
            element: Das Element
        """
        result["track_type"] = element.get_param(ProcessEnum.TRACK_TYPE, "")
        result["gauge"] = element.get_param(ProcessEnum.TRACK_GAUGE, 0.0)
        result["cant"] = element.get_param(ProcessEnum.TRACK_CANT, 0.0)

    def _add_curved_track_attributes(self, result: Dict[str, Any], element: HasClothoid) -> None:
        """
        Fügt CurvedTrack-spezifische Attribute hinzu.

        Args:
            result: Ergebnisdictionary
            element: Das Element
        """
        result["is_curved"] = True
        result["clothoid_parameter"] = element.get_param(ProcessEnum.CLOTHOID_PARAMETER, 0.0)

        start_radius = element.get_param(ProcessEnum.START_RADIUS)
        if start_radius is not None:
            if isinstance(start_radius, float) and start_radius == float("inf"):
                result["start_radius"] = "inf"
            else:
                result["start_radius"] = start_radius

        result["end_radius"] = element.get_param(ProcessEnum.END_RADIUS, 0.0)

    def calculate_clothoid_points(
        self,
        element_id: Union[UUID, str],
        start_station: float,
        end_station: float,
        step: float,
    ) -> List[Tuple[float, float, float]]:
        """
        Berechnet Punkte entlang einer Klothoide.

        Args:
            element_id: ID des Elements
            start_station: Startstation
            end_station: Endstation
            step: Schrittweite

        Returns:
            Liste von Punkten (x, y, z)

        Raises:
            ValueError: Wenn das Element keine Klothoidenfunktionalität hat
        """

        element = self.repository.get_by_id(element_id)
        x1 = element.get_param(ProcessEnum.X_COORDINATE, 0.0)
        y1 = element.get_param(ProcessEnum.Y_COORDINATE, 0.0)
        z1 = element.get_param(ProcessEnum.Z_COORDINATE, 0.0)
        x2 = element.get_param(ProcessEnum.X_COORDINATE_END, 0.0)
        y2 = element.get_param(ProcessEnum.Y_COORDINATE_END, 0.0)
        z2 = element.get_param(ProcessEnum.Z_COORDINATE_END, 0.0)

        # Gesamtlänge
        total_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Höhendifferenz pro Meter
        z_diff_per_m = (z2 - z1) / total_length if total_length > 0 else 0

        # Vereinfachte Klothoidenberechnung (Beispiel)
        # In der Praxis würde hier eine komplexere Berechnung stehen
        points = []
        for station in [
            start_station + i * step for i in range(int((end_station - start_station) / step) + 1)
        ]:
            # Prozentuale Position auf der Klothoide
            t = station / total_length

            # Lineares Sampling zwischen Anfangs- und Endpunkt (vereinfacht)
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            z = z1 + station * z_diff_per_m

            points.append((x, y, z))

        return points
