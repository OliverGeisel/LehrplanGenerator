import json
import pathlib
import re
from typing import List

import PySimpleGUI as gui

from courseplan import courseplan

new_content_line = "New-Content-Line"
new_goal_line = "New-Goal-Line"
new_meta_line = "New-Meta-Line"
new_group = "New-Group"


def create_goal_line(num: int):
    layout = [gui.Combo(values=["First-Look", "Know", "Translate", "Control", "Use", "Comment", "Create"],
                        default_value=["Know"],
                        key=f"goal-expression-{num}"), gui.Input("MasterKey-Word", key=f"goal-word-{num}"),
              gui.MLine("Complete text!", size=(45, 2), key=f"goal-complete-{num}")]
    return layout


inhalt_layout = [create_goal_line(1),
                 [gui.Button("Weiteren Inhalt", key=new_content_line), gui.Button("Weiters Ziel", key=new_goal_line)]]

meta_layout = [[gui.Text("Kursname:"), gui.Input(key="meta-name-input")],
               [gui.Text("Beschreibung:"),
                gui.MLine(key="meta-description-input", size=(45, 5), auto_size_text=True, auto_refresh=True,
                          autoscroll=True, )],
               [gui.Text("Jahr:"), gui.Input(key="meta-year-input")],
               [gui.Text("Schultyp:"),
                gui.Combo(["Gymnasium", "Grundschule", "Realschule", "Universität", "Berufsschule"], ["Gymnasium"],
                          key="meta-typ-input")],
               [gui.Button("Zusätzliche Info", key="New-Meta-Line")]
               ]


def create_structure_line(chap: int, group: int, num: int) -> List[List]:
    return [[gui.Input(key=f"structure-{chap}-{group}-{num}"),
             gui.Input("Thema", key=f"structure-name-{chap}-{group}-{num}"),
             gui.DropDown(["EXTRA", "SKIPPABLE", "IMPORTANT", "MANDATORY"],
                          key=f"structure-weight-{chap}-{group}-{num}")]]


def create_new_group(chap: int, group: int) -> List[List]:
    layout_group = [
        [gui.Input(f"Gruppe {chap}-{group}", key=f"group-{chap}-{group}-name"),
         gui.Button("Update", key=f"group-{chap}-{group}-update")],
        [gui.HSeparator()], create_structure_line(chap, group, 1)[0]]
    return [[gui.Frame(f"Gruppe {chap}-{group}",
                       layout_group, key=f"Frame-group-{chap}-{group}")]]


def create_new_chapter(chap: int) -> List[List]:
    layout_chapter = [
        [gui.Input(f"Kapitel {chap}", key=f"chapter-{chap}-name"), gui.Button("Update", key=f"chapter-{chap}-update")],
        [gui.HSeparator()], create_new_group(chap, 1)[0]]
    return [[gui.Frame(f"Kapitel {chap}",
                       layout_chapter, key=f"Frame-chapter-{chap}")]]


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
    chapter_num = len(frame.Widget.children)
    window.extend_layout(frame, create_new_chapter(chapter_num + 1))
    window.refresh()


def add_line_in_frame(window: gui.Window, frame: gui.Frame, line: List[List]):
    window.extend_layout(frame, line)


