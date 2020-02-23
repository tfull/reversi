import glob
import random
import sys
import re

from .config import Config
from ..core import *
from ..player.builder import Builder


DEBUG = False


class Process:
    def __init__(self, name):
        self.name = name
        self.build()

    def build(self):
        self.game_config = dict(Config.get_global("game", default={}), **Config.get_process(self.name, "game", default={}))
        self.times = Config.get_process(self.name, "times", must=True)
        self.players = {}
        for name in Config.get_process(self.name, "players", must=True):
            self.players[name] = Builder.build_player(self.game_config, name, self.name)

    def allocate_piece(self):
        first = Config.get_process(self.name, "first", default="random")
        names = list(self.players.keys())
        if first == "random":
            rand = random.randint(0, 1)
            player_black = self.players[names[rand]]
            player_black.initialize(Piece.BLACK)
            player_white = self.players[names[1 - rand]]
            player_white.initialize(Piece.WHITE)
        else:
            index = names.index(first)
            player_black = self.players[first]
            player_black.initialize(Piece.BLACK)
            player_white = self.players[names[1 - index]]
            player_white.initialize(Piece.WHITE)
        return { Piece.BLACK: player_black, Piece.WHITE: player_white }

    def run(self, console=True):
        names = list(self.players.keys())
        result = { names[0]: 0, names[1]: 0, "* draw": 0 }

        for i_game in range(self.times):
            if console:
                sys.stdout.write("\033[2K\033[G")
                sys.stdout.write("process: {0} / {1} games".format(i_game + 1, self.times))
                if DEBUG:
                    for name in names:
                        player = self.players[name]
                        sys.stdout.write(", {0} ({1})".format(name, player.debug_string()))
                sys.stdout.flush()
            order = self.allocate_piece()
            game = Game(self.game_config, order[Piece.BLACK], order[Piece.WHITE])
            game.play()
            count = game.count()
            diff = count[self.players[names[0]].piece] - count[self.players[names[1]].piece]
            if diff > 0:
                result[names[0]] += 1
            elif diff < 0:
                result[names[1]] += 1
            else:
                result["* draw"] += 1

        if console:
            sys.stdout.write("\033[2K\033[G")
            sys.stdout.write("complete process! {0} games\n".format(self.times))

        for name in names:
            print("- {0}: {1} win!".format(name, result[name]))
        print("- and {0} draw!".format(result["* draw"]))
