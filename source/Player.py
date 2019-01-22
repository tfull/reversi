import numpy as np
import random

from Piece import Piece

class Player():    
    def __init__(self, resource, piece):
        self.board = resource.create_board()
        self.board_size = resource.board_size
        self.piece = piece

    def select(self):
        movable = self.get_movable()
        if len(movable) > 0:
            return random.choice(movable)
        else:
            return "pass"

    def valid_board_range(self, x, y):
        return x >= 0 and x < self.board_size and y >= 0 and y < self.board_size

    def get_movable(self):
        return [(x, y) for y in range(self.board_size) for x in range(self.board_size) if self.put(self.piece, x, y, test=True)]

    def debug_print(self):
        print(self)
        for y in range(self.board_size):
            for x in range(self.board_size):
                print(self.board[y, x], end="")
            print()

    def put(self, piece, x, y, test=False):
        if self.board[y, x] != Piece.PLAIN.value:
            if test:
                return False
            else:
                raise Exception("put ({0}, {1}): no plain cell".format(x, y))

        targets = []

        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                px = x + dx
                py = y + dy

                if not (self.valid_board_range(px, py) and self.board[py, px] == piece.opposite().value):
                    continue

                target_direction = []

                while True:
                    target_direction.append((px, py))
                    px += dx
                    py += dy
                    if not (self.valid_board_range(px, py) and self.board[py, px] == piece.opposite().value):
                        break

                if self.valid_board_range(px, py) and self.board[py, px] == piece.value:
                    targets.append(target_direction)

        moves = [p for ts in targets for p in ts]

        if test:
            return len(moves) > 0
        else:
            if len(moves) == 0:
                raise Exception("no put")
            else:
                for (mx, my) in moves:
                    self.board[my, mx] = piece.value
                self.board[y, x] = piece.value
                return True
