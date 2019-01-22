import numpy as np
import random

from Board import Board

class Player():    
    def __init__(self, config, piece):
        self.board = Board(config["board_size"])
        self.piece = piece

    def select(self):
        movable = self.get_movable()
        if len(movable) > 0:
            return random.choice(movable)
        else:
            return None

    def get_movable(self):
        return [(x, y) for y in range(self.board.size) for x in range(self.board.size) if self.board.move(self.piece, x, y, test=True)]

    def move(self, piece, x, y):
        self.board.move(piece, x, y)
