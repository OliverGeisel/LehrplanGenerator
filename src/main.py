import json
import pathlib

from gui import maingui, createNew


def run():
    window = maingui.crate_main()
    event, values = window.read()
    if event == "Neuer Plan":
        second_window = createNew.create_new()
        createNew.run_new(second_window)
    if event == "Öffne File":
        file = maingui.popup_import()
        with open(file) as plan:
            content = plan.read()
            path = pathlib.Path(file)

            fileLocation = path.parent
            filename = path.name

        decoder = json.JSONDecoder()
        jsonContent = decoder.decode(content)
        second_window = maingui.create_edit(jsonContent)
        maingui.run_edit(second_window)
    window.close()


if __name__ == "__main__":
    run()
