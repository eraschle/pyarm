"""
Haupteinstiegspunkt für die Anwendung.
"""

import os
import sys
import argparse
from pathlib import Path
import logging
import importlib.util

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.getcwd())

from clients.clientA.code.reader import ClientAJsonReader, ClientACsvReader
from clients.clientA.code.converter import ClientAConverter
from clients.clientB.code.reader import ClientBCsvReader  # würde implementiert werden
from clients.clientB.code.converter import (
    ClientBConverter,
)  # würde implementiert werden
from clients.clientC.code.reader import ClientCSqlReader
from clients.clientC.code.converter import ClientCConverter
from code.repository.json_repository import JsonElementRepository
from code.processes.process1_visualization import VisualizationProcess
from code.processes.process2_calculation import CalculationProcess


# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="Infrastrukturelemente verarbeiten")

    parser.add_argument(
        "--client",
        type=str,
        required=True,
        choices=["clientA", "clientB", "clientC"],
        help="Zu verarbeitender Client",
    )
    parser.add_argument("--project", type=str, help="Zu verarbeitendes Projekt (für Client A)")
    parser.add_argument(
        "--input_dir", type=str, required=True, help="Verzeichnis mit Eingabedateien"
    )
    parser.add_argument(
        "--repository_dir",
        type=str,
        required=True,
        help="Verzeichnis für das Repository",
    )
    parser.add_argument("--output_dir", type=str, required=True, help="Verzeichnis für die Ausgabe")
    parser.add_argument(
        "--process",
        type=str,
        choices=["visualization", "calculation", "fdk_import", "both"],
        default="both",
        help="Auszuführender Prozess",
    )
    parser.add_argument(
        "--fdk_file", type=str, help="Pfad zur FDK-JSON-Datei (für FDK-Import-Prozess)"
    )

    return parser.parse_args()


def get_reader_and_converter(client, project=None):
    """Reader und Converter für den angegebenen Client holen."""
    if client == "clientA":
        readers = [ClientAJsonReader(), ClientACsvReader()]
        converter = ClientAConverter()
    elif client == "clientB":
        readers = [ClientBCsvReader()]
        converter = ClientBConverter()
    elif client == "clientC":
        readers = [ClientCSqlReader(), ClientCFdkReader()]
        converter = ClientCConverter()
    else:
        raise ValueError(f"Unbekannter Client: {client}")

    return readers, converter


def process_files(input_dir, client, project, repository_dir):
    """
    Dateien verarbeiten und in das Repository speichern.

    Args:
        input_dir: Verzeichnis mit Eingabedateien
        client: Client-ID
        project: Projekt-ID (optional)
        repository_dir: Verzeichnis für das Repository
    """
    # Repository initialisieren
    repository = JsonElementRepository(repository_dir)

    # Reader und Converter holen
    readers, converter = get_reader_and_converter(client, project)

    # Pfad zum Eingabeverzeichnis
    input_path = Path(input_dir)
    if project:
        input_path = input_path / client / project
    else:
        input_path = input_path / client

    # Alle Dateien im Eingabeverzeichnis durchlaufen
    processed_files = 0
    converted_elements = 0

    for file_path in input_path.glob("**/*"):
        if file_path.is_file():
            # Passenden Reader finden
            reader = None
            for r in readers:
                if r.can_handle(str(file_path)):
                    reader = r
                    break

            if reader:
                try:
                    # Daten lesen
                    data = reader.read_data(str(file_path))

                    # Daten konvertieren, wenn möglich
                    if converter.can_convert(data):
                        elements = converter.convert(data)

                        # Elemente im Repository speichern
                        repository.save_all(elements)

                        logger.info(
                            f"Datei verarbeitet: {file_path.name}, {len(elements)} Elemente konvertiert"
                        )
                        processed_files += 1
                        converted_elements += len(elements)
                    else:
                        logger.warning(f"Konverter kann Daten nicht konvertieren: {file_path.name}")
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten von {file_path.name}: {e}")

    logger.info(
        f"Verarbeitung abgeschlossen: {processed_files} Dateien, {converted_elements} Elemente"
    )

    return repository


def run_visualization_process(repository_dir, output_dir):
    """Visualisierungsprozess ausführen."""
    logger.info("Starte Visualisierungsprozess...")
    vis_output_dir = os.path.join(output_dir, "visualization")
    process = VisualizationProcess(repository_dir, vis_output_dir)
    process.run()
    logger.info("Visualisierungsprozess abgeschlossen")


def run_calculation_process(repository_dir, output_dir):
    """Berechnungsprozess ausführen."""
    logger.info("Starte Berechnungsprozess...")
    calc_output_dir = os.path.join(output_dir, "calculation")
    process = CalculationProcess(repository_dir, calc_output_dir)
    process.run()
    logger.info("Berechnungsprozess abgeschlossen")


def run_fdk_import_process(fdk_file, repository_dir, output_dir):
    """FDK-Import-Prozess ausführen."""
    if not fdk_file:
        logger.error("Keine FDK-Datei angegeben. Verwende --fdk_file Parameter.")
        return False

    # FDK-Import-Prozess-Klasse dynamisch importieren
    try:
        # Pfad zum Modul ermitteln
        fdk_process_path = os.path.join(os.getcwd(), "code/processes/process3_fdk_import.py")

        # Modul dynamisch laden
        spec = importlib.util.spec_from_file_location("process3_fdk_import", fdk_process_path)
        fdk_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fdk_module)

        # Prozessklasse aus dem Modul holen
        FdkImportProcess = fdk_module.FdkImportProcess

        logger.info(f"Starte FDK-Import-Prozess für Datei: {fdk_file}")
        fdk_output_dir = os.path.join(output_dir, "fdk_import")
        process = FdkImportProcess(fdk_file, repository_dir, fdk_output_dir)
        result = process.run()

        if result["status"] == "success":
            logger.info(
                f"FDK-Import-Prozess abgeschlossen. {result['conversion_stats']['converted_elements']} Elemente importiert."
            )
            return True
        else:
            logger.error(
                f"FDK-Import-Prozess fehlgeschlagen: {result.get('message', 'Unbekannter Fehler')}"
            )
            return False
    except Exception as e:
        logger.error(f"Fehler beim Importieren oder Ausführen des FDK-Prozesses: {str(e)}")
        return False


def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()

    # Verzeichnisse erstellen
    os.makedirs(args.repository_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    # FDK-Import-Prozess ausführen, wenn ausgewählt
    if args.process == "fdk_import":
        if run_fdk_import_process(args.fdk_file, args.repository_dir, args.output_dir):
            logger.info("FDK-Import-Prozess erfolgreich abgeschlossen")
        else:
            logger.error("FDK-Import-Prozess fehlgeschlagen")
        return

    # Standardprozesse ausführen
    process_files(args.input_dir, args.client, args.project, args.repository_dir)

    # Prozesse ausführen
    if args.process in ["visualization", "both"]:
        run_visualization_process(args.repository_dir, args.output_dir)

    if args.process in ["calculation", "both"]:
        run_calculation_process(args.repository_dir, args.output_dir)

    logger.info("Alle Prozesse abgeschlossen")


if __name__ == "__main__":
    main()
