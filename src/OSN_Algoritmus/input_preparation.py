"""Functions related to input data."""

import csv
import logging
import uuid
from collections.abc import Generator
from pathlib import Path

from osn_algoritmus.models import HospitalizacnyPripad, Marker
from osn_algoritmus.utils import (
    create_diagnozy_from_str,
    create_markery_from_str,
    create_vykony_from_str,
    log_error_or_warning,
    standardize_code,
)

logger = logging.getLogger(__name__)


def validate_id(hp_id: str, *, err_if_incorrect: bool) -> str | None:
    """Validate the ID of hospitalizacny pripad.

    Args:
        hp_id: Hospital case ID.
        err_if_incorrect: Flag indicating whether a missing ID is a problem.

    Returns:
        ID of hospitalizacny pripad or None if the ID is empty and err_if_incorrect is True.
        If the ID is empty and err_if_incorrect is False, returns a new ID.

    """
    if hp_id == "":
        msg = "Riadok nemá vyplnené ID."

        if err_if_incorrect:
            log_error_or_warning(logger, msg, error=err_if_incorrect)
            return None

        generated_id = uuid.uuid4().hex
        msg_with_new_id = f"{msg} Nové ID: {generated_id!r}."
        log_error_or_warning(logger, msg_with_new_id, error=err_if_incorrect)
        return generated_id
    return hp_id


