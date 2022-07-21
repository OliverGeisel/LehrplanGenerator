import pathlib
from typing import List

import PySimpleGUI as gui


def run_edit(window: gui.Window):
    try:
        while True:
            event, values = window.read()
            if event == gui.WIN_CLOSED:
                break
    except:
        gui.popup_error("Fehler!")


def create_meta_part(meta) -> list[list]:
    back = [[gui.Text("Kursname:"), gui.Input(meta["name"], key="meta-name-input")],
            [gui.Text("Beschreibung:"),
             gui.MLine(meta["description"], key="meta-description-input", size=(45, 5), auto_size_text=True,
                       auto_refresh=True, autoscroll=True, )],
            [gui.Text("Jahr:"), gui.Input(meta["year"], key="meta-year-input")],
            [gui.Text("Schultyp:"),
             gui.DropDown(["Gymnasium", "Grundschule", "Realschule", "Universität", "Berufsschule"],
                          [meta["typ"]], key="meta-typ-input")],
            [gui.Button("Zusätzliche Info", key="New-Meta-Line")]]

    return back


def create_edit(jsonContent: dict, filen: pathlib.Path):
    meta = jsonContent["meta"]
    content = jsonContent["content"]
    structure = jsonContent["structure"]
    layout = []
    layout.extend(create_meta_part(meta))
    return gui.Window("Edit", layout)
