import math
import random
import sys

import pygame


# ----------------------------
# Basic configuration
# ----------------------------
WIDTH, HEIGHT = 960, 640
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
LIGHT_PINK = (255, 230, 240)
RED = (220, 40, 40)
GREEN = (60, 180, 90)
BROWN = (110, 70, 35)
YELLOW = (230, 200, 60)
BLUE = (60, 100, 220)


# ----------------------------
# Utility helpers
# ----------------------------

def load_font(size):
    """Load a stylized font, or gracefully fall back to a system font."""
    try:
        return pygame.font.Font("Lobster.ttf", size)
    except (pygame.error, FileNotFoundError):
        try:
            return pygame.font.SysFont("cursive", size, bold=True)
        except pygame.error:
            return pygame.font.SysFont("arial", size, bold=True)


# ----------------------------
# Game objects
# ----------------------------
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5.0
        self.width = 44
        self.height = 74
        self.bucket_offset_y = -12
        self.bucket_width = 46
        self.bucket_height = 28

    def move(self, keys, dt):
        if keys[pygame.K_UP]:
            self.y -= self.speed * dt * 60
        if keys[pygame.K_DOWN]:
            self.y += self.speed * dt * 60
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * dt * 60
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * dt * 60

        # Keep the player inside the play area.
        self.x = max(80, min(WIDTH - 80, self.x))
        self.y = max(140, min(HEIGHT - 120, self.y))

    def draw(self, screen):
        # Draw a simple 3D-styled character.
        body_x = self.x - self.width // 2
        body_y = self.y - self.height // 2

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 60), (body_x - 10, body_y + 70, self.width + 20, 18))

        # Legs
        pygame.draw.rect(screen, (40, 60, 120), (body_x + 8, body_y + 58, 10, 26))
        pygame.draw.rect(screen, (40, 60, 120), (body_x + 26, body_y + 58, 10, 26))

        # Torso
        pygame.draw.rect(screen, (90, 120, 220), (body_x + 8, body_y + 24, 28, 34))

        # Head
        pygame.draw.circle(screen, (240, 210, 180), (self.x, body_y + 12), 16)

        # Arms
        pygame.draw.rect(screen, (240, 210, 180), (body_x + 2, body_y + 28, 8, 24))
        pygame.draw.rect(screen, (240, 210, 180), (body_x + 34, body_y + 28, 8, 24))

        # Bucket on head
        bucket_y = body_y + self.bucket_offset_y
        pygame.draw.rect(screen, (220, 120, 40), (self.x - self.bucket_width // 2, bucket_y, self.bucket_width, self.bucket_height))
        pygame.draw.rect(screen, (180, 90, 20), (self.x - self.bucket_width // 2, bucket_y + 4, self.bucket_width, 6))
        pygame.draw.rect(screen, (250, 180, 70), (self.x - self.bucket_width // 2 + 10, bucket_y + 8, self.bucket_width - 20, self.bucket_height - 14))

    def bucket_rect(self):
        bucket_y = self.y - self.height // 2 + self.bucket_offset_y
        return pygame.Rect(self.x - self.bucket_width // 2, bucket_y, self.bucket_width, self.bucket_height)


class Cloud:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = 110
        self.speed = 1.7
        self.direction = 1
        self.width = 120
        self.height = 60

    def update(self, dt):
        self.x += self.direction * self.speed * dt * 60
        if self.x < 120 or self.x > WIDTH - 120:
            self.direction *= -1

    def draw(self, screen):
        # Draw a fluffy cotton candy cloud.
        pygame.draw.ellipse(screen, PINK, (self.x - 70, self.y - 20, 100, 50))
        pygame.draw.ellipse(screen, LIGHT_PINK, (self.x - 35, self.y - 35, 70, 50))
        pygame.draw.ellipse(screen, PINK, (self.x - 10, self.y - 25, 60, 50))
        pygame.draw.ellipse(screen, LIGHT_PINK, (self.x + 10, self.y - 20, 80, 45))
        pygame.draw.circle(screen, WHITE, (int(self.x - 25), int(self.y - 5)), 10)
        pygame.draw.circle(screen, WHITE, (int(self.x + 15), int(self.y - 8)), 8)


class Candy:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.3, 2.3)
        self.vy = random.uniform(2.2, 4.4)
        self.size = 12
        self.dead = False
        self.scale = 0.7
        self.rotation = random.uniform(-0.2, 0.2)

    def update(self, dt, player, score):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 0.03 * dt * 60

        # Simulate depth: closer to the bottom means visually larger.
        depth_factor = 1.0 - min(1.0, max(0.0, (self.y - 100) / (HEIGHT - 180)))
        self.scale = 0.8 + depth_factor * 0.85

        # Collision with bucket when candy is falling within the bucket area.
        bucket_rect = player.bucket_rect()
        candy_rect = pygame.Rect(self.x - self.size * self.scale // 2, self.y - self.size * self.scale // 2,
                                 int(self.size * self.scale), int(self.size * self.scale))
        if bucket_rect.colliderect(candy_rect):
            self.dead = True
            if self.kind == 'candy_cane':
                return 3
            if self.kind == 'toffee':
                return 10
            if self.kind == 'sour_patch':
                return 15
            if self.kind == 'chocolate':
                return 20
        return 0

    def draw(self, screen):
        size = int(self.size * self.scale)
        x, y = int(self.x), int(self.y)

        if self.kind == 'candy_cane':
            pygame.draw.rect(screen, RED, (x - size // 2, y - size // 2, size, size // 3))
            pygame.draw.rect(screen, WHITE, (x - size // 2, y - size // 6, size, size // 3))
            pygame.draw.rect(screen, RED, (x - size // 2, y + size // 6, size, size // 3))
        elif self.kind == 'toffee':
            pygame.draw.rect(screen, (145, 90, 30), (x - size // 2, y - size // 2, size, size))
            pygame.draw.rect(screen, (210, 150, 70), (x - size // 2 + 3, y - size // 2 + 3, size - 6, size - 6))
        elif self.kind == 'sour_patch':
            pygame.draw.circle(screen, (130, 200, 90), (x, y), size // 2)
            pygame.draw.circle(screen, (255, 255, 255), (x - 3, y - 2), 3)
            pygame.draw.circle(screen, (255, 255, 255), (x + 3, y - 2), 3)
            pygame.draw.line(screen, (255, 255, 255), (x - 4, y + 4), (x + 4, y + 4), 2)
        elif self.kind == 'chocolate':
            pygame.draw.rect(screen, BROWN, (x - size // 2, y - size // 2, size, size))
            pygame.draw.rect(screen, (90, 50, 20), (x - size // 2 + 3, y - size // 2 + 3, size - 6, size - 6))


# ----------------------------
# Main game class
# ----------------------------
class CandyGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Candy Catch 2.5D")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = load_font(28)
        self.big_font = load_font(72)
        self.running = True
        self.game_over = False
        self.win = False
        self.difficulty = None
        self.difficulty_name = ""

        self.player = Player(WIDTH // 2, HEIGHT - 120)
        self.cloud = Cloud()
        self.candies = []
        self.score = 0
        self.lives = 10
        self.spawn_timer = 0.0
        self.spawn_interval = 1.10

        self.background = self.make_background()

    def make_background(self):
        surf = pygame.Surface((WIDTH, HEIGHT))
        # Sky gradient
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(18 + 90 * (1 - t))
            g = int(35 + 80 * (1 - t))
            b = int(80 + 120 * (1 - t))
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

        # Horizon / perspective lines
        horizon_y = HEIGHT * 0.45
        for i in range(0, WIDTH + 1, 40):
            pygame.draw.line(surf, (255, 255, 255), (i, HEIGHT), (WIDTH // 2 + (i - WIDTH // 2) * 0.18, horizon_y), 1)

        # Ground plane
        ground_color = (80, 140, 70)
        pygame.draw.rect(surf, ground_color, (0, HEIGHT * 0.6, WIDTH, HEIGHT * 0.4))
        pygame.draw.rect(surf, (100, 180, 100), (0, HEIGHT * 0.6, WIDTH, HEIGHT * 0.4), 3)

        # Distant trees / shapes to make it feel 3D-ish
        for x in range(80, WIDTH, 120):
            y = int(HEIGHT * 0.64)
            pygame.draw.rect(surf, (70, 110, 55), (x, y - 70, 14, 70))
            pygame.draw.polygon(surf, (50, 90, 45), [(x - 25, y - 15), (x + 7, y - 70), (x + 40, y - 15)])
            pygame.draw.polygon(surf, (60, 100, 55), [(x - 15, y - 28), (x + 7, y - 84), (x + 28, y - 28)])
        return surf

    def spawn_candy(self):
        kinds = ['candy_cane', 'toffee', 'sour_patch', 'chocolate']
        kind = random.choice(kinds)
        x = self.cloud.x + random.uniform(-20, 20)
        y = self.cloud.y + 10
        self.candies.append(Candy(kind, x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def select_difficulty(self, key):
        difficulty_map = {
            pygame.K_1: ("Easy", 1.10),
            pygame.K_2: ("Medium", 0.80),
            pygame.K_3: ("Hard", 0.55),
            pygame.K_4: ("Extra Hard", 0.35),
        }
        if key in difficulty_map:
            self.difficulty_name, self.spawn_interval = difficulty_map[key]
            self.difficulty = self.difficulty_name.lower().replace(" ", "_")
            self.spawn_timer = 0.0

    def update(self, dt):
        if self.game_over or self.win:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, dt)
        self.cloud.update(dt)

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_candy()

        for candy in list(self.candies):
            gained = candy.update(dt, self.player, self.score)
            if gained:
                self.score += gained
                candy.dead = True
            if candy.dead:
                self.candies.remove(candy)
            elif candy.y > HEIGHT + 60:
                self.candies.remove(candy)
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True

        if self.score >= 100:
            self.win = True

    def draw_hud(self):
        # Hearts in top-left
        heart_y = 20
        for i in range(self.lives):
            pygame.draw.polygon(self.screen, RED, [(20 + i * 28, heart_y + 10), (28 + i * 28, heart_y), (36 + i * 28, heart_y + 10), (28 + i * 28, heart_y + 20)])
            pygame.draw.polygon(self.screen, (255, 120, 120), [(20 + i * 28, heart_y + 10), (28 + i * 28, heart_y), (36 + i * 28, heart_y + 10), (28 + i * 28, heart_y + 20)])

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH - 180, 20))

    def draw_start_screen(self):
        self.screen.blit(self.background, (0, 0))
        title = self.big_font.render("Candy Catch", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        help_text = self.font.render("Choose a difficulty with 1-4", True, WHITE)
        self.screen.blit(help_text, help_text.get_rect(center=(WIDTH // 2, 200)))

        options = [
            ("1 - Easy", (255, 255, 255)),
            ("2 - Medium", (255, 220, 120)),
            ("3 - Hard", (255, 170, 70)),
            ("4 - Extra Hard", (255, 90, 90)),
        ]
        for idx, (text, color) in enumerate(options):
            label = self.font.render(text, True, color)
            y = 270 + idx * 42
            self.screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))

        controls = self.font.render("Controls: Arrow Keys to move", True, WHITE)
        self.screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 420)))

    def draw_end_screen(self, message):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.cloud.draw(self.screen)
        for candy in self.candies:
            candy.draw(self.screen)
        self.player.draw(self.screen)
        self.draw_hud()

        if self.game_over:
            self.draw_end_screen("You Lose")
        elif self.win:
            self.draw_end_screen("You Win")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()

            if self.difficulty is None:
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        self.select_difficulty(event.key)
                self.draw_start_screen()
                pygame.display.flip()
                continue

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = CandyGame()
    game.run()
