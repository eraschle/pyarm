#!/usr/bin/env python3
"""
Eigenstaendiges Skript fuer den FDK-Import.
Dieses Skript importiert FDK-Daten ohne Abhaengigkeiten von komplexen Modellen.
"""

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="FDK-Daten importieren")

    parser.add_argument("--fdk_file", type=str, required=True, help="Pfad zur FDK-JSON-Datei")
    parser.add_argument("--output_dir", type=str, required=True, help="Verzeichnis fuer die Ausgabe")

    return parser.parse_args()


def read_fdk_data(file_path: str) -> Dict[str, Any]:
    """
    Liest FDK-JSON-Daten aus der angegebenen Datei.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Dictionary mit den gelesenen Daten
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json_content = json.load(f)

        # Pruefen ob es sich um eine FDK-Struktur handelt
        if "anlagenDaten" not in json_content:
            logger.error("Keine FDK-Daten gefunden. 'anlagenDaten' fehlt.")
            return {}

        return json_content["anlagenDaten"]
    except Exception as e:
        logger.error(f"Fehler beim Lesen der FDK-Daten: {str(e)}")
        return {}


def extract_elements(fdk_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extrahiert die verschiedenen Elementtypen aus den FDK-Daten.

    Args:
        fdk_data: FDK-Daten

    Returns:
        Dictionary mit den extrahierten Elementtypen
    """
    # Bauphasen indexieren fuer schnellen Zugriff
    bauphasen_dict = {}
    if "bauphasen" in fdk_data:
        for bauphase in fdk_data.get("bauphasen", []):
            if "id" in bauphase:
                bauphasen_dict[bauphase["id"]] = bauphase

    # Elementtypen und ihre Daten
    elements = {
        "gleisAnlagen": [],
        "masten": [],
        "fundamente": [],
        "entwaesserungssysteme": [],
        "bauphasen": fdk_data.get("bauphasen", []),
        "meta": fdk_data.get("meta", {}),
    }

    # Gleiselemente extrahieren
    for gleis in fdk_data.get("gleisAnlagen", []):
        gleis_data = {
            "id": gleis.get("id"),
            "name": gleis.get("name"),
            "typ": gleis.get("typ"),
            "laenge": gleis.get("laenge"),
            "spurweite": gleis.get("spurweite"),
            "bogenRadius": gleis.get("bogenRadius", 0),
        }

        # IFC-Daten hinzufuegen
        if "ifcDaten" in gleis:
            gleis_data["ifc"] = {
                "globalId": gleis["ifcDaten"].get("globalId"),
                "elementTyp": gleis["ifcDaten"].get("elementTyp"),
                "materialTyp": gleis["ifcDaten"].get("materialTyp"),
                "kategorie": gleis["ifcDaten"].get("kategorie"),
            }

        # Bauphase hinzufuegen
        if "bauphasenId" in gleis and gleis["bauphasenId"] in bauphasen_dict:
            bauphase = bauphasen_dict[gleis["bauphasenId"]]
            gleis_data["bauphase"] = {
                "id": bauphase.get("id"),
                "name": bauphase.get("name"),
                "startDatum": bauphase.get("startDatum"),
                "endDatum": bauphase.get("endDatum"),
            }

        elements["gleisAnlagen"].append(gleis_data)

    # Masten extrahieren
    for mast in fdk_data.get("masten", []):
        mast_data = {
            "id": mast.get("id"),
            "typ": mast.get("typ"),
            "hoehe": mast.get("hoehe"),
            "material": mast.get("material"),
            "fundamentId": mast.get("fundamentId"),
        }

        # Standort
        if "standort" in mast:
            mast_data["standort"] = mast["standort"]

        # IFC-Daten
        if "ifcDaten" in mast:
            mast_data["ifc"] = {
                "globalId": mast["ifcDaten"].get("globalId"),
                "elementTyp": mast["ifcDaten"].get("elementTyp"),
                "materialTyp": mast["ifcDaten"].get("materialTyp"),
                "kategorie": mast["ifcDaten"].get("kategorie"),
            }

        # Bauphase
        if "bauphasenId" in mast and mast["bauphasenId"] in bauphasen_dict:
            bauphase = bauphasen_dict[mast["bauphasenId"]]
            mast_data["bauphase"] = {
                "id": bauphase.get("id"),
                "name": bauphase.get("name"),
                "startDatum": bauphase.get("startDatum"),
                "endDatum": bauphase.get("endDatum"),
            }

        elements["masten"].append(mast_data)

    # Fundamente extrahieren
    for fundament in fdk_data.get("fundamente", []):
        fundament_data = {
            "id": fundament.get("id"),
            "typ": fundament.get("typ"),
            "tiefe": fundament.get("tiefe"),
            "volumen": fundament.get("volumen"),
            "material": fundament.get("material"),
            "tragfaehigkeit": fundament.get("tragfaehigkeit"),
        }

        # Standort
        if "standort" in fundament:
            fundament_data["standort"] = fundament["standort"]

        # IFC-Daten
        if "ifcDaten" in fundament:
            fundament_data["ifc"] = {
                "globalId": fundament["ifcDaten"].get("globalId"),
                "elementTyp": fundament["ifcDaten"].get("elementTyp"),
                "materialTyp": fundament["ifcDaten"].get("materialTyp"),
                "kategorie": fundament["ifcDaten"].get("kategorie"),
            }

        # Bauphase
        if "bauphasenId" in fundament and fundament["bauphasenId"] in bauphasen_dict:
            bauphase = bauphasen_dict[fundament["bauphasenId"]]
            fundament_data["bauphase"] = {
                "id": bauphase.get("id"),
                "name": bauphase.get("name"),
                "startDatum": bauphase.get("startDatum"),
                "endDatum": bauphase.get("endDatum"),
            }

        elements["fundamente"].append(fundament_data)

    # Entwaesserungssysteme extrahieren
    for entwaesserung in fdk_data.get("entwaesserungssysteme", []):
        entwaesserung_data = {
            "id": entwaesserung.get("id"),
            "typ": entwaesserung.get("typ"),
            "material": entwaesserung.get("material"),
        }

        # Typ-spezifische Daten
        if entwaesserung.get("typ") == "Schacht":
            entwaesserung_data["durchmesser"] = entwaesserung.get("durchmesser")
            entwaesserung_data["tiefe"] = entwaesserung.get("tiefe")
        else:
            entwaesserung_data["laenge"] = entwaesserung.get("laenge")

        # Standort
        if "standort" in entwaesserung:
            entwaesserung_data["standort"] = entwaesserung["standort"]

        # IFC-Daten
        if "ifcDaten" in entwaesserung:
            entwaesserung_data["ifc"] = {
                "globalId": entwaesserung["ifcDaten"].get("globalId"),
                "elementTyp": entwaesserung["ifcDaten"].get("elementTyp"),
                "materialTyp": entwaesserung["ifcDaten"].get("materialTyp"),
                "kategorie": entwaesserung["ifcDaten"].get("kategorie"),
            }

        # Bauphase
        if "bauphasenId" in entwaesserung and entwaesserung["bauphasenId"] in bauphasen_dict:
            bauphase = bauphasen_dict[entwaesserung["bauphasenId"]]
            entwaesserung_data["bauphase"] = {
                "id": bauphase.get("id"),
                "name": bauphase.get("name"),
                "startDatum": bauphase.get("startDatum"),
                "endDatum": bauphase.get("endDatum"),
            }

        elements["entwaesserungssysteme"].append(entwaesserung_data)

    return elements


