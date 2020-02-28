from .piece import Piece

class Board():
    def __init__(self, size):
        self.size = size
        self.board = [[Piece.PLAIN for x in range(size)] for y in range(size)]
        self.board[size // 2 - 1][size // 2 - 1] = Piece.BLACK
        self.board[size // 2 - 1][size // 2] = Piece.WHITE
        self.board[size // 2][size // 2 - 1] = Piece.WHITE
        self.board[size // 2][size // 2] = Piece.BLACK
        self.history = []

    def get(self, x, y):
        return self.board[y][x]

    def valid_board_range(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size

    def get_movable(self, piece):
        return [(x, y) for y in range(self.size) for x in range(self.size) if self.move(piece, x, y, test=True)]

    def full(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == Piece.PLAIN:
                    return False

        return True

    def undo(self):
        if len(self.history) > 0:
            piece, xy_list = self.history[-1]
            del self.history[-1]
            if len(xy_list) > 0:
                x, y = xy_list[0]
                self.board[y][x] = Piece.PLAIN
                for (x, y) in xy_list[1:]:
                    self.board[y][x] = self.board[y][x].opposite()
        else:
            raise Exception("no undo")

    def pass_turn(self, piece):
        self.history.append((piece, []))

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
                history_cell = [(x, y)] + moves
                self.history.append((piece, history_cell))
                return True

    def show(self):
        lines = [" |" + "123456789abcdef0"[:self.size]]
        lines.append("-+" + "-" * self.size)
        for y in range(self.size):
            line = chr(ord("A") + y) + "|"
            for x in range(self.size):
                line += self.board[y][x].description()
            lines.append(line)
        print("\n".join(lines))

    def copy_array(self, board, piece):
        fun = lambda x: (0 if x == Piece.PLAIN else (1 if x == piece else -1))
        return [[fun(board[y][x]) for x in range(self.size)] for y in range(self.size)]

    def get_array(self, piece):
        return self.copy_array(self.board, piece)

    def get_history_array(self, piece):
        size = self.size
        board = [[Piece.PLAIN for x in range(size)] for y in range(size)]
        board[size // 2 - 1][size // 2 - 1] = Piece.BLACK
        board[size // 2 - 1][size // 2] = Piece.WHITE
        board[size // 2][size // 2 - 1] = Piece.WHITE
        board[size // 2][size // 2] = Piece.BLACK

        array_list = [self.copy_array(board, piece)]

        for (p, cell) in self.history:
            if len(cell) == 0:
                continue

            x, y = cell[0]
            board[y][x] = piece
            for (x, y) in cell[1:]:
                board[y][x] = board[y][x].opposite()

            array_list.append(self.copy_array(board, piece))

        return array_list

    def get_score(self, piece):
        score = 0
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == piece:
                    score += 1
                elif self.board[y][x] == piece.opposite():
                    score -= 1

        return score
