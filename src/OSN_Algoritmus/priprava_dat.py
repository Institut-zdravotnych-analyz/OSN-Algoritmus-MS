import csv
import uuid

from OSN_Algoritmus._pomocne_funkcie import vyrob_markery, zjednot_kod

NAZVY_STLPCOV = ["id", "vek", "hmotnost", "umela_plucna_ventilacia", "diagnozy", "vykony", "markery", "drg"]


def validuj_hp(hp, vyhodnot_neuplne_pripady):
    """Funkcia na validáciu hospitalizačného prípadu.

    Skontroluje, či hospitalizačný prípad obsahuje neprázdne ID, platný vek, platnú hmotnosť, platný počet hodín umelej pľúcnej ventilácie a neprázdny zoznam diagnóz.

    Args:
        hp (dict): Hospitalizačný prípad, ktorý sa má validovať.
        vyhodnot_neuplne_pripady (bool): Príznak určujúci, či sa neúplné prípady budú ďalej vyhodnocovať.

    Returns:
        bool: True, ak je hospitalizačný prípad platný, False inak.

    """
    # Identifikátor hospitalizačného prípadu nesmie byť prázdny
    if hp["id"] == "":
        if not vyhodnot_neuplne_pripady:
            return False
        hp["id"] = uuid.uuid4().hex
        print(f'WARNING: Prázdne pole "id", priraďujem nové ID: {hp["id"]}')

    # Vek musí byť celé, nezáporné číslo menšie ako 150
    try:
        hp["vek"] = int(hp["vek"])
        if not 0 <= hp["vek"] < 150:
            raise ValueError("Vek musí byť nezáporné číslo menšie ako 150")
    except ValueError:
        if not vyhodnot_neuplne_pripady:
            return False
        print(f"WARNING: HP {hp['id']} nemá správne vyplnený vek.")
        hp["vek"] = None

    # Hmotnosť pacienta ku dňu prijatia v gramoch musí byť prázdna alebo 0 alebo celé číslo medzi 100 a 20000
    # Hmotnosť pacienta s vekom 0 nesmie byť prázdna ani 0
    try:
        if hp["hmotnost"] == "":
            hp["hmotnost"] = 0.0
        else:
            hp["hmotnost"] = float(hp["hmotnost"])

        if not (100 <= hp["hmotnost"] <= 20000 or hp["hmotnost"] == 0):
            print("Hmotnosť nie je v správnom formáte")
            raise ValueError(
                "Hmotnosť musí byť prázdna alebo 0 alebo číslo medzi 100 a 20000.",
            )
        if hp["vek"] is not None and hp["vek"] == 0 and hp["hmotnost"] == 0:
            print("Hmotnosť pacienta s vekom 0 je nulová")
            raise ValueError(
                "Hmotnosť pacienta s vekom 0 nesmie byť nulová ani prázdna.",
            )
    except ValueError:
        if not vyhodnot_neuplne_pripady:
            return False
        print(f"WARNING: HP {hp['id']} nemá správne vyplnenú hmotnosť.")
        hp["hmotnost"] = None

    # Počet hodín umelej pľúcnej ventilácie musí byť celé, nezáporné číslo menšie ako 10000
    try:
        hp["umela_plucna_ventilacia"] = int(hp["umela_plucna_ventilacia"])
        if not 0 <= hp["umela_plucna_ventilacia"] <= 10000:
            raise ValueError(
                "Počet hodín umelej pľúcnej ventilácie musí byť nezáporné číslo menšie ako 10000.",
            )
    except ValueError:
        if not vyhodnot_neuplne_pripady:
            return False
        print(
            f"WARNING: HP {hp['id']} nemá správne vyplnený počet hodín umelej pľúcnej ventilácie.",
        )
        hp["umela_plucna_ventilacia"] = None

    # Zoznam diagnóz nesmie byť prázdny
    if hp["diagnozy"] == "":
        if not vyhodnot_neuplne_pripady:
            return False
        print(f"WARNING: HP {hp['id']} nemá vyplnenú ani jednu diagnózu.")
        hp["diagnozy"] = None

    return True


def priprav_hp(hp):
    """Príprava zoznamov diagnóz, výkonov a odborností v hospitalizačnom prípade. Zjednotenie kódu drg.

    Args:
        hp (dict): hospitalizačný prípad

    """
    hp["diagnozy"] = [zjednot_kod(diagnoza) for diagnoza in hp["diagnozy"].split("~")] if hp["diagnozy"] else []
    hp["vykony"] = [zjednot_kod(vykon.split("&")[0]) for vykon in hp["vykony"].split("~")] if hp["vykony"] else []
    hp["markery"] = vyrob_markery(hp["markery"])
    hp["drg"] = zjednot_kod(hp["drg"])


def priprav_citac_dat(file):
    """Pripraví čítač dát, ktorý načíta vstupný csv súbor a generuje slovníky s dátami.

    Args:
        file (file_handle): prístup k vstupnému súboru

    Returns:
        csv_reader: čítač dát

    """
    try:
        csv_reader = csv.DictReader(
            file,
            fieldnames=NAZVY_STLPCOV,
            delimiter=";",
            strict=True,
        )
    except csv.Error:
        print("ERROR: Zlý formát csv.")
        return None
    return csv_reader


def priprav_zapisovac_dat(file):
    """Pripraví zapisovač dát, ktorý pre slovník s dátami zapíše riadok do csv súboru.

    Args:
        file (file_handle): prístup k výstupnému súboru

    Returns:
        csv_writer: zapisovač dát

    """
    return csv.DictWriter(file, fieldnames=NAZVY_STLPCOV + ["ms"], delimiter=";")
