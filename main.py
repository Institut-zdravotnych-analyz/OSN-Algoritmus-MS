r"""
Program na priraďovanie hospitalizačných prípadov do medicínskych služieb.

Vytvorí kópiu vstupného súboru s pripojeným novým stĺpcom so zoznamom priradených medicínskych služieb.

Args:
    file_path: Relatívna cesta k súboru s dátami.
    --vsetky_vykony_hlavne, -v: Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z výkazaných výkonov mohol byť hlavný.
    --vyhodnot_neuplne_pripady, -n: V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.
    --ponechaj_duplicity, -d: Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.

Returns:
    None

Examples:
    # Spustenie na Linuxe
    python3 ./main.py ./test_data.csv
    # Spustenie so zapnutým prepínačom na vyhodnotenie aj neúplných prípadov
    python3 ./main.py ./test_data.csv --vyhodnot_neuplne_pripady
    # Spustenie so všetkými prepínačmi zapnutými
    python3 ./main.py ./test_data.csv -vnd
    # Spustenie na Windows
    python .\main.py .\test_data_phsk_2.csv -vnd
"""

import argparse
from OSN_Algoritmus.core import grouper_ms

# TODO: add argument output path
if __name__ == "__main__":
    # Nastav argumenty pri spúšťaní
    parser = argparse.ArgumentParser(
        description="Funkcia na priraďovanie hospitalizačných prípadov do medicínskych služieb."
    )
    parser.add_argument(
        "data_path", action="store", help="Relatívna cesta k súboru s dátami."
    )
    parser.add_argument(
        "--vsetky_vykony_hlavne",
        "-v",
        action="store_true",
        help="Pri vyhodnotení príloh predpokladaj, že ktorýkoľvek z vykázaných výkonov mohol byť hlavný. Štandardne sa za hlavný výkon považuje iba prvý vykázaný, prípadne žiaden, pokiaľ zoznam začína znakom '~'.",
    )
    parser.add_argument(
        "--vyhodnot_neuplne_pripady",
        "-n",
        action="store_true",
        help="V prípade, že nie je vyplnená nejaká povinná hodnota, aj tak pokračuj vo vyhodnocovaní. Štandardne vráti hodnotu 'ERROR'.",
    )
    parser.add_argument(
        "--ponechaj_duplicity",
        "-d",
        action="store_true",
        help="Vo výstupnom zozname medicínskych služieb ponechaj aj duplicitné záznamy.",
    )

    args = parser.parse_args()

    result = grouper_ms(
        args.data_path,
        None,
        args.vsetky_vykony_hlavne,
        args.vyhodnot_neuplne_pripady,
        args.ponechaj_duplicity,
    )
