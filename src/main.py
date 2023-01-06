import json
import pathlib

import gui


def run():
    window = gui.crate_main()
    event, values = window.read()
    window.close()  # todo überdenken
    if event == gui.new_plan:
        second_window = gui.create_new()
        try:
            gui.run_new(second_window)
        except:
            input("Achtung Fehler! Kontrolliere und drücke Enter!")
            # gui.popup_error("Fehler!")
    elif event == gui.open_file:
        file = gui.popup_import()
        if file:
            with open(file) as plan:
                content = plan.read()
                path = pathlib.Path(file)
                fileLocation = path.parent
                filename = path.name
            decoder = json.JSONDecoder()
            json_content = decoder.decode(content)
            second_window = gui.create_edit(json_content, path)
            gui.run_edit(second_window)
    else:
        window.close()
    window.close()


if __name__ == "__main__":
    run()
