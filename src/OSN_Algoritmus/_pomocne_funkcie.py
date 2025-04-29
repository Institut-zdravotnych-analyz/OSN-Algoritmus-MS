import re


def zjednot_kod(kod: str):
    return re.sub("[^0-9a-zA-Z]", "", kod).lower()

def vyrob_markery(markery: str):
    if markery:
        return [{"kod": marker.split("&")[0], "hodnota": marker.split("&")[1]} for marker in markery.split("~")]
    return []
