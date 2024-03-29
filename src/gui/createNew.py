import json
import pathlib
import re
from typing import List

import PySimpleGUI as gui
from courseplan import CoursePlan

GOAL_BG_COLOR = "yellow green"
TASK_BG_COLOR = "red4"
GROUP_BG_COLOR = "maroon"
CHAPTER_BG_COLOR = "dark slate blue"

new_content_task = "New-Content-Task"
new_goal = "New-Goal-Line"
new_meta_line = "New-Meta-Line"
new_chapter = "New-Chapter"
new_group = "New-Group"
new_task = "New-Task"
create_new_file = "Create-New"


def add_meta_line(window: gui.Window):
    global extra_meta_count
    frame = window.find_element("meta-frame")
    extra_meta_count += 1
    line = [[gui.Input("Information", key=f"meta-extra-{extra_meta_count}-name"),
             gui.Input("Wert", key=f"meta-extra-{extra_meta_count}-value")]]
    window.extend_layout(frame, line)


meta_layout = [[gui.Text("Kursname:"), gui.Input(key="meta-name-input")],
               [gui.Text("Beschreibung:"),
                gui.MLine(key="meta-description-input", size=(45, 5), auto_size_text=True, auto_refresh=True,
                          autoscroll=True, )],
               [gui.Text("Jahr:"), gui.Input(key="meta-year-input")],
               [gui.Text("Schultyp:"),
                gui.DropDown(["Gymnasium", "Grundschule", "Realschule", "Universität", "Berufsschule"], ["Gymnasium"],
                             key="meta-type-input")],
               [gui.Text("Stufe:"),
                gui.InputText("Klasse X", key="meta-level-input")],
               [gui.Button("Zusätzliche Info", key="New-Meta-Line")]
               ]


def create_goal(num: int) -> List[List]:
    layout = list()
    layout.append([gui.DropDown(values=["First-Look", "Know", "Translate", "Control", "Use", "Comment", "Create"],
                                default_value=["Know"],
                                key=f"goal-expression-{num}"), gui.Input("MasterKey-Word", key=f"goal-word-{num}"),
                   gui.MLine("Complete text!", size=(45, 2), key=f"goal-complete-{num}")])
    layout.append(
        [gui.Button("Weiterer Inhalt", key=f"new-inhalt-{num}",
                    tooltip="Fügt ein Feld für weitere Inhalte, des Goals, hinzu")])
    layout.append([gui.Input("Neuer Inhalt", key=f"goal-content-{num}-{1}", tooltip="Inhalt des Goals")])

    return [[gui.Frame(f"goal-{num}", layout, key=f"goal-frame-{num}", background_color=GOAL_BG_COLOR)]]


inhalt_layout = [[gui.Column(create_goal(1), key="column-goals", background_color=GOAL_BG_COLOR)],
                 [gui.Button("Weiters Ziel", key=new_goal, tooltip="Hinzufügen eines weiteren Ziels")]]


# -------------- TASK ------------------------------------------------------
def create_new_structure_task(chap: int, group: int, num: int) -> List[List]:
    return [[
        gui.Column([[gui.Input(f"Name", key=f"task-{chap}-{group}-{num}-name", tooltip="Name/Titel der Aufgabe"),
                     gui.Text("Thema:", tooltip=f"Das Thema, der Aufgabe {chap}-{group}-{num}."),
                     gui.Input("", key=f"task-{chap}-{group}-{num}-topic",
                               tooltip="Inhalt eines Goals, das umgesetzt werden soll."),
                     gui.DropDown(["INFORMATIONAL", "OPTIONAL", "IMPORTANT", "MANDATORY"], default_value=["MANDATORY"],
                                  key=f"task-{chap}-{group}-{num}-relevance", tooltip="Relevanz der Aufgabe"),
                     gui.Column([[gui.Frame(f"Alternativen",
                                            [[gui.Button("Alternativen", key=f"task-{chap}-{group}-{num}-alternative",
                                                         tooltip="Fügt eine Alternative des zu suchenden Inhalts hinzu."
                                                         )]],
                                            key=f"Frame-task-{chap}-{group}-{num}-alternative",
                                            background_color=TASK_BG_COLOR)]])
                     ]], background_color=TASK_BG_COLOR, key=f"Column-task-{chap}-{group}-{num}")
    ]]


def add_structure_task_alternative(window: gui.Window, chapter: int, group: int, task: int):
    frame: gui.Frame = window.find_element(f"Frame-task-{chapter}-{group}-{task}-alternative")
    num = len(frame.widget.children)
    new_alternative_line = [
        [gui.Text(f"Alternative-{num}", background_color=TASK_BG_COLOR),
         gui.Input(key=f"task-{chapter}-{group}-{task}-alternative-{num}",
                   tooltip="Fügt eine Alternative des zu suchenden Inhalts hinzu.")]
    ]
    window.extend_layout(frame, new_alternative_line)
    window.refresh()


