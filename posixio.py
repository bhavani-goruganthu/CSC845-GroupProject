from tty import setraw
from sys import stdin, stdout
from termios import tcgetattr, tcsetattr, ECHO, TCSADRAIN
from shutil import get_terminal_size

class PosixIO:

    def __enter__(self):
        self.fd = stdin.fileno()
        self.attr = tcgetattr(self.fd)
        newattr = tcgetattr(self.fd)
        newattr[3] = newattr[3] & ~ECHO
        tcsetattr(self.fd, TCSADRAIN, newattr)
        setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        tcsetattr(self.fd, TCSADRAIN, self.attr)
        return False

    def getch(self):
        return stdin.read(1)

    def write(self, s):
        stdout.write(s)
        stdout.flush()

    def columns(self):
        return get_terminal_size().columns