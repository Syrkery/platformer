import pygame
import sqlite3
import random
from pygame.math import Vector2


class CoinAnimation:
    def __init__(self, position):
        self.particles = []
        self.position = position
        self.create_particles()
        self.duration = 0.8
        self.time_passed = 0.0

    def create_particles(self):
        for _ in range(8):
            angle = random.uniform(0, 2 * 3.1415)
            speed = random.uniform(1, 3)
            velocity = Vector2(speed * 0.8, 0).rotate_rad(angle)
            self.particles.append({
                'pos': Vector2(self.position),
                'vel': velocity,
                'size': random.randint(4, 8),
                'alpha': 255
            })

    def update(self, dt):
        self.time_passed += dt
        for p in self.particles:
            p['pos'] += p['vel'] * dt * 60
            p['vel'].y += 0.1 * dt * 60
            p['alpha'] = max(0, 255 - int(self.time_passed / self.duration * 255))
            p['size'] = max(1, p['size'] - 0.1 * dt * 60)

    def is_dead(self):
        return self.time_passed >= self.duration

    def draw(self, screen):
        for p in self.particles:
            surface = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            color = (255, 255, 0, p['alpha'])
            pygame.draw.circle(surface, color, (p['size'], p['size']), p['size'])
            screen.blit(surface, p['pos'] - Vector2(p['size'], p['size']))


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

        self.coin_animations = []
        self.explosions = []

        self.load_level()

        self.font = pygame.font.Font(pygame.font.match_font('consolas', 'monospace'), 24)

    def load_progress(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS results 
                     (id INTEGER PRIMARY KEY, score INT, health INT, time REAL, jumps INT, dies INT)''')
        result = cur.execute("SELECT score, health, time, jumps, dies FROM results ORDER BY id DESC LIMIT 1").fetchone()
        con.close()
        if result:
            self.score, self.health, self.time_elapsed, self.jump, self.die = result
        else:
            self.score, self.health, self.time_elapsed, self.jump, self.die = 0, 100, 0, 0, 0

    def save_progress(self):
        con = sqlite3.connect('platformer.sqlite')
        cur = con.cursor()
        cur.execute("INSERT INTO results (score, health, time) VALUES (?, ?, ?)",
                    (self.score, self.health, self.time_elapsed))
        con.commit()
        con.close()

    def load_level(self):
        try:
            level_file = f"level_{(self.score // 100) + 1}.txt"
            with open(level_file, "r") as f:
                lines = f.readlines()
            self.platforms = [pygame.Rect(*map(int, line.split())) for line in lines[0].split(";") if line]
            self.spikes = [pygame.Rect(*map(int, line.split())) for line in lines[1].split(";") if line]
            self.colours = [tuple(map(int, line.split())) for line in lines[2].split(";") if line]
            self.coins = [pygame.Rect(*map(int, c.split())) for c in lines[3].strip().split(";")]
        except FileNotFoundError:
            self.running = False

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
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < 5000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
            pygame.display.flip()
            self.clock.tick(30)

    def game_loop(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.time_elapsed += dt
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
                self.jump += 1

            if keys[pygame.K_q]:
                self.save_progress()

            if keys[pygame.K_r]:
                self.show_results()

            self.player_velocity.y += self.gravity
            self.player.move_ip(self.player_velocity.x, self.player_velocity.y)

            if self.player.top > self.screen.get_height():
                self.respawn_player()

            self.check_collisions()

            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (0, 0, 255), self.player)
            for platform in self.platforms:
                pygame.draw.rect(self.screen, self.colours[self.platforms.index(platform)], platform)

            for spike in self.spikes:
                pygame.draw.polygon(self.screen, (255, 0, 0),
                                    [(spike.x, spike.y + spike.height), (spike.x + spike.width // 2, spike.y),
                                     (spike.x + spike.width, spike.y + spike.height)])

            for coin in self.coins:
                pygame.draw.rect(self.screen, (255, 255, 0), coin)

            for anim in self.coin_animations:
                anim.draw(self.screen)

            self.update_animations(dt)

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
                if platform.top <= self.player.bottom <= platform.top + 10:
                    self.player.bottom = platform.top
                    self.player_velocity.y = 0
                    self.on_ground = True

        for spike in self.spikes:
            if self.player.colliderect(spike):
                self.health = max(0, self.health - 10)
                self.resp()
                if self.health <= 0:
                    self.respawn_player()
                    self.die += 1

        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.score += 10
                self.coins.remove(coin)
                self.coin_animations.append(CoinAnimation(coin.center))
                if self.score % 100 == 0:
                    self.load_level()

    def update_animations(self, dt):
        for anim in self.coin_animations[:]:
            anim.update(dt)
            if anim.is_dead():
                self.coin_animations.remove(anim)

    def resp(self):
        self.player.topleft = self.start_position
        self.player_velocity = pygame.Vector2(0, 0)

    def respawn_player(self):
        self.health = 100
        self.score = 0
        self.save_progress()
        self.load_level()
        self.player.topleft = self.start_position
        self.player_velocity = pygame.Vector2(0, 0)


if __name__ == "__main__":
    game = Game()
    game.game_loop()