# ------------------- GROUP ------------------------------------------------------

def create_new_group(chap: int, group: int) -> List[List]:
    layout_group = [
        [gui.Input(f"Gruppe {chap}-{group}", key=f"group-{chap}-{group}-name", tooltip="Name der Gruppe"),
         gui.Button("Update", key=f"group-{chap}-{group}-update", tooltip="Aktualisiert den Namen der Gruppe")],
        [gui.Frame(f"Alternativen", [[gui.Button("Alternativen", key=f"group-{chap}-{group}-alternative")]],
                   key=f"Frame-group-{chap}-{group}-alternative", background_color=GROUP_BG_COLOR),
         gui.Text("Thema:", tooltip=f"Das Thema, der Gruppe {chap}-{group}."),
         gui.Input("", key=f"group-{chap}-{group}-topic", tooltip="Inhalt eines Goals, das umgesetzt werden soll.")],
        [gui.HSeparator()], create_new_structure_task(chap, group, 1)[0]]
    return [[gui.Frame(f"Gruppe {chap}-{group}",
                       layout_group, key=f"Frame-group-{chap}-{group}", background_color=GROUP_BG_COLOR)]]


def update_group(window: gui.Window, chapter, group):
    frame: gui.Frame
    frame = window.find_element(f"Frame-group-{chapter}-{group}")
    name: gui.Input
    name = frame.Rows[0][0].get()
    frame.update(name)
    window.refresh()


def add_group_alternative(window: gui.Window, chapter: int, group: int):
    frame: gui.Frame = window.find_element(f"Frame-group-{chapter}-{group}-alternative")
    num = len(frame.widget.children)
    new_alternative_line = [
        [gui.Text(f"Alternative-{num}", background_color=GROUP_BG_COLOR),
         gui.Input(key=f"group-{chapter}-{group}-alternative-{num}")]
    ]
    window.extend_layout(frame, new_alternative_line)
    window.refresh()


# -------- CHAPTER -----------------------------------------------

def create_new_chapter(chap: int, weight: float) -> List[List]:
    layout_chapter = [
        [gui.Input(f"Kapitel {chap}", key=f"chapter-{chap}-name"),
         gui.Button("Update", key=f"chapter-{chap}-update", tooltip="Aktualisiert den Namen des Kapitels"),
         gui.Text("Stundenzahl"), gui.Input(default_text=str(weight), key=f"chapter-{chap}-weight",
                                            tooltip="Studenanzahl, die für dieses Kapitel vorgesehen sind.")],
        [gui.Frame("Alternativen", [[gui.Button("Alternativen", key=f"chapter-{chap}-alternative",
                                                tooltip="Fügt Alternative für das Wissensgebiet hinzu")],
                                    ],
                   key=f"Frame-chapter-{chap}-alternative", background_color=CHAPTER_BG_COLOR),
         gui.Text("Thema:", tooltip=f"Das Thema, des Kapitels {chap}."),
         gui.Input("", key=f"chapter-{chap}-topic", tooltip="Inhalt eines Goals, das umgesetzt werden soll.")],
        [gui.HSeparator()], create_new_group(chap, 1)[0]]
    return [[gui.Frame(f"Kapitel {chap}",
                       layout_chapter, key=f"Frame-chapter-{chap}", background_color=CHAPTER_BG_COLOR)]]


def add_chapter(window: gui.Window):
    frame: gui.Frame
    frame = window.find_element("Structure-Frame")
    chapter_num = len(frame.Widget.children)
    window.extend_layout(frame, create_new_chapter(chapter_num + 1, 2))
    window.refresh()


def update_chapter(window: gui.Window, chapter: int):
    frame: gui.Frame
    frame = window.find_element(f"Frame-chapter-{chapter}")
    name: gui.Input
    name = frame.Rows[0][0].get()
    frame.update(name)
    window.refresh()


def add_chapter_alternative(window: gui.Window, chapter: int):
    frame: gui.Frame = window.find_element(f"Frame-chapter-{chapter}-alternative")
    num = len(frame.widget.children) - 1
    new_alternative_line = [
        [gui.Text(f"Alternative-{num + 1}", background_color=CHAPTER_BG_COLOR),
         gui.Input(key=f"chapter-{chapter}-alternative-{num + 1}")]
    ]
    window.extend_layout(frame, new_alternative_line)
    window.refresh()


