import msvcrt
import shutil
from sys import stdout

class WindowsIO:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def getch(self):
        return ord(msvcrt.getch())

    def write(self, s):
        stdout.write(s)
        stdout.flush()

    def columns(self):
        return shutil.get_terminal_size().columns
