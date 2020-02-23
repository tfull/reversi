from ..core.board import Board


class DefaultPlayer:
    def __init__(self, config, piece, name="basic"):
        self.config = config
        self.name = name
        self.initialize(piece)
        self.game_count = 0
        self.engine = "DefaultPlayer"

    def initialize(self, piece):
        self.board = Board(self.config["board_size"])
        self.set_piece(piece)

    def set_piece(self, piece):
        self.piece = piece

    def select(self):
        movable = self.board.get_movable(self.piece)
        if len(movable) > 0:
            return movable[0]
        else:
            return None

    def move(self, piece, x, y):
        self.board.move(piece, x, y)

    def undo(self):
        self.board.undo()

    def pass_turn(self, piece):
        self.board.pass_turn(piece)

    def complete(self):
        self.game_count += 1

    def debug_string(self):
        st = self.status()
        return "piece: " + st["piece"]

    def status(self):
        st = { "name": self.name }
        if self.piece is not None:
            st["piece"] = self.piece.description()
        else:
            st["piece"] = "-"
        return st

    def print_status(self):
        status = self.status()
        order = ["piece"]
        print(self.name + ":")
        for key in order:
            if key in status:
                print("  {0}: {1}".format(key, status[key]))
