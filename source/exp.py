import random
import sys

from Piece import Piece
from Board import Board
from StandAlone import Game
from RandomPlayer import RandomPlayer
from DeepLearningPlayer import DeepLearningPlayer

def run():
    config = { "board_size": 8 }
    n_game = 10000
    random_player = RandomPlayer(config, options = { "name": "random" })
    dl_player = DeepLearningPlayer(config, options = { "name": "deep" })

    for i_game in range(n_game):
        coin = random.randint(1, 2)
        random_player.initialize(Piece(coin))
        dl_player.initialize(Piece(3 - coin))
        player_black, player_white = (random_player, dl_player) if coin == 1 else (dl_player, random_player)
        players = { Piece.BLACK: player_black, Piece.WHITE: player_white }
        game = Game(config, player_black, player_white)
        game.play()
        count = game.count()
        diff = count[Piece.BLACK] - count[Piece.WHITE]
        if diff > 0:
            win_string = player_black.name + "(x) won!"
        elif diff < 0:
            win_string = player_white.name + "(o) won!"
        else:
            win_string = "draw!"
        status_string = "{0} (x) {1} - {2} (o) {3}".format(player_black.name, count[Piece.BLACK], count[Piece.WHITE], player_white.name)
        print(win_string + ": " + status_string)
        dl_player.learn()

def train(config, n_game, dl_player, other_player):
    for i_game in range(n_game):
        sys.stdout.write("\033[2K\033[Gtrain: {0}".format(i_game + 1))
        sys.stdout.flush()
        piece = random.choice([Piece.BLACK, Piece.WHITE])
        dl_player.initialize(piece)
        other_player.initialize(piece.opposite())
        players = {}
        players[dl_player.piece] = dl_player
        players[other_player.piece] = other_player
        game = Game(config, players[Piece.BLACK], players[Piece.WHITE])
        game.play()
        dl_player.learn()
    sys.stdout.write("\033[2K\033[G")
    sys.stdout.write("train: complete {} games\n".format(n_game))

def test(config, n_game, dl_player, other_player):
    count_win = 0
    count_lose = 0
    count_draw = 0
    for i_game in range(n_game):
        sys.stdout.write("\033[2K\033[Gtest: {0}".format(i_game + 1))
        sys.stdout.flush()
        piece = random.choice([Piece.BLACK, Piece.WHITE])
        dl_player.initialize(piece)
        other_player.initialize(piece.opposite())
        players = {}
        players[dl_player.piece] = dl_player
        players[other_player.piece] = other_player
        game = Game(config, players[Piece.BLACK], players[Piece.WHITE])
        game.play()
        count = game.count()
        diff = count[dl_player.piece] - count[dl_player.piece.opposite()]
        if diff > 0:
            count_win += 1
        elif diff < 0:
            count_lose += 1
        else:
            count_draw += 1

    sys.stdout.write("\033[2K\033[G")
    print("test: {0} win, {1} lose, {2} draw".format(count_win, count_lose, count_draw))

def main():
    config = { "board_size": 8 }
    random_player = RandomPlayer(config, options = { "name": "random" })
    dl_player = DeepLearningPlayer(config, options = { "name": "deep" })
    dl_player.setup_brain()
    dl_player.set_mode("train")
    train(config, 1000, dl_player, random_player)
    dl_player.set_mode("test")
    test(config, 100, dl_player, random_player)

if __name__ == '__main__':
    # run()
    main()
