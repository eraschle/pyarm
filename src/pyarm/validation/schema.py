"""
Schemadefinitionen für das Validierungssystem.

Dieses Modul stellt Klassen zur Verfügung, die Validierungsregeln und Constraints
für verschiedene Elementtypen und deren Parameter definieren.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set

from pyarm.models.parameter import DataType, UnitEnum
from pyarm.models.process_enums import ElementType, ProcessEnum


class ConstraintType(Enum):
    """Arten von Constraints für Parameter."""

    REQUIRED = auto()  # Parameter must be present
    TYPE = auto()  # Parameter must match a specific type
    UNIT = auto()  # Parameter must have a specific unit
    MIN_VALUE = auto()  # Parameter must have a minimum value
    MAX_VALUE = auto()  # Parameter must not exceed a maximum value
    RANGE = auto()  # Parameter must be within a range
    REGEX = auto()  # Parameter must match a regex pattern
    ENUM = auto()  # Parameter must match an enumeration value
    CUSTOM = auto()  # Custom validation function
    MIN_LENGTH = auto()  # Parameter must have a minimum length
    MAX_LENGTH = auto()  # Parameter must not exceed a maximum length


@dataclass
class Constraint:
    """Repräsentiert eine Validierungsregel für einen Parameter."""

    constraint_type: ConstraintType
    value: Any = None
    message: Optional[str] = None
    custom_validator: Optional[Callable[[Any], bool]] = None

    def validate(self, param_value: Any) -> bool:
        """
        Prüft, ob der Parameterwert den Constraint erfüllt.

        Parameter
        ----------
        param_value : Any
            Der zu prüfende Parameterwert

        Rückgabe
        -------
        bool
            True, wenn der Wert den Constraint erfüllt
        """
        if self.constraint_type == ConstraintType.REQUIRED:
            return param_value is not None and param_value != ""

        if param_value is None:
            # If the value is None and we're not checking REQUIRED, the constraint is satisfied
            return True

        if self.constraint_type == ConstraintType.TYPE:
            expected_type = self.value
            if expected_type == DataType.FLOAT:
                return isinstance(param_value, (int, float))
            elif expected_type == DataType.INTEGER:
                return isinstance(param_value, int)
            elif expected_type == DataType.STRING:
                return isinstance(param_value, str)
            elif expected_type == DataType.BOOLEAN:
                return isinstance(param_value, bool)
            return False

        elif self.constraint_type == ConstraintType.UNIT:
            # This check is more complex and requires context - simplified here
            return True

        elif self.constraint_type == ConstraintType.MIN_VALUE:
            return param_value >= self.value

        elif self.constraint_type == ConstraintType.MAX_VALUE:
            return param_value <= self.value

        elif self.constraint_type == ConstraintType.RANGE:
            min_val, max_val = self.value
            return min_val <= param_value <= max_val

        elif self.constraint_type == ConstraintType.REGEX:
            import re

            pattern = self.value
            return bool(re.match(pattern, str(param_value)))

        elif self.constraint_type == ConstraintType.ENUM:
            valid_values = self.value
            return param_value in valid_values

        elif self.constraint_type == ConstraintType.CUSTOM:
            if self.custom_validator is not None:
                return self.custom_validator(param_value)
            return False
            
        elif self.constraint_type == ConstraintType.MIN_LENGTH:
            try:
                return len(str(param_value)) >= self.value
            except (TypeError, ValueError):
                return False
                
        elif self.constraint_type == ConstraintType.MAX_LENGTH:
            try:
                return len(str(param_value)) <= self.value
            except (TypeError, ValueError):
                return False

        return False  # Unknown constraint type

    def get_error_message(self, param_name: str, value: Any) -> str:
        """
        Gibt eine Fehlermeldung für einen verletzten Constraint zurück.

        Parameter
        ----------
        param_name : str
            Name des Parameters
        value : Any
            Aktueller Wert des Parameters

        Rückgabe
        -------
        str
            Fehlermeldung
        """
        if self.message:
            return self.message.format(param_name=param_name, value=value, expected=self.value)

        if self.constraint_type == ConstraintType.REQUIRED:
            message = f"Parameter '{param_name}' is required but not present"
            return message

        elif self.constraint_type == ConstraintType.TYPE:
            return (
                f"Parameter '{param_name}' hat falschen Typ. "
                f"Erwartet: {self.value}, Bekommen: {type(value).__name__}"
            )

        elif self.constraint_type == ConstraintType.UNIT:
            return (
                f"Parameter '{param_name}' hat falsche Einheit. "
                f"Erwartet: {self.value}, Bekommen: {value}"
            )

        elif self.constraint_type == ConstraintType.MIN_VALUE:
            return (
                f"Parameter '{param_name}' ist kleiner als der Mindestwert. "
                f"Wert: {value}, Minimum: {self.value}"
            )

        elif self.constraint_type == ConstraintType.MAX_VALUE:
            return (
                f"Parameter '{param_name}' ist größer als der Maximalwert. "
                "Wert: {value}, Maximum: {self.value}"
            )

        elif self.constraint_type == ConstraintType.RANGE:
            min_val, max_val = self.value
            return (
                f"Parameter '{param_name}' liegt außerhalb des gültigen Bereichs. "
                f"Wert: {value}, Bereich: [{min_val}, {max_val}]"
            )

        elif self.constraint_type == ConstraintType.REGEX:
            return (
                f"Parameter '{param_name}' entspricht nicht dem erwarteten Format. "
                "Wert: {value}, Muster: {self.value}"
            )

        elif self.constraint_type == ConstraintType.ENUM:
            return (
                f"Parameter '{param_name}' hat ungültigen Wert. "
                "Wert: {value}, Gültige Werte: {', '.join(map(str, self.value))}"
            )

        elif self.constraint_type == ConstraintType.CUSTOM:
            return (
                f"Parameter '{param_name}' erfüllt nicht die benutzerdefinierten "
                f"Validierungsregeln. Wert: {value}"
            )
            
        elif self.constraint_type == ConstraintType.MIN_LENGTH:
            return (
                f"Parameter '{param_name}' ist zu kurz. "
                f"Länge: {len(str(value))}, Mindestlänge: {self.value}"
            )
            
        elif self.constraint_type == ConstraintType.MAX_LENGTH:
            return (
                f"Parameter '{param_name}' ist zu lang. "
                f"Länge: {len(str(value))}, Maximallänge: {self.value}"
            )

        return f"Unbekannter Validierungsfehler für Parameter '{param_name}'"
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Regel in ein Dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary-Repräsentation der Regel
        """
        result = {"type": self.constraint_type.name}
        if self.value is not None and not callable(self.value):
            result["value"] = self.value
        if self.message:
            result["message"] = self.message
        return result


