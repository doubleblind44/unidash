import numpy as np
import xmltodict
import requests
import pandas as pd


# Nun ersetzen wir die URLs im Dictionary mit den Inhalten der referenzierten xml-Dateien.
def reorder_dict(dict_url: dict):
    """
    Diese Funktion löst Wörterbücher innerhalb eines Moduls auf und erstellt neue key value pairs.

    :param dict_url: Python Dictionary, das das zu verändernde Modul darstellt.
    """
    # Löst das Wörterbuch des Keys "durchführung" auf
    if "praesenz" in dict_url["modul"]["durchfuehrung"]:
        dict_url["modul"]["praesenz"] = dict_url["modul"]["durchfuehrung"]["praesenz"]
    if "dauer" in dict_url["modul"]["durchfuehrung"]:
        dict_url["modul"]["dauer"] = dict_url["modul"]["durchfuehrung"]["dauer"]
    if "turnus" in dict_url["modul"]["durchfuehrung"]:
        dict_url["modul"]["turnus"] = dict_url["modul"]["durchfuehrung"]["turnus"]
    if "veranstaltung" in dict_url["modul"]["durchfuehrung"]:
        dict_url["modul"]["veranstaltung"] = dict_url["modul"]["durchfuehrung"]["veranstaltung"]
    del dict_url["modul"]["durchfuehrung"]

    # Löst das Wörterbuch des keys "modulname" auf
    if "deutsch" in dict_url["modul"]["modulname"]:
        dict_url["modul"]["modulname deutsch"] = dict_url["modul"]["modulname"]["deutsch"]
    if "englisch" in dict_url["modul"]["modulname"]:
        dict_url["modul"]["modulname englisch"] = dict_url["modul"]["modulname"]["englisch"]
    del dict_url["modul"]["modulname"]


def casting_ects(ects: str) -> float:
    """
    Diese Funktion wandelt die ECTS eines Moduls von String in float um.

    :param ects: Die ECTS, die umgewandelt werden.
    :return:     Die ECTS als float.
    """
    if ects is None:
        return np.nan

    if "," in ects:
        ects = ects.replace(',', '.')
    return float(ects)


def casting_workload(workload: str) -> int:
    """
    Diese Funktion wandelt den Workload eines Moduls von String in integer um. Falls nötig, werden die
    verschiedenen Arten von Stunden addiert.

    :param workload: Der Workload, der umgewandelt werden.
    :return:         Der Workload als integer.
    """
    if workload is None:
        return np.nan

    res = 0
    for part in workload.split(' '):
        if part.isdigit():
            res += int(part)
    return res


def parse_url(content: bytes, dict_modules: dict):
    """
    Die Funktion erstellt aus dem Antwort-Objekt ein Dictionary,
    wandelt die Zahlen im Antwort-Objekt von String in float / integer um und speichert das Dictionary in ein
    Dictionary, in dem die Informationen zu allen Modulen festgehalten werden.

    :param content:      Das Antwort-Objekt, das umgewandelt werden soll.
    :param dict_modules: Das Python Dictionary, in das die Informationen des Moduls gespeichert werden soll.
    """

    dict_url = xmltodict.parse(content)
    if "ectspunkte" in dict_url["modul"]:
        dict_url["modul"]["ectspunkte"] = casting_ects(dict_url["modul"]["ectspunkte"])
    if "workload" in dict_url["modul"]:
        dict_url["modul"]["workload"] = casting_workload(dict_url["modul"]["workload"])
    reorder_dict(dict_url)
    # Der Key für das Modul soll der modulcode sein
    if "modulcode" in dict_url["modul"]:
        dict_modules[dict_url["modul"]["modulcode"]] = dict_url["modul"]


def get_dataframe(file_name: str) -> pd.DataFrame:
    """
    Die Funktion erstellt ein Dataframe aus den Informationen zu den Modulen.

    :param file_name: Die xml-Datei, die in eine Dataframe umgewandelt wird.
    :return:          Das Dataframe, das die Informationen zu den Modulen enthält.
    """
    # Wir wandeln die xml-Datei, die alle Module in der Moduldatenbank enthält, in ein Python Dictionary um.
    file = open(file_name)
    file_content = file.read()
    dict_file = xmltodict.parse(file_content)

    dict_modules = {}
    for modul in dict_file["index"]["modul"]:
        if "url" in modul:
            url = modul["url"]
            response = requests.get(url)
            content = response.text
            parse_url(content, dict_modules)

    # Nun kann ein Dataframe aus den Modulinformationen erstellt werden.
    module_df = pd.DataFrame(dict_modules)
    # switch columns and rows
    module_df = module_df.T
    module_df = module_df.drop("modulcode", axis=1)
    return module_df
