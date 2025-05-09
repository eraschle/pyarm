#!/usr/bin/env python3
"""
Eigenständiges Skript zur Visualisierung von importierten Daten.
Dieses Skript konvertiert die JSON-Ausgabedaten der Import-Tools in ein Format,
das vom Visualisierungsprozess verarbeitet werden kann.
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="Visualisierung von importierten Daten")

    parser.add_argument(
        "--input_file", type=str, required=True, help="Pfad zur importierten JSON-Datei"
    )
    parser.add_argument(
        "--client_type",
        type=str,
        choices=["clientA", "clientB", "clientC", "clientC_fdk"],
        required=True,
        help="Client-Typ (clientA, clientB, clientC oder clientC_fdk)",
    )
    parser.add_argument("--output_dir", type=str, required=True, help="Verzeichnis für die Ausgabe")

    return parser.parse_args()


def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Lädt JSON-Daten aus der angegebenen Datei.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Dictionary mit den geladenen Daten
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der JSON-Datei: {str(e)}")
        return {}


def convert_client_a_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert ClientA-Daten in ein visualisierbares Format.

    Args:
        data: ClientA-Daten

    Returns:
        Visualisierbares Format
    """
    visualization_data = {"scene": {"name": "ClientA Infrastrukturszene", "elements": []}}

    # Projekte durchlaufen
    for project_name, project_data in data.get("projects", {}).items():
        elements = project_data.get("elements", {})

        # Fundamente verarbeiten
        for foundation in elements.get("foundation", []):
            foundation_element = {
                "type": "foundation",
                "id": foundation.get("ID", "unknown"),
                "name": foundation.get("Bezeichnung", "Unbenanntes Fundament"),
                "geometry": {
                    "type": "box",
                    "dimensions": [
                        foundation.get("Breite", 1.0),
                        foundation.get("Breite", 1.0),
                        foundation.get("Höhe", 1.0),
                    ],
                    "position": [
                        float(foundation.get("E", 0.0)),
                        float(foundation.get("N", 0.0)),
                        float(foundation.get("Z", 0.0)),
                    ],
                },
                "material": {
                    "name": foundation.get("Material", "Beton"),
                    "color": [0.7, 0.7, 0.7],
                    "roughness": 0.8,
                },
                "project": project_name,
                "properties": {"mast_id": foundation.get("MastID", "")},
            }
            visualization_data["scene"]["elements"].append(foundation_element)

        # Masten verarbeiten
        for mast in elements.get("mast", []):
            mast_element = {
                "type": "mast",
                "id": mast.get("ID", "unknown"),
                "name": mast.get("Bezeichnung", "Unbenannter Mast"),
                "geometry": {
                    "type": "cylinder",
                    "radius": 0.25,
                    "height": float(mast.get("Höhe", 8.0)),
                    "position": [
                        float(mast.get("E", 0.0)),
                        float(mast.get("N", 0.0)),
                        float(mast.get("Z", 0.0)),
                    ],
                },
                "material": {
                    "name": mast.get("Material", "Stahl"),
                    "color": [0.5, 0.5, 0.5],
                    "roughness": 0.3,
                },
                "project": project_name,
                "properties": {
                    "foundation_id": mast.get("FundamentID", ""),
                    "typ": mast.get("Typ", ""),
                    "azimut": float(mast.get("Azimut", 0.0)),
                },
            }
            visualization_data["scene"]["elements"].append(mast_element)

        # Gleise verarbeiten
        for track in elements.get("track", []):
            track_element = {
                "type": "track",
                "id": track.get("ID", "unknown"),
                "name": track.get("Bezeichnung", "Unbenanntes Gleis"),
                "geometry": {
                    "type": "line",
                    "start": [
                        float(track.get("E", 0.0)),
                        float(track.get("N", 0.0)),
                        float(track.get("Z", 0.0)),
                    ],
                    "end": [
                        float(track.get("E2", 0.0)),
                        float(track.get("N2", 0.0)),
                        float(track.get("Z2", 0.0)),
                    ],
                    "width": float(track.get("Spurweite", 1.435)),
                },
                "material": {
                    "name": "Stahl",
                    "color": [0.1, 0.1, 0.1],
                    "roughness": 0.2,
                },
                "project": project_name,
                "properties": {
                    "gleistyp": track.get("Gleistyp", ""),
                    "ueberhöhung": float(track.get("Überhöhung", 0.0)),
                },
            }
            visualization_data["scene"]["elements"].append(track_element)

        # Kurvengleise verarbeiten
        for curved_track in elements.get("curved_track", []):
            curved_track_element = {
                "type": "curved_track",
                "id": curved_track.get("ID", "unknown"),
                "name": curved_track.get("Bezeichnung", "Unbenanntes Kurvengleis"),
                "geometry": {
                    "type": "curve",
                    "start": [
                        float(curved_track.get("E", 0.0)),
                        float(curved_track.get("N", 0.0)),
                        float(curved_track.get("Z", 0.0)),
                    ],
                    "end": [
                        float(curved_track.get("E2", 0.0)),
                        float(curved_track.get("N2", 0.0)),
                        float(curved_track.get("Z2", 0.0)),
                    ],
                    "width": float(curved_track.get("Spurweite", 1.435)),
                    "start_radius": float(
                        str(curved_track.get("Startradius", "inf")).replace("inf", "9999999")
                    ),
                    "end_radius": float(curved_track.get("Endradius", 0.0)),
                    "clothoid_parameter": float(curved_track.get("Klothoidenparameter", 0.0)),
                },
                "material": {
                    "name": "Stahl",
                    "color": [0.1, 0.1, 0.1],
                    "roughness": 0.2,
                },
                "project": project_name,
                "properties": {
                    "gleistyp": curved_track.get("Gleistyp", ""),
                    "ueberhöhung": float(curved_track.get("Überhöhung", 0.0)),
                },
            }
            visualization_data["scene"]["elements"].append(curved_track_element)

        # Joche verarbeiten
        for joch in elements.get("joch", []):
            joch_element = {
                "type": "joch",
                "id": joch.get("ID", "unknown"),
                "name": joch.get("Bezeichnung", "Unbenanntes Joch"),
                "geometry": {
                    "type": "line",
                    "start": [
                        float(joch.get("E", 0.0)),
                        float(joch.get("N", 0.0)),
                        float(joch.get("Z", 0.0)),
                    ],
                    "end": [
                        float(joch.get("E2", 0.0)),
                        float(joch.get("N2", 0.0)),
                        float(joch.get("Z2", 0.0)),
                    ],
                    "thickness": 0.1,
                },
                "material": {
                    "name": joch.get("Material", "Stahl"),
                    "color": [0.5, 0.5, 0.5],
                    "roughness": 0.3,
                },
                "project": project_name,
                "properties": {
                    "mast1_id": joch.get("Mast1ID", ""),
                    "mast2_id": joch.get("Mast2ID", ""),
                    "spannweite": float(joch.get("Spannweite", 0.0)),
                },
            }
            visualization_data["scene"]["elements"].append(joch_element)

        # Entwässerung verarbeiten
        for drainage in elements.get("drainage", []):
            if drainage.get("Typ") == "Pipe":
                # Entwässerungsleitung
                drainage_element = {
                    "type": "drainage_pipe",
                    "id": drainage.get("ID", "unknown"),
                    "name": drainage.get("Bezeichnung", "Unbenannte Entwässerungsleitung"),
                    "geometry": {
                        "type": "pipe",
                        "start": [
                            float(drainage.get("E", 0.0)),
                            float(drainage.get("N", 0.0)),
                            float(drainage.get("Z", 0.0)),
                        ],
                        "end": [
                            float(drainage.get("E2", 0.0)),
                            float(drainage.get("N2", 0.0)),
                            float(drainage.get("Z2", 0.0)),
                        ],
                        "diameter": float(drainage.get("Durchmesser", 0.0)) / 1000,  # mm zu m
                    },
                    "material": {
                        "name": drainage.get("Material", "PVC"),
                        "color": [0.6, 0.6, 0.6],
                        "roughness": 0.5,
                    },
                    "project": project_name,
                    "properties": {"gefaelle": float(drainage.get("Gefälle", 0.0))},
                }
            else:
                # Entwässerungsschacht
                # ClientA CSVs haben Probleme mit der Datenstruktur, fange Fehler ab
                try:
                    durchmesser = 0.0
                    if (
                        isinstance(drainage.get("Durchmesser"), str)
                        and drainage.get("Durchmesser").isdigit()
                    ):
                        durchmesser = float(drainage.get("Durchmesser", 0.0))

                    drainage_element = {
                        "type": "drainage_shaft",
                        "id": drainage.get("ID", "unknown"),
                        "name": drainage.get("Bezeichnung", "Unbenannter Entwässerungsschacht"),
                        "geometry": {
                            "type": "cylinder",
                            "radius": durchmesser / 2000,  # mm zu m und Durchmesser zu Radius
                            "height": 2.0,  # Standard-Höhe für Schächte
                            "position": [
                                float(drainage.get("E", 0.0)),
                                float(drainage.get("N", 0.0)),
                                float(drainage.get("Z", 0.0)),
                            ],
                        },
                        "material": {
                            "name": drainage.get("Material", "Beton"),
                            "color": [0.7, 0.7, 0.7],
                            "roughness": 0.8,
                        },
                        "project": project_name,
                    }
                except (ValueError, TypeError):
                    # Fallback bei Fehlern in den Daten
                    drainage_element = {
                        "type": "drainage_shaft",
                        "id": drainage.get("ID", "unknown"),
                        "name": drainage.get("Bezeichnung", "Unbenannter Entwässerungsschacht"),
                        "geometry": {
                            "type": "cylinder",
                            "radius": 0.5,  # Standardwert, wenn konvertierung fehlschlägt
                            "height": 2.0,
                            "position": [
                                float(drainage.get("E", 0.0))
                                if isinstance(drainage.get("E"), (int, float, str))
                                and str(drainage.get("E", "")).replace(".", "", 1).isdigit()
                                else 0.0,
                                float(drainage.get("N", 0.0))
                                if isinstance(drainage.get("N"), (int, float, str))
                                and str(drainage.get("N", "")).replace(".", "", 1).isdigit()
                                else 0.0,
                                float(drainage.get("Z", 0.0))
                                if isinstance(drainage.get("Z"), (int, float, str))
                                and str(drainage.get("Z", "")).replace(".", "", 1).isdigit()
                                else 0.0,
                            ],
                        },
                        "material": {
                            "name": drainage.get("Material", "Beton"),
                            "color": [0.7, 0.7, 0.7],
                            "roughness": 0.8,
                        },
                        "project": project_name,
                    }

            visualization_data["scene"]["elements"].append(drainage_element)

    return visualization_data


