"""End-to-end tests for the main.py script."""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from osn_algoritmus.utils import CSV_DELIMITER, INPUT_COLUMNS

PRIPADY = {
    "P5_UnapplicableDRG": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "X",
            "druh_prijatia": 3,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P5_NoDoplnujuceKriterium": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P61B",
            "druh_prijatia": 3,
            "ms": "S49-03",
            "urovne_ms": "4",
        },
    },
    "P5_NekonvUPV": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8p107",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            # S50-05 is applied because of priloha 12
            "ms": "S49-05@S50-05",
            "urovne_ms": "4@4",
        },
    },
    "P5_RiadenaHypotermia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8q902",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            # S50-10 is applied because of priloha 12
            "ms": "S49-06@S50-10",
            "urovne_ms": "4@4",
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
            "druh_prijatia": 3,
            "ms": "S48-05",
            "urovne_ms": "2",
        },
    },
    "P5_Paliativ_vedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@Z515",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S48-05",
            "urovne_ms": "2",
        },
    },
    "P5_VymennaTransf": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8r2637",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            # S50-06 is applied because of priloha 12
            "ms": "S49-11@S50-06",
            "urovne_ms": "3@4",
        },
    },
    "P5_AkutPorod": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "93083",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S48-06",
            "urovne_ms": "2",
        },
    },
    "P5_NemoznostTransportu": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mOSN&novor",
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S48-07",
            "urovne_ms": "2",
        },
    },
    "P5_8p1007UPVMenejNez96": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 95,
            "diagnozy": pd.NA,
            "vykony": "8p1007",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            # S50-13 is applied because of priloha 12
            "ms": "S48-08@S50-13",
            "urovne_ms": "2@3",
        },
    },
    "P5_8p1007UPV96": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 96,
            "diagnozy": pd.NA,
            "vykony": "8p1007",
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            # S50-13 is applied because of priloha 12
            "ms": "S50-13",
            "urovne_ms": "3",
        },
    },
    "P5_PodViabNizkaVaha": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 499,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S49-07",
            "urovne_ms": "4",
        },
    },
    "P5_PodViabNizkyGestVek1": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mGVK&1",
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S49-07",
            "urovne_ms": "4",
        },
    },
    "P5_PodViabNizkyGestVek45": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mGVK&45",
            "drg": "P",
            "druh_prijatia": 3,
            "ms": "S49-07",
            "urovne_ms": "4",
        },
    },
    "P5_PodViabNizkyGestVek47": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mGVK&47",
            "drg": "P61B",
            "druh_prijatia": 3,
            "ms": "S49-03",
            "urovne_ms": "4",
        },
    },
    "P5_SigOP": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "12a100",
            "markery": pd.NA,
            "drg": "P03A",
            "druh_prijatia": 3,
            # S03-30 is applied because of priloha 12
            "ms": "S49-01@S03-30",
            "urovne_ms": "4@4",
        },
    },
    "P5_UPVTazke": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 999,
            "umela_plucna_ventilacia": 96,
            "diagnozy": "XXX@A010@A011",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "druh_prijatia": 3,
            "ms": "S49-02",
            "urovne_ms": "4",
        },
    },
    "P5_BezUPVTazke": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 1000,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "druh_prijatia": 3,
            "ms": "S49-08",
            "urovne_ms": "3",
        },
    },
    "P5_NotApplicableDruhPrijatia2": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 1000,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "druh_prijatia": 2,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P5_NotApplicableDruhPrijatia7": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 0,
            "hmotnost": 1000,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "P03A",
            "druh_prijatia": 7,
            "ms": "S99-99",
            "urovne_ms": "1",
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
            "druh_prijatia": 3,
            # S52-52 is applied because of priloha 14
            "ms": "S52-52",
            "urovne_ms": "2",
        },
    },
    "P6_DietaKraniocerebralnaTraumaVedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S52-01",
            "urovne_ms": "3",
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
            "druh_prijatia": 3,
            # S52-52 is applied because of priloha 14
            "ms": "S52-01@S52-52",
            "urovne_ms": "3@2",
        },
    },
    "P6_DietaBezKraniocerebralnaTrauma": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S52-02",
            "urovne_ms": "3",
        },
    },
    "P6_DietaMarkerNesplnaKriteriaPolytraumy": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX",
            "vykony": pd.NA,
            "markery": "mOSN&nopol",
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S52-64@S52-02",
            "urovne_ms": "2@3",
        },
    },
    "P6_DospelyKraniocerebralnaTraumaVedlajsia": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S02-01",
            "urovne_ms": "4",
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
            "druh_prijatia": 3,
            # S02-56 is applied because of priloha 13
            "ms": "S02-01@S02-56",
            "urovne_ms": "4@2",
        },
    },
    "P6_DospelyBezKraniocerebralnaTrauma": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S02-02",
            "urovne_ms": "3",
        },
    },
    "P6_DospelyMarkerNesplnaKriteriaPolytraumy": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX",
            "vykony": pd.NA,
            "markery": "mOSN&nopol",
            "drg": "W",
            "druh_prijatia": 3,
            "ms": "S02-68@S02-02",
            "urovne_ms": "2@3",
        },
    },
    "P7": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8t130@XXX@34011",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S63-42",
            "urovne_ms": "3",
        },
    },
    "P7_NotApplicableMissingVedlajsi": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8t130@XXX",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P7_NotApplicableReversed": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "34011@8t130",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P8": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8m3050@XXX@13n094",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S40-02 is applied because of priloha 13
            "ms": "S44-21@S40-02",
            "urovne_ms": "3@5",
        },
    },
    "P8_NotApplicableMissingVedlajsi": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8m3050@XXX",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S40-02 is applied because of priloha 13
            "ms": "S40-02",
            "urovne_ms": "5",
        },
    },
    "P8_NotApplicableReversed": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "13n094@8m3050",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P7a": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "5t06f0",
            "markery": "mSTA&C0-CO",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S55-01@S55-02@S55-03@S55-04@S55-05",
            "urovne_ms": "3@3@3@3@3",
        },
    },
    "P7a_NotApplicableMissingMarker": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "5t06f0",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P7a_NotApplicableMissingVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mSTA&C0-CO",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P8a": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "5a90211",
            "markery": "mSTA&C0-C7",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S12-01@S12-05@S12-21",
            "urovne_ms": "4@3@3",
        },
    },
    "P8a_NotApplicableMissingMarker": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "5a90211",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P8a_NotApplicableMissingVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mSTA&C0-C7",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P9_Dieta": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "O239",
            "vykony": "93020",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S11-07 is applied because of priloha 14
            "ms": "S11-05@S11-07",
            "urovne_ms": "3@2",
        },
    },
    "P9_Dieta_NotApplicableMissingVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "O239",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S11-07 is applied because of priloha 14
            "ms": "S11-07",
            "urovne_ms": "2",
        },
    },
    "P9_Dieta_NotApplicableMissingDiagnoza": {
        "flags": [],
        "values": {
            "id": "P9_Dieta",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "93020",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P9_Dospely": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "L032",
            "vykony": "5t06f0",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S25-21 is applied because of priloha 15
            "ms": "S02-04@S25-21",
            "urovne_ms": "3@2",
        },
    },
    "P9_Dospely_NotApplicableMissingVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "L032",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S25-21 is applied because of priloha 15
            "ms": "S25-21",
            "urovne_ms": "2",
        },
    },
    "P9_Dospely_NotApplicableMissingDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "5t06f0",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P9a": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "H900",
            "vykony": pd.NA,
            "markery": "mODB&006",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S05-31 is applied because of priloha 15
            "ms": "S36-08@S05-31",
            "urovne_ms": "4@1",
        },
    },
    "P9a_NotApplicableMissingMarker": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "H900",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S05-31 is applied because of priloha 15
            "ms": "S05-31",
            "urovne_ms": "1",
        },
    },
    "P9a_NotApplicableMissingDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mODB&006",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P9a_NotApplicableDieta": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 17,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "H900",
            "vykony": pd.NA,
            "markery": "mODB&006",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S53-30 is applied because of priloha 14
            "ms": "S53-30",
            "urovne_ms": "3",
        },
    },
    "P10_Dieta": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A150@U821",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S65-01 is applied because of priloha 14
            "ms": "S65-31@S65-01",
            "urovne_ms": "5@5",
        },
    },
    "P10_Dieta_NotApplicableDifferentVeldjsiaDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A150@A000",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S65-01 is applied because of priloha 14
            "ms": "S65-01",
            "urovne_ms": "5",
        },
    },
    "P10_Dospely": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A150@U821",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S27-12 is applied because of priloha 15
            "ms": "S27-01@S27-12",
            "urovne_ms": "5@3",
        },
    },
    "P10_Dospely_NotApplicableDifferentVedlajsiaDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A150@A000",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S27-12 is applied because of priloha 15
            "ms": "S27-12",
            "urovne_ms": "3",
        },
    },
    "P12": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "163002",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S58-08",
            "urovne_ms": "5",
        },
    },
    "P12_NotApplicableVedlajsiVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "XXX@163002",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P13": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8r160",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S01-01",
            "urovne_ms": "4",
        },
    },
    "P13_NotApplicableVedlajsiVykon": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "XXX@8r160",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P14": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "A000",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S63-23",
            "urovne_ms": "2",
        },
    },
    "P14_NotApplicableVedlajsiaDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@A000",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P15": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "W340",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S01-10",
            "urovne_ms": "3",
        },
    },
    "P15_NotApplicableVedlajsiaDiagnoza": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 45,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@W340",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
    "P16_Dieta": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "R402@G935@I601",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S73-28 is applied because of priloha 14
            "ms": "S58-14@S73-28",
            "urovne_ms": "2@2",
        },
    },
    "P16_Dospely": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "R402@G935@I601",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S37-03 is applied because of priloha 15
            "ms": "S17-22@S37-03",
            "urovne_ms": "2@2",
        },
    },
    "P16_DospelyNotApplicableMissingR402": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "G935@I601",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S37-03 is applied because of priloha 15
            "ms": "S37-03",
            "urovne_ms": "2",
        },
    },
    "P16_DospelyNotApplicableMissingG935": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "R402@I601",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S37-03 is applied because of priloha 15
            "ms": "S37-03",
            "urovne_ms": "2",
        },
    },
    "P16_DospelyNotApplicableMissingI601": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "R402@G935",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # S37-03 is applied because of priloha 15
            "ms": "S37-03",
            "urovne_ms": "2",
        },
    },
    "P17": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": "mOSN&anams",
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S98-01",
            "urovne_ms": "1",
        },
    },
    "NEZARADENY_PRIPAD": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 40,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
}