def get_element(window: gui.Window, element_key: str):
    return window.find_element(element_key)


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
        meta_object[i.removeprefix("meta-").removesuffix("-input")] = values[i]
    structure_keys = [key for key in keys if "chapter" in key or "structure" in key]

    goal_keys = [key for key in keys if "goal" in key]
    # group by number
    goal_groups = {}
    for key in goal_keys:
        num = int(key.split("-")[2])
        if num not in goal_groups.keys():
            goal_groups[num] = []
        goal_groups[num].append(key)

    goals = {}
    for i, elements in goal_groups.items():
        goal = {"key": f"goal-{i}", "expression": values[elements[0]], "target": values[elements[1]],
                "completeSentence": values[elements[2]]}
        goals[goal["key"]] = goal

    # Add structure
    structure_keys = [key for key in keys if "chapter" in key or "structure" in key or "group" in key]
    chapter_keys = [key for key in structure_keys if "chapter" in key]
    structure = []
    chapters = []
    chapter_groups = {}
    # chapters
    for key in chapter_keys:
        num = int(key.split("-")[1])
        if num not in chapter_groups.keys():
            chapter_groups[num] = []
        chapter_groups[num].append(key)
    for i, elements in chapter_groups.items():
        chapter = {"key": f"chapter-{i}", "name": values[elements[0]], "groups": []}
        chapters.append(chapter)

    # groups
    group_keys = [key for key in structure_keys if "group" in key]
    group_dict = {}
    for key in group_keys:
        id = key.removeprefix("group-").removesuffix("-name")
        if id not in group_dict.keys():
            group_dict[id] = []
        group_dict[id].append(key)
    for i, elements in group_dict.items():
        group = {"key": elements[0], "name": values[elements[0]], "lines": []}
        chapter = int(elements[0].split("-")[1])
        chapter = chapters[chapter - 1]
        chapter["groups"].append(group)

    # lines
    line_keys = [key for key in structure_keys if "structure" in key]
    line_groups = {}
    for key in line_keys:
        id_with_suffix = key.removeprefix("structure-")
        id = re.search(r"\d+-\d+-\d+", id_with_suffix)
        if id not in line_groups.keys():
            line_groups[id] = []
        line_groups[id].append(key)
    for i, elements in line_groups.items():
        line = {"key": values[elements[0]]}  # TODO add wenn emhr bekannt
        chapter_num = int(elements[0].split("-")[1])
        chapter = chapters[chapter_num - 1]
        group_num = int(elements[0].split("-")[2])
        group = chapter["groups"][group_num - 1]
        group["lines"].append(line)

    # add all
    structure.extend(chapters)

    file_name: str
    file_name = values["create-file-name"]
    file_name = "Plan.json" if file_name in [None, ""] else file_name
    file_name = file_name if file_name.endswith(".json") else file_name + ".json"
    path = pathlib.Path(file_name)
    directory = path.parent
    if not directory.exists():
        directory.mkdir(parents=True)
    if path.exists():
        back = gui.popup_yes_no("File existiert bereits. Überschreiben?")
        if back == "No":
            return
    with open(file_name, "w") as output_file:
        coursePlan = courseplan.CoursePlan(meta_object, goals, structure)
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


goal_count = 0
chapter_count = 0


def get_last_chapter(window: gui.Window) -> gui.Frame:
    chapter = get_element(window, f"Frame-chapter-{chapter_count}")
    return chapter


def run_new(window: gui.Window):
    global goal_count, chapter_count
    goal_count = 1
    chapter_count = 1
    event: str
    while True:
        window.refresh()
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
        elif event == new_group:
            chapter = get_last_chapter(window)
            grop_count = len(chapter.Widget.children) - 2
            group = create_new_group(chapter_count, grop_count + 1)

            add_line_in_frame(window, chapter, group)
        elif event == "new-chapter":
            add_chapter(window)
            chapter_count += 1
        elif event == new_goal_line:
            frame = get_element(window, "Content-Frame")
            goal_count += 1
            line = create_goal_line(goal_count)
            add_line_in_frame(window, frame, [line])
        elif event == "Create-New":
            export_to_json(value)
        elif re.match(r"chapter-\d+-update", event):
            chapter = event.split("-")[1]
            chapter = int(chapter)
            update_chapter(window, chapter)


new_layout = [[gui.Text("Bitte füllen Sie die folgenden Felder aus")],
              [gui.HSeparator()],
              [gui.Frame("Metadata", meta_layout, key="Meta-Frame")],
              [gui.HSeparator()],
              [gui.Frame("Inhalt", inhalt_layout, key="Content-Frame")],
              [gui.HSeparator()],
              [gui.Frame("Struktur", create_new_chapter(1), key="Structure-Frame")],
              [gui.Frame("Absätze",
                         [[gui.Button("Gruppe", key="New-Group"), gui.Button("Kapitel", key="new-chapter")]])],
              [gui.Button("Erstellen!", key="Create-New"), gui.Input("Plan.json", key="create-file-name")]
              ]


def create_new():
    return gui.Window("Neuer Plan", size=(900, 600),
                      layout=[[gui.Column(layout=new_layout, size=(480, 600), expand_x=True, expand_y=True,
                                          scrollable=True, vertical_scroll_only=True, vertical_alignment="t")]],
                      resizable=True)
