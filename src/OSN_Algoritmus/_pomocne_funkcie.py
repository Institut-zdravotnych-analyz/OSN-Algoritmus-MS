import re
from dataclasses import dataclass


@dataclass
class Marker:
    kod: str
    hodnota: str


def zjednot_kod(kod: str):
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()


def vyrob_markery_zo_str(markery: str):
    if markery:
        return [Marker(kod=marker.split("&")[0], hodnota=marker.split("&")[1]) for marker in markery.split("~")]
    return []


def je_podmnozina(podmnozina, nadmnozina):
    """Vráti true ak vsetky kluce a hodnoty v podmnozine su v nadmnozine."""
    return all(k in nadmnozina and nadmnozina[k] == v for k, v in podmnozina.items())


# Kriteria ktore pouzivaju marker ale nemaju ich v strukturovanej forme
KRITERIA_S_MARKERMI = {
    "p5_NOV": [
        {
            "doplnujuce_kriterium": "Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie pracovisko"
        },
        {"doplnujuce_kriterium": "Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)"},
    ],
    "p6_DRGD_deti": [{"doplnujuce_kriterium": "marker Pacient nespĺňa medicínske kritériá polytraumy"}],
    "p6_DRGD_dospeli": [{"doplnujuce_kriterium": "marker Pacient nespĺňa medicínske kritériá polytraumy"}],
}


def pouziva_marker(nazov_tabulky, riadok):
    # TODO: fix priloha 16
    if nazov_tabulky.startswith("p16_"):
        return False
    if riadok["marker"] is not None:
        return True
    if nazov_tabulky in KRITERIA_S_MARKERMI:
        for podmienka in KRITERIA_S_MARKERMI[nazov_tabulky]:
            if je_podmnozina(podmienka, riadok):
                return True
    return False
