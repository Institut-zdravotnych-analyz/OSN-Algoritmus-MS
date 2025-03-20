from copy import deepcopy
from OSN_Algoritmus.priprava_dat import (
    priprav_hp,
    validuj_hp,
    priprav_citac_dat,
    priprav_zapisovac_dat,
)
from OSN_Algoritmus.vyhodnotenie_priloh import prirad_ms


def nacitaj_hospitalizacne_pripady(file_path):
    """
    Generátor, ktorý načíta hospitalizačné prípady zo vstupného súboru.

    Args:
        file_path (str): Cesta k vstupnému súboru.

    Yields:
        dict: Každý hospitalizačný prípad ako slovník.
    """
    with open(file_path, "r", encoding="utf-8") as input_file:
        reader = priprav_citac_dat(input_file)
        for hospitalizacny_pripad in reader:
            yield hospitalizacny_pripad


def spracuj_hospitalizacny_pripad(
    hospitalizacny_pripad,
    vsetky_vykony_hlavne,
    vyhodnot_neuplne_pripady,
    ponechaj_duplicity,
):
    """
    Spracuje hospitalizačný prípad a priradí medicínske služby.

    Args:
        hospitalizacny_pripad (dict): Hospitalizačný prípad na spracovanie.
        vsetky_vykony_hlavne (bool): Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z výkazaných výkonov mohol byť hlavný.
        vyhodnot_neuplne_pripady (bool): V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.
        ponechaj_duplicity (bool): Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.

    Returns:
        None
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

    hospitalizacny_pripad["ms"] = "~".join(medicinske_sluzby)


def grouper_ms(
    file_path,
    vsetky_vykony_hlavne=False,
    vyhodnot_neuplne_pripady=False,
    ponechaj_duplicity=False,
):
    """
    Funkcia na priraďovanie hospitalizačných prípadov do medicínskych služieb.

    Vytvorí kópiu vstupného súboru s pripojeným novým stĺpcom so zoznamom priradených medicínskych služieb.

    Args:
        file_path (str): Relatívna cesta k súboru s dátami.
        vsetky_vykony_hlavne (bool, optional): Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z výkazaných výkonov mohol byť hlavný.
        vyhodnot_neuplne_pripady (bool, optional): V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.
        ponechaj_duplicity (bool, optional): Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.

    Returns:
        str: Relatívna cesta k súboru s výstupnými dátami.
    """
    _vypis_aktivne_prepinace(
        vsetky_vykony_hlavne, vyhodnot_neuplne_pripady, ponechaj_duplicity
    )

    output_path = f"{file_path[:-4]}_output.csv"

    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        writer = priprav_zapisovac_dat(output_file)
        writer.writeheader()

        for hospitalizacny_pripad in nacitaj_hospitalizacne_pripady(file_path):
            spracuj_hospitalizacny_pripad(
                hospitalizacny_pripad,
                vsetky_vykony_hlavne,
                vyhodnot_neuplne_pripady,
                ponechaj_duplicity,
            )
            writer.writerow(hospitalizacny_pripad)
    return output_path


def _vypis_aktivne_prepinace(
    vsetky_vykony_hlavne, vyhodnot_neuplne_pripady, ponechaj_duplicity
):
    """Pomocná funkcia na výpis informácií o aktívnych prepínačoch."""
    if vsetky_vykony_hlavne:
        print(
            "Aktivovaný prepínač 'Všetky výkony hlavné'. Pri vyhodnotení príloh sa bude predpokladať, že ktorýkoľvek z výkazaných výkonov mohol byť hlavný."
        )
    if vyhodnot_neuplne_pripady:
        print(
            "Aktivovaný prepínač 'Vyhodnoť neúplné prípady'. V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak sa bude pokračovať vo vyhodnocovaní."
        )
    if ponechaj_duplicity:
        print(
            "Aktivovaný prepínač 'Ponechaj duplicity'. Vo výstupnom zozname medicínskych služieb budú ponechané aj duplicitné záznamy."
        )
