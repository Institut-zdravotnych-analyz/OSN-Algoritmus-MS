#!/usr/bin/env python
"""Program na priraďovanie hospitalizačných prípadov do medicínskych služieb."""

import argparse

from OSN_Algoritmus.core import grouper_ms, setup_parser


def _vypis_aktivne_prepinace(args: argparse.Namespace):
    if args.vsetky_vykony_hlavne:
        print(
            "Aktivovaný prepínač 'Všetky výkony hlavné'. Pri vyhodnotení príloh sa bude predpokladať, že ktorýkoľvek z"
            " výkazaných výkonov mohol byť hlavný.",
        )
    if args.vyhodnot_neuplne_pripady:
        print(
            "Aktivovaný prepínač 'Vyhodnoť neúplné prípady'. V prípade, že nie je vyplnená nejaká povinná hodnota, aj"
            " tak sa bude pokračovať vo vyhodnocovaní.",
        )
    if args.ponechaj_duplicity:
        print(
            "Aktivovaný prepínač 'Ponechaj duplicity'. Vo výstupnom zozname medicínskych služieb budú ponechané aj"
            " duplicitné záznamy.",
        )


if __name__ == "__main__":
    parser = setup_parser(
        input_path=True,
        output_path=True,
        vsetky_vykony_hlavne=True,
        vyhodnot_neuplne_pripady=True,
        ponechaj_duplicity=True,
    )
    args = parser.parse_args()

    _vypis_aktivne_prepinace(args)

    grouper_ms(
        args.input_path,
        args.output_path,
        vsetky_vykony_hlavne=args.vsetky_vykony_hlavne,
        vyhodnot_neuplne_pripady=args.vyhodnot_neuplne_pripady,
        ponechaj_duplicity=args.ponechaj_duplicity,
    )