def convert_client_b_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert ClientB-Daten in ein visualisierbares Format.

    Args:
        data: ClientB-Daten

    Returns:
        Visualisierbares Format
    """
    visualization_data = {"scene": {"name": "ClientB Infrastrukturszene", "elements": []}}

    elements = data.get("elements", {})

    # Fundamente verarbeiten
    for foundation in elements.get("foundation", []):
        foundation_element = {
            "type": "foundation",
            "id": foundation.get("id", "unknown"),
            "name": foundation.get("bezeichnung", "Unbenanntes Fundament"),
            "geometry": {
                "type": "box",
                "dimensions": [
                    float(foundation.get("breite_m", 1.0)),
                    float(foundation.get("breite_m", 1.0)),
                    float(foundation.get("hoehe_m", 1.0)),
                ],
                "position": [
                    float(foundation.get("x_wert", 0.0)),
                    float(foundation.get("y_wert", 0.0)),
                    float(foundation.get("z_wert", 0.0)),
                ],
            },
            "material": {
                "name": foundation.get("material", "Beton"),
                "color": [0.7, 0.7, 0.7],
                "roughness": 0.8,
            },
            "properties": {"typ": foundation.get("fundament_typ", "")},
        }
        visualization_data["scene"]["elements"].append(foundation_element)

    # Masten verarbeiten
    for mast in elements.get("mast", []):
        mast_element = {
            "type": "mast",
            "id": mast.get("id", "unknown"),
            "name": mast.get("bezeichnung", "Unbenannter Mast"),
            "geometry": {
                "type": "cylinder",
                "radius": 0.25,
                "height": float(mast.get("hoehe_m", 8.0)),
                "position": [
                    float(mast.get("x_wert", 0.0)),
                    float(mast.get("y_wert", 0.0)),
                    float(mast.get("z_wert", 0.0)),
                ],
            },
            "material": {
                "name": mast.get("material", "Stahl"),
                "color": [0.5, 0.5, 0.5],
                "roughness": 0.3,
            },
            "properties": {
                "foundation_id": mast.get("fundament_id", ""),
                "typ": mast.get("mast_typ", ""),
                "azimut": float(mast.get("azimut_grad", 0.0)),
            },
        }
        visualization_data["scene"]["elements"].append(mast_element)

    # Entwässerung verarbeiten
    for drainage in elements.get("drainage", []):
        if drainage.get("typ") == "Pipe":
            # Entwässerungsleitung
            drainage_element = {
                "type": "drainage_pipe",
                "id": drainage.get("id", "unknown"),
                "name": drainage.get("bezeichnung", "Unbenannte Entwässerungsleitung"),
                "geometry": {
                    "type": "pipe",
                    "start": [
                        float(drainage.get("x_wert", 0.0)),
                        float(drainage.get("y_wert", 0.0)),
                        float(drainage.get("z_wert", 0.0)),
                    ],
                    "end": [
                        float(drainage.get("x_wert_ende", 0.0)),
                        float(drainage.get("y_wert_ende", 0.0)),
                        float(drainage.get("z_wert_ende", 0.0)),
                    ],
                    "diameter": float(drainage.get("durchmesser_mm", 0.0)) / 1000,  # mm zu m
                },
                "material": {
                    "name": drainage.get("material", "PVC"),
                    "color": [0.6, 0.6, 0.6],
                    "roughness": 0.5,
                },
                "properties": {"gefaelle": float(drainage.get("gefaelle_promille", 0.0))},
            }
        else:
            # Entwässerungsschacht
            try:
                durchmesser = 0.0
                if isinstance(drainage.get("durchmesser_mm"), (int, float, str)):
                    durchmesser = float(drainage.get("durchmesser_mm", 0.0))

                drainage_element = {
                    "type": "drainage_shaft",
                    "id": drainage.get("id", "unknown"),
                    "name": drainage.get("bezeichnung", "Unbenannter Entwässerungsschacht"),
                    "geometry": {
                        "type": "cylinder",
                        "radius": durchmesser / 2000,  # mm zu m und Durchmesser zu Radius
                        "height": 2.0,  # Standard-Höhe für Schächte
                        "position": [
                            float(drainage.get("x_wert", 0.0)),
                            float(drainage.get("y_wert", 0.0)),
                            float(drainage.get("z_wert", 0.0)),
                        ],
                    },
                    "material": {
                        "name": drainage.get("material", "Beton"),
                        "color": [0.7, 0.7, 0.7],
                        "roughness": 0.8,
                    },
                }
            except (ValueError, TypeError):
                drainage_element = {
                    "type": "drainage_shaft",
                    "id": drainage.get("id", "unknown"),
                    "name": drainage.get("bezeichnung", "Unbenannter Entwässerungsschacht"),
                    "geometry": {
                        "type": "cylinder",
                        "radius": 0.5,  # Standardwert
                        "height": 2.0,
                        "position": [0.0, 0.0, 0.0],  # Standardposition
                    },
                    "material": {
                        "name": drainage.get("material", "Beton"),
                        "color": [0.7, 0.7, 0.7],
                        "roughness": 0.8,
                    },
                }

        visualization_data["scene"]["elements"].append(drainage_element)

    return visualization_data


def convert_client_c_fdk_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert ClientC FDK-Daten in ein visualisierbares Format.

    Args:
        data: ClientC FDK-Daten

    Returns:
        Visualisierbares Format
    """
    visualization_data = {
        "scene": {"name": "ClientC FDK Infrastrukturszene", "elements": []},
        "meta": data.get("meta", {}),
    }

    elements = data.get("elements", {})

    # Bauphasen-Index erstellen
    bauphasen = {}
    for bauphase in data.get("bauphasen", []):
        if "id" in bauphase:
            bauphasen[bauphase["id"]] = bauphase

    # Gleisanlagen verarbeiten
    for gleis in elements.get("gleisAnlagen", []):
        is_curved = gleis.get("bogenRadius", 0) > 0

        # IFC-Daten sammeln
        ifc_data = {}
        if "ifc" in gleis:
            ifc_data = {
                "globalId": gleis["ifc"].get("globalId", ""),
                "elementTyp": gleis["ifc"].get("elementTyp", ""),
                "materialTyp": gleis["ifc"].get("materialTyp", ""),
                "kategorie": gleis["ifc"].get("kategorie", ""),
            }

        # Bauphase-Daten sammeln
        bauphase_data = {}
        if "bauphase" in gleis:
            bauphase_data = {
                "id": gleis["bauphase"].get("id", ""),
                "name": gleis["bauphase"].get("name", ""),
                "startDatum": gleis["bauphase"].get("startDatum", ""),
                "endDatum": gleis["bauphase"].get("endDatum", ""),
            }

        # Gleis-Element erstellen
        gleis_element = {
            "type": "curved_track" if is_curved else "track",
            "id": gleis.get("id", "unknown"),
            "name": gleis.get("name", "Unbenanntes Gleis"),
            "geometry": {
                "type": "curve" if is_curved else "line",
                "length": gleis.get("länge", 0.0),
                "gauge": gleis.get("spurweite", 1435) / 1000.0,  # mm zu m
                "radius": gleis.get("bogenRadius", 0.0),
            },
            "material": {
                "name": ifc_data.get("materialTyp", "Stahl"),
                "color": [0.1, 0.1, 0.1],
                "roughness": 0.2,
            },
            "ifc": ifc_data,
            "bauphase": bauphase_data,
        }

        visualization_data["scene"]["elements"].append(gleis_element)

    # Masten verarbeiten
    for mast in elements.get("masten", []):
        # Standort extrahieren
        position = [0.0, 0.0, 0.0]
        if "standort" in mast:
            standort = mast["standort"]
            # Hier könnten wir komplexere Koordinatenberechnungen durchführen
            position = [
                float(standort.get("kilometerLage", 0.0)) * 1000.0,  # km zu m
                float(standort.get("abstand", 0.0)),
                0.0,  # Z-Koordinate nicht direkt verfügbar
            ]

        # IFC-Daten sammeln
        ifc_data = {}
        if "ifc" in mast:
            ifc_data = {
                "globalId": mast["ifc"].get("globalId", ""),
                "elementTyp": mast["ifc"].get("elementTyp", ""),
                "materialTyp": mast["ifc"].get("materialTyp", ""),
                "kategorie": mast["ifc"].get("kategorie", ""),
            }

        # Bauphase-Daten sammeln
        bauphase_data = {}
        if "bauphase" in mast:
            bauphase_data = {
                "id": mast["bauphase"].get("id", ""),
                "name": mast["bauphase"].get("name", ""),
                "startDatum": mast["bauphase"].get("startDatum", ""),
                "endDatum": mast["bauphase"].get("endDatum", ""),
            }

        # Mast-Element erstellen
        mast_element = {
            "type": "mast",
            "id": mast.get("id", "unknown"),
            "name": mast.get("name", f"Mast {mast.get('id', 'unknown')}"),
            "geometry": {
                "type": "cylinder",
                "radius": 0.25,
                "height": mast.get("höhe", 8.0),
                "position": position,
            },
            "material": {
                "name": mast.get("material", ifc_data.get("materialTyp", "Stahl")),
                "color": [0.5, 0.5, 0.5],
                "roughness": 0.3,
            },
            "properties": {
                "typ": mast.get("typ", ""),
                "fundamentId": mast.get("fundamentId", ""),
            },
            "ifc": ifc_data,
            "bauphase": bauphase_data,
        }

        visualization_data["scene"]["elements"].append(mast_element)

    # Fundamente verarbeiten
    for fundament in elements.get("fundamente", []):
        # Standort extrahieren
        position = [0.0, 0.0, 0.0]
        if "standort" in fundament:
            standort = fundament["standort"]
            position = [
                float(standort.get("kilometerLage", 0.0)) * 1000.0,  # km zu m
                float(standort.get("abstand", 0.0)),
                0.0,  # Z-Koordinate nicht direkt verfügbar
            ]

        # IFC-Daten sammeln
        ifc_data = {}
        if "ifc" in fundament:
            ifc_data = {
                "globalId": fundament["ifc"].get("globalId", ""),
                "elementTyp": fundament["ifc"].get("elementTyp", ""),
                "materialTyp": fundament["ifc"].get("materialTyp", ""),
                "kategorie": fundament["ifc"].get("kategorie", ""),
            }

        # Bauphase-Daten sammeln
        bauphase_data = {}
        if "bauphase" in fundament:
            bauphase_data = {
                "id": fundament["bauphase"].get("id", ""),
                "name": fundament["bauphase"].get("name", ""),
                "startDatum": fundament["bauphase"].get("startDatum", ""),
                "endDatum": fundament["bauphase"].get("endDatum", ""),
            }

        # Fundament-Element erstellen
        fundament_element = {
            "type": "foundation",
            "id": fundament.get("id", "unknown"),
            "name": fundament.get("name", f"Fundament {fundament.get('id', 'unknown')}"),
            "geometry": {
                "type": "box",
                "dimensions": [
                    1.5,  # Standard-Breite
                    1.5,  # Standard-Breite
                    fundament.get("tiefe", 2.0),
                ],
                "position": position,
            },
            "material": {
                "name": fundament.get("material", ifc_data.get("materialTyp", "Beton")),
                "color": [0.7, 0.7, 0.7],
                "roughness": 0.8,
            },
            "properties": {
                "typ": fundament.get("typ", ""),
                "volumen": fundament.get("volumen", 0.0),
                "tragfähigkeit": fundament.get("tragfähigkeit", 0.0),
            },
            "ifc": ifc_data,
            "bauphase": bauphase_data,
        }

        visualization_data["scene"]["elements"].append(fundament_element)

    # Entwässerungssysteme verarbeiten
    for entwaesserung in elements.get("entwässerungssysteme", []):
        is_shaft = entwaesserung.get("typ") == "Schacht"

        # Standort extrahieren
        position = [0.0, 0.0, 0.0]
        end_position = [0.0, 0.0, 0.0]

        if "standort" in entwaesserung:
            standort = entwaesserung["standort"]
            if is_shaft:
                position = [
                    float(standort.get("kilometerLage", 0.0)) * 1000.0,  # km zu m
                    float(standort.get("abstand", 0.0)),
                    0.0,
                ]
            else:
                # Lineares Element mit Start und Ende
                if isinstance(standort.get("kilometerLage"), dict):
                    km_lage = standort["kilometerLage"]
                    position = [
                        float(km_lage.get("start", 0.0)) * 1000.0,  # km zu m
                        float(standort.get("abstand", 0.0)),
                        0.0,
                    ]
                    end_position = [
                        float(km_lage.get("ende", 0.0)) * 1000.0,  # km zu m
                        float(standort.get("abstand", 0.0)),
                        0.0,
                    ]

        # IFC-Daten sammeln
        ifc_data = {}
        if "ifc" in entwaesserung:
            ifc_data = {
                "globalId": entwaesserung["ifc"].get("globalId", ""),
                "elementTyp": entwaesserung["ifc"].get("elementTyp", ""),
                "materialTyp": entwaesserung["ifc"].get("materialTyp", ""),
                "kategorie": entwaesserung["ifc"].get("kategorie", ""),
            }

        # Bauphase-Daten sammeln
        bauphase_data = {}
        if "bauphase" in entwaesserung:
            bauphase_data = {
                "id": entwaesserung["bauphase"].get("id", ""),
                "name": entwaesserung["bauphase"].get("name", ""),
                "startDatum": entwaesserung["bauphase"].get("startDatum", ""),
                "endDatum": entwaesserung["bauphase"].get("endDatum", ""),
            }

        # Entwässerungs-Element erstellen
        if is_shaft:
            entwaesserung_element = {
                "type": "drainage_shaft",
                "id": entwaesserung.get("id", "unknown"),
                "name": entwaesserung.get("name", f"Schacht {entwaesserung.get('id', 'unknown')}"),
                "geometry": {
                    "type": "cylinder",
                    "radius": entwaesserung.get("durchmesser", 1.0) / 2.0,
                    "height": entwaesserung.get("tiefe", 3.5),
                    "position": position,
                },
                "material": {
                    "name": entwaesserung.get("material", ifc_data.get("materialTyp", "Beton")),
                    "color": [0.7, 0.7, 0.7],
                    "roughness": 0.8,
                },
                "ifc": ifc_data,
                "bauphase": bauphase_data,
            }
        else:
            entwaesserung_element = {
                "type": "drainage_pipe",
                "id": entwaesserung.get("id", "unknown"),
                "name": entwaesserung.get(
                    "name", f"Entwässerung {entwaesserung.get('id', 'unknown')}"
                ),
                "geometry": {
                    "type": "pipe",
                    "start": position,
                    "end": end_position,
                    "length": entwaesserung.get("länge", 0.0),
                    "diameter": 0.3,  # Standard-Durchmesser
                },
                "material": {
                    "name": entwaesserung.get("material", ifc_data.get("materialTyp", "PVC")),
                    "color": [0.6, 0.6, 0.6],
                    "roughness": 0.5,
                },
                "ifc": ifc_data,
                "bauphase": bauphase_data,
            }

        visualization_data["scene"]["elements"].append(entwaesserung_element)

    return visualization_data


