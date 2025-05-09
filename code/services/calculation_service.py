"""
Service für die Berechnung von Infrastrukturelementen (Prozess 2).
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from ..common.enums.process_enums import ElementType, ProcessEnum, UnitEnum
from ..common.models.base_models import InfrastructureElement
from ..common.models.element_models import (
    CurvedTrack,
    DrainagePipe,
    DrainageShaft,
    Foundation,
    InfrastructureElementBase,
    LinearElement,
    Mast,
    PipeElement,
    Track,
)
from ..common.models.location import CoordinateLocation, Dimension, LineLocation
from ..common.models.components import Component


class CalculationElement:
    """
    Berechnungselement mit spezifischen Attributen für den Berechnungsprozess.
    """

    def __init__(self, uuid: Union[UUID, str], name: str, element_type: str):
        self.uuid = str(uuid)
        self.name = name
        self.element_type = element_type
        self.properties = {}
        self.calculation_data = {}
        self.dependencies = []

    def add_property(self, name: str, value: Any) -> None:
        """
        Fügt eine Eigenschaft hinzu.

        Args:
            name: Name der Eigenschaft
            value: Wert der Eigenschaft
        """
        self.properties[name] = value

    def add_calculation_data(self, name: str, value: Any) -> None:
        """
        Fügt Berechnungsdaten hinzu.

        Args:
            name: Name der Berechnungsdaten
            value: Wert der Berechnungsdaten
        """
        self.calculation_data[name] = value

    def add_dependency(self, uuid: str) -> None:
        """
        Fügt eine Abhängigkeit hinzu.

        Args:
            uuid: UUID des abhängigen Elements
        """
        if uuid not in self.dependencies:
            self.dependencies.append(uuid)

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Element in ein Dictionary.

        Returns:
            Dictionary-Repräsentation des Elements
        """
        return {
            "uuid": self.uuid,
            "name": self.name,
            "element_type": self.element_type,
            "properties": self.properties,
            "calculation_data": self.calculation_data,
            "dependencies": self.dependencies,
        }


