"""Funkcie na načítanie a predspracovanie súborov s dátami z príloh.

Načíta všetky prílohy zo súborov a vytvorí pomocné zoznamy pre rôzne kritériá.
"""

import csv
from importlib import resources
from pathlib import Path

from ._pomocne_funkcie import Marker, pouziva_marker, zjednot_kod

cesta_k_suborom = Path(str(resources.files("OSN_Algoritmus") / "Prilohy"))


def extrahuj_do_zoznamu(tabulky, nazov_tabulky, nazov_stlpca):
    """Extrahuje hodnoty z tabulky (zoznam slovníkov) do zoznamu hodnôt podľa zadaného názvu tabuľky a názvu stĺpca.

    Args:
    tabulky (dict): Slovník obsahujúci všetky tabuľky.
    nazov_tabulky (str): Názov tabuľky, z ktorej sa majú extrahovať hodnoty.
    nazov_stlpca (str): Názov stĺpca, z ktorého sa majú extrahovať hodnoty.

    Returns:
    list: Zoznam hodnôt extrahovaných zo zadaného stĺpca tabuľky.

    """
    return [t[nazov_stlpca] for t in tabulky[nazov_tabulky]]


def nacitaj_vsetky_prilohy():
    """Načíta všetky prílohy zo súborov a vráti ich vo forme slovníka.

    Returns:
        dict: Slovník obsahujúci načítané prílohy, kde kľúč je názov súboru bez '.csv' a hodnota je zoznam slovnkov (riadkov príslušnej tabuľky).

    """
    prilohy = {}

    for cesta_k_suboru in cesta_k_suborom.glob("*.csv"):
        with open(cesta_k_suboru, encoding="utf-8") as subor:
            nazov_tabulky = cesta_k_suboru.stem
            prilohy[nazov_tabulky] = []
            csv_reader = csv.DictReader(subor, delimiter=";")
            for line in csv_reader:
                prilohy[nazov_tabulky].append(line)

    return prilohy


def priprav_kody(tabulky):
    stlpce_s_kodami = {
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

    for nazov_tabulky, zoznam_stlpcov in stlpce_s_kodami.items():
        for stlpec in zoznam_stlpcov:
            tabulky[nazov_tabulky] = [{**x, stlpec: zjednot_kod(x[stlpec])} for x in tabulky[nazov_tabulky]]

def priprav_markery(tabulky):
    for zoznam_riadkov in tabulky.values():
        for riadok in zoznam_riadkov:
            if riadok.get("kod_markera"):
                riadok["marker"] = Marker(kod=riadok["kod_markera"], hodnota=riadok["hodnota_markera"])
            else:
                riadok["marker"] = None


def zorad_tabulky(tabulky):
    """Zoradí tabulky tak, aby ako prvé boli riadky s markermi, so zachovaním relatívneho poradia."""
    for nazov_tabulky, zoznam_riadkov in tabulky.items():
        zoznam_riadkov.sort(key=lambda riadok: not pouziva_marker(nazov_tabulky, riadok))


def priprav_vsetky_prilohy():
    """Načíta a pripraví všetky prílohy.

    Returns:
        None

    """
    tabulky = nacitaj_vsetky_prilohy()

    priprav_kody(tabulky)
    priprav_markery(tabulky)
    zorad_tabulky(tabulky)

    return tabulky
