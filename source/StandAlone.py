import numpy as np

from Piece import Piece
from Board import Board
from RandomPlayer import RandomPlayer

class Game():
    def __init__(self, config, player_black, player_white):
        self.board = Board(config["board_size"])
        self.player_black = player_black
        self.player_white = player_white
        self.turn_piece = Piece.BLACK

    def play(self):
        flag_pass = False
        player_hash = { Piece.BLACK: self.player_black, Piece.WHITE: self.player_white }
        while True:
            player = player_hash[self.turn_piece]
            move = player.select()
            print(self.turn_piece, move)
            if move is None:
                if flag_pass:
                    return
                else:
                    flag_pass = True
            else:
                x, y = move
                flag_pass = False
                self.board.move(self.turn_piece, x, y)
                self.player_black.move(self.turn_piece, x, y)
                self.player_white.move(self.turn_piece, x, y)
            self.turn_piece = self.turn_piece.opposite()

def main():
    config = { "board_size": 8 }
    player_black = RandomPlayer(config, Piece.BLACK)
    player_white = RandomPlayer(config, Piece.WHITE)
    game = Game(config, player_black, player_white)
    game.play()
    game.board.show()

if __name__ == "__main__":
    main()
