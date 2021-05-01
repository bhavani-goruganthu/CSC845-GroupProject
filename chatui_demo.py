from chatui import ChatUI
from threading import Thread
from time import sleep

try:
    with ChatUI() as ui:
        def do_output():
            while not ui.wait_for_exiting(timeout = 2):
                ui.add_output("timer", "Testing...")
        def do_input():
            line = ui.get_input()
            while line is not None:
                ui.add_output("you", line)
                line = ui.get_input()
        Thread(target = do_output, daemon = True).start()
        Thread(target = do_input, daemon = True).start()
        ui.wait_for_exiting()
except KeyboardInterrupt:
    pass
