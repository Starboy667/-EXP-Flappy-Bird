import pygame
import neat
import time
import os
import random
import neat
import pickle

WIN_WIDTH = 600
WIN_HEIGHT = 800
DRAW_LINES = True
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 40)
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
gen = 0

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5
    JUMP_VEL = -10.5
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def fall(self):
        self.tick_count += 1
        displacement = self.vel * (self.tick_count) + 0.5 * 3 * (self.tick_count) **2
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        if displacement < 0:
            displacement -= 2
        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def jump(self):
        self.vel = self.JUMP_VEL
        self.tick_count = 0
        self.height = self.y

    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotate_bird(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 < 0 - self.WIDTH:
            self.x1 = 0
            self.x2 = self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Bg:
    def __init__(self, y):
        self.y = y
        self.x1 = 0

    def draw(self, win):
        win.blit(BG_IMG, (0, 0))

class Pipe:
    VEL = 7
    GAP = 200
    PIPE_X = 500

    def __init__(self, y):
        self.y = y
        self.x = self.PIPE_X
        self.pipe_top = self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.pipe_bottom = PIPE_IMG
        self.top = 0
        self.bottom = 0

    def draw(self, win):
        self.top = self.y - self.pipe_top.get_height()
        self.bottom = self.y + self.GAP
        win.blit(self.pipe_top, (self.x, self.y - self.pipe_top.get_height()))
        win.blit(self.pipe_bottom, (self.x, self.y + self.GAP))

    def move(self):
        self.x -= self.VEL

    def pick_height(self):
        self.y = random.randrange(50, 450)

    def collide(self, bird, win):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.pipe_top)
        bottom_mask = pygame.mask.from_surface(self.pipe_bottom)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

def rotate_bird(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def draw_game(win, bg, base, birds, pipe, score, gen, alive):
    bg.draw(win)
    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipe.x + pipe.PIPE_TOP.get_width()/2, pipe.y), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipe.x + pipe.pipe_bottom.get_width()/2, pipe.y + 200), 5)
            except:
                pass
        bird.draw(win)
    pipe.draw(win)
    Score = font.render(("Score = " + str(score)), False, (255, 255, 255))
    Gen = font.render(("Gen = " + str(gen)), False, (255, 255, 255))
    Alive = font.render(("Alive = " + str(alive)), False, (255, 255, 255))
    win.blit(Score, (0, 0))
    win.blit(Alive, (0, 30))
    win.blit(Gen, (0, 60))
    pygame.display.flip()

def eval_genomes(genomes, config):
    global win, gen
    done = False
    gen += 1
    nets = []
    birds = []
    ge = []
    alive = 0
    score = 0
    base = Base(730)
    bg = Bg(0)
    pipe = Pipe(600)
    pipe.pick_height()
    clock = pygame.time.Clock()
    for test, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        alive += 1
        ge.append(genome)
    while not done and len(birds) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            # if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            #     for bird in birds:
            #         bird.jump()
            #     break
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
                pygame.quit()
                quit()
                break
        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.fall()
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipe.y), abs(bird.y - pipe.bottom)))
            if output[0] > 0.5:
                bird.jump()
        pipe.move()
        for bird in birds:
            if pipe.collide(bird, win) or bird.y + bird.img.get_height() - 10 >= 730 or bird.y < -50:
                ge[birds.index(bird)].fitness -= 1
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))
                alive -= 1
        if (pipe.x + 100 < bird.x):
            score += 1
            # for genome in ge:
            #     genome.fitness += 5
            pipe.pick_height()
            pipe.x = 600
        base.move()
        draw_game(win, bg, base, birds, pipe, score, gen, alive)

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 50)
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)