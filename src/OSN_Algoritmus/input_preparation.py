"""Priprava hospitalizačných prípadov z vstupného súboru."""

import csv
import logging
import uuid
from typing import IO

from osn_algoritmus.utils import (
    HospitalizacnyPripad,
    create_diagnozy_from_str,
    create_markery_from_str,
    create_vykony_from_str,
    standardize_code,
)

logger = logging.getLogger(__name__)

COLUMN_NAMES = [
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


def _log_error_or_warning(message: str, *, error: bool) -> None:
    if error:
        logger.error(message)
    else:
        logger.warning(message)


def validate_id(hp_id: str, *, error_if_incorrect: bool) -> str | None:
    """Validate the ID of hospitalizacny pripad.

    Args:
        hp_id: Hospital case ID.
        error_if_incorrect: Flag indicating whether a missing ID is a problem.

    Returns:
        ID of hospitalizacny pripad or None if the ID is empty and error_if_incorrect is True.
        If the ID is empty and error_if_incorrect is False, returns a new ID.

    """
    if hp_id == "":
        msg = "Riadok nemá vyplnené ID."

        if error_if_incorrect:
            _log_error_or_warning(msg, error=error_if_incorrect)
            return None

        generated_id = uuid.uuid4().hex
        msg_with_new_id = f"{msg} Nové ID: {generated_id!r}."
        _log_error_or_warning(msg_with_new_id, error=error_if_incorrect)
        return generated_id
    return hp_id


def validate_vek(vek_str: str, hp_id: str, *, error_if_incorrect: bool) -> int | None:
    """Validate vek of the hospitalizacny pripad.

    Args:
        vek_str: vek of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        error_if_incorrect: Flag indicating whether an incorrect vek is a problem.

    Returns:
        Vek of hospitalizacny pripad or None if vek is incorrect.

    """
    if not vek_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený vek: {vek_str!r}."
        _log_error_or_warning(msg, error=error_if_incorrect)
        return None
    return int(vek_str)


def validate_hmotnost(
    hmotnost_str: str,
    vek: int | None,
    hp_id: str,
    *,
    error_if_incorrect: bool,
) -> float | None:
    """Validate hmotnost of the hospitalizacny pripad.

    Hmotnost must be non-zero if age is 0.

    Args:
        hmotnost_str: hmotnost of hospitalizacny pripad
        vek: vek of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        error_if_incorrect: Flag indicating whether an incorrect hmotnost is a problem.

    Returns:
        Hmotnost of hospitalizacny pripad or None if hmotnost is incorrect.

    """
    try:
        parsed_hmotnost = float(hmotnost_str)
    except ValueError:
        if vek is not None and vek == 0:
            msg = f"HP {hp_id} nemá správne vyplnenú hmotnosť: {hmotnost_str!r}."
            _log_error_or_warning(msg, error=error_if_incorrect)
        return None

    if vek == 0 and parsed_hmotnost == 0.0:
        msg = f"HP {hp_id} nemá správne vyplnenú hmotnosť: Ak je vek 0, hmotnosť nemôže byť 0."
        _log_error_or_warning(msg, error=error_if_incorrect)
        if error_if_incorrect:
            return None

    if parsed_hmotnost == 0.0:
        return None
    return parsed_hmotnost


def validate_upv(upv_str: str, hp_id: str, *, error_if_incorrect: bool) -> int | None:
    """Validate počet hodín umelej pľúcnej ventilácie.

    Args:
        upv_str: Počet hodín umelej pľúcnej ventilácie of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        error_if_incorrect: Flag indicating whether an incorrect počet hodín umelej pľúcnej ventilácie is a problem.

    Returns:
        Počet hodín umelej pľúcnej ventilácie or None if počet hodín umelej pľúcnej ventilácie is incorrect.

    """
    if not upv_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený počet hodín umelej pľúcnej ventilácie: {upv_str!r}."
        _log_error_or_warning(msg, error=error_if_incorrect)
        return None
    return int(upv_str)


def validate_druh_prijatia(druh_prijatia_str: str, hp_id: str, *, error_if_incorrect: bool) -> int | None:
    """Validate druh prijatia of hospitalizacny pripad.

    Args:
        druh_prijatia_str: Druh prijatia of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        error_if_incorrect: Flag indicating whether an incorrect druh prijatia is a problem.

    Returns:
        Druh prijatia of hospitalizacny pripad or None if druh prijatia is incorrect.

    """
    if not druh_prijatia_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený druh prijatia: {druh_prijatia_str!r}."
        _log_error_or_warning(msg, error=error_if_incorrect)
        return None

    druh_prijatia = int(druh_prijatia_str)

    if not (1 <= druh_prijatia <= 9):
        msg = f"HP {hp_id} má druh prijatia mimo rozsahu 1-9: {druh_prijatia_str!r}."
        _log_error_or_warning(msg, error=error_if_incorrect)
        return None

    return druh_prijatia


def create_hp_from_row(input_row: dict, *, evaluate_incomplete_pripady: bool) -> HospitalizacnyPripad | None:
    """Validate input row and create HospitalizacnyPripad.

    Args:
        input_row: Row of data representing hospitalizacny pripad.
        evaluate_incomplete_pripady: Flag indicating whether to evaluate incomplete pripady.

    Returns:
        Created HospitalizacnyPripad or None if validation fails.

    """
    hp_id = validate_id(input_row["id"], error_if_incorrect=not evaluate_incomplete_pripady)
    if hp_id is None:
        return None

    vek = validate_vek(input_row["vek"], hp_id, error_if_incorrect=not evaluate_incomplete_pripady)
    if not evaluate_incomplete_pripady and vek is None:
        return None

    hmotnost = validate_hmotnost(
        input_row["hmotnost"],
        vek,
        hp_id,
        error_if_incorrect=not evaluate_incomplete_pripady,
    )
    if vek == 0 and not evaluate_incomplete_pripady and hmotnost is None:
        return None

    upv = validate_upv(
        input_row["umela_plucna_ventilacia"],
        hp_id,
        error_if_incorrect=not evaluate_incomplete_pripady,
    )
    if not evaluate_incomplete_pripady and upv is None:
        return None

    druh_prijatia = validate_druh_prijatia(
        input_row["druh_prijatia"],
        hp_id,
        error_if_incorrect=not evaluate_incomplete_pripady,
    )
    if not evaluate_incomplete_pripady and druh_prijatia is None:
        return None

    diagnozy = create_diagnozy_from_str(input_row["diagnozy"])
    vykony = create_vykony_from_str(input_row["vykony"])
    markery = create_markery_from_str(input_row["markery"])
    drg = standardize_code(input_row["drg"]) if input_row["drg"] else None

    return HospitalizacnyPripad(
        id=hp_id,
        vek=vek,
        hmotnost=hmotnost,
        upv=upv,
        diagnozy=diagnozy,
        vykony=vykony,
        markery=markery,
        drg=drg,
        druh_prijatia=druh_prijatia,
    )


def prepare_data_reader(file: IO[str]) -> csv.DictReader:
    """Prepare data reader that reads input csv file and generates dictionaries with hospitalizacne pripady.

    Args:
        file: Input file object

    Returns:
        Data reader

    """
    return csv.DictReader(file, fieldnames=COLUMN_NAMES, delimiter=";", strict=True)


def prepare_data_writer(file: IO[str]) -> csv.DictWriter:
    """Prepare data writer that writes rows to a csv file.

    Args:
        file: Output file object

    Returns:
        Data writer

    """
    return csv.DictWriter(file, fieldnames=[*COLUMN_NAMES, "ms"], delimiter=";")