def generate_visualization_data(
    elements: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Generiert Visualisierungsdaten aus den extrahierten Elementen.

    Args:
        elements: Extrahierte Elemente

    Returns:
        Visualisierungsdaten
    """
    # Metadaten
    meta = elements.get("meta", {})

    # Elementzaehlung
    element_counts = {
        "gleisAnlagen": len(elements.get("gleisAnlagen", [])),
        "masten": len(elements.get("masten", [])),
        "fundamente": len(elements.get("fundamente", [])),
        "entwaesserungssysteme": len(elements.get("entwaesserungssysteme", [])),
        "bauphasen": len(elements.get("bauphasen", [])),
    }

    # Visualisierungsdaten erstellen
    visualization_data = {
        "meta": {
            "projektName": meta.get("projektName", "Unbekannt"),
            "version": meta.get("version", "Unbekannt"),
            "erstellungsDatum": meta.get("erstellungsDatum", "Unbekannt"),
        },
        "elementCounts": element_counts,
        "elements": elements,
    }

    return visualization_data


def run_fdk_import(fdk_file: str, output_dir: str) -> bool:
    """
    Fuehrt den FDK-Import-Prozess aus.

    Args:
        fdk_file: Pfad zur FDK-JSON-Datei
        output_dir: Ausgabeverzeichnis

    Returns:
        True, wenn der Import erfolgreich war
    """
    try:
        # Ausgabeverzeichnis erstellen
        os.makedirs(output_dir, exist_ok=True)

        # FDK-Daten lesen
        logger.info(f"Lese FDK-Daten aus {fdk_file}...")
        fdk_data = read_fdk_data(fdk_file)
        if not fdk_data:
            logger.error("Keine gueltigen FDK-Daten gefunden.")
            return False

        # Elemente extrahieren
        logger.info("Extrahiere Elemente...")
        elements = extract_elements(fdk_data)

        # Statistik
        total_elements = sum(
            len(els) for key, els in elements.items() if key not in ["meta", "bauphasen"]
        )
        logger.info(f"Insgesamt {total_elements} Elemente extrahiert:")
        for key, els in elements.items():
            if key not in ["meta", "bauphasen"]:
                logger.info(f"  - {key}: {len(els)} Elemente")

        # Visualisierungsdaten generieren
        logger.info("Generiere Visualisierungsdaten...")
        visualization_data = generate_visualization_data(elements)

        # Ausgabedatei speichern
        output_file = os.path.join(output_dir, "fdk_visualization.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(visualization_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Visualisierungsdaten in {output_file} gespeichert.")

        # Metadaten speichern
        meta_file = os.path.join(output_dir, "fdk_metadata.json")
        meta_data = {
            "meta": elements.get("meta", {}),
            "bauphasen": elements.get("bauphasen", []),
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Metadaten in {meta_file} gespeichert.")

        return True
    except Exception as e:
        logger.error(f"Fehler beim FDK-Import: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()

    # FDK-Import-Prozess ausfuehren
    if run_fdk_import(args.fdk_file, args.output_dir):
        logger.info("FDK-Import-Prozess erfolgreich abgeschlossen")
    else:
        logger.error("FDK-Import-Prozess fehlgeschlagen")
        sys.exit(1)


if __name__ == "__main__":
    main()
