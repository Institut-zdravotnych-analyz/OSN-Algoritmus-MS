"""Core functionality of the osn_algoritmus package."""

import argparse
from collections.abc import Generator
from pathlib import Path

from osn_algoritmus.input_preparation import create_hp_from_row, prepare_data_reader, prepare_data_writer
from osn_algoritmus.prilohy_evaluation import prirad_ms


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
        vsetky_vykony_hlavne: If True, add an argument for vsetky_vykony_hlavne flag.
        vyhodnot_neuplne_pripady: If True, add an argument for vyhodnot_neuplne_pripady flag.
        ponechaj_duplicity: If True, add an argument for ponechaj_duplicity flag.

    Returns:
        The ArgumentParser instance with added arguments.

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


def load_input_rows(input_path: Path) -> Generator[dict, None, None]:
    """Yield rows from the input file.

    Args:
        input_path: Path to the file containing hospitalizacne pripady.

    Yields:
        row containing hospitalizacny pripad

    """
    with input_path.open("r", encoding="utf-8") as input_file:
        reader = prepare_data_reader(input_file)
        yield from reader


def process_input_row(
    input_hp_row: dict,
    *,
    all_vykony_hlavne: bool = False,
    evaluate_incomplete_pripady: bool = False,
    allow_duplicates: bool = False,
) -> str:
    """Process input row by creating a hospitalizacny pripad and assigning medicinske sluzby.

    Args:
        input_hp_row: Input row to process.
        all_vykony_hlavne: When evaluation prilohy, assume that any of vykony could be hlavny.
        evaluate_incomplete_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the function will return 'ERROR'.
        allow_duplicates: Keep duplicate records in the output list of medicinske sluzby.

    Returns:
        str: Kody medicinskych sluzieb concatenated by '~'.

    """
    hp = create_hp_from_row(input_hp_row, evaluate_incomplete_pripady=evaluate_incomplete_pripady)

    if hp is None:
        return "ERROR"

    medicinske_sluzby = prirad_ms(hp, all_vykony_hlavne=all_vykony_hlavne)

    if not allow_duplicates:
        # deduplicate medicinske sluzby, keep order
        medicinske_sluzby = list(dict.fromkeys(medicinske_sluzby))

    return "~".join(medicinske_sluzby)


def grouper_ms(
    input_path: Path,
    output_path: Path | None = None,
    *,
    all_vykony_hlavne: bool = False,
    evaluate_incomplete_pripady: bool = False,
    allow_duplicates: bool = False,
) -> None:
    """Assign medicinske sluzby to hospitalizacne pripady.

    Create a copy of the input file with a new column containing the list of assigned medicinske sluzby.

    Args:
        input_path: Path to the file containing hospitalizacne pripady.
        output_path: Path to the output file. If not provided, a new file will be created.
        all_vykony_hlavne: When evaluating prilohy, assume that any of vykony could be hlavny.
        evaluate_incomplete_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the assigned medicinske sluzby will be 'ERROR'.
        allow_duplicates: Keep duplicate records in the output list of medicinske sluzby.

    """
    if output_path is None:
        output_path = Path(input_path).with_stem(f"{input_path.stem}_output")

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = prepare_data_writer(output_file)
        writer.writeheader()

        for row in load_input_rows(input_path):
            row["ms"] = process_input_row(
                row,
                all_vykony_hlavne=all_vykony_hlavne,
                evaluate_incomplete_pripady=evaluate_incomplete_pripady,
                allow_duplicates=allow_duplicates,
            )
            writer.writerow(row)
