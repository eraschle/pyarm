"""
Client C spezifischer Datenleser für das FDK-Format.
Liest Daten aus JSON-Dateien für Client C's FDK-Struktur.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Füge das Stammverzeichnis zum Pythonpfad hinzu, um absolute Importe zu ermöglichen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))


class ClientCFdkReader:
    """
    Leser für FDK-JSON-Dateien des Clients C.
    Parst die neue FDK-Anlagenstruktur aus JSON-Dateien und extrahiert die Daten inklusive
    IFC-Daten und Bauphaseninformationen.
    """

    @property
    def name(self) -> str:
        return "ClientCFdkReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["json"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".json" and "clientC" in str(path) and "FDK" in str(path)

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest FDK-JSON-Daten aus der angegebenen Datei.

        Args:
            file_path: Pfad zur JSON-Datei

        Returns:
            Dictionary mit den gelesenen Daten, gruppiert nach Elementtyp
        """
        with open(file_path, "r", encoding="utf-8") as f:
            json_content = json.load(f)

        # Prüfen ob es sich um eine FDK-Struktur handelt
        if "anlagenDaten" not in json_content:
            return {}

        anlage = json_content["anlagenDaten"]

        # Bauphasen indexieren für schnellen Zugriff
        bauphasen_dict = {}
        if "bauphasen" in anlage:
            for bauphase in anlage["bauphasen"]:
                if "id" in bauphase:
                    bauphasen_dict[bauphase["id"]] = bauphase

        # Daten nach Elementtyp gruppieren
        data = {
            "foundation": self._extract_fundamente(anlage.get("fundamente", []), bauphasen_dict),
            "mast": self._extract_masten(anlage.get("masten", []), bauphasen_dict),
            "track": self._extract_gleise(anlage.get("gleisAnlagen", []), bauphasen_dict),
            "drainage": self._extract_entwaesserung(
                anlage.get("entwässerungssysteme", []), bauphasen_dict
            ),
            "building": self._extract_gebaeude(anlage.get("ifcGebäude", {}), bauphasen_dict),
            "bauphasen": anlage.get("bauphasen", []),
            "meta": anlage.get("meta", {}),
        }

        return data

    def _extract_fundamente(
        self,
        fundamente: List[Dict[str, Any]],
        bauphasen_dict: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extrahiert und transformiert Fundamentdaten.

        Args:
            fundamente: Liste der Fundamentdaten aus der JSON-Datei
            bauphasen_dict: Dictionary mit Bauphasen-Informationen

        Returns:
            Transformierte Fundamentdaten
        """
        results = []
        for fundament in fundamente:
            # Basisdaten extrahieren
            foundation_data = {
                "id": fundament.get("id"),
                "name": f"Fundament {fundament.get('id', 'Unknown')}",
                "type": fundament.get("typ"),
                "material": fundament.get("material"),
                "volume_m3": fundament.get("volumen"),
                "capacity_kn": fundament.get("tragfähigkeit"),
                "depth_m": fundament.get("tiefe"),
            }

            # Standortdaten
            if "standort" in fundament:
                standort = fundament["standort"]
                foundation_data.update(
                    {
                        "km": standort.get("kilometerLage"),
                        "gleis_id": standort.get("gleisId"),
                        "distance_m": standort.get("abstand"),
                    }
                )

            # IFC-Daten hinzufügen
            if "ifcDaten" in fundament:
                ifc = fundament["ifcDaten"]
                foundation_data["ifc_data"] = {
                    "globalId": ifc.get("globalId"),
                    "type": ifc.get("elementTyp"),
                    "material": ifc.get("materialTyp"),
                    "category": ifc.get("kategorie"),
                }

            # Bauphasen-Daten hinzufügen
            if "bauphasenId" in fundament and fundament["bauphasenId"] in bauphasen_dict:
                bauphase = bauphasen_dict[fundament["bauphasenId"]]
                foundation_data["bauphase"] = {
                    "id": bauphase.get("id"),
                    "name": bauphase.get("name"),
                    "start_date": bauphase.get("startDatum"),
                    "end_date": bauphase.get("endDatum"),
                }

            results.append(foundation_data)

        return results

    def _extract_masten(
        self, masten: List[Dict[str, Any]], bauphasen_dict: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extrahiert und transformiert Mastdaten.

        Args:
            masten: Liste der Mastdaten aus der JSON-Datei
            bauphasen_dict: Dictionary mit Bauphasen-Informationen

        Returns:
            Transformierte Mastdaten
        """
        results = []
        for mast in masten:
            # Basisdaten extrahieren
            mast_data = {
                "id": mast.get("id"),
                "name": f"Mast {mast.get('id', 'Unknown')}",
                "type": mast.get("typ"),
                "material": mast.get("material"),
                "height_m": mast.get("höhe"),
                "foundation_id": mast.get("fundamentId"),
            }

            # Standortdaten
            if "standort" in mast:
                standort = mast["standort"]
                mast_data.update(
                    {
                        "km": standort.get("kilometerLage"),
                        "gleis_id": standort.get("gleisId"),
                        "distance_m": standort.get("abstand"),
                    }
                )

            # IFC-Daten hinzufügen
            if "ifcDaten" in mast:
                ifc = mast["ifcDaten"]
                mast_data["ifc_data"] = {
                    "globalId": ifc.get("globalId"),
                    "type": ifc.get("elementTyp"),
                    "material": ifc.get("materialTyp"),
                    "category": ifc.get("kategorie"),
                }

            # Bauphasen-Daten hinzufügen
            if "bauphasenId" in mast and mast["bauphasenId"] in bauphasen_dict:
                bauphase = bauphasen_dict[mast["bauphasenId"]]
                mast_data["bauphase"] = {
                    "id": bauphase.get("id"),
                    "name": bauphase.get("name"),
                    "start_date": bauphase.get("startDatum"),
                    "end_date": bauphase.get("endDatum"),
                }

            results.append(mast_data)

        return results

    def _extract_gleise(
        self, gleise: List[Dict[str, Any]], bauphasen_dict: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extrahiert und transformiert Gleisdaten.

        Args:
            gleise: Liste der Gleisdaten aus der JSON-Datei
            bauphasen_dict: Dictionary mit Bauphasen-Informationen

        Returns:
            Transformierte Gleisdaten
        """
        results = []
        for gleis in gleise:
            # Basisdaten extrahieren
            gleis_data = {
                "id": gleis.get("id"),
                "name": gleis.get("name", f"Gleis {gleis.get('id', 'Unknown')}"),
                "type": gleis.get("typ"),
                "length_m": gleis.get("länge"),
                "gauge_mm": gleis.get("spurweite"),
            }

            # Handhabung von Kurvengleis-Daten
            if "bogenRadius" in gleis and gleis["bogenRadius"] > 0:
                gleis_data["is_curved"] = True
                gleis_data["radius_m"] = gleis.get("bogenRadius")
            else:
                gleis_data["is_curved"] = False

            # IFC-Daten hinzufügen
            if "ifcDaten" in gleis:
                ifc = gleis["ifcDaten"]
                gleis_data["ifc_data"] = {
                    "globalId": ifc.get("globalId"),
                    "type": ifc.get("elementTyp"),
                    "material": ifc.get("materialTyp"),
                    "category": ifc.get("kategorie"),
                }

            # Bauphasen-Daten hinzufügen
            if "bauphasenId" in gleis and gleis["bauphasenId"] in bauphasen_dict:
                bauphase = bauphasen_dict[gleis["bauphasenId"]]
                gleis_data["bauphase"] = {
                    "id": bauphase.get("id"),
                    "name": bauphase.get("name"),
                    "start_date": bauphase.get("startDatum"),
                    "end_date": bauphase.get("endDatum"),
                }

            results.append(gleis_data)

        return results

    def _extract_entwaesserung(
        self,
        entwaesserung: List[Dict[str, Any]],
        bauphasen_dict: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extrahiert und transformiert Entwässerungsdaten.

        Args:
            entwaesserung: Liste der Entwässerungsdaten aus der JSON-Datei
            bauphasen_dict: Dictionary mit Bauphasen-Informationen

        Returns:
            Transformierte Entwässerungsdaten
        """
        results = []
        for element in entwaesserung:
            # Typ bestimmen (Schacht oder Lineenentwässerung)
            element_type = "shaft" if element.get("typ") == "Schacht" else "pipe"

            # Basisdaten extrahieren
            element_data = {
                "id": element.get("id"),
                "name": f"Entwässerung {element.get('id', 'Unknown')}",
                "type": element_type,
                "material": element.get("material"),
            }

            # Spezifische Eigenschaften je nach Typ
            if element_type == "shaft":
                element_data.update(
                    {
                        "diameter_mm": element.get("durchmesser", 0) * 1000,  # Umrechnung in mm
                        "depth_m": element.get("tiefe"),
                    }
                )
            else:  # pipe
                element_data.update(
                    {
                        "length_m": element.get("länge"),
                    }
                )

            # Standortdaten
            if "standort" in element:
                standort = element["standort"]

                # Unterschiedliche Struktur für Start/Ende vs. Punkt
                if "kilometerLage" in standort and isinstance(standort["kilometerLage"], dict):
                    # Lineares Element mit Start und Ende
                    element_data.update(
                        {
                            "km_start": standort["kilometerLage"].get("start"),
                            "km_end": standort["kilometerLage"].get("ende"),
                            "gleis_id": standort.get("gleisId"),
                            "distance_m": standort.get("abstand"),
                        }
                    )
                else:
                    # Punktelement
                    element_data.update(
                        {
                            "km": standort.get("kilometerLage"),
                            "gleis_id": standort.get("gleisId"),
                            "distance_m": standort.get("abstand"),
                        }
                    )

            # IFC-Daten hinzufügen
            if "ifcDaten" in element:
                ifc = element["ifcDaten"]
                element_data["ifc_data"] = {
                    "globalId": ifc.get("globalId"),
                    "type": ifc.get("elementTyp"),
                    "material": ifc.get("materialTyp"),
                    "category": ifc.get("kategorie"),
                }

            # Bauphasen-Daten hinzufügen
            if "bauphasenId" in element and element["bauphasenId"] in bauphasen_dict:
                bauphase = bauphasen_dict[element["bauphasenId"]]
                element_data["bauphase"] = {
                    "id": bauphase.get("id"),
                    "name": bauphase.get("name"),
                    "start_date": bauphase.get("startDatum"),
                    "end_date": bauphase.get("endDatum"),
                }

            results.append(element_data)

        return results

    def _extract_gebaeude(
        self, gebaeude: Dict[str, Any], bauphasen_dict: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extrahiert und transformiert Gebäudedaten.

        Args:
            gebaeude: Gebäudedaten aus der JSON-Datei
            bauphasen_dict: Dictionary mit Bauphasen-Informationen

        Returns:
            Transformierte Gebäudedaten
        """
        # Wenn keine Gebäudedaten vorhanden sind, leere Liste zurückgeben
        if not gebaeude:
            return []

        # Basisdaten extrahieren
        building_data = {
            "id": gebaeude.get("globalId"),
            "name": gebaeude.get("name", "Gebäude"),
            "description": gebaeude.get("beschreibung"),
            "year_built": gebaeude.get("baujahr"),
            "renovation_year": gebaeude.get("sanierungsjahr"),
            "floors": gebaeude.get("geschosse"),
        }

        # Koordinaten hinzufügen
        if "koordinaten" in gebaeude:
            coords = gebaeude["koordinaten"]
            building_data.update(
                {
                    "coord_x": coords.get("x"),
                    "coord_y": coords.get("y"),
                    "coord_z": coords.get("z"),
                }
            )

        return [building_data]

    def get_element_types(self, data: Dict[str, Any]) -> List[str]:
        """
        Ermittelt die verfügbaren Elementtypen in den Daten.

        Args:
            data: Dictionary mit den gelesenen Daten

        Returns:
            Liste der verfügbaren Elementtypen
        """
        return [
            element_type
            for element_type, items in data.items()
            if items and element_type not in ["bauphasen", "meta"]
        ]

    def get_data_for_type(self, data: Dict[str, Any], element_type: str) -> Dict[str, Any]:
        """
        Extrahiert die Daten für einen bestimmten Elementtyp.

        Args:
            data: Dictionary mit den gelesenen Daten
            element_type: Elementtyp

        Returns:
            Dictionary mit den Daten für den angegebenen Elementtyp
        """
        return {"element_type": element_type, "data": data.get(element_type, [])}
