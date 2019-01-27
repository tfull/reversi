from Board import Board

class Player():    
    def __init__(self, config, piece):
        self.config = config
        self.initialize(piece)

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
