import pygame
import sqlite3


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Platformer Game")
        self.clock = pygame.time.Clock()

        self.running = True
        self.load_progress()

        self.gravity = 0.5
        self.jump_strength = -10
        self.player_speed = 5
        self.on_ground = False
        self.player_velocity = pygame.Vector2(0, 0)

        self.start_position = (150, 500)
        self.player = pygame.Rect(*self.start_position, 50, 50)

        self.platforms = [
            pygame.Rect(380, 500, 200, 20),
            pygame.Rect(500, 380, 200, 20),
            pygame.Rect(120, 330, 200, 20),
            pygame.Rect(200, 450, 150, 20),
            pygame.Rect(400, 250, 200, 20),
            pygame.Rect(500, 125, 150, 20),
            pygame.Rect(250, 175, 100, 20)
        ]

        self.spikes = [
            pygame.Rect(380, 480, 20, 20),
            pygame.Rect(550, 360, 20, 20),
            pygame.Rect(250, 310, 20, 20),
            pygame.Rect(560, 230, 20, 20),
            pygame.Rect(520, 230, 20, 20),
            pygame.Rect(480, 230, 20, 20)
        ]

        self.colours = [
            (180, 180, 180),
            (255, 255, 255),
            (0, 0, 255),
            (255, 0, 0),
            (0, 255, 0),
            (251, 85, 1),
            (255, 0, 255)
        ]

        self.font = pygame.font.Font(pygame.font.match_font('consolas', 'monospace'), 24)

    def load_progress(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        result = cur.execute("SELECT score, health, time FROM results ORDER BY id DESC LIMIT 1").fetchone()
        con.close()
        if result:
            self.score, self.health, self.time_elapsed = result
        else:
            self.score, self.health, self.time_elapsed = 0, 100, 0

    def save_progress(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        cur.execute(
            "INSERT INTO results (score, health, time) VALUES (?, ?, ?)",
            (self.score, self.health, self.time_elapsed)
        )
        con.commit()
        con.close()

    def show_results(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        results = cur.execute("SELECT * FROM results ORDER BY id DESC").fetchall()
        con.close()

        self.screen.fill((0, 0, 0))
        y_offset = 50

        header = "{:<5} {:<10} {:<10} {:<10}".format("ID", "Score", "Health", "Time")
        header_surface = self.font.render(header, True, (255, 255, 255))
        self.screen.blit(header_surface, (50, 10))

        for row in results[:10]:
            result_text = "{:<5} {:<10} {:<10} {:<10.2f}".format(row[0], row[1], row[2], row[3])
            result_surface = self.font.render(result_text, True, (255, 255, 255))
            self.screen.blit(result_surface, (50, y_offset))
            y_offset += 40

        pygame.display.flip()
        pygame.time.wait(5000)

    def game_loop(self):
        while self.running:
            self.time_elapsed += self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_velocity.x = -self.player_speed
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_velocity.x = self.player_speed
            else:
                self.player_velocity.x = 0

            if keys[pygame.K_SPACE] and self.on_ground:
                self.player_velocity.y = self.jump_strength
                self.on_ground = False

            if keys[pygame.K_s]:
                self.save_progress()

            if keys[pygame.K_r]:
                self.show_results()

            self.player_velocity.y += self.gravity
            self.player.move_ip(self.player_velocity.x, self.player_velocity.y)

            self.check_collisions()

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (0, 0, 255), self.player)
            for platform in self.platforms:
                pygame.draw.rect(self.screen, self.colours[self.platforms.index(platform)], platform)

            for spike in self.spikes:
                pygame.draw.polygon(self.screen, (255, 0, 0),
                                    [(spike.x, spike.y + spike.height), (spike.x + spike.width // 2, spike.y),
                                     (spike.x + spike.width, spike.y + spike.height)])

            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            health_text = self.font.render(f"Health: {self.health}", True, (255, 255, 255))
            time_text = self.font.render(f"Time: {int(self.time_elapsed)}s", True, (255, 255, 255))

            self.screen.blit(score_text, (10, 10))
            self.screen.blit(health_text, (10, 50))
            self.screen.blit(time_text, (10, 90))

            pygame.display.flip()

        pygame.quit()

    def check_collisions(self):
        self.on_ground = False
        for platform in self.platforms:
            if self.player.colliderect(platform) and self.player_velocity.y >= 0:
                if self.player.bottom >= platform.top and self.player.bottom <= platform.top + 10:
                    self.player.bottom = platform.top
                    self.player_velocity.y = 0
                    self.on_ground = True

        for spike in self.spikes:
            if self.player.colliderect(spike):
                self.respawn_player()

        if self.player.bottom > 600:
            self.player.bottom = 600
            self.player_velocity.y = 0
            self.on_ground = True

    def respawn_player(self):
        self.health = 100
        self.player.topleft = self.start_position
        self.player_velocity = pygame.Vector2(0, 0)


if __name__ == "__main__":
    game = Game()
    game.game_loop()
