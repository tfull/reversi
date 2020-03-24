import queue
import threading

from ..core import *
from .default_player import DefaultPlayer


class NetworkPlayer(DefaultPlayer):
    def __init__(self, config, piece=None, name="net", options=None):
        super(NetworkPlayer, self).__init__(config, piece)
        options = {} if options is None else options
        self.name = name
        self.engine = "NetworkPlayer"
        self.config = config

    def set_queue(self, read_queue, write_queue):
        self.read_queue = read_queue
        self.write_queue = write_queue

    def move(self, piece, x, y):
        super(NetworkPlayer, self).move(piece, x, y)

        self.write_queue.put({
            "game": "move",
            "piece": str(piece),
            "target": self.history[-1]
        })

        if piece == self.piece.opposite():
            self.write_queue.put({
                "game": "movable",
                "target": self.board.get_movable(self.piece)
            })

        print("player: move", (x, y), self.piece.description())

    def select(self):
        if self.board.full():
            return None

        movable = self.board.get_movable(self.piece)

        # debug
        """
        import random
        return random.choice(movable) if len(movable) > 0 else None
        """

        while True:
            try:
                self.read_queue.get_nowait()
            except queue.Empty:
                break

        while True:
            action = self.read_queue.get()
            print("player:", action, str(movable))

            if type(action) == str:
                if action == "surrender":
                    return "surrender"
                elif action == "pass":
                    if len(movable) == 0:
                        return None
            elif type(action) == tuple:
                if len(action) == 2:
                    if type(action[0]) == int and type(action[1]) == int:
                        if action in movable:
                            return action

            self.write_queue.put({
                "game": "error",
                "message": "invalid move"
            })

    def complete(self):
        super(NetworkPlayer, self).complete()
        self.write_queue.put({ "game": "complete" })
