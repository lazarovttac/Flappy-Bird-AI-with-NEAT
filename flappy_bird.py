

import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 275
WIN_HEIGHT = 500

BIRD_IMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")), pygame.image.load(
    os.path.join("imgs", "bird2.png")), pygame.image.load(os.path.join("imgs", "bird3.png"))]

PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))

STAT_FONT = pygame.font.SysFont("lato", 25)

# The bird class is the player


class Bird:
    # Multiple images for animation
    IMGS = BIRD_IMGS

    # Tilting variables
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -5.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -80:
                self.tilt -= self.ROT_VEL

    # Animation
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -70:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 100
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        # Storing to types of Pipes, one that faces up, and one that faces down. (Images)
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, WIN_HEIGHT / 2)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        bottom_offset = (int(self.x - bird.x),
                         int(self.bottom - round(bird.y)))
        top_offset = (int(self.x - bird.x), int(self.top - round(bird.y)))

        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        if t_point or b_point:
            return True
        else:
            return False


class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # Two x positions, for two images, one starts at 0, and the other at its WIDTH
        # That means that we have to images, one after each other
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        # Then we move them at the same speed
        # And when any of them is of screen it automatically returns it back to teh other side
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)

    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(WIN_WIDTH/2, WIN_HEIGHT/2)
    base = Base(WIN_HEIGHT - BASE_IMG.get_height() / 2)
    pipes = [Pipe(WIN_WIDTH + (WIN_WIDTH / 3))]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True

    clock = pygame.time.Clock()
    score = 0

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # bird.move()
        add_pipe = False
        remove = []
        for pipe in pipes:
            if pipe.collide(bird):
                pass

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH + (WIN_WIDTH / 3)))

        for pipe in remove:
            pipes.remove(pipe)

        if bird.y + bird.img.get_height() > WIN_HEIGHT:
            pass

        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()


main()
