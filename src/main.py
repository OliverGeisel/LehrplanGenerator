import json
import pathlib

from gui import maingui, createNew


def run():
    window = maingui.crate_main()
    event, values = window.read()
    window.close()  # todo überdenken
    if event == maingui.new_plan:
        second_window = createNew.create_new()
        try:
            createNew.run_new(second_window)
        except:
            input("Achtung Fehler! Kontrolliere und drücke Enter!")
            # gui.popup_error("Fehler!")
    elif event == maingui.open_file:
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
    else:
        window.close()
    window.close()


if __name__ == "__main__":
    run()
