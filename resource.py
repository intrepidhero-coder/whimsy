import os
import sys


EXEDIR = (
    hasattr(sys, "_MEIPASS")
    and os.path.abspath(os.path.dirname(sys.executable))
    or os.path.abspath(os.path.dirname(sys.argv[0]))
)


def RESOURCE(filename):
    return os.path.join(EXEDIR, filename)
