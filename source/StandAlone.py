import numpy as np

from Piece import Piece
from RandomPlayer import RandomPlayer

class Resource():
    def __init__(self, options):
        self.board = None
        self.board_size = options["board_size"]

    def create_board(self):
        if self.board is not None:
            return np.copy(self.board)

        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.board[3, 3] = Piece.BLACK.value
        self.board[3, 4] = Piece.WHITE.value
        self.board[4, 3] = Piece.WHITE.value
        self.board[4, 4] = Piece.BLACK.value
        return np.copy(self.board)

class Game():
    def __init__(self, resource, player_black, player_white):
        self.board = resource.create_board()
        self.board_size = resource.board_size
        self.player_black = player_black
        self.player_white = player_white
        self.turn_piece = Piece.BLACK

    def play(self):
        flag_pass = False
        while True:
            player = { Piece.BLACK: self.player_black, Piece.WHITE: self.player_white }[self.turn_piece]
            move = player.select()
            print(self.turn_piece, move)
            if move == "pass":
                if flag_pass:
                    return
                else:
                    flag_pass = True
            else:
                x, y = move
                flag_pass = False
                self.put(self.turn_piece, x, y)
                self.player_black.put(self.turn_piece, x, y)
                self.player_white.put(self.turn_piece, x, y)
            self.turn_piece = self.turn_piece.opposite()

    def valid_board_range(self, x, y):
        return x >= 0 and x < self.board_size and y >= 0 and y < self.board_size

    def put_result(self):
        for y in range(self.board_size):
            for x in range(self.board_size):
                print(str(self.board[y, x]), end="")
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

def main():
    resource = Resource({ "board_size": 8 })
    game = Game(resource, RandomPlayer(resource, Piece.BLACK), RandomPlayer(resource, Piece.WHITE))
    game.play()
    game.put_result()

if __name__ == "__main__":
    main()
