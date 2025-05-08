"""Data models."""

from typing import NamedTuple


class Marker(NamedTuple):
    """Represents a marker. TODO: add link or some info about markers."""

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
    def je_dieta(self) -> bool:
        """Returns True if the hp is dieta."""
        if self.vek is None:
            msg = "Cannot determine if the hp is dieta because the vek is not defined."
            raise ValueError(msg)
        return self.vek <= 18

    @property
    def hlavny_vykon(self) -> str:
        """Returns hlavny vykon."""
        if len(self.vykony) == 0:
            msg = "Cannot determine hlavny vykon because the vykony are not defined."
            raise ValueError(msg)
        return self.vykony[0]

    @property
    def vedlajsie_vykony(self) -> list[str]:
        """Returns vedlajsie vykony."""
        return self.vykony[1:]

    @property
    def hlavna_diagnoza(self) -> str:
        """Returns hlavna diagnoza."""
        if len(self.diagnozy) == 0:
            msg = "Cannot determine hlavna diagnoza because the diagnozy are not defined."
            raise ValueError(msg)
        return self.diagnozy[0]

    @property
    def vedlajsie_diagnozy(self) -> list[str]:
        """Returns vedlajsie diagnozy."""
        return self.diagnozy[1:]
