import re


def zjednot_kod(kod):
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()
