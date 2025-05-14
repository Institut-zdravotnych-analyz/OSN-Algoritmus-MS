"""Data models.

More info: https://www.cksdrg.sk/sk/documents/file/DR%20davka%20274e_1.2?id=525
"""

from typing import NamedTuple


class Marker(NamedTuple):
    """Represents a DRG marker."""

    kod: str
    hodnota: str


class HospitalizacnyPripad(NamedTuple):
    """Represents a hospitalizacny pripad."""

    id: str
    vek: int | None
    hmotnost: float | None
    upv: int | None
    diagnozy: list[str]
    vykony: list[str]
    markery: list[Marker]
    drg: str | None
    druh_prijatia: int | None

    @property
    def je_dieta(self) -> bool | None:
        """Returns True if the hp is dieta, False if dospely, or None if vek is not defined."""
        if self.vek is None:
            return None
        return self.vek <= 18

    @property
    def age_category(self) -> str | None:
        """Returns the age category of the hp."""
        if self.vek is None:
            return None
        if self.vek >= 19:
            return "dospeli"
        if self.vek >= 16:
            return "deti_16"
        if self.vek >= 7:
            return "deti_7"
        if self.vek >= 1:
            return "deti_1"
        return "deti_0"
