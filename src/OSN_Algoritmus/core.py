"""Hlavný modul pre OSN-Algoritmus-MS."""

import argparse
from copy import deepcopy
from pathlib import Path

from OSN_Algoritmus.priprava_dat import (
    priprav_citac_dat,
    priprav_hp,
    priprav_zapisovac_dat,
    validuj_hp,
)
from OSN_Algoritmus.vyhodnotenie_priloh import prirad_ms


def setup_parser(parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """Add common command-line arguments to an ArgumentParser instance.

    Args:
        parser: An existing ArgumentParser instance. If None, a new one is created.

    Returns:
        The ArgumentParser instance with added arguments.

    """
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.add_argument(
        "--vsetky_vykony_hlavne",
        "-v",
        action="store_true",
        help=(
            "Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z vykázaných výkonov mohol byť hlavný. Štandardne sa"
            " za hlavný výkon považuje iba prvý vykázaný, prípadne žiaden, pokiaľ zoznam začína znakom '~'."
        ),
    )
    parser.add_argument(
        "--vyhodnot_neuplne_pripady",
        "-n",
        action="store_true",
        help=(
            "V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne vráti "
            "hodnotu 'ERROR'."
        ),
    )
    parser.add_argument(
        "--ponechaj_duplicity",
        "-d",
        action="store_true",
        help="Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.",
    )
    return parser


def load_hospitalizacne_pripady(input_path: Path):
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
        hospitalizacny_pripad (dict): Hospitalizacny pripad to process.
        vsetky_vykony_hlavne (bool): Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z výkazaných výkonov mohol byť
            hlavný.
        vyhodnot_neuplne_pripady (bool): V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo
            vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.
        ponechaj_duplicity (bool): Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.

    Returns:
        str: Zoznam medicínskych služieb oddelených "~".

    """
    hp = deepcopy(hospitalizacny_pripad)

    if not validuj_hp(hp, vyhodnot_neuplne_pripady):
        hp["ms"] = "ERROR"
        return hp

    priprav_hp(hp)
    medicinske_sluzby = prirad_ms(hp, vsetky_vykony_hlavne)

    if not ponechaj_duplicity:
        # deduplikuj medicinske sluzby
        medicinske_sluzby = set(medicinske_sluzby)

    return "~".join(medicinske_sluzby)


def grouper_ms(
    input_path: Path,
    output_path: Path | None = None,
    *,
    vsetky_vykony_hlavne: bool = False,
    vyhodnot_neuplne_pripady: bool = False,
    ponechaj_duplicity: bool = False,
):
    """Assign medicinske sluzby to hospitalizacne pripady.

    Create a copy of the input file with a new column containing the list of assigned medicinske sluzby.

    Args:
        input_path: Path to the file containing hospitalizacne pripady.
        output_path: Path to the output file. If not provided, a new file will be created.
        vsetky_vykony_hlavne: Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z výkazaných výkonov mohol byť hlavný.
        vyhodnot_neuplne_pripady: V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo
            vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.
        ponechaj_duplicity: Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.

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
