"""
Defines the process protocol for the PyArm system.
All processes must implement this protocol.
"""

from typing import List, Protocol

from pyarm.interfaces.validator import IValidator


class IProcessProtocol(Protocol):
    """
    Base protocol for all processes.
    Each process must implement this protocol.
    """

    def get_process_name(self) -> str:
        """
        Returns the name of the process.

        Returns
        -------
        str
            Name of the process
        """
        ...

    def get_validators(self) -> List[IValidator]:
        """
        Returns the validators used by this process.

        Returns
        -------
        List[IValidator]
            A list of validators for this process
        """
        ...
