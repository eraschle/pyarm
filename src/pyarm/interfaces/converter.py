"""
Protocol for components that can convert data to another format.
"""

from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)


@runtime_checkable
class IDataConverter(Protocol[T]):
    """
    Protocol for components that can convert data to another format.
    """

    @property
    def name(self) -> str:
        """Name of the converter"""
        ...

    @property
    def version(self) -> str:
        """Version of the converter"""
        ...

    @property
    def supported_types(self) -> list[str]:
        """List of supported data types"""
        ...

    def can_convert(self, data: dict[str, Any]) -> bool:
        """
        Checks if this converter can convert the specified data.

        Parameters
        ----------
        data: dict[str, Any]
            Data to be converted

        Returns
        -------
        bool
            True if this converter can convert the data
        """
        ...

    def convert(self, data: dict[str, Any]) -> T:
        """
        Converts the specified data.

        Parameters
        ----------
        data: dict[str, Any]
            Data to be converted

        Returns
        -------
        T
            Converted data
        """
        ...
