"""Main module for OSN-Algoritmus-MS."""

import argparse
from collections.abc import Generator
from copy import deepcopy
from pathlib import Path

from OSN_Algoritmus.priprava_dat import (
    priprav_citac_dat,
    priprav_hp,
    priprav_zapisovac_dat,
    validuj_hp,
)
from OSN_Algoritmus.vyhodnotenie_priloh import prirad_ms


def setup_parser(
    *,
    input_path: bool = False,
    output_path: bool = False,
    vsetky_vykony_hlavne: bool = False,
    vyhodnot_neuplne_pripady: bool = False,
    ponechaj_duplicity: bool = False,
) -> argparse.ArgumentParser:
    """Add common command-line arguments to an ArgumentParser instance.

    Args:
        input_path: If True, add an argument for the input path.
        output_path: If True, add an argument for the output path.
        vsetky_vykony_hlavne: If True, add an argument for the vsetky_vykony_hlavne flag.
        vyhodnot_neuplne_pripady: If True, add an argument for the vyhodnot_neuplne_pripady flag.
        ponechaj_duplicity: If True, add an argument for the ponechaj_duplicity flag.

    Returns:
        The ArgumentParser instance with added arguments.

    """
    parser = argparse.ArgumentParser(
        description="Skript na priraďovanie hospitalizačných prípadov do medicínskych služieb."
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
                " sa za hlavný výkon považuje iba prvý vykázaný, prípadne žiaden, pokiaľ zoznam začína znakom '~'."
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


def load_hospitalizacne_pripady(input_path: Path) -> Generator[dict, None, None]:
    """Yield hospitalizacne pripady from the input file.

    Args:
        input_path: Path to the file containing hospitalizacne pripady.

    Yields:
        dict: hospitalizacny pripad

    """
    with input_path.open("r", encoding="utf-8") as input_file:
        reader = priprav_citac_dat(input_file)
        yield from reader


def process_hospitalizacny_pripad(
    hospitalizacny_pripad: dict,
    *,
    vsetky_vykony_hlavne: bool = False,
    vyhodnot_neuplne_pripady: bool = False,
    ponechaj_duplicity: bool = False,
) -> str:
    """Process hospitalizacny pripad and assign medicinske sluzby.

    Args:
        hospitalizacny_pripad: Hospitalizacny pripad to process.
        vsetky_vykony_hlavne: When evaluation prilohy, assume that any of vykony could be hlavny.
        vyhodnot_neuplne_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the function will return 'ERROR'.
        ponechaj_duplicity: Keep duplicate records in the output list of medicinske sluzby.

    Returns:
        str: Kody medicinskych sluzieb concatenated by '~'.

    """
    hp = deepcopy(hospitalizacny_pripad)

    if not validuj_hp(hp, vyhodnot_neuplne_pripady):
        return "ERROR"

    priprav_hp(hp)
    medicinske_sluzby = prirad_ms(hp, vsetky_vykony_hlavne)

    if not ponechaj_duplicity:
        # deduplicate medicinske sluzby, keep order
        medicinske_sluzby = list(dict.fromkeys(medicinske_sluzby))

    return "~".join(medicinske_sluzby)


def grouper_ms(
    input_path: Path,
    output_path: Path | None = None,
    *,
    vsetky_vykony_hlavne: bool = False,
    vyhodnot_neuplne_pripady: bool = False,
    ponechaj_duplicity: bool = False,
) -> None:
    """Assign medicinske sluzby to hospitalizacne pripady.

    Create a copy of the input file with a new column containing the list of assigned medicinske sluzby.

    Args:
        input_path: Path to the file containing hospitalizacne pripady.
        output_path: Path to the output file. If not provided, a new file will be created.
        vsetky_vykony_hlavne: When evaluating prilohy, assume that any of vykony could be hlavny.
        vyhodnot_neuplne_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the assigned medicinske sluzby will be 'ERROR'.
        ponechaj_duplicity: Keep duplicate records in the output list of medicinske sluzby.

    """
    if output_path is None:
        output_path = Path(input_path).with_stem(f"{input_path.stem}_output")

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = priprav_zapisovac_dat(output_file)
        writer.writeheader()

        for hospitalizacny_pripad in load_hospitalizacne_pripady(input_path):
            hospitalizacny_pripad["ms"] = process_hospitalizacny_pripad(
                hospitalizacny_pripad,
                vsetky_vykony_hlavne=vsetky_vykony_hlavne,
                vyhodnot_neuplne_pripady=vyhodnot_neuplne_pripady,
                ponechaj_duplicity=ponechaj_duplicity,
            )
            writer.writerow(hospitalizacny_pripad)
