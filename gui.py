import os
import sys


from PySide2.QtWidgets import QApplication, QTextEdit
from PySide2.QtGui import QTextCursor, QIcon
from PySide2.QtCore import Qt, Slot


import main


STYLESHEET = """
QTextEdit {
    background-color: #111111;
    color: #EEEEEE;
    font-size: 13pt;
    font-family: serif;
    border: 1px solid black;
}
"""


EXEDIR = (
    hasattr(sys, "_MEIPASS")
    and os.path.abspath(os.path.dirname(sys.executable))
    or os.path.abspath(os.path.dirname(sys.argv[0]))
)


def RESOURCE(filename):
    return os.path.join(EXEDIR, "data", filename)


class Gui(QTextEdit):
    def __init__(self):
        QTextEdit.__init__(self)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLESHEET)
        self.setWindowIcon(QIcon(RESOURCE("noun_Lighthouse_1548448.png")))
        if os.name == "nt":
            import ctypes

            myappid = "MyOrg.Mygui.1.0.0"  # Arbitrary
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.backstop = 0
        self.game = main.engine()
        main.output = self.append
        # get the first prompt
        nextprompt = next(self.game)
        self.processOutput(nextprompt)

    def moveToLastLine(self):
        tc = self.textCursor()
        pos = tc.position()
        doc = self.document()
        if doc.findBlock(pos) != doc.lastBlock():
            tc.setPosition(doc.lastBlock().position())
            tc.movePosition(QTextCursor.EndOfLine)
            self.setTextCursor(tc)

    def moveToHome(self, select=False):
        tc = self.textCursor()
        pos = self.backstop
        if select:
            tc.setPosition(pos, QTextCursor.KeepAnchor)
        else:
            tc.setPosition(pos)
        self.setTextCursor(tc)

    def keyPressEvent(self, event):
        key = event.key()
        self.moveToLastLine()
        if key == Qt.Key_Home:
            self.moveToHome(select=event.modifiers() & Qt.ShiftModifier)
        elif key in (Qt.Key_Backspace, Qt.Key_Left):
            if self.textCursor().position() > self.backstop:
                QTextEdit.keyPressEvent(self, event)
        elif key in (Qt.Key_Up, Qt.Key_Down):
            pass
        elif key == Qt.Key_Tab:
            pass
        elif key == Qt.Key_Return:
            self.enterCommand()
        else:
            QTextEdit.keyPressEvent(self, event)

    def enterCommand(self):
        tc = self.textCursor()
        tc.setPosition(self.backstop)
        tc.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cmdString = tc.selectedText()
        tc.movePosition(QTextCursor.EndOfLine)
        self.setTextCursor(tc)
        print(cmdString)
        try:
            nextprompt = self.game.send(cmdString)
        except StopIteration:
            self.close()
        else:
            self.processOutput(nextprompt)

    def processOutput(self, message):
        self.append(message)
        self.backstop = self.textCursor().position()

    def quit(self):
        self.close()

    def closeEvent(self, event):
        self.close()


class Main:
    def __init__(self):
        app = QApplication([])
        gui = Gui()
        gui.show()
        app.exec_()


if __name__ == "__main__":
    Main()
