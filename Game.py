import pygame
from GameEnvironments import GameEnvironments as ge
from Obj import Obj, DinoExpert, Cactus, DinoHuman, Pterosaur
import random


class Game:

    def __init__(self, population, ia_playing):
        """
        population: lista de NeuralNetwork (um por dino) quando ia_playing=True,
                    ou None quando humano está jogando.
        """
        self.ground_sprite = pygame.sprite.Group()
        self.dino_sprite = pygame.sprite.Group()
        self.enemies_sprite = pygame.sprite.Group()
        self.dino = None
        self.ia_playing = ia_playing
        self.tick_game = 0
        self.ground1 = Obj("assets/ground.png", 0, ge.WINDOW_HEIGHT - 26, self.ground_sprite)
        self.ground2 = Obj("assets/ground.png", ge.WINDOW_WIDTH, ge.WINDOW_HEIGHT - 26, self.ground_sprite)
        self.distance_to_next_enemy = ge.WINDOW_WIDTH / 2
        self.ticks_text = 0
        self.max_game_speed = 20
        self.dino_enemy_focus = False
        self.show_game_info = True
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.spawn_pterosaur = False

        self.enemies_data = [
            {"sprite": "assets/cactus/catus_1.png", "y": 620, "type": "cactus"},
            {"sprite": "assets/cactus/catus_2.png", "y": 620, "type": "cactus"},
            {"sprite": "assets/cactus/catus_3.png", "y": 640, "type": "cactus"},
            {"sprite": "assets/pterosaur/pterosaur_0.png", "y": 500, "type": "pterosaur"},
        ]

        # Mapeamento índice → DinoExpert (para recuperar fitness ao final)
        self._dino_by_index: dict[int, DinoExpert] = {}

        if ia_playing:
            for idx, brain in enumerate(population):
                color = (
                    random.randrange(50, 256),
                    random.randrange(50, 256),
                    random.randrange(50, 256),
                )
                dino = DinoExpert(
                    "assets/dino/dino_0.png",
                    20, DinoExpert.DINO_Y,
                    brain, idx, color,
                    self.dino_sprite
                )
                self._dino_by_index[idx] = dino
        else:
            self.dino = DinoHuman("assets/dino/dino_0.png", 20, DinoExpert.DINO_Y, self.dino_sprite)

        self.game_speed = 8

    # ------------------------------------------------------------------
    # Fitness
    # ------------------------------------------------------------------

    def get_fitness_scores(self):
        """Retorna lista de fitness na ordem original da população."""
        n = len(self._dino_by_index)
        scores = [0.0] * n
        for idx, dino in self._dino_by_index.items():
            scores[idx] = dino.fitness
        return scores

    # ------------------------------------------------------------------
    # Draw / Update
    # ------------------------------------------------------------------

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
            self.get_dino_decisions()

        return len(self.dino_sprite.sprites())

    # ------------------------------------------------------------------
    # Ground
    # ------------------------------------------------------------------

    def anim_ground(self):
        self.ground1.rect.x -= self.game_speed
        self.ground2.rect.x -= self.game_speed

        if self.ground1.rect.right <= 0:
            self.ground1.rect.x = self.ground2.rect.right
        if self.ground2.rect.right <= 0:
            self.ground2.rect.x = self.ground1.rect.right

    # ------------------------------------------------------------------
    # Enemies
    # ------------------------------------------------------------------

    def generate_enemies(self):
        all_enemies = self.enemies_sprite.sprites()
        total_enemies = len(all_enemies)
        last_enemy = None

        if total_enemies > 0:
            last_enemy = all_enemies[-1]
            distance_last_enemy = abs(ge.WINDOW_WIDTH - last_enemy.rect.x)
        else:
            distance_last_enemy = 2000

        MIN_TIME = 1.5
        min_safe_distance = self.game_speed * ge.FPS * MIN_TIME

        if distance_last_enemy < max(self.distance_to_next_enemy, min_safe_distance):
            return

        allow_pterosaur = self.game_speed >= 0
        self.spawn_pterosaur = self.spawn_pterosaur or (ge.get_probability(0.005) and allow_pterosaur)

        if self.spawn_pterosaur:
            if last_enemy and last_enemy.enemy_type == "cactus":
                return

            enemy_data = self.enemies_data[3]
            Pterosaur(enemy_data["sprite"], ge.WINDOW_WIDTH, random.randrange(500, 601), self.enemies_sprite)
            self.spawn_pterosaur = False

        if not self.spawn_pterosaur:
            if last_enemy and last_enemy.enemy_type == "pterosaur":
                spawn_cactus = ge.get_probability(0.05)
            else:
                spawn_cactus = ge.get_probability(0.06)

            if spawn_cactus:
                enemy_type = random.randrange(0, 3)
                enemy_data = self.enemies_data[enemy_type]
                Cactus(enemy_data["sprite"], ge.WINDOW_WIDTH, enemy_data["y"], self.enemies_sprite)

        self.distance_to_next_enemy = random.randrange(
            int(min_safe_distance),
            int(min_safe_distance * 2)
        )

    # ------------------------------------------------------------------
    # IA decisions
    # ------------------------------------------------------------------

    def get_dino_decisions(self):
        for dino in self.dino_sprite.sprites():
            next_enemies = self.find_next_enemies(dino)

            dist = ge.WINDOW_WIDTH
            height = 0
            etype = 0

            if next_enemies:
                e1 = next_enemies[0]
                dist = abs(dino.rect.x - e1.rect.x)
                height = abs(e1.rect.bottom - ge.WINDOW_HEIGHT)
                etype = 1 if e1.enemy_type == "pterosaur" else 0

            brain_input = [
                dist / ge.WINDOW_WIDTH,
                height / 160,
                etype,
                self.game_speed / self.max_game_speed,
            ]

            dino.enemy_in_focus = next_enemies[0] if next_enemies else None
            dino.get_decision(brain_input)

    def find_next_enemies(self, dino):
        enemies = sorted(self.enemies_sprite.sprites(), key=lambda e: e.rect.x)
        for enemy in enemies:
            if dino.rect.left <= (enemy.rect.right + 5):
                return [enemy]
        return []

    # ------------------------------------------------------------------
    # Collisions & rewards
    # ------------------------------------------------------------------

    def collisions(self):
        if self.ia_playing:
            for dino in self.dino_sprite.sprites():
                dino.collisions(self.enemies_sprite)
        else:
            self.dino.collisions(self.enemies_sprite)

    def reward_passed_enemies(self):
        all_dinos = self.dino_sprite.sprites()
        for enemy in self.enemies_sprite.sprites():
            if enemy.passed:
                continue
            for dino in all_dinos:
                if enemy.rect.right < dino.rect.left:
                    enemy.passed = True
                    for d in all_dinos:
                        d.plus_fitness(10)
                    break

    # ------------------------------------------------------------------
    # Manual / debug controls
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------

    def draw_dino_focus(self, window):
        for dino in self.dino_sprite.sprites():
            if dino.enemy_in_focus is not None:
                pygame.draw.line(
                    window, dino.color,
                    (dino.rect.x + 50, dino.rect.y),
                    (dino.enemy_in_focus.rect.x, dino.enemy_in_focus.rect.y)
                )

    def draw_dino_status(self, window):
        text_surface = self.font.render("GAME SPEED: " + str(self.game_speed), True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.x = ge.WINDOW_WIDTH - 150
        text_rect.y = 10
        window.blit(text_surface, text_rect)

        x, y = 10, 10
        for dino in self.dino_sprite.sprites():
            text_surface = self.font.render(
                str(dino.id) + ": " + "{:.1f}".format(dino.fitness),
                True, dino.color
            )
            text_rect = text_surface.get_rect()
            text_rect.x = x
            text_rect.y = y
            window.blit(text_surface, text_rect)
            y += 20
            if y >= 300:
                x += 100
                y = 10