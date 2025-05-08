"""Functions related to preparation of prilohy tables."""

import csv
from importlib import resources
from pathlib import Path
from typing import Any

from .utils import Marker, standardize_code, uses_marker

TABLES_FOLDER = Path(str(resources.files("osn_algoritmus") / "Prilohy"))


def load_all_tables() -> dict[str, list[dict[str, str]]]:
    """Load all tables from files and return them in a dictionary.

    Returns:
        Dictionary containing loaded tables, where the key is the filename without '.csv' and the value is a list of
        rows of the corresponding table.

    """
    tables = {}

    for path in TABLES_FOLDER.glob("*.csv"):
        with path.open(encoding="utf-8") as file:
            table_name = path.stem
            csv_reader = csv.DictReader(file, delimiter=";")
            tables[table_name] = list(csv_reader)

    return tables


def prepare_kody(tables: dict[str, list[dict[str, str]]]) -> None:
    """Convert columns with diagnozy and vykony to lowercase and remove non-alphanumeric characters.

    Args:
        tables: Dictionary containing loaded prilohy.

    """
    columns_with_codes = {
        "p5_NOV": ["drg"],
        "p5_signifikantne_OP": ["kod_vykonu"],
        "p5_tazke_problemy_u_novorodencov": ["kod_diagnozy"],
        "p6_DRGD_deti": ["drg"],
        "p6_DRGD_dospeli": ["drg"],
        "p7_VV_deti_hv": ["kod_hlavneho_vykonu"],
        "p7_VV_deti_vv": ["kod_vykonu"],
        "p7a_MV_deti": ["kod_vykonu"],
        "p8_VV_dospeli_hv": ["kod_hlavneho_vykonu"],
        "p8_VV_dospeli_vv": ["kod_vykonu"],
        "p8a_MV_dospeli": ["kod_vykonu"],
        "p9_VD_deti": ["kod_hlavneho_vykonu"],
        "p9_VD_dospeli": ["kod_hlavneho_vykonu"],
        "p9_VD_diagnozy": ["kod_hlavnej_diagnozy"],
        "p9a_MD_dospeli": ["kod_hlavnej_diagnozy"],
        "p10_DD_deti": ["kod_vedlajsej_diagnozy"],
        "p10_DD_diagnozy": ["kod_hlavnej_diagnozy"],
        "p10_DD_dospeli": ["kod_vedlajsej_diagnozy"],
        "p12_V_deti": ["kod_vykonu"],
        "p13_V_dospeli": ["kod_vykonu"],
        "p14_D_deti": ["kod_diagnozy"],
        "p15_D_dospeli": ["kod_diagnozy"],
        "p16_koma": ["kod_diagnozy"],
        "p16_opuch_mozgu": ["kod_diagnozy"],
        "p16_vybrane_ochorenia": ["kod_diagnozy"],
    }

    for table_name, columns in columns_with_codes.items():
        for column in columns:
            tables[table_name] = [{**x, column: standardize_code(x[column])} for x in tables[table_name]]


def prepare_markery(tables: dict[str, list[dict[str, Any]]]) -> None:
    """Create a list of markers for each row in tables with markers.

    Args:
        tables: Dictionary containing loaded prilohy.

    """
    for zoznam_riadkov in tables.values():
        for riadok in zoznam_riadkov:
            if riadok.get("kod_markera"):
                riadok["marker"] = Marker(kod=riadok["kod_markera"], hodnota=riadok["hodnota_markera"])
                del riadok["kod_markera"]
                del riadok["hodnota_markera"]
            else:
                riadok["marker"] = None


def sort_rows_by_markery(tables: dict[str, list[dict[str, Any]]]) -> None:
    """Sort rows so that rows with markers are first, preserving relative order."""
    for table_name, rows in tables.items():
        rows.sort(key=lambda row: not uses_marker(table_name, row))


def prepare_tables() -> dict[str, list[dict[str, Any]]]:
    """Load and prepare all tables.

    Returns:
        Dictionary containing loaded and prepared tables.

    """
    tables = load_all_tables()

    prepare_kody(tables)
    prepare_markery(tables)
    sort_rows_by_markery(tables)

    return tables
