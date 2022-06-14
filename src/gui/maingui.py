import pathlib
from typing import List

import PySimpleGUI as gui

start_layout = [[gui.Text("Willkommen. Bitte wählen Sie aus!")],
                [gui.Text("Neuen Plan erstellnen"), gui.HSeparator(color=gui.DEFAULT_BACKGROUND_COLOR),
                 gui.Button("Neuer Plan")],
                [gui.Text("Bearbeiten"), gui.Button("Öffne File")]
                ]


def get_element(window: gui.Window, element_key: str):
    return window.find_element(element_key)


icon_path = pathlib.Path("./res/icon/favicon.ico")


def crate_main():
    window = gui.Window(title="Lehrplan Konfiguration", layout=start_layout)#, icon=str(icon_path),
                        #use_custom_titlebar=True, titlebar_icon=str(icon_path))
    return window


def add_line_in_frame(window: gui.Window, frame: gui.Frame, line: List[List]):
    window.extend_layout(frame, line)
    window.element_list()


def popup_import():
    return gui.popup_get_file("Plan der geöffnet werden soll!", "Öffnen", "./plan.json")


def create_edit(jsonContent):
    return gui.Window("Edit", [[]])


def run_edit(window: gui.Window):
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED:
            break