P5_PRIPAD = PRIPADY["P5_NoDoplnujuceKriterium"]["values"]
INVALID_PRIPADY = {
    "Invalid_NoID": {"flags": [], "values": {**P5_PRIPAD, "id": pd.NA, "ms": "ERROR", "urovne_ms": "ERROR"}},
    "Invalid_NoVek": {"flags": [], "values": {**P5_PRIPAD, "vek": pd.NA, "ms": "ERROR", "urovne_ms": "ERROR"}},
    "Invalid_FloatVek": {"flags": [], "values": {**P5_PRIPAD, "vek": 10.5, "ms": "ERROR", "urovne_ms": "ERROR"}},
    "Invalid_NegativeVek": {"flags": [], "values": {**P5_PRIPAD, "vek": -1, "ms": "ERROR", "urovne_ms": "ERROR"}},
    "Invalid_StringVek": {"flags": [], "values": {**P5_PRIPAD, "vek": "abc", "ms": "ERROR", "urovne_ms": "ERROR"}},
    "Invalid_ZeroHmotnostNovorodenec": {
        "flags": [],
        "values": {**P5_PRIPAD, "hmotnost": 0, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_NoHmotnostNovorodenec": {
        "flags": [],
        "values": {**P5_PRIPAD, "hmotnost": pd.NA, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_StringHmotnost": {
        "flags": [],
        "values": {**P5_PRIPAD, "hmotnost": "abc", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_NegativeUPV": {
        "flags": [],
        "values": {**P5_PRIPAD, "umela_plucna_ventilacia": -1, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_StringUPV": {
        "flags": [],
        "values": {**P5_PRIPAD, "umela_plucna_ventilacia": "abc", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_NoDruhPrijatia": {
        "flags": [],
        "values": {**P5_PRIPAD, "druh_prijatia": pd.NA, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_StringDruhPrijatia": {
        "flags": [],
        "values": {**P5_PRIPAD, "druh_prijatia": "abc", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_DruhPrijatia10": {
        "flags": [],
        "values": {**P5_PRIPAD, "druh_prijatia": 10, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_DruhPrijatia0": {
        "flags": [],
        "values": {**P5_PRIPAD, "druh_prijatia": 0, "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_VykonyNoVedlajsiVykon": {
        "flags": [],
        "values": {**P5_PRIPAD, "vykony": "8r160@", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_MarkeryNoKod": {
        "flags": [],
        "values": {**P5_PRIPAD, "markery": "&nopol", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_MarkeryNoHodnota": {
        "flags": [],
        "values": {**P5_PRIPAD, "markery": "mOSN&", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_MarkeryWrongDelimiterTilde": {
        "flags": [],
        "values": {**P5_PRIPAD, "markery": "mOSN&nopol&mGVK&3", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_MarkeryWrongDelimiterAmpersand": {
        "flags": [],
        "values": {**P5_PRIPAD, "markery": "mOSN@nopol", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
    "Invalid_Diagnozy": {
        "flags": [],
        "values": {**P5_PRIPAD, "diagnozy": "AAA@", "ms": "ERROR", "urovne_ms": "ERROR"},
    },
}

P17_PRIPAD = PRIPADY["P17"]["values"]
EVALUATE_INCOMPLETE_PRIPADY_PRIPADY = {
    "VNP_NoID": {"flags": ["-n"], "values": {**P17_PRIPAD, "id": pd.NA}},
    "VNP_ZeroHmotnostNovorodenec": {"flags": ["-n"], "values": {**P5_PRIPAD, "hmotnost": 0}},
    "VNP_NoHmotnostNovorodenec": {"flags": ["-n"], "values": {**P5_PRIPAD, "hmotnost": pd.NA}},
    "VNP_StringHmotnost": {"flags": ["-n"], "values": {**P17_PRIPAD, "hmotnost": "abc"}},
    "VNP_NegativeUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": -1}},
    "VNP_LargeUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": 10001}},
    "VNP_StringUPV": {"flags": ["-n"], "values": {**P17_PRIPAD, "umela_plucna_ventilacia": "abc"}},
    "VNP_DruhPrijatia": {
        "flags": ["-n"],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": "XXX@S060",
            "vykony": pd.NA,
            "markery": pd.NA,
            "drg": "W",
            "druh_prijatia": pd.NA,
            "ms": "S52-01",
            "urovne_ms": "3",
        },
    },
}

ALL_VYKONY_HLAVNE_PRIPADY = {
    # Check that if we make the original hlavny vykon vedlajsi, the algorithm assigns the same ms and uroven
    "VVH_P7": {
        "flags": ["-v"],
        "values": {**PRIPADY["P7"]["values"], "vykony": "XXX@8t130@34011"},
    },
    # Check that we deduplicate the ms correctly, e.g. remove only urovne_ms for duplicated ms
    "VVH_DuplicatedVykony": {
        "flags": ["-v"],
        "values": {
            "id": "X",
            "vek": 10,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "8t130@8t130@5a50h61@34011",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            # 8t130 is duplicated, so S63-42 would be twice here without deduplication
            "ms": "S63-42@S03-65",
            # 3@3 is twice here, since each corresponds to deduplicated medicinske sluzby
            "urovne_ms": "3@3",
        },
    },
    "VVH_P8": {
        "flags": ["-v"],
        "values": {**PRIPADY["P8"]["values"], "vykony": "XXX@8m3050@13n094"},
    },
    "VVH_P9_Dieta": {
        "flags": ["-v"],
        "values": {**PRIPADY["P9_Dieta"]["values"], "vykony": "XXX@93020"},
    },
    "VVH_P9_Dospely": {
        "flags": ["-v"],
        "values": {**PRIPADY["P9_Dospely"]["values"], "vykony": "XXX@5t06f0"},
    },
    "VVH_P12": {"flags": ["-v"], "values": {**PRIPADY["P12"]["values"], "vykony": "XXX@163002"}},
    "VVH_P13": {"flags": ["-v"], "values": {**PRIPADY["P13"]["values"], "vykony": "XXX@8r160"}},
}

ALL_VYKONY_HLAVNE_ALLOW_DUPLICATES_PRIPADY = {
    "VVHPD_P7": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P7"]["values"],
            "vykony": f"{PRIPADY['P7']['values']['vykony']}@8t130",
            "ms": "@".join([PRIPADY["P7"]["values"]["ms"]] * 2),
            "urovne_ms": "@".join([PRIPADY["P7"]["values"]["urovne_ms"]] * 2),
        },
    },
    "VVHPD_P8": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P8"]["values"],
            "vykony": f"{PRIPADY['P8']['values']['vykony']}@8m3050",
            # We can't do ms * 2 as above because of the order of the codes
            # (ms * 2 would be S44-21@S40-02@S44-21@S40-02)
            "ms": "S44-21@S44-21@S40-02@S40-02",
            "urovne_ms": "3@3@5@5",
        },
    },
    "VVHPD_P9_Dieta": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P9_Dieta"]["values"],
            "vykony": f"{PRIPADY['P9_Dieta']['values']['vykony']}@93020",
            # We can't double the ms because S11-07 appears only once
            "ms": "S11-05@S11-05@S11-07",
            "urovne_ms": "3@3@2",
        },
    },
    "VVHPD_P9_Dospely": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P9_Dospely"]["values"],
            "vykony": f"{PRIPADY['P9_Dospely']['values']['vykony']}@5t06f0",
            # We can't double the ms because S25-21 appears only once
            "ms": "S02-04@S02-04@S25-21",
            "urovne_ms": "3@3@2",
        },
    },
    "VVHPD_P12": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P12"]["values"],
            "vykony": "@".join([PRIPADY["P12"]["values"]["vykony"]] * 2),
            "ms": "@".join([PRIPADY["P12"]["values"]["ms"]] * 2),
            "urovne_ms": "@".join([PRIPADY["P12"]["values"]["urovne_ms"]] * 2),
        },
    },
    "VVHPD_P13": {
        "flags": ["-vd"],
        "values": {
            **PRIPADY["P13"]["values"],
            "vykony": "@".join([PRIPADY["P13"]["values"]["vykony"]] * 2),
            "ms": "@".join([PRIPADY["P13"]["values"]["ms"]] * 2),
            "urovne_ms": "@".join([PRIPADY["P13"]["values"]["urovne_ms"]] * 2),
        },
    },
}

P2_UROVEN_MS_PRIPAD = {
    "id": "X",
    "vek": pd.NA,
    "hmotnost": 1500,
    "umela_plucna_ventilacia": 0,
    "diagnozy": pd.NA,
    "vykony": "5v295",
    "markery": pd.NA,
    "drg": pd.NA,
    "druh_prijatia": pd.NA,
    "ms": "S51-74",
    "urovne_ms": pd.NA,
}

PRIPADY_P2_UROVEN_MS = {
    "P2_Vek0": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 0,
            "urovne_ms": "4",
        },
    },
    "P2_Vek1": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 1,
            "urovne_ms": "3",
        },
    },
    "P2_Vek6": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 6,
            "urovne_ms": "3",
        },
    },
    "P2_Vek7": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 7,
            "urovne_ms": "2",
        },
    },
    "P2_Vek15": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 15,
            "urovne_ms": "2",
        },
    },
    "P2_Vek16": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 16,
            "urovne_ms": "1",
        },
    },
    "P2_Vek18": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 18,
            "urovne_ms": "1",
        },
    },
    "P2_Vek19": {
        "flags": [],
        "values": {
            **P2_UROVEN_MS_PRIPAD,
            "vek": 19,
            "ms": "S14-21",
            "urovne_ms": "1",
        },
    },
}

