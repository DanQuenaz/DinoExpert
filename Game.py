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
        self.show_game_info = True
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

                # 🎨 se não tiver cor, cria uma
                if not hasattr(genoma, "color"):
                    genoma.color = (
                        random.randrange(50, 256),
                        random.randrange(50, 256),
                        random.randrange(50, 256)
                    )

                DinoExpert("assets/dino/dino_0.png",20, DinoExpert.DINO_Y, brain, genoma, id, genoma.color, self.dino_sprite)
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
        if self.tick_game >= 600:
            self.game_speed = self.game_speed + 1 if self.game_speed < self.max_game_speed else self.max_game_speed
            self.tick_game = 0

        self.anim_ground()
        self.ground_sprite.update()
        self.dino_sprite.update()
        self.enemies_sprite.update(self.game_speed)
        self.generate_enemies()
        self.collisions()

        if self.ia_playing:
            self.reward_passed_enemies()

        if self.ia_playing:
            self.get_dino_decisions()

        return len(self.dino_sprite.sprites())

    def anim_ground(self):
        self.ground1.rect.x -= self.game_speed
        self.ground2.rect.x -= self.game_speed

        if self.ground1.rect.right <= 0:
            self.ground1.rect.x = self.ground2.rect.right

        if self.ground2.rect.right <= 0:
            self.ground2.rect.x = self.ground1.rect.right

    def generate_enemies(self):
        all_enemies = self.enemies_sprite.sprites()
        total_enemies = len(all_enemies)
        distance_last_enemy = 2000
        last_enemy = None

        if total_enemies > 0:
            last_enemy = all_enemies[-1]
            distance_last_enemy = abs(ge.WINDOW_WIDTH - last_enemy.rect.x)

        can_spawn = distance_last_enemy >= self.distance_to_next_enemy

        if not can_spawn:
            return

        allow_pterosaur = self.game_speed >= 10

        spawn_pterosaur = ge.get_probability(0.2) and allow_pterosaur

        min_distance_between_types = 350

        if spawn_pterosaur:
            if last_enemy and last_enemy.enemy_type == "cactus" and distance_last_enemy < min_distance_between_types:
                return

            enemy_data = self.enemies_data[3]
            Pterosaur(
                enemy_data["sprite"],
                ge.WINDOW_WIDTH - 100,
                random.randrange(500, 601),
                self.enemies_sprite
            )

        else:
            if last_enemy and last_enemy.enemy_type == "pterosaur" and distance_last_enemy < min_distance_between_types:
                return

            enemy_type = random.randrange(0, 3)
            enemy_data = self.enemies_data[enemy_type]
            Cactus(
                enemy_data["sprite"],
                ge.WINDOW_WIDTH,
                enemy_data["y"],
                self.enemies_sprite
            )

        self.distance_to_next_enemy = random.randrange(750, 2000)

    def get_dino_decisions(self):
        all_dinos = self.dino_sprite.sprites()

        for dino in all_dinos:
            next_enemies = self.find_next_two_enemies(dino)

            # Defaults
            dist1 = ge.WINDOW_WIDTH
            height1 = 0
            type1 = 0
            width1 = 0

            dist2 = ge.WINDOW_WIDTH
            height2 = 0
            type2 = 0
            width2 = 0

            if len(next_enemies) >= 1:
                e1 = next_enemies[0]
                dist1 = abs(dino.rect.x - e1.rect.x)
                height1 = abs(e1.rect.bottom - ge.WINDOW_HEIGHT)
                type1 = 1 if e1.enemy_type == "pterosaur" else 0
                width1 = e1.rect.width

            if len(next_enemies) >= 2:
                e2 = next_enemies[1]
                dist2 = abs(dino.rect.x - e2.rect.x)
                height2 = abs(e2.rect.bottom - ge.WINDOW_HEIGHT)
                type2 = 1 if e2.enemy_type == "pterosaur" else 0
                width2 = e2.rect.width

            brain_input = (
                dist1 / ge.WINDOW_WIDTH,
                height1 / 160,
                type1,
                width1 / 100,

                dist2 / ge.WINDOW_WIDTH,
                height2 / 160,
                type2,
                width2 / 100,

                self.game_speed / self.max_game_speed
            )

            dino.enemy_in_focus = next_enemies[0] if len(next_enemies) > 0 else None
            dino.get_decision(brain_input)

    def find_next_two_enemies(self, dino):
        enemies = self.enemies_sprite.sprites()
        enemies.sort(key=lambda x: x.rect.x)

        next_enemies = []

        for enemy in enemies:
            if dino.rect.left <= (enemy.rect.right + 5):
                next_enemies.append(enemy)
                if len(next_enemies) == 2:
                    break

        return next_enemies

    def collisions(self):
        if self.ia_playing:
            all_dinos = self.dino_sprite.sprites()
            for dino in all_dinos:
                dino.collisions(self.enemies_sprite)
        else:
            self.dino.collisions(self.enemies_sprite)

    def reward_passed_enemies(self):
        all_dinos = self.dino_sprite.sprites()
        all_enemies = self.enemies_sprite.sprites()

        for enemy in all_enemies:
            if enemy.passed:
                continue

            for dino in all_dinos:
                if enemy.rect.right < dino.rect.left:
                    enemy.passed = True

                    for d in all_dinos:
                        d.plus_fitness(10)

                    break

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





