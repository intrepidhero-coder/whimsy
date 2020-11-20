from PySide2.QtWidgets import QTextEdit, QApplication

print("\u202eHello World")

app = QApplication([])
gui = QTextEdit()
gui.append("\u202eHello World")
gui.append("\u202eWhat did you mean?")
gui.show()
app.exec_()



