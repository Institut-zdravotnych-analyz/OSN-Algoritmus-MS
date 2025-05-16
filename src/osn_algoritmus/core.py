"""Core functionality of the osn_algoritmus package."""

import csv
import logging
from pathlib import Path

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from osn_algoritmus.input_preparation import check_csv_columns, create_hp_from_dict, yield_csv_rows
from osn_algoritmus.prilohy_evaluation import prirad_ms, prirad_urovne_ms
from osn_algoritmus.utils import (
    CSV_DELIMITER,
    INPUT_COLUMNS,
    deduplicate_ms,
    get_number_of_lines,
    remove_ms_with_undefined_uroven,
)

logger = logging.getLogger(__name__)


def process_hp_dict(
    hp_dict: dict,
    *,
    all_vykony_hlavne: bool = False,
    evaluate_incomplete_pripady: bool = False,
    allow_duplicates: bool = False,
) -> tuple[str, str] | None:
    """Process raw dictionary with hp data by validating it and assigning medicinske sluzby.

    Args:
        hp_dict: dictionary representing hospitalizacny pripad.
        all_vykony_hlavne: When evaluating prilohy, assume that any of vykony could be hlavny.
        evaluate_incomplete_pripady: If a required value is not filled in, continue with the evaluation anyway.
            Without this flag, the function will return 'ERROR'.
        allow_duplicates: Keep duplicate records in the output list of medicinske sluzby.

    Returns:
        Kody medicinskych sluzieb concatenated by '@' and urovne medicinskych sluzieb concatenated by '@' or None if
        the hp_dict is invalid.

    """
    hp = create_hp_from_dict(hp_dict, eval_incomplete=evaluate_incomplete_pripady)

    if hp is None:
        return None

    medicinske_sluzby = prirad_ms(hp, all_vykony_hlavne=all_vykony_hlavne)
    urovne_ms = prirad_urovne_ms(hp, medicinske_sluzby)

    if not allow_duplicates:
        medicinske_sluzby, urovne_ms = deduplicate_ms(medicinske_sluzby, urovne_ms)

    valid_ms, valid_urovne_ms = remove_ms_with_undefined_uroven(medicinske_sluzby, urovne_ms)

    ms_str = "@".join(valid_ms)
    urovne_ms_str = "@".join(str(uroven) for uroven in valid_urovne_ms)

    return ms_str, urovne_ms_str


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
        allow_duplicates: Keep duplicates in the output list of medicinske sluzby.

    """
    logger.info("Spustenie algoritmu.")

    found_incorrect_columns = check_csv_columns(input_path, INPUT_COLUMNS)
    if found_incorrect_columns:
        msg = f"Nespravné hlavičky vstupného súboru. Očakávané: {INPUT_COLUMNS}. Nájdené: {found_incorrect_columns}."
        raise ValueError(msg)

    number_of_rows = get_number_of_lines(input_path) - 1
    logger.info(f"Počet riadkov vstupného súboru: {number_of_rows}")

    if output_path is None:
        output_path = Path(input_path).with_stem(f"{input_path.stem}_output")

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=[*INPUT_COLUMNS, "ms", "urovne_ms"], delimiter=CSV_DELIMITER)
        writer.writeheader()

        with logging_redirect_tqdm():
            for row in tqdm(yield_csv_rows(input_path), total=number_of_rows, desc="Spracovanie prípadov"):
                ms_result = process_hp_dict(
                    row,
                    all_vykony_hlavne=all_vykony_hlavne,
                    evaluate_incomplete_pripady=evaluate_incomplete_pripady,
                    allow_duplicates=allow_duplicates,
                )

                row["ms"], row["urovne_ms"] = ("ERROR", "ERROR") if ms_result is None else ms_result

                writer.writerow(row)

    logger.info(f"Algoritmus dokončený. Výsledky sú v {output_path}")
