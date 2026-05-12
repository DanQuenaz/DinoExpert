from GameEnvironments import GameEnvironments as ge
from Game import Game
from GeneticAlgorithm import GeneticAlgorithmTrainer

import os
os.environ["SDL_VIDEODRIVER"] = "windows"
os.environ["SDL_HINT_RENDER_DRIVER"] = "opengl"

import pygame


# Hiperparâmetros do algoritmo genético
GA_CONFIG = {
    "input_size": 4,           # dist, height, type, game_speed
    "hidden_layers": [8, 6],
    "output_size": 2,          # [jump, down]
    "population_size": 200,
    "mutation_rate": 0.08,
    "mutation_strength": 0.4,
    "elite_size": 5,
}


class Main:
    def __init__(self, ia_playing):
        title = "Dino Expert" if ia_playing else "Dino Noob"

        pygame.display.init()
        ge.WINDOW_WIDTH = pygame.display.Info().current_w - 100

        self.window = pygame.display.set_mode([ge.WINDOW_WIDTH, ge.WINDOW_HEIGHT])
        pygame.display.set_caption(title)

        self.loop = True
        self.fps = pygame.time.Clock()
        self.game = None
        self.ia_playing = ia_playing

    def draw(self):
        self.window.fill((255, 255, 255))
        self.game.draw(self.window)

    def events(self):
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                self.loop = False
                pygame.quit()
                exit()
            if not self.ia_playing:
                self.game.dino.events(events)
            else:
                self.game.manual_generate_enemies(events)

    def run_episode(self, population):
        """
        Roda um episódio completo com a população atual.
        Retorna lista de fitness na mesma ordem da população.
        """
        self.game = Game(population, self.ia_playing)
        self.loop = True

        while self.loop:
            self.draw()
            self.events()
            self.fps.tick(ge.FPS)

            alive = self.game.update()
            pygame.display.update()

            if alive <= 0:
                break

        # Coleta o fitness acumulado de cada dino (mesma ordem da população)
        return self.game.get_fitness_scores()

    def run_human(self):
        self.game = Game(None, self.ia_playing)
        self.loop = True
        while self.loop:
            self.draw()
            self.events()
            self.fps.tick(ge.FPS)
            if self.game.update() <= 0:
                break
            pygame.display.update()


ia_playing = True

if ia_playing:
    trainer = GeneticAlgorithmTrainer(**GA_CONFIG)

    main = Main(ia_playing)
    generation = 0

    while True:
        generation += 1
        population = trainer.population

        fitness_scores = main.run_episode(population)

        best_score = max(fitness_scores)
        avg_score = sum(fitness_scores) / len(fitness_scores)
        print(f"Geração {generation} | Melhor fitness: {best_score:.1f} | Média: {avg_score:.1f}")

        # Evolui para a próxima geração usando os fitness do jogo
        trainer.evolve(fitness_scores)

else:
    Main(ia_playing).run_human()
