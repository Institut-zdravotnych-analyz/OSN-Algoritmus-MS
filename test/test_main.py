"""End-to-end tests for the main.py script."""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
MAIN_SCRIPT = PROJECT_ROOT / "main.py"


INPUT_COLS = ["id", "vek", "hmotnost", "umela_plucna_ventilacia", "diagnozy", "vykony", "markery", "drg"]
PRIPADY = {
    "P5_UnapplicableDRG": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "X",
            "ms": "S99-99",
        },
    },
    "P5_NoDoplnujuceKriterium": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P61B",
            "ms": "S49-03",
        },
    },
    "P5_NekonvUPV": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8p107&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            # S50-05 is applied because of priloha 12
            "ms": "S49-05~S50-05",
        },
    },
    "P5_RiadenaHypotermia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8q902&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            # S50-10 is applied because of priloha 12
            "ms": "S49-06~S50-10",
        },
    },
    "P5_Paliativ_hlavna": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "Z515",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P",
            "ms": "S48-05",
        },
    },
    "P5_Paliativ_vedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX~Z515",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P",
            "ms": "S48-05",
        },
    },
    "P5_VymennaTransf": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8r2637&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            # S50-06 is applied because of priloha 12
            "ms": "S49-11~S50-06",
        },
    },
    "P5_AkutPorod": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "93083&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            "ms": "S48-06",
        },
    },
    "P5_NemoznostTransportu": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mOSN&novor",
            "drg": "P",
            "ms": "S48-07",
        },
    },
    "P5_8p1007UPVMenejNez96": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 95,
            "diagnozy": "X",
            "vykony": "8p1007&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            # S50-13 is applied because of priloha 12
            "ms": "S48-08~S50-13",
        },
    },
    "P5_8p1007UPV96": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 96,
            "diagnozy": "X",
            "vykony": "8p1007&Z&20230101",
            "markery": pd.NA,
            "drg": "P",
            # S50-13 is applied because of priloha 12
            "ms": "S50-13",
        },
    },
    "P5_PodViabNizkaVaha": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 499,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P",
            "ms": "S49-07",
        },
    },
    "P5_PodViabNizkyGestVek1": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mGVK&1",
            "drg": "P",
            "ms": "S49-07",
        },
    },
    "P5_PodViabNizkyGestVek23": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mGVK&23",
            "drg": "P",
            "ms": "S49-07",
        },
    },
    # mGVK > 23: Should not be applied
    "P5_PodViabNizkyGestVek24": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mGVK&24",
            "drg": "P61B",
            "ms": "S49-03",
        },
    },
    "P5_SigOP": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "12a100&Z&20230101",
            "markery": pd.NA,
            "drg": "P03A",
            # S03-30 is applied because of priloha 12
            "ms": "S49-01~S03-30",
        },
    },
    "P5_UPVTazke": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 96,
            "diagnozy": "XXX~A010~A011",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "ms": "S49-02",
        },
    },
    "P5_BezUPVTazke": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 1000,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "ms": "S49-08",
        },
    },
    "P6_UnapplicableDRG": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "X",
            # S52-52 is applied because of priloha 14
            "ms": "S52-52",
        },
    },
    "P6_DietaKraniocerebralnaTraumaVedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX~S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "ms": "S52-01",
        },
    },
    "P6_DietaKraniocerebralnaTraumaHlavna": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            # S52-52 is applied because of priloha 14
            "ms": "S52-01~S52-52",
        },
    },
    "P6_DietaBezKraniocerebralnaTrauma": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "ms": "S52-02",
        },
    },
    "P6_DietaMarkerNesplnaKriteriaPolytraumy": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mOSN&nopol",
            "drg": "W",
            "ms": "S52-64",
        },
    },
    "P6_DospelyKraniocerebralnaTraumaVedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX~S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "ms": "S02-01",
        },
    },
    "P6_DospelyKraniocerebralnaTraumaHlavna": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            # S02-56 is applied because of priloha 13
            "ms": "S02-01~S02-56",
        },
    },
    "P6_DospelyBezKraniocerebralnaTrauma": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "ms": "S02-02",
        },
    },
    "P6_DospelyMarkerNesplnaKriteriaPolytraumy": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": "mOSN&nopol",
            "drg": "W",
            "ms": "S02-68",
        },
    },
    # prilohy_7_8
    "P7": {
        "flags": [],
        "values": {
            "id": "P7",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8t130&Z&20230101~XXX&Z&20230101~34011&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S63-42",
        },
    },
    "P7_NotApplicableMissingVedlajsi": {
        "flags": [],
        "values": {
            "id": "P7",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8t130&Z&20230101~XXX&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S99-99",
        },
    },
    "P7_NotApplicableReversed": {
        "flags": [],
        "values": {
            "id": "P7",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "34011&Z&20230101~8t130&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S99-99",
        },
    },
    "P8": {
        "flags": [],
        "values": {
            "id": "P8",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "93041&Z&20230101~XXX&Z&20230101~5t600&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S12-04",
        },
    },
    # priloha_9
    # je_dieta = True
    "P9_Dieta": {
        "flags": [],
        "values": {
            "id": "P9_Dieta",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "O239",
            "vykony": "93020&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            # S11-07 is applied because of priloha 14
            "ms": "S11-05~S11-07",
        },
    },
    # je_dieta = False
    "P9_Dospely": {
        "flags": [],
        "values": {
            "id": "P9_Dospely",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "L032",
            "vykony": "5t06f0&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            # S25-21 is applied because of priloha 15
            "ms": "S02-04~S25-21",
        },
    },
    # skip priloha_10 for now as it will be changed in next version
    # prilohy_12_13
    # je_dieta = True
    "P12": {
        "flags": [],
        "values": {
            "id": "P12",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "12a100&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S03-30",
        },
    },
    # je_dieta = False
    "P13": {
        "flags": [],
        "values": {
            "id": "P13",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "8r160&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S01-01",
        },
    },
    # priloha_14_15
    # je_dieta = True
    "P14": {
        "flags": [],
        "values": {
            "id": "P14",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A000",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S63-23",
        },
    },
    # je_dieta = False
    "P15": {
        "flags": [],
        "values": {
            "id": "P15",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "W340",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S01-10",
        },
    },
    # priloha_16
    "P16": {
        "flags": [],
        "values": {
            "id": "P16",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "R402~G935~I601",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            # S37-03 is applied because of priloha 15
            "ms": "S37-03~S17-22",
        },
    },
    # priloha_17
    "P17": {
        "flags": [],
        "values": {
            "id": "P17",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": "93091&Z&20230101",
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S98-98",
        },
    },
    "NEZARADENY_PRIPAD": {
        "flags": [],
        "values": {
            "id": "NEZARADENY_PRIPAD",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "X",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "ms": "S99-99",
        },
    },
}

