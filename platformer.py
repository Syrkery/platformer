from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
import sys


class Log_or_reg(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('log_or_reg.ui', self)
        self.Yes.clicked.connect(self.log)
        self.No.clicked.connect(self.reg)

    def log(self):
        self.log_window = log(self)
        self.log_window.show()
        self.close()

    def reg(self):
        self.reg_window = reg(self)
        self.reg_window.show()
        self.close()


class reg(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('reg.ui', self)


class log(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('log.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Log_or_reg()
    main_window.show()
    sys.exit(app.exec())
