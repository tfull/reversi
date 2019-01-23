import numpy as np

from Piece import Piece

class Board():
    def __init__(self, size):
        self.size = size
        self.board = [[Piece.PLAIN for x in range(size)] for y in range(size)]
        self.board[size // 2 - 1][size // 2 - 1] = Piece.BLACK
        self.board[size // 2 - 1][size // 2] = Piece.WHITE
        self.board[size // 2][size // 2 - 1] = Piece.WHITE
        self.board[size // 2][size // 2] = Piece.BLACK

    def get(self, x, y):
        return self.board[y][x]

    def valid_board_range(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def move(self, piece, x, y, test=False):
        if self.board[y][x] != Piece.PLAIN:
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

                if not (self.valid_board_range(px, py) and self.board[py][px] == piece.opposite()):
                    continue

                target_direction = []

                while True:
                    target_direction.append((px, py))
                    px += dx
                    py += dy
                    if not (self.valid_board_range(px, py) and self.board[py][px] == piece.opposite()):
                        break

                if self.valid_board_range(px, py) and self.board[py][px] == piece:
                    targets.append(target_direction)

        moves = [p for ts in targets for p in ts]

        if test:
            return len(moves) > 0
        else:
            if len(moves) == 0:
                raise Exception("put ({0}, {1}): illegal move".format(x, y))
            else:
                for (mx, my) in moves:
                    self.board[my][mx] = piece
                self.board[y][x] = piece
                return True

    def show(self):
        lines = [" |" + "12345678"[:self.size]]
        lines.append("-+" + "-" * self.size)
        for y in range(self.size):
            line = chr(ord("A") + y) + "|"
            for x in range(self.size):
                line += self.board[y][x].description()
            lines.append(line)
        print("\n".join(lines))