UNDEFINED_UROVEN_MS_PRIPADY = {
    # Based on priloha 12, the vykon 330113 is assigned to S68-23, which has undefined uroven for vek 7
    "UNDEFINED_UROVEN_MS_P12": {
        "flags": [],
        "values": {
            "id": "X",
            "vek": 7,
            "hmotnost": 0,
            "umela_plucna_ventilacia": 0,
            "diagnozy": pd.NA,
            "vykony": "330113",
            "markery": pd.NA,
            "drg": pd.NA,
            "druh_prijatia": pd.NA,
            "ms": "S99-99",
            "urovne_ms": "1",
        },
    },
}

ALL_TEST_CASES = {
    **PRIPADY,
    **PRIPADY_P2_UROVEN_MS,
    **INVALID_PRIPADY,
    **EVALUATE_INCOMPLETE_PRIPADY_PRIPADY,
    **ALL_VYKONY_HLAVNE_PRIPADY,
    **ALL_VYKONY_HLAVNE_ALLOW_DUPLICATES_PRIPADY,
    **UNDEFINED_UROVEN_MS_PRIPADY,
}


@pytest.mark.parametrize("test_case_data", ALL_TEST_CASES.values(), ids=ALL_TEST_CASES.keys())
def test_single_case(test_case_data: dict, tmp_path: Path) -> None:
    """Test the main script with a single input row."""
    pripad = pd.DataFrame([test_case_data["values"]])[INPUT_COLUMNS]
    expected_output = pd.DataFrame([test_case_data["values"]]).astype("string")

    input_csv_path = tmp_path / "input.csv"
    pripad.to_csv(input_csv_path, sep=CSV_DELIMITER, index=False)

    output_csv_path = tmp_path / "output.csv"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "osn_algoritmus",
            str(input_csv_path),
            str(output_csv_path),
            *test_case_data["flags"],
        ],
        check=True,
    )

    assert output_csv_path.exists()
    output = pd.read_csv(output_csv_path, sep=CSV_DELIMITER).astype("string")

    pd.testing.assert_frame_equal(output, expected_output)


