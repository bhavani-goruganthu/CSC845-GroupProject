from queue import Queue
from threading import Thread, Event
import platform
import time

class ChatUI:

    def __init__(self):
        if platform.system() == "Windows":
            from windowsio import WindowsIO
            self.io = WindowsIO()
        else:
            from posixio import PosixIO
            self.io = PosixIO()
        self.exiting = Event()
        self.input_queue = Queue()
        self.output_queue = Queue()

    def __enter__(self):
        self.io.__enter__()
        Thread(target = self.__input_thread).start()
        Thread(target = self.__output_thread).start()
        Thread(target = self.__cursor_thread).start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.io.__exit__(exc_type, exc_value, traceback)
        return False

    def __input_thread(self):
        line = ""
        while True:
            self.output_queue.put(('input', line))
            c = self.io.getch()
            if '\x20' <= c and c <= '\x7E': # printable
                line += c
            elif c == '\x0D': # CR
                self.input_queue.put(line)
                line = ""
            elif c == '\x1B': # ESC
                line = ""
            elif c == '\x08' or c == '\x7F': # BS or DEL
                line = line[:-1]
            elif c == '\x03' or c == '\x04' or c == '\x1A': # ^C, ^D, or ^Z
                self.exiting.set()
                self.input_queue.put(None)
                self.output_queue.put(('exiting'))
                return

    def __output_thread(self):
        last_line = ""
        cursor = False
        while True:
            self.io.write("\r" + self.__format_input(last_line, cursor))
            command = self.output_queue.get()
            op = command[0]
            if op == 'input':
                last_line = command[1]
            elif op == 'output':
                line = command[1]
                self.io.write("\r" + self.__format_output(line) + "\n")
            elif op == 'cursor':
                cursor = command[1]
            else:
                self.io.write("\r" + self.__format_input(last_line, False) + "\r\n")
                return

    def __cursor_thread(self):
        while not self.exiting.is_set():
            self.exiting.wait(0.5)
            self.output_queue.put(('cursor', True))
            self.exiting.wait(0.5)
            self.output_queue.put(('cursor', False))

    def __format_input(self, line, cursor):
        max_length = self.io.columns() - 1
        length = len(line)
        cursor_char = (' ', '_')[cursor]
        if length + 3 > max_length:
            return ">+" + line[(length + 3) - max_length:] + cursor_char
        else:
            return "> " + line + cursor_char + " " * (max_length - (length + 3))

    def __format_output(self, line):
        max_length = self.io.columns() - 1
        length = len(line)
        if length > max_length:
            return line[:max_length - 3] + "..."
        else:
            return line + " " * (max_length - length)

    def get_input(self, block = True, timeout = None):
        return self.input_queue.get(block, timeout)

    def add_output(self, line):
        self.output_queue.put(('output', line))

    def is_exiting(self):
        return self.exiting.is_set()

    def wait_for_exiting(self, timeout = None):
        return self.exiting.wait(timeout)