P5_PRIPAD = PRIPADY["P5_NoDoplnujuceKriterium"]["values"]
INVALID_PRIPADY = {
    "Invalid_NoID": {"flags": [], "values": {**P5_PRIPAD, "id": pd.NA, "ms": "ERROR"}},
    "Invalid_NoVek": {"flags": [], "values": {**P5_PRIPAD, "vek": pd.NA, "ms": "ERROR"}},
    "Invalid_FloatVek": {"flags": [], "values": {**P5_PRIPAD, "vek": 10.5, "ms": "ERROR"}},
    "Invalid_NegativeVek": {"flags": [], "values": {**P5_PRIPAD, "vek": -1, "ms": "ERROR"}},
    "Invalid_LargeVek": {"flags": [], "values": {**P5_PRIPAD, "vek": 150, "ms": "ERROR"}},
    "Invalid_StringVek": {"flags": [], "values": {**P5_PRIPAD, "vek": "abc", "ms": "ERROR"}},
    "Invalid_TooLowHmotnost": {"flags": [], "values": {**P5_PRIPAD, "hmotnost": 99, "ms": "ERROR"}},
    "Invalid_TooHighHmotnost": {"flags": [], "values": {**P5_PRIPAD, "hmotnost": 20001, "ms": "ERROR"}},
    "Invalid_ZeroHmotnostNovorodenec": {"flags": [], "values": {**P5_PRIPAD, "hmotnost": 0, "ms": "ERROR"}},
    "Invalid_NoHmotnostNovorodenec": {"flags": [], "values": {**P5_PRIPAD, "hmotnost": pd.NA, "ms": "ERROR"}},
    "Invalid_StringHmotnost": {"flags": [], "values": {**P5_PRIPAD, "hmotnost": "abc", "ms": "ERROR"}},
    "Invalid_NegativeUPV": {"flags": [], "values": {**P5_PRIPAD, "umela_plucna_ventilacia": -1, "ms": "ERROR"}},
    "Invalid_LargeUPV": {"flags": [], "values": {**P5_PRIPAD, "umela_plucna_ventilacia": 10001, "ms": "ERROR"}},
    "Invalid_StringUPV": {"flags": [], "values": {**P5_PRIPAD, "umela_plucna_ventilacia": "abc", "ms": "ERROR"}},
    "Invalid_EmptyDiagnozy": {"flags": [], "values": {**P5_PRIPAD, "diagnozy": pd.NA, "ms": "ERROR"}},
}

