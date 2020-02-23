import numpy as np

from .piece import Piece
from .board import Board


class Game:
    def __init__(self, config, player_black, player_white):
        self.board = Board(config["board_size"])
        self.player_black = player_black
        self.player_white = player_white
        self.turn_piece = Piece.BLACK
        self.done = False

    def play(self):
        flag_pass = False
        player_hash = { Piece.BLACK: self.player_black, Piece.WHITE: self.player_white }
        while True:
            player = player_hash[self.turn_piece]
            move = player.select()
            valid_moves = self.board.get_movable(self.turn_piece)
            if move is None:
                if len(valid_moves) > 0:
                    raise Exception("invalid pass")

                self.board.pass_turn(self.turn_piece)
                self.player_black.pass_turn(self.turn_piece)
                self.player_white.pass_turn(self.turn_piece)

                if flag_pass:
                    self.complete()
                    return
                else:
                    flag_pass = True
            else:
                x, y = move
                if move not in valid_moves:
                    raise Exception("invalid move ({0}, {1})".format(x, y))
                flag_pass = False
                self.board.move(self.turn_piece, x, y)
                self.player_black.move(self.turn_piece, x, y)
                self.player_white.move(self.turn_piece, x, y)
            self.turn_piece = self.turn_piece.opposite()

    def count(self):
        if not self.done:
            raise Exception("not finished")

        record = { Piece.BLACK: 0, Piece.WHITE: 0 }

        for y in range(self.board.size):
            for x in range(self.board.size):
                piece = self.board.get(x, y)
                if piece != Piece.PLAIN:
                    record[self.board.get(x, y)] += 1

        return record

    def complete(self):
        self.done = True
        self.player_black.complete()
        self.player_white.complete()
