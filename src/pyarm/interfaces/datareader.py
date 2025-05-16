"""
Protocols for reading data
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IDataReader(Protocol):
    """
    Protocol for components that can read data from a source.
    Different data sources implement this protocol.
    """

    @property
    def name(self) -> str:
        """Name of the reader"""
        ...

    @property
    def version(self) -> str:
        """Version of the reader"""
        ...

    @property
    def supported_formats(self) -> list[str]:
        """List of supported file formats"""
        ...

    def can_handle(self, file_path: str) -> bool:
        """
        Checks if this reader can handle the specified file.

        Parameters
        ----------
        file_path: str
            Path to the file

        Returns
        -------
        bool
            True if this reader can handle the file
        """
        ...

    def read_data(self, file_path: str) -> dict[str, Any]:
        """
        Reads data from the specified file.

        Parameters
        ----------
        file_path: str
            Path to the file

        Returns
        -------
        dict[str, Any]
            Dictionary with the read data
        """
        ...
