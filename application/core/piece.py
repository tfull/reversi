from enum import Enum

class Piece(Enum):
    PLAIN = 0
    BLACK = 1
    WHITE = 2

    def __str__(self):
        if self == Piece.BLACK:
            return "black"
        elif self == Piece.WHITE:
            return "white"
        else:
            return "plain"

    def opposite(self):
        if self == Piece.BLACK:
            return Piece.WHITE
        elif self == Piece.WHITE:
            return Piece.BLACK
        else:
            raise Exception("opposite of plain")

    def description(self):
        if self == Piece.BLACK:
            return "x"
        elif self == Piece.WHITE:
            return "o"
        else:
            return "."
