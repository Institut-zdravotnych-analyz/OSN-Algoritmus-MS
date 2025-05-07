"""Modul s pomocnymi funkciami a datovymi typmi."""

import re
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


def standardize_code(kod: str) -> str:
    """Convert input to lowercase and remove all non-alphanumeric characters."""
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()


def create_diagnozy_from_str(diagnozy: str) -> list[str]:
    """Create a list of kód diagnózy from a string."""
    return [standardize_code(diagnoza) for diagnoza in diagnozy.split("~")] if diagnozy else []


def create_vykony_from_str(vykony: str) -> list[str]:
    """Create a list of kód výkonu from a string."""
    if not vykony:
        return []
    kody_vykonov = []
    for vykon_str in vykony.split("~"):
        parts = vykon_str.split("&")
        if len(parts) != 3:
            msg = f"Neplatný formát výkonu: '{vykon_str}'. Očakáva sa formát 'kod_vykonu&lokalizacia&datum_vykonu'."
            raise ValueError(msg)
        kody_vykonov.append(standardize_code(parts[0]))
    return kody_vykonov


def create_markery_from_str(markery: str) -> list[Marker]:
    """Create a list of marker from a string."""
    if not markery:
        return []
    result = []
    for marker_str in markery.split("~"):
        parts = marker_str.split("&")
        if len(parts) != 2:
            msg = f"Invalid marker format: '{marker_str}'. Expected format 'kod&hodnota'."
            raise ValueError(msg)
        result.append(Marker(kod=parts[0], hodnota=parts[1]))
    return result


def is_subdict(subdict: dict, superdict: dict) -> bool:
    """Return True if all keys and values in the subdict are in the superdict."""
    return all(k in superdict and superdict[k] == v for k, v in subdict.items())


def uses_marker(table_name: str, row: dict) -> bool:
    """Return True if the row in the table uses a marker."""
    # Tables that use markers but are not in structured form in this project.
    tables_with_markers = {
        "p5_NOV": [
            {
                "doplnujuce_kriterium": "Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie pracovisko",  # noqa: E501
            },
            {
                "doplnujuce_kriterium": "Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)",
            },
        ],
        "p6_DRGD_deti": [{"doplnujuce_kriterium": "marker Pacient nespĺňa medicínske kritériá polytraumy"}],
        "p6_DRGD_dospeli": [{"doplnujuce_kriterium": "marker Pacient nespĺňa medicínske kritériá polytraumy"}],
    }
    if row["marker"] is not None:
        return True
    if table_name in tables_with_markers:
        for condition in tables_with_markers[table_name]:
            if is_subdict(condition, row):
                return True
    return False
