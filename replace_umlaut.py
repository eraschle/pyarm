import glob
import os
from pathlib import Path

REPLACE_MAP = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ß": "ss",
}


def search_replace_values(file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    for search_value, replace_value in REPLACE_MAP.items():
        content = content.replace(search_value, replace_value)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


if __name__ == "__main__":
    directory = Path(__file__).parent
    py_files = glob.glob(os.path.join(directory, "*.py"))
    for py_file in py_files:
        if py_file == __file__:
            continue
        search_replace_values(py_file)
        print(f"Ersetzungen in {py_file} vorgenommen.")
