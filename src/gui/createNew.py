import json
import re
from typing import List

import PySimpleGUI as gui

from courseplan import courseplan

new_content_line = "New-Content-Line"
new_meta_line = "New-Meta-Line"
# todo incomplete
inhalt_layout = [[gui.Button("Weiters Ziel", key="New-Content-Line")]]

meta_layout = [[gui.Text("Kursname:"), gui.Input(key="meta-name-input")],
               [gui.Text("Beschreibung:"), gui.Input(key="meta-description-input")],
               [gui.Text("Jahr:"), gui.Input(key="meta-year-input")],
               [gui.Text("Schultyp:"),
                gui.Combo(["Gymnasium", "Grundschule", "Realschule", "Universität", "Berufsschule"], ["Gymnasium"],
                          key="meta-typ-input")],
               [gui.Button("Zusätzliche Info", key="New-Meta-Line")]
               ]


def create_structure_line(chap: int, num: int):
    return [[gui.Input(key=f"structure-{chap}-{num}")]]


def create_new_chapter(chap: int):
    layout_chapter = [
        [gui.Input(f"Kapitel {chap}", key=f"chapter-{chap}-name"), gui.Button("Update", key=f"chapter-{chap}-update")],
        [gui.HSeparator()], create_structure_line(chap, 1)[0]]
    return [[gui.Frame(f"Kapitel {chap}",
                       layout_chapter, key=f"Frame-chapter-{chap}")]]


new_layout = [[gui.Text("Bitte füllen Sie die folgenden Felder aus")],
              [gui.HSeparator()],
              [gui.Frame("Metadata", meta_layout, key="Meta-Frame")],
              [gui.HSeparator()],
              [gui.Frame("Inhalt", inhalt_layout, key="Content-Frame")],
              [gui.HSeparator()],
              [gui.Frame("Struktur", create_new_chapter(1), key="Structure-Frame")],
              [gui.Frame("Absätze",
                         [[gui.Button("Gruppe", key="new-group"), gui.Button("Kapitel", key="new-chapter")]])],
              [gui.Button("Erstellen!", key="Create-New")]
              ]


def export_to_json(values: dict[str, any]):
    encoder = json.JSONEncoder()

    for i in values:
        print(i)
    year = values["meta-year-input"]
    year = int(year) if year != "" else 0
    values["meta-year-input"] = year
    keys = list(values.keys())
    meta_keys = [key for key in keys if "meta" in key]
    meta_object = {}
    for i in meta_keys:
        meta_object[i] = values[i]
    structure_keys = [key for key in keys if "chapter" in key or "structure" in key]

    content = {}

    structure = {}
    for i in structure_keys:
        structure[i] = values[i]

    with open("Test.json", "w") as output_file:
        coursePlan = courseplan.CoursePlan(meta_object, content, structure)
        output_file.write("{\n")
        for i, elem in enumerate(coursePlan.getAll().items()):
            name = elem[0]
            values = elem[1]
            enc_name = encoder.encode(name)
            enc_values = encoder.encode(values)
            output_file.write(f"{enc_name}:{enc_values}")
            if i == len(coursePlan) - 1:
                output_file.write("}")
            else:
                output_file.write(",\n")


def update_chapter(window: gui.Window, chapter: int):
    frame: gui.Frame
    frame = window.find_element(f"Frame-chapter-{chapter}")
    name: gui.Input
    name = frame.Rows[0][0].get()
    frame.Title = name
    window.refresh()


def add_chapter(window: gui.Window):
    frame: gui.Frame
    frame = window.find_element("Structure-Frame")
    chapter_count = len(frame.Widget.children)
    window.extend_layout(frame, create_new_chapter(chapter_count + 1))
    window.refresh()


def add_line_in_frame(window: gui.Window, frame: gui.Frame, line: List[List]):
    window.extend_layout(frame, line)
    window.element_list()


def get_element(window: gui.Window, element_key: str):
    return window.find_element(element_key)


def run_new(window: gui.Window):
    while True:
        event: str
        event, value = window.read()
        if event in [gui.WIN_CLOSE_ATTEMPTED_EVENT, gui.WIN_CLOSED]:
            break
        elif event == new_meta_line:
            frame = get_element(window, "Meta-Frame")
            line = [[gui.Text("hallo"), gui.Input()]]
            add_line_in_frame(window, frame, line)
        elif event == new_content_line:
            frame = get_element(window, "Content-Frame")
            line = [[gui.Input(), gui.Input()]]
            add_line_in_frame(window, frame, line)
        elif event == "Create-New":
            export_to_json(value)
        elif re.match(r"chapter-\d+-update", event):
            chapter = event.split("-")[1]
            chapter = int(chapter)
            update_chapter(window, chapter)
        elif event == "new-chapter":
            add_chapter(window)


def create_new():
    return gui.Window("Neuer Plan", layout=new_layout)
