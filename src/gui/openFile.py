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


def create_edit(jsonContent: dict):
    meta = jsonContent["meta"]

    return gui.Window("Edit", [[]])
