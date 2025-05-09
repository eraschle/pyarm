"""
Client C spezifischer Datenleser.
Liest Daten aus SQL-Dateien für Client C.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set


class ClientCSqlReader:
    """
    Leser für SQL-Dateien des Clients C.
    Parst INSERT-Anweisungen aus SQL-Dateien und extrahiert die Daten.
    Unterstützt auch Metadaten und Property Sets aus erweiterten SQL-Schemas.
    """

    @property
    def name(self) -> str:
        return "ClientCSqlReader"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_formats(self) -> List[str]:
        return ["sql"]

    def can_handle(self, file_path: str) -> bool:
        path = Path(file_path)
        return path.suffix.lower() == ".sql" and ("clientC" in str(path))

    def read_data(self, file_path: str) -> Dict[str, Any]:
        """
        Liest SQL-Daten aus der angegebenen Datei und extrahiert die INSERT-Anweisungen.

        Args:
            file_path: Pfad zur SQL-Datei

        Returns:
            Dictionary mit den gelesenen Daten, gruppiert nach Elementtyp
        """
        with open(file_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Daten nach Elementtyp gruppieren
        data = {
            "foundation": self._extract_table_data(sql_content, "foundations"),
            "mast": self._extract_table_data(sql_content, "masts"),
            "joch": self._extract_table_data(sql_content, "yokes"),
            "track": self._extract_table_data(sql_content, "tracks"),
            "curved_track": self._extract_table_data(sql_content, "curved_tracks"),
            "drainage": self._extract_table_data(sql_content, "drainage"),
        }

        # Metadaten extrahieren (nur wenn vorhanden)
        metadata = {
            "element_types": self._extract_table_data(sql_content, "element_types"),
            "property_sets": self._extract_table_data(sql_content, "property_sets"),
            "properties": self._extract_table_data(sql_content, "properties"),
            "element_properties": self._extract_table_data(sql_content, "element_properties"),
        }

        # Verknüpfen von Properties mit Elementen
        self._enrich_elements_with_properties(data, metadata)

        return data

    def _extract_table_data(self, sql_content: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Extrahiert Daten für eine bestimmte Tabelle aus dem SQL-Content.

        Args:
            sql_content: SQL-Inhalt als String
            table_name: Name der Tabelle

        Returns:
            Liste von Dictionaries mit den extrahierten Daten
        """
        # Regex, um INSERT-Statements für die angegebene Tabelle zu finden
        pattern = rf"INSERT\s+INTO\s+{table_name}\s*\(([^)]+)\)\s*VALUES\s*((?:\([^;]+\),?)+);"
        match = re.search(pattern, sql_content, re.IGNORECASE | re.DOTALL)

        if not match:
            return []

        # Spalten extrahieren
        columns_str = match.group(1)
        columns = [col.strip() for col in columns_str.split(",")]

        # Werte extrahieren
        values_str = match.group(2)
        value_pattern = r"\(([^)]+)\)"
        value_matches = re.finditer(value_pattern, values_str)

        result = []
        for value_match in value_matches:
            values_row = value_match.group(1)
            values = self._parse_values(values_row)

            if len(columns) == len(values):
                row_data = dict(zip(columns, values))
                result.append(row_data)

        return result

    def _parse_values(self, values_str: str) -> List[Any]:
        """
        Parst eine Reihe von Werten aus einem SQL-INSERT-Statement.

        Args:
            values_str: String mit den zu parsenden Werten

        Returns:
            Liste der geparsten Werte
        """
        values = []
        value_pattern = r"'([^']*)'|NULL|([-+]?\d*\.?\d+)|([^,\s]+)"

        for match in re.finditer(value_pattern, values_str):
            string_val, num_val, other_val = match.groups()

            if string_val is not None:
                values.append(string_val)
            elif match.group(0).upper() == "NULL":
                values.append(None)
            elif num_val is not None:
                # Numerischen Wert parsen
                if "." in num_val:
                    values.append(float(num_val))
                else:
                    values.append(int(num_val))
            elif other_val is not None:
                values.append(other_val)

        return values

    def _enrich_elements_with_properties(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        metadata: Dict[str, List[Dict[str, Any]]],
    ) -> None:
        """
        Reichert die Elemente mit Property-Informationen an.

        Args:
            data: Dictionary mit Elementtypen und ihren Daten
            metadata: Dictionary mit Metadaten (element_types, property_sets, properties, element_properties)
        """
        # Wenn keine Property-Daten vorhanden sind, nichts tun
        if not metadata["element_properties"]:
            return

        # Erstelle einen Index von Property-IDs zu Property-Definitionen
        property_dict = {prop["id"]: prop for prop in metadata["properties"]}

        # Erstelle einen Index von Property-Set-IDs zu Property-Set-Definitionen
        pset_dict = {pset["id"]: pset for pset in metadata["property_sets"]}

        # Erstelle einen Index von Element-Typ-IDs zu Element-Typ-Definitionen
        element_type_dict = {et["id"]: et for et in metadata["element_types"]}

        # Gruppiere Element-Properties nach Element-ID
        element_property_dict: Dict[str, List[Dict[str, Any]]] = {}
        for ep in metadata["element_properties"]:
            element_id = ep["element_id"]
            if element_id not in element_property_dict:
                element_property_dict[element_id] = []
            element_property_dict[element_id].append(ep)

        # Durchlaufe alle Elementtypen und füge Properties hinzu
        for element_type, elements in data.items():
            for element in elements:
                element_id = element.get("id")
                if not element_id or element_id not in element_property_dict:
                    continue

                # Properties-Liste erstellen, falls nicht vorhanden
                if "properties" not in element:
                    element["properties"] = []

                # Property-Sets-Dictionary erstellen, falls nicht vorhanden
                if "property_sets" not in element:
                    element["property_sets"] = {}

                # Für jede Property dieses Elements
                for ep in element_property_dict[element_id]:
                    property_id = ep["property_id"]
                    if property_id not in property_dict:
                        continue

                    # Property-Definition holen
                    prop_def = property_dict[property_id]

                    # Property-Set-ID ermitteln und Property-Set-Definition holen
                    pset_id = prop_def.get("property_set_id")
                    pset_def = pset_dict.get(pset_id, {})
                    pset_name = pset_def.get("name", "Unknown")

                    # Wert aus dem richtigen Feld holen, je nach Datentyp
                    value = None
                    data_type = prop_def.get("data_type", "String").lower()
                    if data_type == "string":
                        value = ep.get("value_string")
                    elif data_type in ["float", "number"]:
                        value = ep.get("value_number")
                    elif data_type == "boolean":
                        value = ep.get("value_boolean")
                    elif data_type == "date":
                        value = ep.get("value_date")

                    # Property als Dictionary erstellen
                    property_data = {
                        "id": property_id,
                        "name": prop_def.get("name"),
                        "value": value,
                        "data_type": data_type,
                        "unit": prop_def.get("unit"),
                        "property_set": pset_name,
                    }

                    # Property zu Properties-Liste hinzufügen
                    element["properties"].append(property_data)

                    # Property-Set-Eintrag erstellen oder aktualisieren
                    if pset_name not in element["property_sets"]:
                        # Element-Typ-ID des Property-Sets ermitteln
                        element_type_id = pset_def.get("element_type_id")
                        element_type_info = element_type_dict.get(element_type_id, {})

                        element["property_sets"][pset_name] = {
                            "id": pset_id,
                            "description": pset_def.get("description"),
                            "element_type": element_type_info.get("name"),
                            "properties": {},
                        }

                    # Property zum Property-Set hinzufügen
                    element["property_sets"][pset_name]["properties"][prop_def.get("name")] = value

    def get_element_types(self, data: Dict[str, Any]) -> List[str]:
        """
        Ermittelt die verfügbaren Elementtypen in den Daten.

        Args:
            data: Dictionary mit den gelesenen Daten

        Returns:
            Liste der verfügbaren Elementtypen
        """
        return [element_type for element_type, items in data.items() if items]

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