def export_to_json(values: dict[str, any]):
    encoder = json.JSONEncoder()

    year = values["meta-year-input"]
    year = int(year) if year != "" else 0
    values["meta-year-input"] = year
    keys = list(values.keys())

    # ------------------META-PART------------------
    meta_object = export_meta_json(keys, values)

    # -------------------------CONTENT-PART---------------------

    goals = export_content_json(keys, values)

    # ------------------------STRUCTURE-PART---------------------

    structure = export_structure_json(keys, values)
    # write out
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
        course_plan = CoursePlan(meta_object, goals, structure)
        output_file.write("{\n")
        for key, elem in enumerate(course_plan.getAll().items()):
            name = elem[0]
            values = elem[1]
            enc_name = encoder.encode(name)
            enc_values = encoder.encode(values)
            output_file.write(f"{enc_name}:{enc_values}")
            if key == len(course_plan) - 1:
                output_file.write("}")
            else:
                output_file.write(",\n")


def export_structure_json(keys, values: dict[str, str]):
    structure_keys = [key for key in keys if "chapter" in key or "group" in key or "task" in key]
    chapter_keys = [key for key in structure_keys if "chapter" in key]
    structure = []
    chapters: list[dict] = []
    chapter_groups = {}
    # chapters
    # keys starts with chapter-{chapter_num}
    for key in chapter_keys:
        num = int(key.split("-")[1])
        if num not in chapter_groups.keys():
            chapter_groups[num] = []
        chapter_groups[num].append(key)
    for key, elements in chapter_groups.items():
        chapter = {"key": f"chapter-{key}",
                   "name": values[elements[0]],
                   "weight": float(values[elements[1]]),
                   "alternatives": [values[elem] for elem in elements[2:-1] if values[elem] not in ["", " ", "\t"]],
                   "topic": values[elements[-1]],
                   "groups": []
                   }
        chapters.append(chapter)
    # groups
    group_keys = [key for key in structure_keys if "group" in key]
    group_dict: dict[str, list[str]] = {}
    for key in group_keys:
        id_num = re.search(r"group-(\d+-\d+)", key).group(1)
        if id_num not in group_dict.keys():
            group_dict[id_num] = []
        group_dict[id_num].append(key)
    for key, elements in group_dict.items():
        group = {"key": elements[0].removesuffix("-name"),
                 "name": values[elements[0]],
                 "alternatives": [values[elem] for elem in elements[1:-1] if values[elem] not in ["", " ", "\t"]],
                 "topic": values[elements[-1]],
                 "tasks": list()
                 }
        chapter_num = int(key.split("-")[0])
        chapter = chapters[chapter_num - 1]
        chapter["groups"].append(group)
    # tasks
    task_keys = [key for key in structure_keys if "task" in key]
    task_groups: dict[str, list[str]] = {}
    for key in task_keys:
        id_with_suffix = key.removeprefix("task-")
        id_num = re.search(r"\d+-\d+-\d+", id_with_suffix).group(0)
        if id_num not in task_groups.keys():
            task_groups[id_num] = []
        task_groups[id_num].append(key)
    for key, elements in task_groups.items():
        task = {"key": elements[0].removesuffix("-name"),
                "name": values[elements[0]],
                "topic": values[elements[1]],
                "relevance": values[elements[2]],
                "alternatives": [values[elem] for elem in elements[3:] if values[elem] not in ["", " ", "\t"]]
                }
        chapter_num = int(elements[0].split("-")[1])
        chapter = chapters[chapter_num - 1]
        group_num = int(elements[0].split("-")[2])
        group = chapter["groups"][group_num - 1]
        group["tasks"].append(task)
    # add all
    structure.extend(chapters)
    return structure


def export_content_json(keys, values):
    goal_keys = [key for key in keys if key.startswith("goal")]
    # group by number
    goal_groups = {}
    for key in goal_keys:
        num = int(key.split("-")[2])
        if num not in goal_groups.keys():
            goal_groups[num] = []
        goal_groups[num].append(key)
    goals = {}
    for key, elements in goal_groups.items():
        content_elements = []
        for content_key in elements[3:]:
            content_elements.append(values[content_key])
        goal = {"key": f"goal-{key}",
                "expression": values[elements[0]],
                "target": values[elements[1]],
                "completeSentence": values[elements[2]],
                "content": content_elements
                }
        goals[goal["key"]] = goal
    return goals


def export_meta_json(keys, values):
    extra_meta_keys = [key for key in keys if key.startswith("meta-extra")]
    normal_meta_keys = [key for key in keys if key.startswith("meta-") and key.endswith("input")]
    meta_object = {}
    meta_groups = dict()
    extra_metas = []
    for key in extra_meta_keys:
        key_num = re.search(r"\d+", key)
        if key_num is not None:
            key_num = int(key_num.group(0))
            if key_num not in meta_groups:
                meta_groups[key_num] = []
            meta_groups[key_num].append(key)
    for group, group_keys in meta_groups.items():
        extra_metas.append({"name": values[group_keys[0]],
                            "value": values[group_keys[1]]})
    for key in normal_meta_keys:
        meta_object[key.removeprefix("meta-").removesuffix("-input")] = values[key]
    meta_object["extra"] = extra_metas
    return meta_object


