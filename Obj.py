import pygame
import random

from GameEnvironments import GameEnvironments as ge


class Obj(pygame.sprite.Sprite):
    def __init__(self, image, x, y, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.rect[0] = x
        self.rect[1] = y


class Pterosaur(Obj):
    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)
        self.ticks = 0
        self.tick_time = 0
        self.enemy_type = "pterosaur"

    def update(self, *args):
        self.move(args[0])
        self.anim()

    def anim(self):
        self.tick_time += 1

        if self.tick_time >= (ge.FPS/4):
            self.ticks = (self.ticks + 1) % 2
            self.image = pygame.image.load("assets/pterosaur/pterosaur_" + str(self.ticks) + ".png")
            self.tick_time = 0

    def move(self, speed):
        self.rect.x -= (speed + 4)
        if self.rect.x <= -200:
            self.kill()


class Cactus(Obj):
    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)
        self.enemy_type = "cactus"

    def update(self, *args):
        self.move(args[0])

    def move(self, speed):
        self.rect.x -= speed
        if self.rect.x <= -200:
            self.kill()


class Dino(Obj):
    DINO_X = 20
    DINO_Y = 300
    DINO_DOWN_Y = DINO_Y + 30
    JUMP_FORCE = -1.1

    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)

        self.color = (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))

        self.is_down = False
        self.is_jump = False
        self.ticks = 0
        self.vel = 4
        self.grav = 1.3
        self.extra_jump_force = 11
        self.jump_force = 0
        self.ticks_time = 0
        self.enemy_in_focus = None

    def update(self, *args):
        self.anim()
        self.move()

    def anim(self):
        x = self.rect.x
        y = self.rect.y

        self.ticks_time += 1
        if not self.im_in_ground():
            self.image = pygame.image.load("assets/dino/dino_0.png")
            colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
            colorImage.fill(self.color)
            self.image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        elif self.ticks_time >= (ge.FPS / 8):
            if not self.is_down:
                self.ticks = (self.ticks + 1) % 3
                self.image = pygame.image.load("assets/dino/dino_" + str(self.ticks) + ".png")
                colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
                colorImage.fill(self.color)
                self.image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y
            elif self.is_down:
                self.ticks = (self.ticks + 1) % 2
                self.image = pygame.image.load("assets/dino_down/dino_down_" + str(self.ticks) + ".png")
                colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
                colorImage.fill(self.color)
                self.image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.rect = self.image.get_rect()
                self.rect.x = x
                self.rect.y = y + 24

            self.ticks_time = 0

    def move(self):
        self.vel = self.vel + self.grav if self.vel < (self.grav + 10) else (self.grav + 10)

        self.rect.y += self.vel

        if self.im_in_ground():
            self.rect.bottom = ge.TOP_GROUND

    def jump(self):
        if self.im_in_ground():
            self.vel = self.vel * DinoExpert.JUMP_FORCE - self.extra_jump_force

    def get_down(self):
        self.is_down = True
        self.grav = 2.6
        self.extra_jump_force = 20

    def get_up(self):
        self.is_down = False
        self.grav = 1.3
        self.extra_jump_force = 10

    def im_in_ground(self):
        return self.rect.bottom >= ge.TOP_GROUND


class DinoExpert(Dino):

    def __init__(self, image, x, y, brain, genoma, id, *groups):
        super().__init__(image, x, y, *groups)
        self.brain = brain
        self.genoma = genoma
        self.id = id
        self.fitness = 0


    def get_decision(self, brain_input):
        p = self.brain.activate(brain_input)
        decision = max(enumerate(p), key=lambda x: x[1])[0]
        if p[decision] >= 0.5:
            if decision == 0:
                self.get_down()
            elif decision == 1:
                self.get_up()
            elif decision == 2:
                self.jump()


    def collisions(self, obj):
        col = pygame.sprite.spritecollide(self, obj, False)
        if col:
            self.genoma.fitness -= 45
            self.fitness -= 45
            self.kill()
        else:
            self.genoma.fitness += 0.1
            self.fitness += 0.1


class DinoHuman(Dino):
    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)

    def events(self, events):
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_UP or events.key == pygame.K_SPACE:
                self.jump()
            elif events.key == pygame.K_DOWN:
                self.get_down()
        elif events.type == pygame.KEYUP:
            if events.key == pygame.K_DOWN:
                self.get_up()

    def collisions(self, obj):
        col = pygame.sprite.spritecollide(self, obj, False)
        if col:
            print("Morreu")