P17_PRIPAD = PRIPADY["P17"]["values"]
VYHODNOT_NEUPLNE_PRIPADY_PRIPADY = {
    "VNP_NoID": {"flags": ["-n"], "values": {**P17_PRIPAD, "id": pd.NA}},
    "VNP_NoVek": {"flags": ["-n"], "values": {**P17_PRIPAD, "vek": pd.NA}},
    "VNP_FloatVek": {"flags": ["-n"], "values": {**P17_PRIPAD, "vek": 10.5}},
    "VNP_NegativeVek": {"flags": ["-n"], "values": {**P17_PRIPAD, "vek": -1}},
    "VNP_LargeVek": {"flags": ["-n"], "values": {**P17_PRIPAD, "vek": 150}},
    "VNP_StringVek": {"flags": ["-n"], "values": {**P17_PRIPAD, "vek": "abc"}},
    "VNP_FloatHmotnost": {"flags": ["-n"], "values": {**P17_PRIPAD, "hmotnost": 999.9}},
    "VNP_TooLowHmotnost": {"flags": ["-n"], "values": {**P17_PRIPAD, "hmotnost": 99}},
    "VNP_TooHighHmotnost": {"flags": ["-n"], "values": {**P17_PRIPAD, "hmotnost": 20001}},
    "VNP_ZeroHmotnostNovorodenec": {"flags": ["-n"], "values": {**P5_PRIPAD, "hmotnost": 0}},
    "VNP_NoHmotnostNovorodenec": {"flags": ["-n"], "values": {**P5_PRIPAD, "hmotnost": pd.NA}},
    "VNP_StringHmotnost": {"flags": ["-n"], "values": {**P17_PRIPAD, "hmotnost": "abc"}},
    "VNP_NegativeUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": -1}},
    "VNP_LargeUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": 10001}},
    "VNP_StringUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": "abc"}},
    "VNP_EmptyDiagnozy": {"flags": ["-n"], "values": {**P17_PRIPAD, "diagnozy": pd.NA}},
}

