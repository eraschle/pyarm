import math
from typing import Any

from pyarm.models.process_enums import ProcessEnum


def calculate_line_length(params: dict[ProcessEnum, Any]) -> float | None:
    # Berechne Länge, wenn Start- und Endpunkte vorhanden sind
    point = (
        params.get(ProcessEnum.X_COORDINATE),
        params.get(ProcessEnum.Y_COORDINATE),
        params.get(ProcessEnum.Z_COORDINATE) or 0.0,
    )
    other = (
        params.get(ProcessEnum.X_COORDINATE_END),
        params.get(ProcessEnum.Y_COORDINATE_END),
        params.get(ProcessEnum.Z_COORDINATE_END) or 0.0,
    )
    return calculate_length(point, other)


def calculate_length(point: tuple[Any, ...], other: tuple[Any, ...]) -> float | None:
    pow_values = []
    for pnt, oth in zip(point, other):
        pow_values.append(abs(float(pnt) - float(oth)) ** 2)
    if len(pow_values) != 3:
        return None
    pow_sum = sum(pow_values)
    try:
        return math.sqrt(pow_sum)
    except ValueError:
        return None