goal_count = 0
chapter_count = 0
extra_meta_count = 0


def get_last_chapter_frame(window: gui.Window) -> gui.Frame:
    chapter = window.find_element(f"Frame-chapter-{chapter_count}")
    return chapter


def get_chapter_num(key: str) -> int:
    chapter = key.split("-")[1]
    return int(chapter)


def get_chapter_group_num(key: str) -> tuple[int, int]:
    return get_chapter_num(key), int(key.split("-")[2])


def get_chapter_group_task_num(key: str) -> tuple[int, int, int]:
    chapter = key.split("-")[1]
    chapter = int(chapter)
    group = int(key.split("-")[2])
    return chapter, group, int(key.split("-")[3])


def run_new(window: gui.Window):
    global goal_count, chapter_count, extra_meta_count
    goal_count = 1
    chapter_count = 1
    event: str
    n = 1
    while True:
        window.refresh()
        event, value = window.read()
        if event in [gui.WIN_CLOSE_ATTEMPTED_EVENT, gui.WIN_CLOSED]:
            break
        # add extra meta line
        elif event == new_meta_line:
            add_meta_line(window)
        # add content in selected goal
        elif re.match(r"new-inhalt-\d+", event):
            num = event.split("-")[-1]
            frame = window.find_element(f"goal-frame-{num}")
            content_num = len(frame.Widget.children) - 1
            line = [
                [gui.Input(str(content_num), key=f"goal-content-{num}-{content_num}",
                           tooltip="Term, der im Ziel vorkommt")]]
            window.extend_layout(frame, line)
        # add goal
        elif event == new_goal:
            goals_column = window.find_element("column-goals")
            goal_count += 1
            goal_frame = create_goal(goal_count)
            window.extend_layout(goals_column, goal_frame)
        # add task (step) in chapter/group
        elif event == new_task:
            chapter = get_last_chapter_frame(window)
            group_num = len(chapter.Widget.children) - 3
            chap_num = chapter.key.split("-")[2]
            group = window.find_element(f"Frame-group-{chap_num}-{group_num}")
            new_task_num = len(group.Widget.children) - 2
            line = create_new_structure_task(chap_num, group_num, new_task_num)
            window.extend_layout(group, line)
            del group_num, chap_num
        # add task alternative
        elif re.match(r"task-\d+-\d+-\d+-alternative", event):
            add_structure_task_alternative(window, *get_chapter_group_task_num(event))
        # add new group in selected chapter
        elif event == new_group:
            chapter = get_last_chapter_frame(window)
            group_num = len(chapter.Widget.children) - 3
            group = create_new_group(chapter_count, group_num + 1)
            window.extend_layout(chapter, group)
            del group_num
        # rename group
        elif re.match(r"group-\d+-\d+-update", event):
            update_group(window, *get_chapter_group_num(event))
        # add new group alternative
        elif re.match(r"group-\d+-\d+-alternative", event):
            add_group_alternative(window, *get_chapter_group_num(event))
        # add new chapter
        elif event == new_chapter:
            add_chapter(window)
            chapter_count += 1
        # rename chapter
        elif re.match(r"chapter-\d+-update", event):
            update_chapter(window, get_chapter_num(event))
        # add chapter alternative
        elif re.match(r"chapter-\d+-alternative", event):
            add_chapter_alternative(window, get_chapter_num(event))
        # export to json
        elif event == create_new_file:
            export_to_json(value)
        else:
            window.close()
            break
        # trick to get full window with scrollbar
        old_size = window.size
        n *= -1
        window.size = (old_size[0], old_size[1] + n)


new_layout = [[gui.Text("Bitte füllen Sie die folgenden Felder aus")],
              [gui.HSeparator()],
              [gui.Frame("Metadata", meta_layout, key="meta-frame", background_color="cadet blue")],
              [gui.HSeparator()],
              [gui.Frame("Inhalt", inhalt_layout, key="value-frame", background_color="medium sea green")],
              [gui.HSeparator()],
              [gui.Frame("Struktur", create_new_chapter(1, 2), key="Structure-Frame", background_color="dark violet")],
              [gui.Frame("Absätze",
                         [[gui.Button("Aufgabe", key=new_task), gui.Button("Gruppe", key=new_group),
                           gui.Button("Kapitel", key=new_chapter)]])],
              [gui.HSeparator()],
              [gui.Button("Erstellen!", key=create_new_file), gui.Input("Plan.json", key="create-file-name")]
              ]


def create_new():
    return gui.Window("Neuer Plan", size=(1200, 750),
                      layout=[[gui.Column(layout=new_layout, size=(480, 600), expand_x=True, expand_y=True,
                                          scrollable=True, vertical_scroll_only=True, vertical_alignment="t")]],
                      resizable=True, auto_size_text=True)
