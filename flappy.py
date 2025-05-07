import pygame as pg
from pygame.locals import *
import random

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
gap = 200 # pipe gap
frequency = 1500 #ms
last_pipe = pg.time.get_ticks() - frequency
score = 0
high_score = 0
pass_pipe = False

# Load Images
bg = pg.image.load('img/bg.png')
ground = pg.image.load('img/ground.png')
restart_btn = pg.image.load('img/restart.png')

# Draw the text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Reset game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(HEIGHT / 2)
    flappy.vel = 0
    return 0

# Bird Class
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pg.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

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
            self.image = pg.transform.rotate(self.images[self.index], -90)

# Pipe Class
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, position):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/pipe.png')
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

# Button Class
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

# Sprite Groups
bird_group = pg.sprite.Group()
pipe_group = pg.sprite.Group()

flappy = Bird(100, int(HEIGHT / 2))
bird_group.add(flappy)

# Restart Button Instance
button = Button(WIDTH // 2 - 50, HEIGHT // 2, restart_btn)

# Game Loop
run = True
while run:
    clock.tick(FPS)
    screen.blit(bg, (0, 0))
    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    screen.blit(ground, (gr_scroll, 768))

    # Score check
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and \
           bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and \
           not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, WHITE, WIDTH // 2, 20)

    # Collision
    if pg.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False

    # Pipe generation and scrolling
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

        pipe_group.update()

        # Game Over Screen
    if game_over:
        # Draw subtle dark overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # RGBA: last value is alpha (transparency)
        screen.blit(overlay, (0, 0))

        # Draw game over texts
        draw_text("GAME OVER", font, WHITE, WIDTH // 2 - 150, HEIGHT // 2 - 200)
        draw_text(f"SCORE = {score}", font, WHITE, WIDTH // 2 - 100, HEIGHT // 2 - 140)
        draw_text(f"HIGH SCORE = {high_score}", font, WHITE, WIDTH // 2 - 180, HEIGHT // 2 - 80)

        if button.draw():
            game_over = False
            if score > high_score:
                high_score = score
            score = reset_game()


    # Event handling
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
            elif game_over:
                game_over = False
                if score > high_score:
                    high_score = score
                score = reset_game()

        # Show start screen if game hasn't started yet
    if not flying and not game_over:
        # Draw semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  # dark transparent overlay
        screen.blit(overlay, (0, 0))

        # Draw instruction text
        draw_text("PRESS SPACEBAR TO START", font, WHITE, WIDTH // 2 - 300, HEIGHT // 2 - 50)


    pg.display.update()

pg.quit()