def validate_vek(vek_str: str, hp_id: str, *, err_if_incorrect: bool) -> int | None:
    """Validate vek of the hospitalizacny pripad.

    Args:
        vek_str: vek of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect vek is a problem.

    Returns:
        Vek of hospitalizacny pripad or None if vek is incorrect.

    """
    if not vek_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený vek: {vek_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        return None
    return int(vek_str)


def validate_hmotnost(
    hmotnost_str: str,
    vek: int | None,
    hp_id: str,
    *,
    err_if_incorrect: bool,
) -> float | None:
    """Validate hmotnost of the hospitalizacny pripad.

    Hmotnost must be non-zero if age is 0.

    Args:
        hmotnost_str: hmotnost of hospitalizacny pripad
        vek: vek of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect hmotnost is a problem.

    Returns:
        Hmotnost of hospitalizacny pripad or None if hmotnost is incorrect.

    """
    try:
        parsed_hmotnost = float(hmotnost_str)
    except ValueError:
        if vek is not None and vek == 0:
            msg = f"HP {hp_id} nemá správne vyplnenú hmotnosť: {hmotnost_str!r}."
            log_error_or_warning(logger, msg, error=err_if_incorrect)
        return None

    if vek == 0 and parsed_hmotnost == 0.0:
        msg = f"HP {hp_id} nemá správne vyplnenú hmotnosť: Ak je vek 0, hmotnosť nemôže byť 0."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        if err_if_incorrect:
            return None

    if parsed_hmotnost == 0.0:
        return None
    return parsed_hmotnost


def validate_upv(upv_str: str, hp_id: str, *, err_if_incorrect: bool) -> int | None:
    """Validate počet hodín umelej pľúcnej ventilácie.

    Args:
        upv_str: Počet hodín umelej pľúcnej ventilácie of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect počet hodín umelej pľúcnej ventilácie is a problem.

    Returns:
        Počet hodín umelej pľúcnej ventilácie or None if počet hodín umelej pľúcnej ventilácie is incorrect.

    """
    if not upv_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený počet hodín umelej pľúcnej ventilácie: {upv_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        return None
    return int(upv_str)


def validate_druh_prijatia(druh_prijatia_str: str, hp_id: str, *, err_if_incorrect: bool) -> int | None:
    """Validate druh prijatia of hospitalizacny pripad.

    Args:
        druh_prijatia_str: Druh prijatia of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect druh prijatia is a problem.

    Returns:
        Druh prijatia of hospitalizacny pripad or None if druh prijatia is incorrect.

    """
    if not druh_prijatia_str.isdigit():
        msg = f"HP {hp_id} nemá správne vyplnený druh prijatia: {druh_prijatia_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        return None

    druh_prijatia = int(druh_prijatia_str)

    if not (1 <= druh_prijatia <= 9):
        msg = f"HP {hp_id} má druh prijatia mimo rozsahu 1-9: {druh_prijatia_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        return None

    return druh_prijatia


def validate_vykony(vykony_str: str, hp_id: str, *, err_if_incorrect: bool) -> list[str] | None:
    """Validate vykony of the hospitalizacny pripad.

    Args:
        vykony_str: Vykony of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect vykony is a problem.

    Returns:
        Vykony of hospitalizacny pripad or None if vykony is incorrect.

    """
    try:
        vykony = create_vykony_from_str(vykony_str)
    except ValueError:
        msg = f"HP {hp_id} nemá správne vyplnené vykony: {vykony_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        if err_if_incorrect:
            return None
        return []
    return vykony


def validate_markery(markery_str: str, hp_id: str, *, err_if_incorrect: bool) -> list[Marker] | None:
    """Validate markery of the hospitalizacny pripad.

    Args:
        markery_str: Markery of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect markery is a problem.

    Returns:
        Markery of hospitalizacny pripad or None if markery is incorrect.

    """
    try:
        markery = create_markery_from_str(markery_str)
    except ValueError:
        msg = f"HP {hp_id} nemá správne vyplnené markery: {markery_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        if err_if_incorrect:
            return None
        markery = []
    return markery


def validate_diagnozy(diagnozy_str: str, hp_id: str, *, err_if_incorrect: bool) -> list[str] | None:
    """Validate diagnozy of the hospitalizacny pripad.

    Args:
        diagnozy_str: Diagnozy of hospitalizacny pripad
        hp_id: ID of hospitalizacny pripad
        err_if_incorrect: Flag indicating whether an incorrect diagnozy is a problem.

    Returns:
        Diagnozy of hospitalizacny pripad or None if diagnozy is incorrect.

    """
    try:
        diagnozy = create_diagnozy_from_str(diagnozy_str)
    except ValueError:
        msg = f"HP {hp_id} nemá správne vyplnené diagnozy: {diagnozy_str!r}."
        log_error_or_warning(logger, msg, error=err_if_incorrect)
        if err_if_incorrect:
            return None
        return []
    return diagnozy


def create_hp_from_dict(hp_dict: dict, *, eval_incomplete: bool) -> HospitalizacnyPripad | None:
    """Validate input dictionary and create HospitalizacnyPripad.

    Args:
        hp_dict: dictionary representing hospitalizacny pripad.
        eval_incomplete: Flag indicating whether to evaluate incomplete pripady.

    Returns:
        Created HospitalizacnyPripad or None if validation fails.

    """
    hp_id = validate_id(hp_dict["id"], err_if_incorrect=not eval_incomplete)
    if hp_id is None:
        return None

    vek = validate_vek(hp_dict["vek"], hp_id, err_if_incorrect=not eval_incomplete)
    hmotnost = validate_hmotnost(hp_dict["hmotnost"], vek, hp_id, err_if_incorrect=not eval_incomplete)
    upv = validate_upv(hp_dict["umela_plucna_ventilacia"], hp_id, err_if_incorrect=not eval_incomplete)
    druh_prijatia = validate_druh_prijatia(hp_dict["druh_prijatia"], hp_id, err_if_incorrect=not eval_incomplete)
    vykony_val = validate_vykony(hp_dict["vykony"], hp_id, err_if_incorrect=not eval_incomplete)
    markery_val = validate_markery(hp_dict["markery"], hp_id, err_if_incorrect=not eval_incomplete)
    diagnozy_val = validate_diagnozy(hp_dict["diagnozy"], hp_id, err_if_incorrect=not eval_incomplete)

    if not eval_incomplete:
        validation_failed = (
            vek is None
            or (vek == 0 and hmotnost is None)
            or upv is None
            or druh_prijatia is None
            or vykony_val is None
            or markery_val is None
            or diagnozy_val is None
        )
        if validation_failed:
            return None

    vykony = [] if vykony_val is None else vykony_val
    markery = [] if markery_val is None else markery_val
    diagnozy = [] if diagnozy_val is None else diagnozy_val
    drg = standardize_code(hp_dict["drg"]) if hp_dict["drg"] else None

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


def yield_csv_rows(csv_path: Path, fieldnames: list[str]) -> Generator[dict, None, None]:
    """Yield rows from the input csv file without header with predefined fieldnames.

    Args:
        csv_path: Path to the csv file containing hospitalizacne pripady.
        fieldnames: List of fieldnames to use for the rows.

    Yields:
        row from the input csv

    """
    with csv_path.open("r", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file, fieldnames=fieldnames, delimiter=";", strict=True)
        yield from reader
