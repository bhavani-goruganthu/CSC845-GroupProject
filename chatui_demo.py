from chatui import ChatUI
from threading import Thread
from time import sleep

with ChatUI() as ui:
    def do_output():
        while not ui.is_exiting():
            ui.add_output("Hello")
            sleep(2)
    def do_input():
        while not ui.is_exiting():
            line = ui.get_input()
            if line != None:
                ui.add_output("You said: <" + line + ">")
    Thread(target = do_output).start()
    Thread(target = do_input).start()
    ui.wait_for_exiting()
