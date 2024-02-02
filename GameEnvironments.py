import random


class GameEnvironments:
    WINDOW_HEIGHT = 720
    WINDOW_WIDTH = 1366
    FPS = 30
    TOP_GROUND = 712

    def __init__(self):
        pass

    @staticmethod
    def get_probability(probability):
        return random.random() <= probability
