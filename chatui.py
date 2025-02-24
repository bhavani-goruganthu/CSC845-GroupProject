from queue import Queue
from threading import Thread, Event
import platform


class ChatUI:

    def __init__(self):
        if platform.system() == "Windows":
            from windowsio import WindowsIO
            self.io = WindowsIO()
        else:
            from posixio import PosixIO
            self.io = PosixIO()
        self.exiting = Event()
        self.exited = Event()
        self.input_queue = Queue()
        self.output_queue = Queue()

    def __enter__(self):
        self.io.__enter__()
        Thread(target = self.__input_thread, daemon = True).start()
        Thread(target = self.__output_thread, daemon = True).start()
        Thread(target = self.__cursor_thread, daemon = True).start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.send_exit_signals()
        self.exited.wait()
        self.io.__exit__(exc_type, exc_value, traceback)
        return False

    def send_exit_signals(self):
        self.exiting.set()
        self.input_queue.put(None)
        self.output_queue.put(('exiting',))

    def __input_thread(self):
        line = ""
        while True:
            self.output_queue.put(('input', line))
            c = self.io.getch()
            if 0x20 <= c <= 0x7E:  # printable
                line += chr(c)
            elif c == 0x0D:  # CR
                line = line.strip()
                if line != "":
                    self.input_queue.put(line)
                line = ""
            elif c == 0x1B:  # ESC
                line = ""
            elif c == 0x08 or c == 0x7F:  # BS or DEL
                line = line[:-1]
            elif c == 0x03 or c == 0x04 or c == 0x1A:  # ^C, ^D, or ^Z
                self.send_exit_signals()
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
                prefix = (command[1] + " *" if command[1] else "!")
                line = command[2]
                self.io.write("\r" + self.__format_output(prefix, line) + "\n")
            elif op == 'cursor':
                cursor = command[1]
            else:
                self.io.write("\r" + self.__format_input(last_line, False) + "\r\n")
                self.exited.set()
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

    def __format_output(self, prefix, line):
        return format_output(self.io.columns(), prefix, line)

    def get_input(self, block = True, timeout = None):
        """Read one line of input from the user. Returns None if the user exits."""
        return None if self.is_exiting() else self.input_queue.get(block, timeout)

    def add_output(self, prefix, line):
        """Displays one line of output to the user."""
        self.output_queue.put(('output', prefix, line))

    def is_exiting(self):
        """Returns True or False depending on whether the user has exited
        the program."""
        return self.exiting.is_set()

    def wait_for_exiting(self, timeout = None):
        """Waits until the user exits or the given timeout has elapsed, and then
        returns the same as is_exiting()."""
        return self.exiting.wait(timeout)


def format_output(columns, prefix, line):
    max_length = columns - 1
    words = line.split()
    formatted_lines = []
    formatted_line = [prefix]
    at_start_of_line = True
    length = len(prefix)
    while len(words) > 0:
        word = words[0]
        if length + 1 + len(word) <= max_length:
            formatted_line.append(word)
            length += 1 + len(word)
            at_start_of_line = False
            words.pop(0)
        elif at_start_of_line:
            partial_length = max_length - length - 1
            formatted_line.append(word[:partial_length])
            length = max_length
            at_start_of_line = False
            words[0] = word[partial_length:]
        else:
            if length < max_length:
                formatted_line.append(" " * (max_length - length - 1))
            formatted_lines.append(formatted_line)
            formatted_line = [' ']
            length = 1
            at_start_of_line = True
    if length < max_length:
        formatted_line.append(" " * (max_length - length - 1))
    formatted_lines.append(formatted_line)
    return "\r\n".join([" ".join(words) for words in formatted_lines])
