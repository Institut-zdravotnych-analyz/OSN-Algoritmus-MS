"""Utility functions."""

import argparse
import logging
import re
from pathlib import Path

from osn_algoritmus.models import Marker

logger = logging.getLogger(__name__)

CSV_DELIMITER = "|"

INPUT_COLUMNS = [
    "id",
    "vek",
    "hmotnost",
    "umela_plucna_ventilacia",
    "diagnozy",
    "vykony",
    "markery",
    "drg",
    "druh_prijatia",
]


def log_error_or_warning(logger: logging.Logger, message: str, *, error: bool) -> None:
    """Log an error or warning message."""
    if error:
        logger.error(message)
    else:
        logger.warning(message)


def standardize_code(kod: str) -> str:
    """Convert input to lowercase and remove all non-alphanumeric characters."""
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()


def create_diagnozy_from_str(diagnozy_str: str) -> list[str]:
    """Create a list of kód diagnózy from a string."""
    if not diagnozy_str:
        return []
    diagnozy = []
    for kod in diagnozy_str.split("@"):
        if kod == "":
            msg = f"Invalid format of diagnozy: {diagnozy_str!r}. Expected format 'diagnoza1@diagnoza2@...'."
            raise ValueError(msg)
        diagnozy.append(standardize_code(kod))
    return diagnozy


def create_vykony_from_str(vykony_str: str) -> list[str]:
    """Create a list of kód výkonu from a string."""
    if not vykony_str:
        return []
    vykony = vykony_str.split("@")
    if "" in vykony[1:]:
        msg = (
            f"Invalid format of vykony: {vykony_str!r}."
            " Only the first vykon can be empty. Expected format '[vykon1]@vykon2@...'."
        )
        raise ValueError(msg)
    return vykony


def create_markery_from_str(markery: str) -> list[Marker]:
    """Create a list of marker from a string."""
    if not markery:
        return []
    result = []
    for marker_str in markery.split("@"):
        parts = marker_str.split("&")
        if len(parts) != 2 or any(part == "" for part in parts):
            msg = f"Invalid marker format: {marker_str!r}. Expected format 'kod&hodnota'."
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


def setup_parser(
    *,
    input_path: bool = False,
    output_path: bool = False,
    vsetky_vykony_hlavne: bool = False,
    vyhodnot_neuplne_pripady: bool = False,
    ponechaj_duplicity: bool = False,
) -> argparse.ArgumentParser:
    """Create a parser for the command-line arguments.

    Args:
        input_path: If True, add an argument for the input path.
        output_path: If True, add an argument for the output path.
        vsetky_vykony_hlavne: If True, add an argument for vsetky_vykony_hlavne flag.
        vyhodnot_neuplne_pripady: If True, add an argument for vyhodnot_neuplne_pripady flag.
        ponechaj_duplicity: If True, add an argument for ponechaj_duplicity flag.

    Returns:
        The parser with the added arguments.

    """
    parser = argparse.ArgumentParser(
        prog="python -m osn_algoritmus",
        description="Skript na priraďovanie hospitalizačných prípadov do medicínskych služieb.",
    )

    if input_path:
        parser.add_argument("input_path", type=Path, help="Cesta k súboru so vstupnými dátami.")
    if output_path:
        parser.add_argument(
            "output_path",
            type=Path,
            nargs="?",
            default=None,
            help="Cesta k výstupnému súboru. Ak nie je zadaná, vytvorí sa odvodením od vstupného súboru.",
        )
    if vsetky_vykony_hlavne:
        parser.add_argument(
            "--vsetky_vykony_hlavne",
            "-v",
            action="store_true",
            help=(
                "Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z vykázaných výkonov mohol byť hlavný. Štandardne"
                " sa za hlavný výkon považuje iba prvý vykázaný, prípadne žiaden, pokiaľ zoznam začína znakom '@'."
            ),
        )
    if vyhodnot_neuplne_pripady:
        parser.add_argument(
            "--vyhodnot_neuplne_pripady",
            "-n",
            action="store_true",
            help=(
                "V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne"
                " vráti hodnotu 'ERROR'."
            ),
        )
    if ponechaj_duplicity:
        parser.add_argument(
            "--ponechaj_duplicity",
            "-d",
            action="store_true",
            help="Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.",
        )
    return parser

def get_number_of_lines(file_path: Path) -> int:
    """Get the number of lines in a file."""
    with file_path.open("r") as f:
        return sum(1 for _ in f)
