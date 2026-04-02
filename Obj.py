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
        self.passed = False

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
        self.passed = False

    def update(self, *args):
        self.move(args[0])

    def move(self, speed):
        self.rect.x -= speed
        if self.rect.x <= -200:
            self.kill()


class Dino(Obj):
    DINO_X = 20.0
    DINO_Y = 300.0
    DINO_DOWN_Y = DINO_Y + 30.0
    JUMP_FORCE = -23.0

    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)

        self.color = (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))

        self.is_down = False
        self.is_jump = False
        self.down_timer = 0
        self.ticks = 0
        self.vel = 4
        self.grav = 1.3
        self.jump_force = 0
        self.ticks_time = 0
        self.enemy_in_focus = None

    def update(self, *args):
        self.anim()
        self.move()

    def anim(self):
        x = self.rect.x
        bottom = self.rect.bottom

        self.ticks_time += 1

        if not self.im_in_ground():
            self.image = pygame.image.load("assets/dino/dino_0.png")

            colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
            colorImage.fill(self.color)
            self.image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = bottom

        elif self.ticks_time >= (ge.FPS / 8):

            if not self.is_down:
                self.ticks = (self.ticks + 1) % 3
                self.image = pygame.image.load(f"assets/dino/dino_{self.ticks}.png")

            else:
                self.ticks = (self.ticks + 1) % 2
                self.image = pygame.image.load(f"assets/dino_down/dino_down_{self.ticks}.png")

            colorImage = pygame.Surface(self.image.get_size()).convert_alpha()
            colorImage.fill(self.color)
            self.image.blit(colorImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.bottom = bottom

            self.ticks_time = 0

    def move(self):
        if self.down_timer > 0:
            self.down_timer -= 1
            self.is_down = True
            self.grav = 3
        else:
            self.is_down = False
            self.grav = 1.3

        self.vel += self.grav
        if self.vel > 10:
            self.vel = 10

        self.rect.y += self.vel

        if self.rect.bottom >= ge.TOP_GROUND:
            self.rect.bottom = ge.TOP_GROUND
            self.vel = 0

    def jump(self):
        if self.im_in_ground():
            self.down_timer = 0
            self.is_down = False
            self.grav = 1.3
            self.vel = self.JUMP_FORCE

    def get_down(self):
        self.down_timer = 10

    def im_in_ground(self):
        return self.rect.bottom >= ge.TOP_GROUND - 1


class DinoExpert(Dino):

    def __init__(self, image, x, y, brain, genoma, id, color, *groups):
        super().__init__(image, x, y, *groups)
        self.brain = brain
        self.genoma = genoma
        self.id = id
        self.fitness = 0
        self.color = color

    def get_decision(self, brain_input):
        p = self.brain.activate(brain_input)

        # Output 0 = jump
        # Output 1 = down

        if p[0] > 0.5:
            self.jump()

        if p[1] > 0.5:
            self.get_down()

    def collisions(self, obj):
        col = pygame.sprite.spritecollide(self, obj, False)
        if col:
            self.plus_fitness(-50)
            self.kill()
        else:
            self.plus_fitness(0.01)

    def plus_fitness(self, value):
        self.genoma.fitness += value
        self.fitness += value


class DinoHuman(Dino):
    def __init__(self, image, x, y, *groups):
        super().__init__(image, x, y, *groups)

    def events(self, events):
        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_UP or events.key == pygame.K_SPACE:
                self.jump()
            elif events.key == pygame.K_DOWN:
                self.get_down()

    def collisions(self, obj):
        col = pygame.sprite.spritecollide(self, obj, False)
        if col:
            print("Morreu")
