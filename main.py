import pygame
from GameEnvironments import GameEnvironments as ge
from Game import Game
import neat


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
            if not self.ia_playing:
                self.game.dino.events(events)
            else:
                self.game.manual_generate_enemies(events)

    def update(self, genomas, config):
        self.game = Game(genomas, config, self.ia_playing)
        self.loop = True
        while self.loop:
            self.draw()
            self.events()
            self.fps.tick(ge.FPS)
            if self.game.update() <= 0:
                self.loop = False
                break
            pygame.display.update()


ia_playing = True

if ia_playing:
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, 'config.txt')
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    population.run(Main(ia_playing).update)
else:
    Main(ia_playing).update(None, None)
