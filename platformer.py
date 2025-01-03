from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QTextBrowser
import sys, sqlite3


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
        self.pl_name = self.findChild(QPlainTextEdit, 'player_name')
        self.mail = self.findChild(QPlainTextEdit, 'email')
        self.password = self.findChild(QPlainTextEdit, 'pass')
        self.rep_password = self.findChild(QPlainTextEdit, 'pass_rep')
        self.problems = self.findChild(QTextBrowser, 'problems')
        self.Back.clicked.connect(self.go_back)
        self.Confirm.clicked.connect(self.confirm)

    def confirm(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        player_name = self.player_name.toPlainText()
        email = self.email.toPlainText()
        password = self.pas.toPlainText()
        pass_rep = self.pass_rep.toPlainText()

        def pass_check(parol, rep):
            up = sym = num = 0
            if len(parol) < 8:
                self.problems.append('Password must be at least 8 characters.')
            if parol != rep:
                self.problems.append("Passwords do not match.")
            for i in parol:
                if i.isdigit():
                    num += 1
                elif i.isupper():
                    up += 1
                elif not i.isalnum():
                    sym += 1
            if up < 1:
                self.problems.append('Password must contain at least 1 uppercase letter.')
            if sym < 1:
                self.problems.append('Password must contain at least 1 special character.')
            if num < 1:
                self.problems.append('Password must contain at least 1 number.')
            return all([len(parol) >= 8, parol == rep, up >= 1, sym >= 1, num >= 1])

        try:
            name_check = [row[0] for row in cur.execute("SELECT name FROM players").fetchall()]
            email_check = [row[0] for row in cur.execute("SELECT email FROM players").fetchall()]
        except sqlite3.Error as e:
            print(e)

        try:
            name_ch = player_name not in name_check
            email_ch = email not in email_check
            pass_valid = pass_check(password, pass_rep)
        except Exception as e:
            print(e)

        try:
            if name_ch and email_ch and pass_valid:
                try:
                    cur.execute(
                        "INSERT INTO players (name, email, password, score) VALUES (?, ?, ?, ?)",
                        (player_name, email, password, 0)
                    )
                    con.commit()
                    self.problems.append('Registration successful!')
                    self.open_main_window()
                except sqlite3.Error as e:
                    self.problems.append(f"Database error: {e}")
            else:
                if not name_ch:
                    self.problems.append("Username already exists.")
                if not email_ch:
                    self.problems.append("Email already exists.")
        except Exception as e:
            print(e)

        con.close()

    def open_main_window(self):
        self.main_window = main()
        self.main_window.show()
        self.close()

    def go_back(self):
        self.parent.show()
        self.close()


class log(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        uic.loadUi('log.ui', self)
        self.pl_name = self.findChild(QPlainTextEdit, 'player_name')
        self.mail = self.findChild(QPlainTextEdit, 'email')
        self.password = self.findChild(QPlainTextEdit, 'pass')
        self.Back.clicked.connect(self.go_back)
        self.Confirm.clicked.connect(self.confirm)

    def confirm(self):
        try:
            con = sqlite3.connect('platformer.sqlite')
            cur = con.cursor()
            name = mail = passw = False
            pl_name = self.pl_name.toPlainText()
            e_mail = self.mail.toPlainText()
            pasw = self.password.toPlainText()
        except Exception as e:
            print(e)

        try:
            name_check = cur.execute("SELECT name FROM players").fetchall()
            email_check = cur.execute("SELECT email FROM players WHERE name = ?", (pl_name,)).fetchall()
            pasw_check = cur.execute("SELECT password FROM players WHERE name = ?", (pl_name,)).fetchall()
        except sqlite3.Error as e:
            self.problems.append(f"Database error: {str(e)}")
            return
        if (pl_name,) in name_check:
            name = True
        else:
            self.problems.append('Invalid pl_name')
            self.user_name.clear()

        if (e_mail,) in email_check:
            mail = True
        else:
            self.problems.append('Invalid e-mail')
            self.email.clear()

        if (pasw,) in pasw_check:
            passw = True
        else:
            self.problems.append('Invalid password')
            self.password.clear()

        if name and mail and passw:
            self.problems.append('OK!')
            self.open_main_window()
        con.close()

    def open_main_window(self):
        self.main_window = main()
        self.main_window.show()
        self.close()

    def go_back(self):
        self.parent.show()
        self.close()


class main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Log_or_reg()
    main_window.show()
    sys.exit(app.exec())
