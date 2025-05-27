import pygame as pg
from pygame.locals import *
import random
import os, sys
import pathlib, json, sys, os

def resource_path(rel_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, rel_path)


APP_DIR  = pathlib.Path(os.getenv("APPDATA", pathlib.Path.home())) / "FlappyBird"
APP_DIR.mkdir(exist_ok=True)

HS_PATH  = APP_DIR / "highscore.txt"

def load_highscore() -> int:
    try:
        return int(HS_PATH.read_text())
    except (FileNotFoundError, ValueError):
        return 0

def save_highscore(val: int):
    HS_PATH.write_text(str(val))

pg.init()



clock = pg.time.Clock()
FPS = 60

WIDTH = 864
HEIGHT = 936

overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
overlay.fill((0, 0, 0, 120))


screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('Flappy Bird')

# Font and color
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
high_score = load_highscore()
pass_pipe = False
new_highscore = False
game_over_time = None

# Load Images
bg = pg.image.load(resource_path('img/bg-edit.png'))
ground = pg.image.load(resource_path('img/ground-edit.png'))
restart_btn = pg.image.load(resource_path('img/restart.png'))

# Text render
# Fungsi baru untuk menampilkan teks terpusat secara horizontal
def draw_text(text, font, text_color, y_ratio):
    img = font.render(text, True, text_color)
    rect = img.get_rect(center=(WIDTH // 2, int(HEIGHT * y_ratio)))
    screen.blit(img, rect)


# Reset
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(HEIGHT / 2)
    flappy.vel = 0
    return 0

# Bird
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pg.image.load(resource_path(f'img/bird{num}-edit.png'))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.dead_image = pg.transform.rotate(self.images[self.index], -90)


    def update(self):
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
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
            self.image = self.dead_image

# Pipe
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, position):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(resource_path('img/pipe-edit.png'))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pg.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(gap / 2)]

    def update(self):
        self.rect.x -= scroll_spd
        if self.rect.right < 0:
            self.kill()
            

# Button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Groups
bird_group = pg.sprite.Group()
pipe_group = pg.sprite.Group()

flappy = Bird(100, int(HEIGHT / 2))
bird_group.add(flappy)

button = Button(WIDTH // 2 - 50, HEIGHT // 2, restart_btn)

# Main Loop
run = True
while run:
    clock.tick(FPS)
    screen.blit(bg, (0, 0))
    bg_overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    bg_overlay.fill((0, 0, 0, 100)) 
    screen.blit(bg_overlay, (0, 0))

    bird_group.draw(screen)
    if not game_over:
        bird_group.update()
    pipe_group.draw(screen)
    screen.blit(ground, (gr_scroll, 768))
    screen.blit(font.render(str(int(clock.get_fps())), True, WHITE), (10, 10)) 



    # Score logic
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and \
           bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and \
           not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, WHITE, 0.05)

    # Collision
    if pg.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        if not game_over:
            game_over = True
            game_over_time = pg.time.get_ticks()
            if score > high_score:
                high_score = score
                new_highscore = True
                save_highscore(high_score)
                

    if flappy.rect.bottom >= 768:
        if not game_over:
            game_over = True
            game_over_time = pg.time.get_ticks()
            if score > high_score:
                high_score = score
                new_highscore = True
                save_highscore(high_score)
        flying = False

    if not game_over and flying:
        time_now = pg.time.get_ticks()
        if time_now - last_pipe > frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, -1)
            top_pipe = Pipe(WIDTH, int(HEIGHT / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        gr_scroll -= scroll_spd
        if abs(gr_scroll) > 35:
            gr_scroll = 0
        if not game_over:
            pipe_group.update()

    if game_over:
        screen.blit(overlay, (0, 0))

        draw_text("GAME OVER", font, WHITE, 0.3)
        draw_text(f"SCORE = {score}", font, WHITE, 0.37)
        if new_highscore:
            draw_text("NEW HIGHSCORE!", font, WHITE, 0.44)
        else:
            draw_text(f"HIGH SCORE = {high_score}", font, WHITE, 0.44)

        if game_over_time and pg.time.get_ticks() - game_over_time >= 1000:
            if button.draw():
                game_over = False
                new_highscore = False
                score = reset_game()
                game_over_time = None

    # Events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True
            flappy.vel = -10
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if not flying and not game_over:
                flying = True
                flappy.vel = -10
            elif game_over and game_over_time and pg.time.get_ticks() - game_over_time >= 1000:
                game_over = False
                new_highscore = False
                score = reset_game()
                game_over_time = None

    if not flying and not game_over:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        draw_text("PRESS SPACEBAR TO START", font, WHITE, 0.5)

    pg.display.update()

pg.quit()