def process_visualization(input_file: str, client_type: str, output_dir: str) -> bool:
    """
    Verarbeitet die importierten Daten für die Visualisierung.

    Args:
        input_file: Pfad zur importierten JSON-Datei
        client_type: Client-Typ (clientA, clientB, clientC oder clientC_fdk)
        output_dir: Ausgabeverzeichnis

    Returns:
        True, wenn die Verarbeitung erfolgreich war
    """
    try:
        # Ausgabeverzeichnis erstellen
        os.makedirs(output_dir, exist_ok=True)

        # Daten laden
        logger.info(f"Lade importierte Daten aus {input_file}...")
        data = load_json_data(input_file)

        if not data:
            logger.error("Keine gültigen Daten gefunden.")
            return False

        # Daten konvertieren
        logger.info(f"Konvertiere {client_type}-Daten in visualisierbares Format...")
        visualization_data = None

        if client_type == "clientA":
            visualization_data = convert_client_a_data(data)
        elif client_type == "clientB":
            visualization_data = convert_client_b_data(data)
        elif client_type == "clientC_fdk":
            visualization_data = convert_client_c_fdk_data(data)
        else:
            logger.error(f"Nicht unterstützter Client-Typ: {client_type}")
            return False

        if not visualization_data:
            logger.error("Fehler bei der Konvertierung.")
            return False

        # Statistiken
        element_count = len(visualization_data["scene"]["elements"])
        element_types = {}
        for element in visualization_data["scene"]["elements"]:
            element_type = element.get("type", "unknown")
            element_types[element_type] = element_types.get(element_type, 0) + 1

        logger.info(f"Insgesamt {element_count} Elemente für die Visualisierung vorbereitet:")
        for element_type, count in element_types.items():
            logger.info(f"  - {element_type}: {count} Elemente")

        # Ausgabedatei speichern
        output_file = os.path.join(output_dir, f"{client_type}_visualization.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(visualization_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Visualisierungsdaten in {output_file} gespeichert.")

        return True
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()

    # Visualisierung
    if process_visualization(args.input_file, args.client_type, args.output_dir):
        logger.info("Visualisierung erfolgreich erstellt.")
    else:
        logger.error("Fehler bei der Erstellung der Visualisierung.")
        sys.exit(1)


if __name__ == "__main__":
    main()