def test_multiple_cases(tmp_path: Path) -> None:
    """Test the main script with multiple input rows."""
    test_data = list(ALL_TEST_CASES.values())[:10]
    hp_rows = [test_case_data["values"] for test_case_data in test_data]
    hp_df = pd.DataFrame(hp_rows)[INPUT_COLUMNS]
    expected_output = pd.DataFrame(hp_rows).astype("string")

    input_csv_path = tmp_path / "input.csv"
    hp_df.to_csv(input_csv_path, sep=CSV_DELIMITER, index=False)

    output_csv_path = tmp_path / "output.csv"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "osn_algoritmus",
            str(input_csv_path),
            str(output_csv_path),
        ],
        check=True,
    )

    assert output_csv_path.exists()
    output = pd.read_csv(output_csv_path, sep=CSV_DELIMITER).astype("string")

    pd.testing.assert_frame_equal(output, expected_output)


def test_incorrect_columns(tmp_path: Path) -> None:
    """Test the main script with incorrect input columns."""
    pripad_df = pd.DataFrame([P5_PRIPAD]).rename(columns={"id": "ID"})

    input_csv_path = tmp_path / "input_incorrect_cols.csv"
    pripad_df.to_csv(input_csv_path, sep=CSV_DELIMITER, index=False)

    output_csv_path = tmp_path / "output.csv"

    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "osn_algoritmus",
            str(input_csv_path),
            str(output_csv_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode == 1
    assert "Nespravné hlavičky vstupného súboru" in process.stderr
    assert not output_csv_path.exists()
