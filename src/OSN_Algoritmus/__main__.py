"""Program na priraďovanie hospitalizačných prípadov do medicínskych služieb."""

import logging

from .core import grouper_ms, setup_parser


def main() -> None:
    """Run the program."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s: %(message)s")
    logger = logging.getLogger(__name__)
    parser = setup_parser(
        input_path=True,
        output_path=True,
        vsetky_vykony_hlavne=True,
        vyhodnot_neuplne_pripady=True,
        ponechaj_duplicity=True,
    )
    args = parser.parse_args()

    if args.vsetky_vykony_hlavne:
        logger.info(
            "Aktivovaný prepínač 'Všetky výkony hlavné'. Pri vyhodnotení príloh sa bude predpokladať, že ktorýkoľvek z"
            " výkazaných výkonov mohol byť hlavný.",
        )
    if args.vyhodnot_neuplne_pripady:
        logger.info(
            "Aktivovaný prepínač 'Vyhodnoť neúplné prípady'. V prípade, že nie je vyplnená nejaká povinná hodnota, aj"
            " tak sa bude pokračovať vo vyhodnocovaní.",
        )
    if args.ponechaj_duplicity:
        logger.info(
            "Aktivovaný prepínač 'Ponechaj duplicity'. Vo výstupnom zozname medicínskych služieb budú ponechané aj"
            " duplicitné záznamy.",
        )

    grouper_ms(
        args.input_path,
        args.output_path,
        all_vykony_hlavne=args.vsetky_vykony_hlavne,
        evaluate_incomplete_pripady=args.vyhodnot_neuplne_pripady,
        allow_duplicates=args.ponechaj_duplicity,
    )


if __name__ == "__main__":
    main()
