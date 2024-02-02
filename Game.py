import pygame
from GameEnvironments import GameEnvironments as ge
from Obj import Obj, DinoExpert, Cactus, DinoHuman, Pterosaur
import random
import neat


class Game:

    def __init__(self, genomas, config, ia_playing):
        self.ground_sprite = pygame.sprite.Group()
        self.dino_sprite = pygame.sprite.Group()
        self.enemies_sprite = pygame.sprite.Group()
        self.dino = None
        self.ia_playing = ia_playing
        self.tick_game = 0
        self.ground1 = Obj("assets/ground.png", 0, ge.WINDOW_HEIGHT - 26, self.ground_sprite)
        self.ground2 = Obj("assets/ground.png", ge.WINDOW_WIDTH, ge.WINDOW_HEIGHT - 26, self.ground_sprite)
        self.distance_to_next_enemy = ge.WINDOW_WIDTH
        self.ticks_text = 0
        self.max_game_speed = 20
        self.dino_enemy_focus = False
        self.show_game_info = False
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 15)

        self.enemies_data = [
            {
                "sprite": "assets/cactus/catus_1.png",
                "y": 620,
                "type": "cactus"
            },
            {
                "sprite": "assets/cactus/catus_2.png",
                "y": 620,
                "type": "cactus"
            },
            {
                "sprite": "assets/cactus/catus_3.png",
                "y": 640,
                "type": "cactus"
            },
            {
                "sprite": "assets/pterosaur/pterosaur_0.png",
                "y": 500,
                "type": "pterosaur"
            }
        ]
        if ia_playing:
            for id, genoma in genomas:
                brain = neat.nn.FeedForwardNetwork.create(genoma, config)
                genoma.fitness = 0
                DinoExpert("assets/dino/dino_0.png", 20, DinoExpert.DINO_Y, brain, genoma, id, self.dino_sprite)
        else:
            self.dino = DinoHuman("assets/dino/dino_0.png", 20, DinoExpert.DINO_Y, self.dino_sprite)

        self.game_speed = 8
        self.distance_last_enemy = 0

    def draw(self, window):
        self.ground_sprite.draw(window)
        self.dino_sprite.draw(window)
        self.enemies_sprite.draw(window)
        if self.ia_playing and self.show_game_info:
            self.draw_dino_status(window)
        if self.dino_enemy_focus:
            self.draw_dino_focus(window)

    def update(self):
        self.tick_game += 1
        if self.tick_game >= 150:
            self.game_speed = self.game_speed + 1 if self.game_speed <= self.max_game_speed else self.max_game_speed
            self.tick_game = 0

        self.anim_ground()
        self.ground_sprite.update()
        self.dino_sprite.update()
        self.enemies_sprite.update(self.game_speed)
        self.generate_enemies()
        self.collisions()

        if self.ia_playing:
            self.get_dino_decisions()

        return len(self.dino_sprite.sprites())

    def anim_ground(self):
        self.ground1.rect[0] -= self.game_speed
        self.ground1.rect[0] = self.ground1.rect[0] % (-ge.WINDOW_WIDTH)

        self.ground2.rect[0] -= self.game_speed
        self.ground2.rect[0] = self.ground1.rect[0] % ge.WINDOW_WIDTH

    def generate_enemies(self):
        all_enemies = self.enemies_sprite.sprites()
        total_enemies = len(all_enemies)
        distance_last_enemy = 2000

        if total_enemies > 0:
            last_enemy = all_enemies[total_enemies - 1]
            distance_last_enemy = abs(ge.WINDOW_WIDTH - last_enemy.rect.x)

        if ge.get_probability(0.2) and distance_last_enemy >= self.distance_to_next_enemy:
            enemy_data = self.enemies_data[3]
            Pterosaur(enemy_data["sprite"], ge.WINDOW_WIDTH-100, random.randrange(500, 601), self.enemies_sprite)
            self.distance_to_next_enemy = random.randrange(750, 2000)

        elif distance_last_enemy >= self.distance_to_next_enemy:
            enemy_type = random.randrange(0, 3)
            enemy_data = self.enemies_data[enemy_type]
            Cactus(enemy_data["sprite"], ge.WINDOW_WIDTH, enemy_data["y"], self.enemies_sprite)
            self.distance_to_next_enemy = random.randrange(750, 2000)

    def get_dino_decisions(self):
        all_dinos = self.dino_sprite.sprites()
        all_cactus = self.enemies_sprite.sprites()

        for dino in all_dinos:
            next_cactus = self.find_next_cactus(dino)
            distance_to_next_cactus = abs(dino.rect.x - next_cactus.rect.x) if next_cactus is not None else ge.WINDOW_WIDTH
            height_next_cactus = abs(next_cactus.rect.bottom - ge.WINDOW_HEIGHT) if next_cactus is not None else 0
            brain_input = (distance_to_next_cactus/ge.WINDOW_WIDTH, height_next_cactus/160, self.game_speed/self.max_game_speed)
            dino.enemy_in_focus = next_cactus
            dino.get_decision(brain_input)

    def find_next_cactus(self, dino):
        all_enemies = self.enemies_sprite.sprites()
        all_enemies.sort(key=lambda x: x.rect.x, reverse=False)
        total_enemies = len(all_enemies)

        if total_enemies <= 0:
            return None

        if total_enemies == 1 and dino.rect.left <= (all_enemies[0].rect.right + 5):
            return all_enemies[0]

        for cactus in all_enemies:
            if dino.rect.left <= (cactus.rect.right + 5):
                return cactus

        return None

    def collisions(self):
        if self.ia_playing:
            all_dinos = self.dino_sprite.sprites()
            for dino in all_dinos:
                dino.collisions(self.enemies_sprite)
        else:
            self.dino.collisions(self.enemies_sprite)

    def manual_generate_enemies(self, events):
        if events.type == pygame.KEYUP:
            if events.key == pygame.K_c:
                enemy_type = random.randrange(0, 3)
                enemy_data = self.enemies_data[enemy_type]
                Cactus(enemy_data["sprite"], ge.WINDOW_WIDTH, enemy_data["y"], self.enemies_sprite)
            elif events.key == pygame.K_p:
                enemy_data = self.enemies_data[3]
                Pterosaur(enemy_data["sprite"], ge.WINDOW_WIDTH, random.randrange(500, 601), self.enemies_sprite)
            elif events.key == pygame.K_s:
                self.game_speed += 1
                if self.game_speed > self.max_game_speed:
                    self.max_game_speed = self.game_speed
            elif events.key == pygame.K_e:
                self.dino_enemy_focus = not self.dino_enemy_focus
            elif events.key == pygame.K_g:
                self.show_game_info = not self.show_game_info

    def draw_dino_focus(self, window):
        all_dinos = self.dino_sprite.sprites()
        for dino in all_dinos:
            if dino.enemy_in_focus is not None:
                pygame.draw.line(window, dino.color, (dino.rect.x+50, dino.rect.y), (dino.enemy_in_focus.rect.x, dino.enemy_in_focus.rect.y))

    def draw_dino_status(self, window):
        text_surface = self.font.render("GAME SPEED: " + str(self.game_speed), True, (0,0,0))
        text_rect = text_surface.get_rect()
        text_rect.x = ge.WINDOW_WIDTH - 150
        text_rect.y = 10
        window.blit(text_surface, text_rect)


        # self.ticks_text += 1
        all_dinos = self.dino_sprite.sprites()
        x = 10
        y = 10

        # if self.ticks_text >= (ge.FPS/2):
        #     all_dinos.sort(key=lambda x: x.fitness, reverse=False)
        #     self.ticks_text = 0

        for dino in all_dinos:
            text_surface = self.font.render(str(dino.id) + ": " + "{:.1f}".format(dino.fitness), True, dino.color)
            text_rect = text_surface.get_rect()
            text_rect.x = x
            text_rect.y = y
            window.blit(text_surface, text_rect)
            y += 20

            if y >= 300:
                x += 100
                y = 10





