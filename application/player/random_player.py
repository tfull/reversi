import random

from .default_player import DefaultPlayer

class RandomPlayer(DefaultPlayer):
    def __init__(self, config, piece=None, name="random", options=None):
        super(RandomPlayer, self).__init__(config, piece)
        options = {} if options is None else options
        self.name = name
        self.engine = "RandomPlayer"

    def select(self):
        movable = self.board.get_movable(self.piece)
        if len(movable) > 0:
            return random.choice(movable)
        else:
            return None
