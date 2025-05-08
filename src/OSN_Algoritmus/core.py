"""Core functionality of the osn_algoritmus package."""

import csv
from pathlib import Path

from osn_algoritmus.input_preparation import create_hp_from_dict, yield_csv_rows
from osn_algoritmus.prilohy_evaluation import prirad_ms

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

def process_hp_dict(
    hp_dict: dict,
    *,
    all_vykony_hlavne: bool = False,
    evaluate_incomplete_pripady: bool = False,
    allow_duplicates: bool = False,
) -> str:
    """Process raw dictionary with hp data by validating it and assigning medicinske sluzby.

    Args:
        hp_dict: dictionary representing hospitalizacny pripad.
        all_vykony_hlavne: When evaluating prilohy, assume that any of vykony could be hlavny.
        evaluate_incomplete_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the function will return 'ERROR'.
        allow_duplicates: Keep duplicate records in the output list of medicinske sluzby.

    Returns:
        str: Kody medicinskych sluzieb concatenated by '~'.

    """
    hp = create_hp_from_dict(hp_dict, eval_incomplete=evaluate_incomplete_pripady)

    if hp is None:
        return "ERROR"

    medicinske_sluzby = prirad_ms(hp, all_vykony_hlavne=all_vykony_hlavne)

    if not allow_duplicates:
        # deduplicate medicinske sluzby, keep order
        medicinske_sluzby = list(dict.fromkeys(medicinske_sluzby))

    return "~".join(medicinske_sluzby)


def process_csv(
    input_path: Path,
    output_path: Path | None = None,
    *,
    all_vykony_hlavne: bool = False,
    evaluate_incomplete_pripady: bool = False,
    allow_duplicates: bool = False,
) -> None:
    """Assign medicinske sluzby to hospitalizacne pripady from a csv file.

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
        writer = csv.DictWriter(output_file, fieldnames=[*INPUT_COLUMNS, "ms"], delimiter=";")
        writer.writeheader()

        for row in yield_csv_rows(input_path, INPUT_COLUMNS):
            row["ms"] = process_hp_dict(
                row,
                all_vykony_hlavne=all_vykony_hlavne,
                evaluate_incomplete_pripady=evaluate_incomplete_pripady,
                allow_duplicates=allow_duplicates,
            )
            writer.writerow(row)
