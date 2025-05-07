import pygame as pg
from pygame.locals import *
import random
from collections import deque

pg.init()

clock = pg.time.Clock()
FPS = 60

WIDTH = 864
HEIGHT = 936

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Flappy Bird')

# Define font and color
font = pg.font.SysFont('Bauhaus 93', 60)
WHITE = (255, 255, 255)

# Game Variables
gr_scroll = 0
scroll_spd = 4
flying = False
game_over = False
gap = 200
frequency = 1500
last_pipe = pg.time.get_ticks() - frequency
score = 0
high_score = 0
pass_pipe = False
game_over_time = 0
pipe_queue = deque()  # queue to store pipes

# Load Images
bg = pg.image.load('img/bg.png')
ground = pg.image.load('img/ground.png')
restart_btn = pg.image.load('img/restart.png')

# Draw text with center anchor
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

# Reset game
def reset_game():
    pipe_group.empty()
    pipe_queue.clear()
    flappy.rect.x = 100
    flappy.rect.y = int(HEIGHT / 2)
    flappy.vel = 0
    return 0

# Bird class
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.images = [pg.image.load(f'img/bird{n}.png') for n in range(1, 4)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            self.vel = min(self.vel, 8)
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            keys = pg.key.get_pressed()
            if (pg.mouse.get_pressed()[0] == 1 or keys[pg.K_SPACE]) and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pg.mouse.get_pressed()[0] == 0 and not keys[pg.K_SPACE]:
                self.clicked = False

            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)

            self.image = pg.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pg.transform.rotate(self.images[self.index], -90)

# Pipe class
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, position):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pg.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - gap // 2]
        if position == -1:
            self.rect.topleft = [x, y + gap // 2]

    def update(self):
        self.rect.x -= scroll_spd
        if self.rect.right < 0:
            self.kill()

# Button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos) and pg.mouse.get_pressed()[0] == 1:
            action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Sprite groups
bird_group = pg.sprite.Group()
pipe_group = pg.sprite.Group()
flappy = Bird(100, int(HEIGHT / 2))
bird_group.add(flappy)

button = Button(WIDTH // 2 - 50, HEIGHT // 2, restart_btn)

# Game loop
run = True
while run:
    clock.tick(FPS)
    screen.blit(bg, (0, 0))
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    screen.blit(ground, (gr_scroll, 768))

    if not game_over and flying:
        # Pipe generation
        time_now = pg.time.get_ticks()
        if time_now - last_pipe > frequency:
            pipe_height = random.randint(-300, 100)
            top_pipe = Pipe(WIDTH, HEIGHT // 2 + pipe_height, 1)
            btm_pipe = Pipe(WIDTH, HEIGHT // 2 + pipe_height, -1)
            pipe_group.add(top_pipe)
            pipe_group.add(btm_pipe)
            pipe_queue.append((top_pipe, btm_pipe))
            last_pipe = time_now

        # Scroll
        gr_scroll -= scroll_spd
        if abs(gr_scroll) > 35:
            gr_scroll = 0

        pipe_group.update()

    # Score checking
    if not game_over and flying and len(pipe_queue) > 0:
        next_top, next_btm = pipe_queue[0]
        if flappy.rect.left > next_top.rect.right:
            score += 1
            pass_pipe = False
            pipe_queue.popleft()

    draw_text(str(score), font, WHITE, WIDTH // 2, 50)

    # Collision
    if pg.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            game_over = True
            flying = False
            game_over_time = pg.time.get_ticks()
            if score > high_score:
                high_score = score

    if flappy.rect.bottom >= 768:
        if not game_over:
            game_over = True
            flying = False
            game_over_time = pg.time.get_ticks()
            if score > high_score:
                high_score = score

    # Game Over UI
    if game_over:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        draw_text("GAME OVER", font, WHITE, WIDTH // 2, HEIGHT // 2 - 200)
        draw_text(f"SCORE = {score}", font, WHITE, WIDTH // 2, HEIGHT // 2 - 120)
        draw_text(f"HIGH SCORE = {high_score}", font, WHITE, WIDTH // 2, HEIGHT // 2 - 40)

        if pg.time.get_ticks() - game_over_time > 1000:
            if button.draw():
                game_over = False
                score = reset_game()

    # Start screen
    if not flying and not game_over:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        draw_text("PRESS SPACEBAR TO START", font, WHITE, WIDTH // 2, HEIGHT // 2)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if not flying and not game_over:
                flying = True
                flappy.vel = -10
            elif game_over and pg.time.get_ticks() - game_over_time > 1000:
                game_over = False
                score = reset_game()
        if event.type == pg.MOUSEBUTTONDOWN:
            if not flying and not game_over:
                flying = True
                flappy.vel = -10

    pg.display.update()

pg.quit()