@dataclass
class SchemaDefinition:
    """
    Schema zur Definition der Validierungsregeln für Elementtypen.
    """

    # Element-Typ, für den dieses Schema gilt
    element_type: ElementType

    # Erforderliche Parameter für diesen Element-Typ
    required_params: Set[ProcessEnum] = field(default_factory=set)

    # Erwartete Typen für Parameter
    param_types: Dict[ProcessEnum, DataType] = field(default_factory=dict)

    # Erwartete Einheiten für Parameter
    param_units: Dict[ProcessEnum, UnitEnum] = field(default_factory=dict)

    # Validierungsconstraints für Parameter
    constraints: Dict[ProcessEnum, List[Constraint]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialisiert die Constraints basierend auf den anderen Eigenschaften."""
        # Für alle erforderlichen Parameter einen REQUIRED-Constraint erstellen
        for param_enum in self.required_params:
            if param_enum not in self.constraints:
                self.constraints[param_enum] = []

            # REQUIRED-Constraint hinzufügen
            required_constraint = Constraint(
                constraint_type=ConstraintType.REQUIRED,
                message=(
                    f"Parameter '{{param_name}}' ist für Element vom Typ "
                    f"'{self.element_type.value}' erforderlich"
                ),
            )
            self.constraints[param_enum].append(required_constraint)

        # Für alle Parameter mit definiertem Typ einen TYPE-Constraint erstellen
        for param_enum, datatype in self.param_types.items():
            if param_enum not in self.constraints:
                self.constraints[param_enum] = []

            # TYPE-Constraint hinzufügen
            type_constraint = Constraint(
                constraint_type=ConstraintType.TYPE,
                value=datatype,
                message=(
                    f"Parameter '{{param_name}}' muss vom Typ "
                    f"'{datatype.value}' sein, ist aber vom Typ '{{value.__class__.__name__}}'"
                ),
            )
            self.constraints[param_enum].append(type_constraint)

        # Für alle Parameter mit definierter Einheit einen UNIT-Constraint erstellen
        for param_enum, unit in self.param_units.items():
            if param_enum not in self.constraints:
                self.constraints[param_enum] = []

            # UNIT-Constraint hinzufügen
            unit_constraint = Constraint(
                constraint_type=ConstraintType.UNIT,
                value=unit,
                message=(
                    f"Parameter '{{param_name}}' muss die Einheit "
                    f"'{unit.value}' haben, hat aber '{{value}}'"
                ),
            )
            self.constraints[param_enum].append(unit_constraint)

    def add_constraint(self, param_enum: ProcessEnum, constraint: Constraint) -> None:
        """
        Fügt einen Constraint für einen Parameter hinzu.

        Parameter
        ----------
        param_enum : ProcessEnum
            Der Parameter-Enum, für den der Constraint gilt
        constraint : Constraint
            Der hinzuzufügende Constraint
        """
        if param_enum not in self.constraints:
            self.constraints[param_enum] = []
        self.constraints[param_enum].append(constraint)

    def add_range_constraint(
        self,
        param_enum: ProcessEnum,
        min_value: float,
        max_value: float,
        message: Optional[str] = None,
    ) -> None:
        """
        Fügt einen Bereichsconstraint für einen Parameter hinzu.

        Parameter
        ----------
        param_enum : ProcessEnum
            Der Parameter-Enum, für den der Constraint gilt
        min_value : float
            Der Mindestwert
        max_value : float
            Der Maximalwert
        message : Optional[str]
            Optionale benutzerdefinierte Fehlermeldung
        """
        if param_enum not in self.constraints:
            self.constraints[param_enum] = []

        constraint = Constraint(
            constraint_type=ConstraintType.RANGE,
            value=(min_value, max_value),
            message=message
            or f"Parameter '{{param_name}}' muss zwischen {min_value} und {max_value} liegen",
        )
        self.constraints[param_enum].append(constraint)

    def add_regex_constraint(
        self, param_enum: ProcessEnum, pattern: str, message: Optional[str] = None
    ) -> None:
        """
        Fügt einen Regex-Constraint für einen Parameter hinzu.

        Parameter
        ----------
        param_enum : ProcessEnum
            Der Parameter-Enum, für den der Constraint gilt
        pattern : str
            Das Regex-Muster
        message : Optional[str]
            Optionale benutzerdefinierte Fehlermeldung
        """
        if param_enum not in self.constraints:
            self.constraints[param_enum] = []

        constraint = Constraint(
            constraint_type=ConstraintType.REGEX,
            value=pattern,
            message=message
            or f"Parameter '{{param_name}}' muss dem Muster '{pattern}' entsprechen",
        )
        self.constraints[param_enum].append(constraint)

    def add_enum_constraint(
        self, param_enum: ProcessEnum, valid_values: List[Any], message: Optional[str] = None
    ) -> None:
        """
        Fügt einen Enum-Constraint für einen Parameter hinzu.

        Parameter
        ----------
        param_enum : ProcessEnum
            Der Parameter-Enum, für den der Constraint gilt
        valid_values : List[Any]
            Die gültigen Werte
        message : Optional[str]
            Optionale benutzerdefinierte Fehlermeldung
        """
        if param_enum not in self.constraints:
            self.constraints[param_enum] = []

        constraint = Constraint(
            constraint_type=ConstraintType.ENUM,
            value=valid_values,
            message=message
            or f"Parameter '{{param_name}}' muss einen der folgenden Werte haben: "
            f"{', '.join(map(str, valid_values))}",
        )
        self.constraints[param_enum].append(constraint)

    def add_custom_constraint(
        self, param_enum: ProcessEnum, validator: Callable[[Any], bool], message: str
    ) -> None:
        """
        Fügt einen benutzerdefinierten Constraint für einen Parameter hinzu.

        Parameter
        ----------
        param_enum : ProcessEnum
            Der Parameter-Enum, für den der Constraint gilt
        validator : Callable[[Any], bool]
            Die Validierungsfunktion
        message : str
            Die Fehlermeldung
        """
        if param_enum not in self.constraints:
            self.constraints[param_enum] = []

        constraint = Constraint(
            constraint_type=ConstraintType.CUSTOM, custom_validator=validator, message=message
        )
        self.constraints[param_enum].append(constraint)