VSETKY_VYKONY_HLAVNE_PRIPADY = {
    "VVH_P7": {
        "flags": ["-v"],
        "values": {**PRIPADY["P7"]["values"], "vykony": "XXX&Z&20230101~8t130&Z&20230101~34011&Z&20230101"},
    },
    "VVH_P8": {
        "flags": ["-v"],
        "values": {**PRIPADY["P8"]["values"], "vykony": "XXX&Z&20230101~5t600&Z&20230101~93041&Z&20230101"},
    },
    "VVH_P9_Dieta": {
        "flags": ["-v"],
        "values": {**PRIPADY["P9_Dieta"]["values"], "vykony": "XXX&Z&20230101~93020&Z&20230101"},
    },
    "VVH_P9_Dospely": {
        "flags": ["-v"],
        "values": {**PRIPADY["P9_Dospely"]["values"], "vykony": "XXX&Z&20230101~5t06f0&Z&20230101"},
    },
    "VVH_P12": {"flags": ["-v"], "values": {**PRIPADY["P12"]["values"], "vykony": "XXX&Z&20230101~12a100&Z&20230101"}},
    "VVH_P13": {"flags": ["-v"], "values": {**PRIPADY["P13"]["values"], "vykony": "XXX&Z&20230101~8r160&Z&20230101"}},
    "VVH_P17_Analyticka_MS": {"flags": ["-v"], "values": {**P17_PRIPAD, "vykony": "XXX&Z&20230101~93091&Z&20230101"}},
}

VSETKY_VYKONY_HLAVNE_PONECHAJ_DUPLICITY_PRIPADY = {
    "VVHPD_P7": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P7"]["values"],
            "vykony": f"{PRIPADY['P7']['values']['vykony']}~93084&Z&20230101",
            "ms": "~".join([PRIPADY["P7"]["values"]["ms"]] * 2),
        },
    },
    "VVHPD_P8": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P8"]["values"],
            "vykony": f"{PRIPADY['P8']['values']['vykony']}~93041&Z&20230101",
            "ms": "~".join([PRIPADY["P8"]["values"]["ms"]] * 2),
        },
    },
    "VVHPD_P9_Dieta": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P9_Dieta"]["values"],
            "vykony": f"{PRIPADY['P9_Dieta']['values']['vykony']}~93020&Z&20230101",
            # We can't double the ms because S11-07 appears only once
            "ms": "S11-05~S11-05~S11-07",
        },
    },
    "VVHPD_P9_Dospely": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P9_Dospely"]["values"],
            "vykony": f"{PRIPADY['P9_Dospely']['values']['vykony']}~5t06f0&Z&20230101",
            # We can't double the ms because S25-21 appears only once
            "ms": "S02-04~S02-04~S25-21",
        },
    },
    "VVHPD_P12": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P12"]["values"],
            "vykony": "~".join([PRIPADY["P12"]["values"]["vykony"]] * 2),
            "ms": "~".join([PRIPADY["P12"]["values"]["ms"]] * 2),
        },
    },
    "VVHPD_P13": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P13"]["values"],
            "vykony": "~".join([PRIPADY["P13"]["values"]["vykony"]] * 2),
            "ms": "~".join([PRIPADY["P13"]["values"]["ms"]] * 2),
        },
    },
}
ALL_TEST_CASES = {
    **PRIPADY,
    **INVALID_PRIPADY,
    **VYHODNOT_NEUPLNE_PRIPADY_PRIPADY,
    **VSETKY_VYKONY_HLAVNE_PRIPADY,
    **VSETKY_VYKONY_HLAVNE_PONECHAJ_DUPLICITY_PRIPADY,
}


@pytest.mark.parametrize("test_case_data", ALL_TEST_CASES.values(), ids=ALL_TEST_CASES.keys())
def test_single_case(test_case_data: dict, tmp_path: Path) -> None:
    """Test the main script with a single input row."""
    pripad = pd.DataFrame([test_case_data["values"]])[INPUT_COLS]
    expected_output = pd.DataFrame([test_case_data["values"]])

    input_csv_path = tmp_path / "input.csv"
    pripad.to_csv(input_csv_path, sep=";", index=False, header=False)

    output_csv_path = tmp_path / "output.csv"
    subprocess.run([sys.executable, MAIN_SCRIPT, input_csv_path, output_csv_path, *test_case_data["flags"]], check=True)

    assert output_csv_path.exists()
    output = pd.read_csv(output_csv_path, sep=";").replace({float("nan"): pd.NA})

    pd.testing.assert_frame_equal(output, expected_output)
