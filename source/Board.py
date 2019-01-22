from Piece import Piece

class Board():
    def __init__(self, size):
        self.size = size
        self.board = [[Piece.PLAIN.value for x in range(size)] for y in range(size)]
        self.board[size // 2 - 1][size // 2 - 1] = Piece.BLACK.value
        self.board[size // 2 - 1][size // 2] = Piece.WHITE.value
        self.board[size // 2][size // 2 - 1] = Piece.WHITE.value
        self.board[size // 2][size // 2] = Piece.BLACK.value

    def valid_board_range(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def move(self, piece, x, y, test=False):
        if self.board[y][x] != Piece.PLAIN.value:
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

                if not (self.valid_board_range(px, py) and self.board[py][px] == piece.opposite().value):
                    continue

                target_direction = []

                while True:
                    target_direction.append((px, py))
                    px += dx
                    py += dy
                    if not (self.valid_board_range(px, py) and self.board[py][px] == piece.opposite().value):
                        break

                if self.valid_board_range(px, py) and self.board[py][px] == piece.value:
                    targets.append(target_direction)

        moves = [p for ts in targets for p in ts]

        if test:
            return len(moves) > 0
        else:
            if len(moves) == 0:
                raise Exception("put ({0}, {1}): illegal move".format(x, y))
            else:
                for (mx, my) in moves:
                    self.board[my][mx] = piece.value
                self.board[y][x] = piece.value
                return True

    def show(self):
        lines = [" |" + "12345678"[:self.size]]
        lines.append("-+" + "-" * self.size)
        for y in range(self.size):
            line = chr(ord("A") + y) + "|"
            for x in range(self.size):
                line += Piece(self.board[y][x]).description()
            lines.append(line)
        print("\n".join(lines))
