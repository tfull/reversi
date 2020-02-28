import random

from .default_player import DefaultPlayer

class CuiPlayer(DefaultPlayer):
    def __init__(self, config, piece=None, name="random", options=None):
        super(CuiPlayer, self).__init__(config, piece)
        options = {} if options is None else options
        self.name = name
        self.mode = "start"

    def select(self):
        self.mode = "put"
        self.position = None

        while True:
            if self.position is not None:
                p = self.position
                self.position = None
                return p
            else:
                time.sleep(0.1)

        self.mode = "wait"
