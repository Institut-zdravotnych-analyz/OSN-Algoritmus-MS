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
