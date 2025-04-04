import re


def zjednot_kod(kod: str):
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()
