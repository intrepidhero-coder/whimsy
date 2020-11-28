from PySide2.QtWidgets import QApplication, QTextEdit
from PySide2.QtGui import QTextCursor
from PySide2.QtCore import Qt, QProcess, Slot


class Gui(QTextEdit):
    def __init__(self):
        QTextEdit.__init__(self)
        self.backstop = 0
        self.shell = QProcess(self)
        self.shell.setProgram("/bin/sh")
        self.shell.setArguments(["-i"])
        self.shell.setProcessChannelMode(QProcess.MergedChannels)
        self.shell.readyRead.connect(self.readProcessOutput)
        self.shell.finished.connect(self.closeEvent)
        self.shell.start()
        if not self.shell.waitForStarted():
            self.append("Failed to start shell")

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
        self.shell.write(cmdString.encode())
        self.shell.write("\n".encode())

    @Slot()
    def readProcessOutput(self):
        stdOut = self.shell.readAll().data()
        self.append(stdOut.decode())
        self.backstop = self.textCursor().position()

    def quit(self):
        self.close()

    def closeEvent(self, event):
        self.shell.kill()
        self.shell.waitForFinished()
        self.close()


class Main:
    def __init__(self):
        app = QApplication([])
        gui = Gui()
        gui.show()
        app.exec_()


if __name__ == "__main__":
    Main()