class CalculationService:
    """
    Service für die Berechnung von Infrastrukturelementen.
    Bereitet Daten für den Berechnungsprozess auf.
    """

    def __init__(self, repository):
        """
        Initialisiert den Service.

        Args:
            repository: Repository für den Zugriff auf Elemente
        """
        self.repository = repository

    def get_element(self, uuid: Union[UUID, str]) -> Optional[CalculationElement]:
        """
        Ruft ein Element für die Berechnung ab.

        Args:
            uuid: UUID des Elements

        Returns:
            Berechnungselement oder None
        """
        element = self.repository.get_by_id(uuid)
        if element:
            return self._prepare_element_for_calculation(element)
        return None

    def get_elements_by_type(self, element_type: ElementType) -> List[CalculationElement]:
        """
        Ruft Elemente eines bestimmten Typs für die Berechnung ab.

        Args:
            element_type: Typ der abzurufenden Elemente

        Returns:
            Liste der Berechnungselemente
        """
        elements = self.repository.get_by_type(element_type)
        return [self._prepare_element_for_calculation(element) for element in elements]

    def get_all_elements(self) -> List[CalculationElement]:
        """
        Ruft alle Elemente für die Berechnung ab.

        Returns:
            Liste aller Berechnungselemente
        """
        elements = self.repository.get_all()
        return [self._prepare_element_for_calculation(element) for element in elements]

    def _prepare_element_for_calculation(
        self, element: InfrastructureElement
    ) -> CalculationElement:
        """
        Bereitet ein Element für die Berechnung auf.

        Args:
            element: Das aufzubereitende Element

        Returns:
            Berechnungselement
        """
        calc_element = CalculationElement(
            uuid=element.uuid,
            name=element.name,
            element_type=element.element_type.value,
        )

        # Grundlegende Eigenschaften für alle Elementtypen
        material = element.get_material()
        if material:
            calc_element.add_property("material", material)
        else:
            calc_element.add_property("material", element.get_param(ProcessEnum.MATERIAL, ""))

        # Koordinaten aus Komponenten oder Parametern
        location = element.get_location()
        if location:
            calc_element.add_property(
                "position",
                {
                    "x": location.x,
                    "y": location.y,
                    "z": location.z,
                    "azimuth": location.azimuth
                },
            )
        else:
            # Fallback auf Parameter
            calc_element.add_property(
                "position",
                {
                    "x": element.get_param(ProcessEnum.X_COORDINATE, 0.0),
                    "y": element.get_param(ProcessEnum.Y_COORDINATE, 0.0),
                    "z": element.get_param(ProcessEnum.Z_COORDINATE, 0.0),
                    "azimuth": element.get_param(ProcessEnum.AZIMUTH)
                },
            )

        # Für lineare Elemente auch Endpunkt hinzufügen
        line = element.get_line()
        if line:
            calc_element.add_property(
                "end_position",
                {
                    "x": line.end.x,
                    "y": line.end.y,
                    "z": line.end.z,
                },
            )
        elif element.get_param(ProcessEnum.X_COORDINATE_END) is not None:
            # Fallback auf Parameter
            calc_element.add_property(
                "end_position",
                {
                    "x": element.get_param(ProcessEnum.X_COORDINATE_END, 0.0),
                    "y": element.get_param(ProcessEnum.Y_COORDINATE_END, 0.0),
                    "z": element.get_param(ProcessEnum.Z_COORDINATE_END, 0.0),
                },
            )

        # Dimensionen aus Komponenten oder Parametern
        dimension = element.get_dimension()
        if dimension:
            dim_dict = {}
            if dimension.width is not None:
                dim_dict["width"] = dimension.width
            if dimension.height is not None:
                dim_dict["height"] = dimension.height
            if dimension.depth is not None:
                dim_dict["depth"] = dimension.depth
            if dimension.length is not None:
                dim_dict["length"] = dimension.length
            if dimension.diameter is not None:
                dim_dict["diameter"] = dimension.diameter
            if dimension.radius is not None:
                dim_dict["radius"] = dimension.radius
                
            if dim_dict:
                calc_element.add_property("dimensions", dim_dict)

        # Referenzen zu abhängigen Elementen (aus components und alten Attributen)
        # Aus Komponenten
        ref_component = element.get_component("reference")
        if ref_component and hasattr(ref_component, "referenced_uuids"):
            for uuid in ref_component.referenced_uuids:
                calc_element.add_dependency(uuid)
                
        # Aus direkten Attributen für Kompatibilität
        if hasattr(element, "foundation_uuid") and element.foundation_uuid:
            calc_element.add_dependency(str(element.foundation_uuid))
        
        if hasattr(element, "references"):
            for ref_type, ref_uuid in element.references.items():
                calc_element.add_dependency(str(ref_uuid))

        # Elementspezifische Attribute hinzufügen
        element_type = element.element_type
        
        if element_type == ElementType.FOUNDATION:
            self._add_foundation_calculation(calc_element, element)
        elif element_type == ElementType.MAST:
            self._add_mast_calculation(calc_element, element)
        elif element_type == ElementType.TRACK:
            self._add_track_calculation(calc_element, element)
            
            # Prüfen auf Kurvengeometrie
            if element.get_param(ProcessEnum.CLOTHOID_PARAMETER) is not None:
                self._add_curved_track_calculation(calc_element, element)
        elif element_type == ElementType.DRAINAGE_PIPE:
            self._add_pipe_calculation(calc_element, element)
        elif element_type == ElementType.DRAINAGE_SHAFT:
            self._add_shaft_calculation(calc_element, element)
        elif isinstance(element, LinearElement):
            # Generische Berechnung für lineare Elemente
            self._add_linear_element_calculation(calc_element, element)

        return calc_element

    def _add_foundation_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Foundation-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property(
            "foundation_type", element.get_param(ProcessEnum.FOUNDATION_TYPE, "")
        )

        # Dimensionen bevorzugt aus der Komponente
        dimension = element.get_dimension()
        if dimension:
            width = dimension.width or 0.0
            depth = dimension.depth or 0.0
            height = dimension.height or 0.0
        else:
            width = element.get_param(ProcessEnum.FOUNDATION_WIDTH, 0.0)
            depth = element.get_param(ProcessEnum.FOUNDATION_DEPTH, 0.0)
            height = element.get_param(ProcessEnum.FOUNDATION_HEIGHT, 0.0)

        # Dimensionen speichern, wenn noch nicht vorhanden
        if "dimensions" not in calc_element.properties:
            calc_element.add_property("dimensions", {"width": width, "depth": depth, "height": height})

        # Berechnungsdaten
        volume = width * depth * height
        weight = volume * 2500  # Annahme: Beton mit 2500 kg/m³

        calc_element.add_calculation_data("volume", volume)
        calc_element.add_calculation_data("weight", weight)
        
        # Nur Bottom Pressure berechnen, wenn es eine gültige Grundfläche gibt
        if width > 0 and depth > 0:
            calc_element.add_calculation_data("bottom_pressure", weight / (width * depth))
        else:
            calc_element.add_calculation_data("bottom_pressure", 0.0)

    def _add_mast_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Mast-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property("mast_type", element.get_param(ProcessEnum.MAST_TYPE, ""))
        calc_element.add_property(
            "profile_type", element.get_param(ProcessEnum.MAST_PROFILE_TYPE, "")
        )

        # Höhe aus Dimension oder Parameter
        dimension = element.get_dimension()
        if dimension and dimension.height is not None:
            height = dimension.height
        else:
            height = element.get_param(ProcessEnum.MAST_HEIGHT, 0.0)
        
        calc_element.add_property("height", height)

        # Berechnungsdaten
        # Für DP-Profile: Vereinfachte Gewichtsberechnung
        weight_per_meter = 0.0
        mast_type = calc_element.properties.get("mast_type", "")
        
        if "DP18" in mast_type:
            weight_per_meter = 40.0  # kg/m
        elif "DP20" in mast_type:
            weight_per_meter = 45.0  # kg/m
        elif "DP22" in mast_type:
            weight_per_meter = 50.0  # kg/m
        elif "DP24" in mast_type:
            weight_per_meter = 55.0  # kg/m

        weight = height * weight_per_meter
        calc_element.add_calculation_data("weight", weight)

        # Vereinfachte Berechnung des Widerstandsmoments
        profile_type = calc_element.properties.get("profile_type", "")
        if "HEB" in profile_type:
            resistance_moment = 100.0  # cm³
        else:
            resistance_moment = 80.0  # cm³

        calc_element.add_calculation_data("resistance_moment", resistance_moment)

    def _add_linear_element_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Berechnungsdaten für lineare Elemente hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Position berechnen
        start_pos = calc_element.properties.get("position", {})
        end_pos = calc_element.properties.get("end_position", {})
        
        # Länge berechnen
        if start_pos and end_pos:
            x1, y1 = start_pos.get("x", 0.0), start_pos.get("y", 0.0)
            x2, y2 = end_pos.get("x", 0.0), end_pos.get("y", 0.0)
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            
            # Direkt als Eigenschaft speichern
            if "dimensions" not in calc_element.properties:
                calc_element.add_property("dimensions", {"length": length})
            else:
                calc_element.properties["dimensions"]["length"] = length
            
            calc_element.add_calculation_data("length", length)
            
            # Richtung berechnen
            if length > 0:
                direction = {
                    "dx": (x2 - x1) / length,
                    "dy": (y2 - y1) / length
                }
                calc_element.add_calculation_data("direction", direction)

    def _add_track_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Track-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property("track_type", element.get_param(ProcessEnum.TRACK_TYPE, ""))
        calc_element.add_property("gauge", element.get_param(ProcessEnum.TRACK_GAUGE, 0.0))
        calc_element.add_property("cant", element.get_param(ProcessEnum.TRACK_CANT, 0.0))

        # Generische lineare Berechnungen durchführen
        self._add_linear_element_calculation(calc_element, element)

        # Gewicht pro Meter für verschiedene Schienentypen
        track_type = calc_element.properties.get("track_type", "")
        weight_per_meter = 0.0
        if "UIC60" in track_type:
            weight_per_meter = 60.0  # kg/m
        elif "UIC54" in track_type:
            weight_per_meter = 54.0  # kg/m
        
        # Gewicht berechnen, wenn Länge bekannt
        length = calc_element.calculation_data.get("length", 0.0)
        if length > 0:
            weight = length * weight_per_meter
            calc_element.add_calculation_data("weight", weight)
        else:
            calc_element.add_calculation_data("weight", 0.0)

    def _add_curved_track_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt CurvedTrack-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property("is_curved", True)
        calc_element.add_property(
            "clothoid_parameter", element.get_param(ProcessEnum.CLOTHOID_PARAMETER, 0.0)
        )

        # Radius aus Dimension oder Parameter
        dimension = element.get_dimension()
        start_radius = None
        if dimension and dimension.radius is not None:
            start_radius = dimension.radius
        else:
            start_radius = element.get_param(ProcessEnum.START_RADIUS)
            
        if start_radius is not None:
            if isinstance(start_radius, float) and start_radius == float("inf"):
                calc_element.add_property("start_radius", "inf")
            else:
                calc_element.add_property("start_radius", start_radius)

        calc_element.add_property("end_radius", element.get_param(ProcessEnum.END_RADIUS, 0.0))

        # Berechnungsdaten
        # Vereinfachte Berechnung der Länge einer Klothoide
        a = element.get_param(ProcessEnum.CLOTHOID_PARAMETER, 0.0)
        r2 = element.get_param(ProcessEnum.END_RADIUS, 0.0)

        if r2 > 0:
            # Vereinfachte Formel für die Länge einer Klothoide: L = A²/R
            length = a**2 / r2
            calc_element.add_calculation_data("clothoid_length", length)

        # Überhöhung
        cant = element.get_param(ProcessEnum.TRACK_CANT, 0.0)
        gauge = element.get_param(ProcessEnum.TRACK_GAUGE, 0.0)

        if r2 > 0 and gauge > 0:
            # Vereinfachte Berechnung der theoretischen Überhöhung
            v_max = 15.0  # m/s (54 km/h)
            theoretical_cant = v_max**2 * gauge / (9.81 * r2) * 1000  # in mm
            calc_element.add_calculation_data("theoretical_cant", theoretical_cant)
            calc_element.add_calculation_data("cant_deficiency", theoretical_cant - cant)

    def _add_pipe_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Pipe-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property("pipe_material", element.get_param(ProcessEnum.PIPE_MATERIAL, ""))
        
        # Durchmesser aus Dimension oder Parameter
        dimension = element.get_dimension()
        if dimension and dimension.diameter is not None:
            diameter = dimension.diameter
        else:
            diameter = element.get_param(ProcessEnum.PIPE_DIAMETER, 0.0)
            
        calc_element.add_property("diameter", diameter)
        calc_element.add_property("slope", element.get_param(ProcessEnum.PIPE_SLOPE, 0.0))
        
        # Generische lineare Berechnungen durchführen
        self._add_linear_element_calculation(calc_element, element)
        
        # Volumenstrom-Kapazität (vereinfachte Manning-Formel)
        # Annahme: n=0.013 für PVC-Rohre
        n = 0.013
        
        # Durchmesser in m
        d_meters = diameter / 1000.0
        
        # Gefälle in m/m
        slope_m_m = element.get_param(ProcessEnum.PIPE_SLOPE, 0.0) / 1000.0
        
        if d_meters > 0 and slope_m_m > 0:
            # Querschnittsfläche
            area = 3.14159 * (d_meters/2)**2
            
            # Hydraulischer Radius
            r_hydraulic = d_meters / 4
            
            # Manning-Formel: v = (1/n) * R^(2/3) * S^(1/2)
            velocity = (1/n) * (r_hydraulic**(2/3)) * (slope_m_m**0.5)
            
            # Durchfluss Q = v * A
            flow_capacity = velocity * area
            
            calc_element.add_calculation_data("flow_capacity", flow_capacity)
            calc_element.add_calculation_data("flow_capacity_l_s", flow_capacity * 1000)

    def _add_shaft_calculation(
        self, calc_element: CalculationElement, element: InfrastructureElement
    ) -> None:
        """
        Fügt Shaft-spezifische Berechnungsdaten hinzu.

        Args:
            calc_element: Berechnungselement
            element: Das Element
        """
        # Eigenschaften
        calc_element.add_property("shaft_material", element.get_param(ProcessEnum.SHAFT_MATERIAL, ""))
        
        # Durchmesser und Tiefe aus Dimension oder Parameter
        dimension = element.get_dimension()
        if dimension:
            diameter = dimension.diameter or element.get_param(ProcessEnum.SHAFT_DIAMETER, 0.0)
            depth = dimension.depth or element.get_param(ProcessEnum.SHAFT_DEPTH, 0.0)
        else:
            diameter = element.get_param(ProcessEnum.SHAFT_DIAMETER, 0.0)
            depth = element.get_param(ProcessEnum.SHAFT_DEPTH, 0.0)
            
        calc_element.add_property("diameter", diameter)
        calc_element.add_property("depth", depth)
        
        # Berechnung des Volumens
        if diameter > 0 and depth > 0:
            # Umrechnung in Meter
            d_meters = diameter / 1000.0
            
            # Volumen eines Zylinders V = π * r² * h
            volume = 3.14159 * (d_meters/2)**2 * depth
            calc_element.add_calculation_data("volume", volume)
            calc_element.add_calculation_data("capacity_l", volume * 1000)

    def calculate_track_forces(
        self, element_id: Union[UUID, str], speed: float, load: float
    ) -> Dict[str, Any]:
        """
        Berechnet Kräfte auf einem Gleis.

        Args:
            element_id: ID des Elements
            speed: Geschwindigkeit in m/s
            load: Last in kN/m

        Returns:
            Berechnete Kräfte

        Raises:
            ValueError: Wenn das Element kein Gleis ist
        """
        element = self.repository.get_by_id(element_id)
        if not element or element.element_type != ElementType.TRACK:
            raise ValueError(f"Element {element_id} ist kein Gleis")

        # Position extrahieren, bevorzugt aus Komponenten
        location = element.get_location()
        if location:
            x1, y1, z1 = location.x, location.y, location.z
        else:
            x1 = element.get_param(ProcessEnum.X_COORDINATE, 0.0)
            y1 = element.get_param(ProcessEnum.Y_COORDINATE, 0.0)
            z1 = element.get_param(ProcessEnum.Z_COORDINATE, 0.0)
            
        # Endpunkte extrahieren, bevorzugt aus Komponenten
        line = element.get_line()
        if line:
            x2, y2, z2 = line.end.x, line.end.y, line.end.z
        else:
            x2 = element.get_param(ProcessEnum.X_COORDINATE_END, 0.0)
            y2 = element.get_param(ProcessEnum.Y_COORDINATE_END, 0.0)
            z2 = element.get_param(ProcessEnum.Z_COORDINATE_END, 0.0)

        # Länge berechnen
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2) ** 0.5

        # Basisparameter
        gauge = element.get_param(ProcessEnum.TRACK_GAUGE, 0.0)
        cant = element.get_param(ProcessEnum.TRACK_CANT, 0.0) / 1000.0  # von mm in m umwandeln

        # Kurveneigenschaften
        is_curved = element.get_param(ProcessEnum.CLOTHOID_PARAMETER) is not None
        
        # Radius aus Dimension oder Parameter
        dimension = element.get_dimension()
        radius = float("inf")
        if dimension and dimension.radius is not None:
            radius = dimension.radius
        elif element.get_param(ProcessEnum.END_RADIUS) is not None:
            radius = element.get_param(ProcessEnum.END_RADIUS)
            
        # Gewicht berechnen
        track_type = element.get_param(ProcessEnum.TRACK_TYPE, "")
        weight_per_meter = 60.0 if "UIC60" in track_type else 54.0  # kg/m

        # Kräfte berechnen
        vertical_force = load * length  # kN

        # Querkraft in Kurven (vereinfacht)
        lateral_force = 0.0
        if radius < float("inf") and radius > 0:
            # Zentrifugalkraft ohne Überhöhung
            centrifugal_force = load * speed**2 / radius  # kN

            # Reduktion durch Überhöhung
            cant_effect = load * 9.81 * cant / gauge
            lateral_force = centrifugal_force - cant_effect

        return {
            "vertical_force": vertical_force,
            "lateral_force": lateral_force,
            "length": length,
            "weight": weight_per_meter * length,
            "is_curved": is_curved,
            "radius": radius if radius < float("inf") else "inf",
        }

    def calculate_structure_load(self, element_id: Union[UUID, str]) -> Dict[str, Any]:
        """
        Berechnet die Strukturlast einer Tragstruktur (Fundament, Mast, etc.).

        Args:
            element_id: ID des Elements

        Returns:
            Berechnete Last

        Raises:
            ValueError: Wenn das Element keine Tragstruktur ist
        """
        element = self.repository.get_by_id(element_id)
        if not element:
            raise ValueError(f"Element {element_id} nicht gefunden")

        calc_element = self._prepare_element_for_calculation(element)
        result = calc_element.to_dict()

        # Rekursiv abhängige Elemente laden
        dependencies = []
        for dep_id in calc_element.dependencies:
            dep_element = self.repository.get_by_id(dep_id)
            if dep_element:
                dependencies.append(self._prepare_element_for_calculation(dep_element).to_dict())

        result["dependencies"] = dependencies

        # Gesamtlast berechnen
        total_weight = calc_element.calculation_data.get("weight", 0.0)

        # Lastfall für verschiedene Elementtypen
        if element.element_type == ElementType.FOUNDATION:
            result["load_case"] = {
                "self_weight": total_weight,
                "soil_pressure": calc_element.calculation_data.get("bottom_pressure", 0.0),
                "max_allowed_pressure": 250.0,  # kN/m²
            }
        elif element.element_type == ElementType.MAST:
            # Last durch angehängte Elemente berücksichtigen
            attached_weight = 0.0
            for dep in dependencies:
                # Alle angehängten Elemente berücksichtigen
                attached_weight += dep.get("calculation_data", {}).get("weight", 0.0)

            total_weight += attached_weight
            height = calc_element.properties.get("height", 0.0)
            result["load_case"] = {
                "self_weight": calc_element.calculation_data.get("weight", 0.0),
                "attached_weight": attached_weight,
                "total_weight": total_weight,
                "foundation_moment": total_weight * height / 2.0,
                "max_allowed_moment": 500.0,  # kNm
            }

        return result