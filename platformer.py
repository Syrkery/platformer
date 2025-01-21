import pygame
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QTextBrowser, QLabel, QPushButton
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
        self.problems = self.findChild(QTextBrowser, 'problems')
        self.Back.clicked.connect(self.go_back)
        self.Confirm.clicked.connect(self.confirm)

    def confirm(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()

        pl_name = self.pl_name.toPlainText()
        e_mail = self.mail.toPlainText()
        pasw = self.password.toPlainText()

        try:
            user_data = cur.execute(
                "SELECT email, password FROM players WHERE name = ?", (pl_name,)
            ).fetchone()
            if not user_data:
                self.problems.append('Invalid username.')
                self.pl_name.clear()
            elif user_data[0] != e_mail:
                self.problems.append('Invalid email.')
                self.mail.clear()
            elif user_data[1] != pasw:
                self.problems.append('Invalid password.')
                self.password.clear()
            else:
                self.problems.append('Login successful!')
                self.open_main_window()
        except sqlite3.Error as e:
            self.problems.append(f"Database error: {e}")
        finally:
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
        try:
            self.label = self.findChild(QLabel, 'label')
            self.play_button = self.findChild(QPushButton, 'play')
            self.editor_button = self.findChild(QPushButton, 'editor')
            self.stats_button = self.findChild(QPushButton, 'stats')
            self.levels_button = self.findChild(QPushButton, 'levels_ch')
            self.logout_button = self.findChild(QPushButton, 'exit')
        except Exception as e:
            print(e)

        self.play_button.clicked.connect(self.open_game_window)
        self.editor_button.clicked.connect(self.open_editor_window)
        self.stats_button.clicked.connect(self.open_stats_window)
        self.levels_button.clicked.connect(self.open_levels_window)
        self.logout_button.clicked.connect(self.logout)

    def set_user(self, username):
        self.label.setText(f"Добро пожаловать, {username}!")

    def open_game_window(self):
        self.game_window = GameWindow()
        self.game_window.show()
        self.close()

    def open_editor_window(self):
        self.editor_window = EditorWindow(self)
        self.editor_window.show()
        self.close()

    def open_stats_window(self):
        self.stats_window = StatsWindow(self)
        self.stats_window.show()
        self.close()

    def open_levels_window(self):
        self.levels_window = LevelsWindow(self)
        self.levels_window.show()
        self.close()

    def logout(self):
        self.login_window = Log_or_reg()
        self.login_window.show()
        self.close()


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("game.ui", self)
        self.init_pygame()

    def init_pygame(self):
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            self.clock = pygame.time.Clock()

            self.running = True
            self.score = 0
            self.health = 100
            self.time_elapsed = 0

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_game)
            self.timer.start(16)

            self.player = pygame.Rect(400, 500, 50, 50)

            self.platforms = [
                pygame.Rect(300, 400, 200, 20),
                pygame.Rect(500, 300, 200, 20),
                pygame.Rect(100, 200, 200, 20)
            ]

            self.enemies = [pygame.Rect(350, 370, 40, 40)]

            self.objects = [pygame.Rect(120, 180, 20, 20)]
        except Exception as e:
            print(e)

    def update_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.close()

        if not self.running:
            return

        self.time_elapsed += 1 / 60
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_ip(5, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_ip(0, -5)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_ip(0, 5)

        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 0, 255), self.player)
        for platform in self.platforms:
            pygame.draw.rect(self.screen, (0, 255, 0), platform)
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, (255, 0, 0), enemy)
        for obj in self.objects:
            pygame.draw.rect(self.screen, (255, 255, 0), obj)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        health_text = font.render(f"Health: {self.health}", True, (255, 255, 255))
        time_text = font.render(f"Time: {int(self.time_elapsed)}s", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(health_text, (10, 50))
        self.screen.blit(time_text, (10, 90))

        pygame.display.flip()
        self.clock.tick(60)

    def closeEvent(self, event):
        self.running = False
        pygame.quit()
        event.accept()


class EditorWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Редактор уровней")
        self.setGeometry(100, 100, 800, 600)
        self.show()


class StatsWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Статистика")
        self.setGeometry(100, 100, 800, 600)
        self.show()


class LevelsWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Выбор уровня")
        self.setGeometry(100, 100, 800, 600)
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Log_or_reg()
    main_window.show()
    sys.exit(app.exec())
